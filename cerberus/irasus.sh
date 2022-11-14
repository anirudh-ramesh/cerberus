#!/bin/bash

pip install -r requirements.txt
sudo apt install postgis postgresql-12-postgis-2.5
touch user_management/migrations/_init_it.py
python3 manage.py makemigrations
python3 manage.py migrate


python3 create_table.py

python3 manage.py runserver





