#!/bin/bash

pip install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate


python3 create_table.py

python3 manage.py runserver





