#!/bin/bash
echo "Restart Postgres"
service postgresql restart
# Collect static files
echo "Collect static files"
python cerberus/manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
ls
python cerberus/manage.py makemigrations
python cerberus/manage.py migrate

#===========CREATE TABLE===================
python cerberus/create_table.py
# Start server
echo "Starting server"
python cerberus/manage.py runserver 0.0.0.0:8000 
