from flask import Flask, request, jsonify 
import mysql.connector
from ping3 import ping
import random
app = Flask(__name__)



# Connect to the MySQL cluster
def get_mysql_connection(host, user="root", password="root", database="sakila"):
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

def direct_hit(query):
    try:
        # Connect to the master node
        connection = get_mysql_connection({info["master"]["private_ip"]})
        # Execute the query
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchall()
        # Process the result as needed
        # ...
        cursor.close()
        res = dict()
        res["result"]=result
        return jsonify(res)
    except Exception as e:
        err = dict()
        err["error"] = str(e)
        return jsonify(err)
    finally:
        if connection.is_connected():
            connection.close()

   
def random_mode(query):
    try:
        # Connect to a random worker node
        workers = {info["workers"]} 
        worker = random.choice(workers)
        connection =  get_mysql_connection(worker["private_ip"])

        # Execute the query
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchall()
        # Process the result as needed
        # ...
        cursor.close()
        res = dict()
        res["result"]=result
        return jsonify(res)
    except Exception as e:
        err = dict()
        err["error"] = str(e)
        return jsonify(err)
    finally:
        if connection.is_connected():
            connection.close()
            
def customized_mode(query):
    lowest_ping = float('inf')
    best_worker = None

    for worker in info["workers"]:
        private_ip = worker["private_ip"]
        current_ping = ping(private_ip)

        if current_ping is not None and current_ping < lowest_ping:
            lowest_ping = current_ping
            best_worker = worker
    
    try:
        connection =  get_mysql_connection(best_worker["private_ip"])
        # Execute the query
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchall()
        # Process the result as needed
        # ...
        cursor.close()
        res = dict()
        res["result"]=result
        return jsonify(res)
    except Exception as e:
        err = dict()
        err["error"] = str(e)
        return jsonify(err)
    finally:
        if connection.is_connected():
            connection.close()

def handle_write(query):
    try:
        # Connect to the master node
        connection = get_mysql_connection({info["master"]["private_ip"]})
        # Execute the query
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.comit()
        # Process the result as needed
        # ...
        cursor.close()
        res = dict()
        res["result"]=result
        return jsonify(res)
    except Exception as e:
        err = dict()
        err["error"] = str(e)
        return jsonify(err)
    finally:
        if connection.is_connected():
            connection.close()
    
@app.route('/')
def hello():
    return 'Hello, World!'

    
@app.route("/query", methods=["POST"])
def execute_query():
    data = request.get_json()
    mode = data.get("mode")
    query = data.get("query")

    if mode == "direct-hit":
        # Send query to the master node
        return direct_hit(query)
    elif mode == "random":
        # Send query to a random worker node
        return random_mode(query)
    elif mode == "customized":
        # Measure ping and send query to the worker with the lowest ping
        return customized_mode(query)
    elif mode == "write":
        # Write queries are alaways handled by the master
        return handle_write(query)


        
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)