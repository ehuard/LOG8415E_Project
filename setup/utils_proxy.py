
# Most of the things here habe been given by chatGPT
def get_flaskpy_file(info):

    file_string = f'''from flask import Flask, request, jsonify 
import mysql.connector
from ping3 import ping
import random
app = Flask(__name__)



# Connect to the MySQL cluster
def get_mysql_connection(host, user='proxy', password='pwd', database='sakila'):
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

    
def handle_write(query):
    try:
        # Connect to the master node
        connection = get_mysql_connection('{info['master']['private_ip']}')
        # Execute the query
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        result = connection.commit()
        # Process the result as needed
        # ...
        cursor.close()
        res = dict()
        res['result']=result
        return jsonify(res)
    except Exception as e:
        err = dict()
        err['error'] = str(e)
        return jsonify(err)
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()


def direct_hit(query):
    try:
        # Connect to the master node
        connection = get_mysql_connection('{info['master']['private_ip']}')
        # Execute the query
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchall()
        # Process the result as needed
        # ...
        cursor.close()
        res = dict()
        res['result']=result
        return jsonify(res)
    except Exception as e:
        err = dict()
        err['error'] = str(e)
        return jsonify(err)
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()

   
def random_mode(query):
    try:
        # Connect to a random worker node
        workers = {info['workers']} 
        worker = random.choice(workers)
        print('Connection to random worker ', worker)
        connection =  get_mysql_connection(worker['private_ip'])

        # Execute the query
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchall()
        # Process the result as needed
        # ...
        cursor.close()
        res = dict()
        res['result']=result
        return jsonify(res)
    except Exception as e:
        err = dict()
        err['error'] = str(e)
        return jsonify(err)
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            
def customized_mode(query):
    lowest_ping = float('inf')
    best_worker = None

    for worker in info['workers']:
        private_ip = worker['private_ip']
        current_ping = ping(private_ip)

        if current_ping is not None and current_ping < lowest_ping:
            lowest_ping = current_ping
            best_worker = worker
    
    try:
        print('Connection to worker ',best_worker,' with ping=',lowest_ping)
        connection =  get_mysql_connection(best_worker['private_ip'])
        # Execute the query
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchall()
        # Process the result as needed
        # ...
        cursor.close()
        res = dict()
        res['result']=result
        return jsonify(res)
    except Exception as e:
        err = dict()
        err['error'] = str(e)
        return jsonify(err)
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()


    
@app.route('/')
def hello():
    return 'Hello, World!'

    
@app.route('/query', methods=['POST'])
def execute_query():
    data = request.get_json()
    mode = data.get('mode')
    query = data.get('query')

    if mode == 'direct-hit':
        # Send query to the master node
        return direct_hit(query)
    elif mode == 'random':
        # Send query to a random worker node
        return random_mode(query)
    elif mode == 'customized':
        # Measure ping and send query to the worker with the lowest ping
        return customized_mode(query)
    elif mode == 'write':
        return handle_write(query)

        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)'''
    return file_string


def setup_instance_cmd(info):
    """
    Returns the commands used to setup the proxy instance and launch the flask application
    """
    cmd = "pip install flask \n \
pip install ping3 \n \
pip install mysql-connector-python \n"
    py_file = get_flaskpy_file(info)
    cmd += f'''echo "{py_file}" > ./flask_app.py \n \
python3 flask_app.py'''
    return cmd


def create_proxy_user_cmd(info):
    """
    Dynamically creates the command used on the master node to create a new user, proxy on a distant machine
    """      
    cmd =  f'''sudo /opt/mysqlcluster/home/mysqlc/bin/mysql -uroot -proot -e "CREATE USER 'proxy'@'{info['proxy']['private_dns']}' IDENTIFIED BY 'pwd';" \n\
sudo /opt/mysqlcluster/home/mysqlc/bin/mysql -uroot -proot -e "GRANT ALL PRIVILEGES ON *.* TO 'proxy'@'{info['proxy']['private_dns']}';"1>oy.txt 2>hmm.txt'''
    return cmd


# import json 

# with open("data.json", 'r') as var_file: 
#             data = json.load(var_file)           
#             instance_standalone = data["standalone"]
#             instance_master = data["master"]

# a=setup_instance_cmd(data)
# print(a)