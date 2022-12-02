#!/bin/bash
python cerberus/create_table.py

# Collect static files
echo "Collect static files"
python cerberus/manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
ls
python cerberus/manage.py makemigrations
python cerberus/manage.py migrate

# Start server
echo "Starting server"
python cerberus/manage.py runserver 0.0.0.0:8000  
