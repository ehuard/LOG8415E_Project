import boto3
import utils_create_instances as utils_instances
import paramiko
from scp import SCPClient
import time


if __name__ == "__main__":
    ec2_ressource = boto3.resource("ec2")
    ec2_client = boto3.client('ec2')
    ami_id = "ami-03a6eaae9938c858c" 

    response_vpcs = ec2_client.describe_vpcs()
    vpc_id = response_vpcs.get('Vpcs', [{}])[0].get('VpcId', '') # we use the default subnet
    # It should already have multiple subnets listed, on different availability zones
    # (at least it is the case for us with our student accounts)
    ec2_client_subnets = ec2_client.describe_subnets()['Subnets']

    key_pair_name = "key_pair_project" 
    # Create EC2 key pair
    key_pair = utils_instances.create_key_pair(ec2_client, key_pair_name)

    # We want to delete everything previously created with the same name
    # so we can create them again without any conflict
    # Delete security groups (and associated instances) if they already exist
    for group_name in ["project_sg"]:
        deleted = utils_instances.delete_security_group_by_name(ec2_client, group_name)

    security_group = utils_instances.create_security_group(ec2_client, "project_sg")

    instances_id = utils_instances.create_ec2_instances(ec2_ressource, ami_id, "m4.large", security_group, ec2_client_subnets, key_pair_name, 1)

    # We wait for the instances to be running
    utils_instances.wait_instances_to_run(ec2_client, instances_id)
    # We get the public dns name
    instances_dns = [utils_instances.get_public_dns(ec2_client, id) for id in instances_id]
    print(instances_dns)

    # write instance id and public dns in a file so we can use this information in other scripts
    with open('./instances_info.txt', 'w') as f:
        f.write(f"{instances_id[0]} {instances_dns[0]}\n")
