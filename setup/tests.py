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

    all_instances_id = ['i-015628312703771d2', 'i-03566aaad53e2a635', 'i-036ded1be5e2b4b3b', 'i-0acea032142e1bbd0']
    instances_dns = [utils_instances.get_public_dns(ec2_client, id) for id in all_instances_id]

    dns_list = [utils_instances.get_private_dns(ec2_client, id) for id in all_instances_id]

    info = {
        "standalone":None,
        "master":{"id":all_instances_id[1], "private_dns":dns_list[1]},
        "workers":[{"id":all_instances_id[2], "private_dns":dns_list[2]},
                   {"id":all_instances_id[3], "private_dns":dns_list[3]}]
    }

    with open('data.json', 'w') as fp:
        json.dump(info, fp)

    script = utils_scripts.get_master_config(info)
    print(info)
    print(dns_list)
    print("\n\n\n",script)

    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(instances_dns[1], username="ubuntu", key_filename="key_pair_project.pem")



    command = f"echo \"{script}\" > /opt/mysqlcluster/deploy/conf/config.ini"
    stdin, stdout, stderr = ssh.exec_command(command)
  
    ssh.close()
