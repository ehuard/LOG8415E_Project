# from ping3 import ping
# # pinger = ping3.Ping(timeout=1)
# import mysql.connector

# a = ping("192.168.1.75")
# print(a)

import requests

# Flask proxy server URL
proxy_url = "http://ec2-44-215-127-221.compute-1.amazonaws.com:5000/query" 

# SQL query and mode information
query = "SELECT * FROM actor LIMIT 5"
mode = "direct-hit"

# JSON payload
payload = {
    "query": query,
    "mode": mode
}

# Send POST request to the Flask proxy
response = requests.post(proxy_url, json=payload)

# Check the response
if response.status_code == 200:
    result = response.json()#["result"]
    print("Query Result:")
    print(result)
else:
    print("Error:", response.text)


#sudo /opt/mysqlcluster/home/mysqlc/bin/mysql -uroot -proot -e "CREATE USER 'proxy'@'ip-172-31-12-60.ec2.internal' IDENTIFIED BY 'pwd';"

#sudo /opt/mysqlcluster/home/mysqlc/bin/mysql -uroot -proot -e "GRANT ALL PRIVILEGES ON *.* TO 'proxy'@'ip-172-31-12-60.ec2.internal';"

# netstat -pnltu