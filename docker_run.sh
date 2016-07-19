#!/bin/sh
docker pull purush/telemetry-schema-services
docker run -d -v /tmp:/var/log/syslog -p 127.0.0.1:5514:514/udp  --name rsyslog voxxit/rsyslog &
docker run --log-driver=syslog --log-opt syslog-address=udp://127.0.0.1:5514 --log-opt syslog-facility=daemon -p 8080:8080 purush/telemetry-schema-services &
