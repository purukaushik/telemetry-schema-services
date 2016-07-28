# ubuntu 16.04 xenial image
FROM ubuntu

# apt update it
RUN apt-get update
# get essentials
RUN apt-get install -y tar git curl wget dialog net-tools build-essential python python-dev python-distribute python-pip

# add project directory
ADD . /telemetry-schema-service/

# pip install requirements.txt
RUN pip install -r /telemetry-schema-service/requirements.txt

# exposing 8080 for flask app
EXPOSE 8080

# make mozschemas_service.py runnable
RUN chmod +x /telemetry-schema-service/mozschemas_service.py

# workdir
WORKDIR /telemetry-schema-service

# run gunicorn
CMD gunicorn -w 4 -b 0.0.0.0:8080 mozschemas_service:app
