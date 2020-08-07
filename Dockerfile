
FROM python:3.7-slim-buster as base
FROM base as builder

# set environment variables
ENV PY_VERSION=3.7
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install libspatialindex-dev -y && \
    apt-get install git bash -y && \
    apt-get clean

# create the app folder and copy contents
RUN mkdir /app
WORKDIR /app

# copy and execute pipenv environment
#COPY Pipfile /Pipfile
#COPY Pipfile.lock /app/Pipfile.lock
RUN pip install --upgrade pip
RUN pip install pipenv

# Get requirements.txt file by using pipenv
COPY Pipfile* /tmp/
RUN cd /tmp && pipenv lock --requirements > requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY tracker /app/
COPY docker-entrypoint.sh /app/

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
