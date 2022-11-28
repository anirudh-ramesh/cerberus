#!/bin/bash

pip install -r requirements.txt
sudo apt-get install gdal-bin python-gdal
sudo apt install postgis postgresql-12-postgis-2.5
python3 manage.py makemigrations
python3 manage.py migrate

python3 create_table.py

python3 manage.py runserver





