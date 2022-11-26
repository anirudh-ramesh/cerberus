ARG PYTHON_VERSION=3.9.14

FROM python:${PYTHON_VERSION}

MAINTAINER Anirudh Ramesh

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /cerberus

COPY requirements.txt /cerberus/

RUN pip install -r requirements.txt

COPY . /cerberus/

RUN apt update &&\
  apt install -y binutils libproj-dev gdal-bin
RUN apt install -y binutils libproj-dev gdal-bin
RUN apt install -y postgresql
RUN apt install -y postgis postgresql-postgis


RUN python3 manage.py makemigrations
RUN python3 manage.py migrate

RUN python3 create_table.py

RUN python3 manage.py runserver
