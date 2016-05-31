# telemetry-schema-services
Service API to retrieve telemetry schemas and validate them against incoming json.

## Running the service ##

In order to run the service use:

    $ python core_service.py
Currently only configured to run on port 5000.

## Usage ##
  * Retrieve a schema:
    * To retrieve a schema version say - telemetry/main.4.schema.json (from the github repo):
        `$ curl -i http://127.0.0.1:5000/schema/telemetry/main/4`
   
  * Validate a JSON payload via POST:
	  * To validate a JSON payload with a particular version schema, send a POST with same uri as the schema GET request:
	  `$ curl -iH "Content-type: application/json" -X POST http://127.0.0.1:5000/schema/telemetry/main/4 --data @sample_v4_ping.json`
