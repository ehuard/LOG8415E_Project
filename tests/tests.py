# Deprecated since I added the firewalls
# Only keep it here to see the basic requests

import requests

# Flask proxy server URL
proxy_url = "http://ec2-3-235-249-218.compute-1.amazonaws.com:5000/query" 

# SQL query and mode information
#query = "SELECT * FROM actor LIMIT 5;"
query = "INSERT INTO actor VALUES(205, 'Jean', 'Reno', NOW());"
mode = "write"
#mode = 'direct-hit'

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


#sudo /opt/mysqlcluster/home/mysqlc/bin/mysql -uroot -proot -e "CREATE USER 'proxy'@'ip-172-31-10-64.ec2.internal' IDENTIFIED BY 'pwd';"

#sudo /opt/mysqlcluster/home/mysqlc/bin/mysql -uroot -proot -e "GRANT ALL PRIVILEGES ON *.* TO 'proxy'@'ip-172-31-10-64.ec2.internal';"


# sudo /opt/mysqlcluster/home/mysqlc/bin/mysql -uroot -proot -e ""
# netstat -pnltu