ARG PYTHON_VERSION=3.9.14

FROM python:${PYTHON_VERSION}

MAINTAINER Anirudh Ramesh

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY . /app/

RUN apt update &&\
  apt install -y binutils libproj-dev gdal-bin
# RUN apt install -y binutils libproj-dev gdal-bin
# #RUN apt install -y postgresql
# RUN apt install -y postgis postgresql-postgis

RUN adduser --disabled-password --gecos '' myuser

# RUN python3 cerberus/manage.py makemigrations
# RUN python3 cerberus/manage.py migrate


# RUN python3 cerberus/manage.py runserver

