#!/bin/bash

############################################
# Things we do for every machine
sudo apt-get update

# if needed, stop mysql before and uninstall
#sudo service mysqld stop
sudo apt-get remove mysql-server mysql mysql-devel

sudo mkdir -p /opt/mysqlcluster/home
cd /opt/mysqlcluster/home
# give all rights to the user "ubuntu" there
sudo chown ubuntu: .
sudo chmod u+w .


wget http://dev.mysql.com/get/Downloads/MySQL-Cluster-7.2/mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz
tar -xvf mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz
rm mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz
# link between files (easier)
ln -s mysql-cluster-gpl-7.2.1-linux2.6-x86_64 mysqlc

sudo touch /etc/profile.d/mysqlc.sh
sudo chmod 766 /etc/profile.d/mysqlc.sh
sudo echo 'export MYSQLC_HOME=/opt/mysqlcluster/home/mysqlc' > /etc/profile.d/mysqlc.sh
sudo echo 'export PATH=$MYSQLC_HOME/bin:$PATH' >> /etc/profile.d/mysqlc.sh
# set environment variables for the current shell only (run the command again when opening a new shell)
source /etc/profile.d/mysqlc.sh 
sudo apt-get -y install libncurses5


############################################
# Proper to the master:
cd ~
sudo mkdir -p opt/mysqlcluster/deploy
cd opt/mysqlcluster/deploy
# give all rights to the user "ubuntu" there
sudo chown ubuntu: .
sudo chmod u+w .
mkdir conf
mkdir mysqld_data
mkdir ndb_data
cd conf

echo "[mysqld]
ndbcluster
datadir=/opt/mysqlcluster/deploy/mysqld_data
basedir=/opt/mysqlcluster/home/mysqlc
port=3306" >> my.cnf
