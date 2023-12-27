import boto3
import utils_create_instances as utils_instances
import utils_create_scripts as utils_scripts
import utils_proxy
import utils_gatekeeper
import paramiko
from scp import SCPClient
import time
import json


if __name__ == "__main__":
    ec2_ressource = boto3.resource("ec2")
    ec2_client = boto3.client('ec2')
    ami_id = "ami-0fc5d935ebf8bc3bc" # ami for ubuntu instances
    ami_id = "ami-0c7217cdde317cfec" # for my aws free tier ubuntu instances

    response_vpcs = ec2_client.describe_vpcs()
    vpc_id = response_vpcs.get('Vpcs', [{}])[0].get('VpcId', '') # we use the default subnet
    # It should already have multiple subnets listed, on different availability zones
    # (at least it is the case for us with our student accounts)
    ec2_client_subnets = ec2_client.describe_subnets()['Subnets']


    key_pair_name = "key_pair_project3" 
    # Create EC2 key pair
    key_pair = utils_instances.create_key_pair(ec2_client, key_pair_name)
    info = {}

    # We want to delete everything previously created with the same name
    # so we can create them again without any conflict
    # Delete security groups (and associated instances) if they already exist
    if 0==1:
        for group_name in ["mysql_sg", "proxy_sg", "trusted_host_sg", "gatekeeper_sg"]:
            deleted = utils_instances.delete_security_group_by_name(ec2_client, group_name)

    
        security_group_mysql = utils_instances.create_security_group(ec2_client, "mysql_sg", [22, 1186, 3306, 2206])
        # Remember to remove useless ports in the security group for proxy once the gatekeeper is fully implemented
        security_group_proxy = utils_instances.create_security_group(ec2_client, "proxy_sg", [22, 80, 1186, 2206, 3306, 5000])
        security_group_trusted_host = utils_instances.create_security_group(ec2_client, "trusted_host_sg", [22, 80, 5000])
        security_group_gatekeeper = utils_instances.create_security_group(ec2_client, "gatekeeper_sg", [22, 80, 5000])



        instance_id_standalone = utils_instances.create_ec2_instances(ec2_ressource, ami_id, "t2.micro", security_group_mysql, ec2_client_subnets, key_pair_name, 1)
        info["standalone"] = {"id":instance_id_standalone}
        instance_id_master = utils_instances.create_ec2_instances(ec2_ressource, ami_id, "t2.micro", security_group_mysql, ec2_client_subnets, key_pair_name, 1)
        info["master"] = {"id":instance_id_master}
        instances_id_workers = utils_instances.create_ec2_instances(ec2_ressource, ami_id, "t2.micro", security_group_mysql, ec2_client_subnets, key_pair_name, 3)
        info["workers"] = [None,None,None]
        for idx,instances_id_work in enumerate(instances_id_workers):
            info["workers"][idx] = {"id":instances_id_work}
        instance_id_proxy = utils_instances.create_ec2_instances(ec2_ressource, ami_id, "t2.micro", security_group_proxy, ec2_client_subnets, key_pair_name, 1)
        instance_id_trusted_host = utils_instances.create_ec2_instances(ec2_ressource, ami_id, "t2.micro", security_group_trusted_host, ec2_client_subnets, key_pair_name, 1)
        instance_id_gatekeeper = utils_instances.create_ec2_instances(ec2_ressource, ami_id, "t2.micro", security_group_gatekeeper, ec2_client_subnets, key_pair_name, 1)

        all_instances_id = instance_id_standalone + instance_id_master + instances_id_workers + instance_id_proxy + instance_id_trusted_host + instance_id_gatekeeper 
        # We wait for the instances to be running
        utils_instances.wait_instances_to_run(ec2_client, all_instances_id)
        # We get the public dns name
        public_dns_list = [utils_instances.get_public_dns(ec2_client, id) for id in all_instances_id]
        private_dns_list = [utils_instances.get_private_dns(ec2_client, id) for id in all_instances_id]
        private_ip_list = [utils_instances.get_private_ip(ec2_client, id) for id in all_instances_id]
        info = {
            "standalone": {"id":instance_id_standalone[0], "private_dns":private_dns_list[0], "public_dns":public_dns_list[0], "private_ip":private_ip_list[0]},
            "master":{"id":instance_id_master[0], "private_dns":private_dns_list[1], "public_dns":public_dns_list[1], "private_ip":private_ip_list[1]},
            "workers":[{"id":instances_id_workers[0], "private_dns":private_dns_list[2], "public_dns":public_dns_list[2], "private_ip":private_ip_list[2]},
                    {"id":instances_id_workers[1], "private_dns":private_dns_list[3], "public_dns":public_dns_list[3], "private_ip":private_ip_list[3]},
                    {"id":instances_id_workers[2], "private_dns":private_dns_list[4], "public_dns":public_dns_list[4], "private_ip":private_ip_list[4]}
                    ],
            "proxy":{"id":instance_id_proxy[0], "private_dns":private_dns_list[5], "public_dns":public_dns_list[5], "private_ip":private_ip_list[5]},
            "trusted_host":{"id":instance_id_trusted_host[0], "private_dns":private_dns_list[6], "public_dns":public_dns_list[6], "private_ip":private_ip_list[6]},
            "gatekeeper":{"id":instance_id_gatekeeper[0], "private_dns":private_dns_list[7], "public_dns":public_dns_list[7], "private_ip":private_ip_list[7]}
        }

        print(public_dns_list)

        # write instance id and public dns in a file so we can use this information in other scripts
        with open('data.json', 'w') as fp:
            json.dump(info, fp)
    #    public_dns_list = None
        time.sleep(25)
        print("\n\n######\n\n")
        print(public_dns_list)
        print(info)
        exit()
    public_dns_list = ['ec2-44-211-238-6.compute-1.amazonaws.com', 'ec2-44-214-43-110.compute-1.amazonaws.com', 'ec2-3-231-222-18.compute-1.amazonaws.com', 'ec2-3-238-121-139.compute-1.amazonaws.com', 'ec2-34-229-254-222.compute-1.amazonaws.com', 'ec2-3-231-56-192.compute-1.amazonaws.com', 'ec2-34-205-9-76.compute-1.amazonaws.com', 'ec2-34-236-245-22.compute-1.amazonaws.com']
    info = {'standalone': {'id': 'i-0edef124611d77aba', 'private_dns': 'ip-172-31-12-18.ec2.internal', 'public_dns': 'ec2-44-211-238-6.compute-1.amazonaws.com', 'private_ip': '172.31.12.18'}, 'master': {'id': 'i-048aa5c3ae5591a80', 'private_dns': 'ip-172-31-14-62.ec2.internal', 'public_dns': 'ec2-44-214-43-110.compute-1.amazonaws.com', 'private_ip': '172.31.14.62'}, 'workers': [{'id': 'i-00d5d38adcf48ffde', 'private_dns': 'ip-172-31-12-185.ec2.internal', 'public_dns': 'ec2-3-231-222-18.compute-1.amazonaws.com', 'private_ip': '172.31.12.185'}, {'id': 'i-00ecb12650d698233', 'private_dns': 'ip-172-31-69-10.ec2.internal', 'public_dns': 'ec2-3-238-121-139.compute-1.amazonaws.com', 'private_ip': '172.31.69.10'}, {'id': 'i-03f4ef3a545795b6c', 'private_dns': 'ip-172-31-49-150.ec2.internal', 'public_dns': 'ec2-34-229-254-222.compute-1.amazonaws.com', 'private_ip': '172.31.49.150'}], 'proxy': {'id': 'i-0586cfc74baa63a51', 'private_dns': 'ip-172-31-8-107.ec2.internal', 'public_dns': 'ec2-3-231-56-192.compute-1.amazonaws.com', 'private_ip': '172.31.8.107'}, 'trusted_host': {'id': 'i-0e217481084067d42', 'private_dns': 'ip-172-31-5-17.ec2.internal', 'public_dns': 'ec2-34-205-9-76.compute-1.amazonaws.com', 'private_ip': '172.31.5.17'}, 'gatekeeper': {'id': 'i-08866506ef4878ef8', 'private_dns': 'ip-172-31-13-139.ec2.internal', 'public_dns': 'ec2-34-236-245-22.compute-1.amazonaws.com', 'private_ip': '172.31.13.139'}}
    #############################################################
    ################  STANDALONE INIT ###########################
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(public_dns_list[0], username="ubuntu", key_filename="key_pair_project3.pem")

    with SCPClient(ssh.get_transport()) as scp:
        scp.put("setup/setup_mysql_standalone.sh", remote_path='initialize.sh')

    command = f'chmod 777 initialize.sh'
    stdin, stdout, stderr = ssh.exec_command(command)
    command = f'. ./initialize.sh 1>std.txt 2>err.txt'
    stdin, stdout, stderr = ssh.exec_command(command)
    ssh.close()


