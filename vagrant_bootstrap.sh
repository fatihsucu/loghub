#!/usr/bin/env bash
apt-get update


# MONGODB FOR CELERY BACKEND
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | sudo tee /etc/apt/sources.list.d/mongodb.list
sudo apt-get update
sudo apt-get install -y mongodb-10gen

#pyhon packages and vim
apt-get install -y python-pip python-setuptools vim
pip install celery pymongo flower ipython flask flask-mail

#CELERY BROKER
apt-get install -y rabbitmq-server
apt-get install -y librabbitmq-dev


#adding user
groupadd loghub
useradd -g loghub \
	-G adm,cdrom,sudo,dip,plugdev \
	-d /home/loghub \
	-s /bin/bash loghub