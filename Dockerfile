# ubuntu 16.04 xenial image
FROM ubuntu

# apt update it
RUN apt-get update
# get essentials
RUN apt-get install -y tar git curl wget dialog net-tools build-essential
# get python
RUN apt-get install -y python python-dev python-distribute python-pip
# clone our repo
#RUN git clone https://github.com/purukaushik/telemetry-schema-services.git
# FIXME: remove this when testcases branch is finally merged into master
RUN git clone -b testcases https://github.com/purukaushik/telemetry-schema-services.git

# pip install requirements.txt
RUN pip install -r /telemetry-schema-services/requirements.txt

# package for logging in mozlog format
RUN git clone https://github.com/mozilla/mozilla-cloud-services-logger.git
WORKDIR /mozilla-cloud-services-logger
RUN pwd
RUN python ./setup.py install

EXPOSE 8080
WORKDIR /telemetry-schema-services

CMD /telemetry-schema-services/mozschemas_service.py -p 8080 --host='0.0.0.0'