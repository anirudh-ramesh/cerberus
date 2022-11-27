#!/bin/sh

# wait for PSQL server to start
sleep 10

cd cerberus
  
# prepare init migration
su -m myuser -c "python3 manage.py makemigrations"  
# migrate db, so we have the latest db schema
su -m myuser -c "python3 manage.py migrate"  
# start development server on public ip interface, on port 8000
su -m myuser -c "python3 manage.py runserver 0.0.0.0:8000"  
