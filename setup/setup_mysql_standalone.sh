#!/bin/bash
sudo apt-get update




# Install mySQL
sudo apt-get -y install mysql-server 

# Downloading the database
wget https://downloads.mysql.com/docs/sakila-db.tar.gz
tar -xzvf sakila-db.tar.gz
rm sakila-db.tar.gz

# Good if you are doing it line by line in the console but I can't get it to work in a bash script
# # log in
# sudo mysql -u root
# # install the database
# SOURCE sakila-db/sakila-schema.sql;
# SOURCE sakila-db/sakila-data.sql;
# USE sakila;
# # SHOW FULL TABLES; # to be sure that it is installed well
# quit # back to the shell


# Create Sakila database
sudo mysql -u root -e "CREATE DATABASE IF NOT EXISTS sakila;"
# Load Sakila schema
sudo mysql -u root -e "SOURCE sakila-db/sakila-schema.sql;"
# Load Sakila data
sudo mysql -u root -e "SOURCE sakila-db/sakila-data.sql;"
# use the database
sudo mysql -u root -e "USE sakila;"


# install sysbench
sudo apt-get -y install sysbench



# Commands to use to run the benchmlark (will be moved in another file)
sudo sysbench oltp_read_only --table_size=100000 --threads=4 --tables=4 --mysql-db=sakila --mysql-user=root --db-driver=mysql prepare
sudo sysbench oltp_read_only --table_size=100000 --threads=4 --tables=4 --mysql-db=sakila --mysql-user=root --db-driver=mysql run
# dropping result tables
sudo sysbench oltp_read_only --table_size=100000 --threads=4 --tables=4 --mysql-db=sakila --mysql-user=root --db-driver=mysql cleanup