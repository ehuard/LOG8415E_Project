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
datadir=/opt/mysqlcluster/deploy/ndb_data \n\n"
    
    for i in range(nb_datanodes):
        script += f"[ndbd] \n\
hostname={info['workers'][i]['private_dns']} \n\
nodeid={3+i} \n\n"

    script += "[mysqld] \nnodeid=50"
    return script