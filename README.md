# telemetry-schema-services
Service API to retrieve telemetry schemas and validate them against incoming json.
	
## Running the service ##

In order to run the service use:

    $ python core_service.py
Currently only configured to run on port 8080 with localhost as the host.
 
## Usage ##
  Schemas are retrieved from [this github repo](https://github.com/mozilla-services/mozilla-pipeline-schemas).
  
  
  In general, the uri <-> schema name mapping is:
  &lt;namespace&gt;/&lt;doctype&gt;/&lt;version&gt; translates to namespace/doctype.version.schema.json
  
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