#############################################################
    #################  PROXY INIT ###############################
    ssh.connect(public_dns_list[5], username="ubuntu", key_filename="key_pair_project3.pem")
    stdin, stdout, stderr = ssh.exec_command("sudo apt-get update")
    time.sleep(10)
    stdin, stdout, stderr = ssh.exec_command("sudo apt-get -y install python3-pip")
    time.sleep(10)
    command = 'pip3 install flask ping3 mysql-connector-python\n\
        export PATH="$HOME/.local/bin:$PATH"'
    stdin, stdout, stderr = ssh.exec_command(command)
    time.sleep(10)
    command = utils_proxy.setup_instance_cmd(info)
    stdin, stdout, stderr = ssh.exec_command(command)
    ssh.close()

    #############################################################
    #################  WEB FACING INIT ###############################
    ssh.connect(public_dns_list[7], username="ubuntu", key_filename="key_pair_project3.pem")
    stdin, stdout, stderr = ssh.exec_command("mkdir templates")
    with SCPClient(ssh.get_transport()) as scp:
        scp.put("templates/read.html", remote_path='templates/read.html')
        scp.put("templates/write.html", remote_path='templates/write.html')
        scp.put("templates/result.html", remote_path='templates/result.html')

    stdin, stdout, stderr = ssh.exec_command("sudo apt-get update")
    time.sleep(10)
    stdin, stdout, stderr = ssh.exec_command("sudo apt-get -y install python3-pip")
    time.sleep(10)
    command = 'sudo pip3 install flask requests\n\
        export PATH="$HOME/.local/bin:$PATH"'
    stdin, stdout, stderr = ssh.exec_command(command)
    time.sleep(10)
    f = utils_gatekeeper.get_extern_flask_app(info)
    command = f'''echo \"{f}\" >flask_app.py'''
    stdin, stdout, stderr = ssh.exec_command(command)
    ssh.close()

    #############################################################
    ################  MASTER INIT ###############################
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(public_dns_list[1], username="ubuntu", key_filename="key_pair_project3.pem")

    with SCPClient(ssh.get_transport()) as scp:
        scp.put("setup/setup_mysql_master.sh", remote_path='initialize.sh')

    command = f'chmod 777 initialize.sh'
    stdin, stdout, stderr = ssh.exec_command(command)
    #command = utils_scripts.get_firewall_cmd(info)
    #stdin, stdout, stderr = ssh.exec_command(command)
    command = f'. ./initialize.sh 1>>std.txt 2>>err.txt'
    stdin, stdout, stderr = ssh.exec_command(command)
    ssh.close()

    #############################################################
    ################  WORKERS INIT ##############################
    for dns in public_dns_list[2:5]:
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(dns, username="ubuntu", key_filename="key_pair_project3.pem")

        with SCPClient(ssh.get_transport()) as scp:
            scp.put("setup/setup_mysql_slaves.sh", remote_path='initialize.sh')

        command = f'chmod 777 initialize.sh'
        stdin, stdout, stderr = ssh.exec_command(command)
        #command = utils_scripts.get_firewall_cmd(info)
        #stdin, stdout, stderr = ssh.exec_command(command)
        command = f'. ./initialize.sh 1>>std.txt 2>>err.txt'
        stdin, stdout, stderr = ssh.exec_command(command)
        ssh.close()


    time.sleep(120) # wait enough time so first part of initialization is over

    #############################################################
    ################  MASTER LAUNCH #############################
    ssh.connect(public_dns_list[1], username="ubuntu", key_filename="key_pair_project3.pem")
    config_master = utils_scripts.get_master_config(info)
    command = f"echo \"{config_master}\" > /opt/mysqlcluster/deploy/conf/config.ini"
    stdin, stdout, stderr = ssh.exec_command(command)
    time.sleep(1)
    command = utils_scripts.get_mycnf_cmd(info)
    stdin, stdout, stderr = ssh.exec_command(command)
    time.sleep(1)
    command = utils_scripts.get_start_master_cmd()
    stdin, stdout, stderr = ssh.exec_command(command)
    ssh.close()
    time.sleep(25)
    print("SQL Master node has been launched (phase 1)")
    
    #############################################################
    ################  WORKERS LAUNCH ############################
    for dns in public_dns_list[2:5]:
        ssh.connect(dns, username="ubuntu", key_filename="key_pair_project3.pem")

        command = utils_scripts.get_start_datanode_cmd(info)
        stdin, stdout, stderr = ssh.exec_command(command)
        ssh.close()

    
    #############################################################
    ##############  MASTER LAUNCH PHASE 2 #######################
    ssh.connect(public_dns_list[1], username="ubuntu", key_filename="key_pair_project3.pem")

    command = utils_scripts.get_start_sql_node_cmd()
    stdin, stdout, stderr = ssh.exec_command(command)
    time.sleep(180)
    ssh.close()
    ssh.connect(public_dns_list[1], username="ubuntu", key_filename="key_pair_project3.pem")
    command = utils_scripts.get_setup_users_cmd()
    stdin, stdout, stderr = ssh.exec_command(command)
    print("Workers node have been launched, master has finished its second phase")
    time.sleep(2)
    command = utils_scripts.get_sakiladb_cmd()
    stdin, stdout, stderr = ssh.exec_command(command)
    #Create proxy user
    command = utils_proxy.create_proxy_user_cmd(info)
    print(command)
    stdin, stdout, stderr = ssh.exec_command(command)
    ssh.close()

    


    