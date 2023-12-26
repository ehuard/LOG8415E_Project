from ping3 import ping
# pinger = ping3.Ping(timeout=1)
import mysql.connector

a = ping("192.168.1.75")
print(a)