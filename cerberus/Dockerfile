ARG PYTHON_VERSION=3.11.0

FROM python:${PYTHON_VERSION}

MAINTAINER Anirudh Ramesh

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /goodenough

COPY requirements.txt /goodenough/

RUN pip install -r requirements.txt

COPY . /goodenough/
