import paramiko
from scp import SCPClient
import time
import json


def get_benckmark_cmd(cluster:bool, mode="oltp_read_write", num_threads=4):
     """
     
     Refers to https://manpages.org/sysbench
     The commands on mes Coyle's blog https://www.jamescoyle.net/how-to/1131-benchmark-mysql-server-performance-with-sysbench 
     don't work with the version of sysbench I installed
     """
     # --max-requests=0 means unlimited (and by default, it is not)
     output_file = f"bench_result_{mode}.txt"
     base = f"sudo sysbench {mode} --table-size=1000000 --threads={num_threads} --max-requests=0 --db-driver=mysql --mysql-db=sakila --mysql-user=root"
     if cluster: 
          base+= " --mysql-password=root --mysql-host=127.0.0.1" # don't forget the space between root and --mysql-password
     cmd = f"{base} prepare 1>std_prep_{mode}.txt 2>err_prep_{mode}.txt \n\
            {base} run 1>{output_file} 2>err_run_{mode}.txt \n\
            {base} cleanup"
     return cmd
     

if __name__ == "__main__":

    with open("data.json", 'r') as var_file: 
            data = json.load(var_file)           
            instance_standalone = data["standalone"]
            instance_master = data["master"]

    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(instance_standalone["public_dns"], username="ubuntu", key_filename="key_pair_project.pem")
    command = get_benckmark_cmd(cluster=False)
    stdin, stdout, stderr = ssh.exec_command(command)
    ssh.close()

    ssh.connect(instance_master["public_dns"], username="ubuntu", key_filename="key_pair_project.pem")
    command = get_benckmark_cmd(cluster=True)
    stdin, stdout, stderr = ssh.exec_command(command)
    ssh.close()
    
    time.sleep(65)
    ssh.connect(instance_standalone["public_dns"], username="ubuntu", key_filename="key_pair_project.pem")
    command = get_benckmark_cmd(cluster=False, mode="oltp_read_only")
    stdin, stdout, stderr = ssh.exec_command(command)
    ssh.close()

    ssh.connect(instance_master["public_dns"], username="ubuntu", key_filename="key_pair_project.pem")
    command = get_benckmark_cmd(cluster=True, mode="oltp_read_only")
    stdin, stdout, stderr = ssh.exec_command(command)
    ssh.close()

    time.sleep(65)
    files_to_retrieve = ["bench_result_oltp_read_write.txt", "bench_result_oltp_read_only.txt"]
    for file_name in files_to_retrieve:
        remote_file_path = file_name
        local_file_path = f"tests/benchmark_results/standalone_{file_name}"
        ssh.connect(instance_standalone["public_dns"], username="ubuntu", key_filename="key_pair_project.pem")
        with SCPClient(ssh.get_transport()) as scp:
            scp.get(remote_file_path, local_path=local_file_path)
        ssh.close()

        local_file_path = f"tests/benchmark_results/cluster_{file_name}"
        ssh.connect(instance_master["public_dns"], username="ubuntu", key_filename="key_pair_project.pem")
        with SCPClient(ssh.get_transport()) as scp:
            scp.get(remote_file_path, local_path=local_file_path)
        ssh.close()
