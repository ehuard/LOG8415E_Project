import boto3
import utils_create_instances as utils_instances
import utils_create_scripts as utils_scripts
import paramiko
from scp import SCPClient
import time
import json


if __name__ == "__main__":
    ec2_ressource = boto3.resource("ec2")
    ec2_client = boto3.client('ec2')
    ami_id = "ami-0fc5d935ebf8bc3bc" # ami for ubuntu instances

    response_vpcs = ec2_client.describe_vpcs()
    vpc_id = response_vpcs.get('Vpcs', [{}])[0].get('VpcId', '') # we use the default subnet
    # It should already have multiple subnets listed, on different availability zones
    # (at least it is the case for us with our student accounts)
    ec2_client_subnets = ec2_client.describe_subnets()['Subnets']

    key_pair_name = "key_pair_project" 
    # Create EC2 key pair
    key_pair = utils_instances.create_key_pair(ec2_client, key_pair_name)
    info = {}

    # We want to delete everything previously created with the same name
    # so we can create them again without any conflict
    # Delete security groups (and associated instances) if they already exist
    for group_name in ["project_sg"]:
        deleted = utils_instances.delete_security_group_by_name(ec2_client, group_name)

    # https://stackoverflow.com/questions/43313528/data-nodes-cannot-connect-to-mysql-cluster
    # security_group = utils_instances.create_security_group(ec2_client, "project_sg", [22, 1186, 3306, 5000])
    #security_group = utils_instances.create_security_group_legacy(ec2_client, "project_sg", [22, 53, 58, 68, 1186, 2202, 2206, 3306, 5000, 8336])
    security_group = utils_instances.create_security_group_legacy(ec2_client, "project_sg", [22, 1186, 3306, 2206])

    instance_id_standalone = utils_instances.create_ec2_instances(ec2_ressource, ami_id, "t2.micro", security_group, ec2_client_subnets, key_pair_name, 1)
    info["standalone"] = {"id":instance_id_standalone}
    instance_id_master = utils_instances.create_ec2_instances(ec2_ressource, ami_id, "t2.micro", security_group, ec2_client_subnets, key_pair_name, 1)
    info["master"] = {"id":instance_id_master}
    instances_id_workers = utils_instances.create_ec2_instances(ec2_ressource, ami_id, "t2.micro", security_group, ec2_client_subnets, key_pair_name, 3)
    info["workers"] = [None,None,None]
    for idx,instances_id_work in enumerate(instances_id_workers):
        info["workers"][idx] = {"id":instances_id_work}
    
    all_instances_id = instance_id_standalone + instance_id_master + instances_id_workers
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
                   ]
    }

    print(public_dns_list)

    # write instance id and public dns in a file so we can use this information in other scripts
    with open('data.json', 'w') as fp:
        json.dump(info, fp)
#    public_dns_list = None
    time.sleep(15)

    #############################################################
    ################  STANDALONE INIT ###########################
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(public_dns_list[0], username="ubuntu", key_filename="key_pair_project.pem")

    with SCPClient(ssh.get_transport()) as scp:
        scp.put("setup/setup_mysql_standalone.sh", remote_path='initialize.sh')

    command = f'chmod 777 initialize.sh'
    stdin, stdout, stderr = ssh.exec_command(command)
    command = f'. ./initialize.sh 1>std.txt 2>err.txt'
    stdin, stdout, stderr = ssh.exec_command(command)
    ssh.close()
    
    #############################################################
    ################  MASTER INIT ###############################
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(public_dns_list[1], username="ubuntu", key_filename="key_pair_project.pem")

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
    for dns in public_dns_list[2:]:
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(dns, username="ubuntu", key_filename="key_pair_project.pem")

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
    ssh.connect(public_dns_list[1], username="ubuntu", key_filename="key_pair_project.pem")
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
    print("Hey")
    
    #############################################################
    ################  WORKERS LAUNCH ############################
    for dns in public_dns_list[2:]:
        ssh.connect(dns, username="ubuntu", key_filename="key_pair_project.pem")

        command = utils_scripts.get_start_datanode_cmd(info)
        stdin, stdout, stderr = ssh.exec_command(command)
        ssh.close()

    
    #############################################################
    ##############  MASTER LAUNCH PHASE 2 #######################
    ssh.connect(public_dns_list[1], username="ubuntu", key_filename="key_pair_project.pem")

    command = utils_scripts.get_start_sql_node_cmd()
    stdin, stdout, stderr = ssh.exec_command(command)
    time.sleep(180)
    ssh.close()
    ssh.connect(public_dns_list[1], username="ubuntu", key_filename="key_pair_project.pem")
    command = utils_scripts.get_setup_users_cmd()
    stdin, stdout, stderr = ssh.exec_command(command)
    time.sleep(2)
    command = utils_scripts.get_sakiladb_cmd()
    stdin, stdout, stderr = ssh.exec_command(command)
    ssh.close()