
FROM python:3.7-slim-buster as base
FROM base as builder

# set environment variables
ENV PY_VERSION=3.8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install libspatialindex-dev -y && \
    apt-get install libgdal-dev -y && \ 
    apt-get install proj-bin -y && \
    apt-get install git bash -y && \
    apt-get clean


# create the app folder and copy contents
RUN mkdir /app
WORKDIR /app

# copy and execute pipenv environment
RUN pip install --upgrade pip
RUN pip install pipenv

# Get requirements.txt file by using pipenv
COPY Pipfile* /tmp/
RUN cd /tmp && pipenv lock --requirements > requirements.txt
RUN pip install -r /tmp/requirements.txt

# install pandas manually
RUN apt-get install -y g++
WORKDIR /
RUN git clone https://github.com/pandas-dev/pandas.git
RUN pip install Cython
WORKDIR /pandas
RUN python setup.py install
RUN pip install geopandas
WORKDIR /
RUN rm -rf pandas
WORKDIR /app

COPY tracker /app/
COPY docker-entrypoint.sh /app/

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
