# ubuntu 16.04 xenial image
FROM ubuntu

# apt update it
RUN apt-get update
# get essentials
RUN apt-get install -y tar git curl wget dialog net-tools build-essential python python-dev python-distribute python-pip

# add project directory
ADD . /telemetry-schema-services/

# pip install requirements.txt
RUN pip install -r /telemetry-schema-services/requirements.txt

# package for logging in mozlog format
RUN git clone https://github.com/mozilla/mozilla-cloud-services-logger.git

# exposing 8080 for flask app
EXPOSE 8080

# make mozschemas_service.py runnable
RUN chmod +x /telemetry-schema-services/mozschemas_service.py

# run gunicorn
#CMD /telemetry-schema-services/mozschemas_service.py -p 8080 --host='0.0.0.0'

# workdir
WORKDIR /telemetry-schema-services
RUN pwd

CMD gunicorn -w 4 -b 0.0.0.0:8080 mozschemas_service:app