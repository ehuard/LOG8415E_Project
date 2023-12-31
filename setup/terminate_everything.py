import boto3
import utils_create_instances as utils_instances
import time



if __name__ == "__main__":
    ec2_ressource = boto3.resource("ec2")
    ec2_client = boto3.client('ec2')
    ami_id = "ami-0fc5d935ebf8bc3bc" # ami for ubuntu instances
    ami_id = "ami-0c7217cdde317cfec" # for my aws free tier ubuntu instances


    response_vpcs = ec2_client.describe_vpcs()
    vpc_id = response_vpcs.get('Vpcs', [{}])[0].get('VpcId', '') # we use the default subnet
    ec2_client_subnets = ec2_client.describe_subnets()['Subnets']
    key_pair_name = "key_pair_project" 
    
    # We want to delete everything previously created with the names used (make sure to use the same names as is main.py)
    # Delete security groups (and associated instances) if they already exist
    for group_name in ["mysql_sg", "proxy_sg", "trusted_host_sg", "gatekeeper_sg"]:
        deleted = utils_instances.delete_security_group_by_name(ec2_client, group_name)
