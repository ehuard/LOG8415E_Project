def get_master_config(info):
    """
    Create the content of the config.ini file to put on master node.
    The content has to be created dynamically to have the right private dns

    Parameters:
    - info : A dictionnary containing all the information necessary on our instances.
        Look at main.py to see its content 

    Returns:
    - script: the content of the config.ini file (in a string format).
    """

    script = f"[ndb_mgmd] \n\
        hostname={info['master']['private_dns']} \n\
        datadir=/opt/mysqlcluster/deploy/ndb_data \n\
        nodeid=1 \n\n"
    
    nb_datanodes = len(info["workers"])
    script += f"[ndbd default] \n\
        noofreplicas={nb_datanodes} \n\
        ServerPort=2206 \n\
        datadir=/opt/mysqlcluster/deploy/ndb_data \n\n"
    
    for i in range(nb_datanodes):
        script += f"[ndbd] \n\
            hostname={info['workers'][i]['private_dns']} \n\
            nodeid={3+i} \n\n"

    script += "[mysqld] \nnodeid=50"
    return script


def get_mycnf_cmd(info):
    """
    """
    cmd = f"echo \"[mysqld] \
        ndbcluster \n\
        #bind-address=127.0.0.1 \n\
        #ndb_read_backup=ON \n\
        #ndb_optimized_node_selection=1 \n \
        datadir=/opt/mysqlcluster/deploy/mysqld_data \n \
        basedir=/opt/mysqlcluster/home/mysqlc \n \
        port=3306 \n\n\
        #[mysql_cluster] \n\
        #ndb-connectstring={info['master']['private_dns']}  # location of management server\" > /opt/mysqlcluster/deploy/conf/my.cnf"
    return cmd

def get_firewall_cmd(info):
    """
    """
    cmd = f"sudo ufw enable\n\
        sudo ufw allow \"OpenSSH\" \n\
        sudo ufw allow from {info['workers'][0]['private_ip']} \n\
        sudo ufw allow from {info['workers'][1]['private_ip']} \n\
        sudo ufw allow from {info['workers'][2]['private_ip']} \n\
        sudo ufw allow from {info['master']['private_ip']} \n"
    return cmd


def get_start_datanode_cmd(info):
    """
    Create the command used to start the datanode.
    The command has to be created dynamically to use the private dns of the master node

    Parameters:
    - info : A dictionnary containing all the information necessary on our instances.
        Look at main.py to see its content 

    Returns:
    - cmd: the content of the command(in a string format).
    """
    cmd = f"source /etc/profile.d/mysqlc.sh \n\
    echo \"\nStart datanode!\n\" >> std.txt \n \
    echo \"\nStart datanode!\n\" >> err.txt \n \
    ndbd -c {info['master']['private_dns']} 1>>std.txt 2>>err.txt"
    return cmd

def get_start_master_cmd():
    """
    Create the command used to start the master node.

    Returns:
    - cmd: the content of the command(in a string format).
    """
    cmd = f"source /etc/profile.d/mysqlc.sh \n\
    echo \"\nStart Master!\n\" >> std.txt \n \
    echo \"\nStart Master!\n\" >> err.txt \n \
    /opt/mysqlcluster/home/mysqlc/scripts/mysql_install_db --basedir=/opt/mysqlcluster/home/mysqlc --no-defaults --datadir=/opt/mysqlcluster/deploy/mysqld_data 1>>std.txt 2>>err.txt \n \
    ndb_mgmd -f /opt/mysqlcluster/deploy/conf/config.ini --initial --configdir=/opt/mysqlcluster/deploy/conf  1>>std.txt 2>>err.txt"
    return cmd


def get_start_sql_node_cmd():
    """
    """
    cmd = f"source /etc/profile.d/mysqlc.sh \n\
        echo \"\nStart SQL node!\n\" >> std.txt \n \
        echo \"\nStart SQL node!\n\" >> err.txt \n \
        mysqld --defaults-file=/opt/mysqlcluster/deploy/conf/my.cnf --user=root & 1>>std.txt 2>>err.txt"
    return cmd


def get_setup_users_cmd():
    """
    Create the command used to start setup the users.

    Returns:
    - cmd: the content of the command(in a string format).
    """
    cmd = f"source /etc/profile.d/mysqlc.sh \n\
        echo \"\nSetup users!\n\" >> std.txt \n \
        echo \"\nSetup users!\n\" >> err.txt \n \
        sudo /opt/mysqlcluster/home/mysqlc/bin/mysql -e \"CREATE USER 'myapp'@'%' IDENTIFIED BY 'testpwd';\" \n \
        sudo /opt/mysqlcluster/home/mysqlc/bin/mysql -e \"GRANT ALL PRIVILEGES ON * . * TO 'myapp'@'%' IDENTIFIED BY 'password' WITH GRANT OPTION;\" \n \
        sudo /opt/mysqlcluster/home/mysqlc/bin/mysql -e \"\n \
            USE mysql; \n \
            UPDATE user SET plugin='mysql_native_password' WHERE User='root'; \n \
            FLUSH PRIVILEGES;SET PASSWORD FOR 'root'@'localhost' = PASSWORD('root');\" 1>>std.txt 2>>err.txt" 
    return cmd

def get_sakiladb_cmd():
    """
    
    """
    cmd = f"sudo /opt/mysqlcluster/home/mysqlc/bin/mysql -u root -proot -e \" \n \
        SOURCE sakila-db/sakila-schema.sql; \n\
        SOURCE sakila-db/sakila-data.sql; \n\
        USE sakila;\" 1>>std.txt 2>>err.txt"
    return cmd