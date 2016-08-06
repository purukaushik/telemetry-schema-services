# telemetry-schema-services
[![CircleCI](https://circleci.com/gh/purukaushik/telemetry-schema-service.svg?style=svg)](https://circleci.com/gh/purukaushik/telemetry-schema-service)

(To see what the API currently supports - [see here](/API.md))


Service API to retrieve telemetry schemas and validate them against incoming json.

## Building and Running the service standalone
The service is a Flask app that runs in a [Gunicorn](http://gunicorn.org/#quickstart) WSGI http server. 

1. Clone the repository and cd in

    ```
    git clone https://github.com/purukaushik/telemetry-schema-service.git
    cd telemetry-schema-service    
    ```
    
2. Install python dependencies :

    ```
    pip install -r requirements.txt
    ```
    
3. Set git checkout path in `os_dir` in [`git_config.json`](https://github.com/purukaushik/telemetry-schema-service/blob/master/app/git_config.json#L4)

4. Run nose tests

    ```
    nose2
    ```
    
5. Run Gunicorn

    ```
    gunicorn -w 4 -b 0.0.0.0:8080 mozschemas_service:app
    ```

## Building the service into a Docker image

The app is built into a docker container and hence the only prerequisite is docker, installed and running on your system.

1. Clone the repository and cd in

    ```
    git clone https://github.com/purukaushik/telemetry-schema-service.git
    cd telemetry-schema-service
    ```
    
2. Set git checkout path in 'os_dir' in [`git_config.json`](https://github.com/purukaushik/telemetry-schema-service/blob/master/app/git_config.json#L4)
3.  Docker build in /telemetry-schema-service:

    ```
    docker build -t telemetry-schema-service .
    ```

## Running the service in Docker container##
The default logging is directed to `stdout`. In order to use `docker logs` run with:

```
docker run --log-driver=json-file -p 8080:8080 telemetry-schema-service & 
```

## API ##
    
  Once the flask app is up and running, either in Gunicorn or in the Docker container, the schemas can be requested.
  
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

    ./app/mozschemas_cli.py [(-n <namespace>)]
    ./app/mozschemas_cli.py [(-n <namespace>  -d <doctype>)]
    ./app/mozschemas_cli.py [(-n <namespace>  -d <doctype> -v <version>)]
    ./app/mozschemas_cli.py (-h | --help)
    Options:
    -h --help       Show this screen.
    -n namespace    List all docTypes under namespace
    -n namespace -d doctype List versions under namespace and docType
    -n namespace -d doctype -v version Show schema @ namespace/docType/version
