#!/bin/bash

############################################
# Things we do for every machine
sudo apt-get update

# if needed, stop mysql before and uninstall
#sudo service mysqld stop
sudo apt-get remove mysql-server mysql mysql-devel

sudo mkdir -p /opt/mysqlcluster/home
cd /opt/mysqlcluster/home
# give all rights to the user "ubuntu"
sudo chown ubuntu: .
sudo chmod u+w .


wget http://dev.mysql.com/get/Downloads/MySQL-Cluster-7.2/mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz
tar -xvf mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz
# link between files (easier)
ln -s mysql-cluster-gpl-7.2.1-linux2.6-x86_64 mysqlc

sudo touch /etc/profile.d/mysqlc.sh
sudo chmod 766 /etc/profile.d/mysqlc.sh
sudo echo "export MYSQLC_HOME=/opt/mysqlcluster/home/mysqlc" > /etc/profile.d/mysqlc.sh
sudo echo "export PATH=$MYSQLC_HOME/bin:$PATH" >> /etc/profile.d/mysqlc.sh
# set environment variables for the current shell only (run the command again when opening a new shell)
source /etc/profile.d/mysqlc.sh 


############################################
# Proper to the master:

mkdir -p mysqlcluster/deploy
cd mysqlcluster/deploy
mkdir conf
mkdir mysqld_data
mkdir ndb_data
cd conf

echo "[mysqld]
ndbcluster
datadir=/opt/mysqlcluster/deploy/mysqld_data
basedir=/opt/mysqlcluster/home/mysqlc
port=3306" >> my.cnf
