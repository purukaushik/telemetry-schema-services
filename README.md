# telemetry-schema-services
[![CircleCI](https://circleci.com/gh/purukaushik/telemetry-schema-service.svg?style=svg)](https://circleci.com/gh/purukaushik/telemetry-schema-service)

(To see what the API currently supports - [see here](/API.md))


Service API to retrieve telemetry schemas and validate them against incoming json.
	
## Running the service ##

  Schema service can be started with the following options:

    ./mozschemas_service.py [-p <port>] [--host=<host>]
    ./mozschemas_service.py (-h | --help)
    Options:
    -h --help       Show this screen.
    --host=<host>   Hostname [default: 127.0.0.1]
    -p <port>       Port number to run flask on [default: 5000]


 
## Usage ##
  Schemas are retrieved from [this github repo](https://github.com/mozilla-services/mozilla-pipeline-schemas).
  
  
  In general, the uri <-> schema name mapping is:
  `<namespace>/<doctype>/<version>` translates to namespace/doctype.version.schema.json
  
  e.g telemetry/main/4 refers to the main.4.schema.json located in telemetry/ folder.
  

  * Retrieve a schema:
     To retrieve a schema version, say - telemetry/main.4.schema.json (from the github repo):

        $ curl -i http://localhost:8080/schema/telemetry/main/4
	 To retrieve a schema version with minification of json:
	 
        $ curl -i http://localhost:8080/schema/telemetry/main/4?minify=true
			
   
  * Validate a JSON payload via POST:
	  * To validate a JSON payload with a particular version schema, send a POST with same uri as the schema GET request:
	  
	  `$ curl -iH "Content-type: application/json" -X POST http://localhost:8080/validate/telemetry/main/4 --data @sample_v4_ping.json`
	  * To use the file upload utility:
	  
            http://localhost:8080/validate/telemetry/main/4
			
		will pull up the file upload screen.
		
		
   	On clicking 'upload and validate' the service will POST the uploaded json and validate it with the schema specified in the uri.

## CLI version
To run the schema retrieval as a CLI program from terminal, the following will be useful:

    ./mozschemas_cli.py [(-n <namespace>)]
    ./mozschemas_cli.py [(-n <namespace>  -d <doctype>)]
    ./mozschemas_cli.py [(-n <namespace>  -d <doctype> -v <version>)]
    ./mozschemas_cli.py (-h | --help)
    Options:
    -h --help       Show this screen.
    -n namespace    List all docTypes under namespace
    -n namespace -d doctype List versions under namespace and docType
    -n namespace -d doctype -v version Show schema @ namespace/docType/version
