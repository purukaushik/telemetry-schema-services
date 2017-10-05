## telemetry-schema-service -what it can currently do

### Layout of [mozilla-pipeline-schemas](https://github.com/mreid-moz/mozilla-pipeline-schemas/tree/common)
1. One folder telemetry for namespace

```
/telemetry
---- main.4.schema.json
---- common.4.schema.json
---- crash.1.schema.json
```

2. Schema files named `docType.version.schema.json`
3. [`git_checkout.py`](https://github.com/purukaushik/telemetry-schema-service/blob/master/app/git_checkout.py) pulls this repo down to a location specified on [`git_config.json`](https://github.com/purukaushik/telemetry-schema-service/blob/master/app/git_config.json#L4)

## Services in telemetry-schema-service (v1.0)##

### /file service 

**Endpoint** - `/file/<filename>.json` 

Fetches `<filename>.json` from `/telemetry` folder in file system location specified in [`git_config.json`](https://github.com/purukaushik/telemetry-schema-service/blob/master/app/git_config.json#L4). 

### /schema service
1.  **Endpoint** - `/schema/<namespace>`
    * HTML page containing `<docType:String>, <URI-endpoint-to-docType:String>`

2.  **Endpoint** - `/schema/<namespace>/<docType>`
    * HTML page containing `<version:Int>, <URI-endpoint-to-schema:String>, <URI-endpoint-to-validate-page:String>, <URI-endpoint-to-minify-schema:String`

3.  **Endpoint** - `/schema/<namespace>/<docType>/<version>`

    **Query Parameters**

    ​	i. `minify=true` - minifies JSON result

    ​	ii. `inline=true`(in v2.0 of service) -  resolves all $refs in schema and produces inlined full schema

    ​

    * JSON schema located at `mozilla-pipeline-schemas/telemetry/<docType>.<version>.schema.json` -> same as doing `/file/<docType>.<version>.schema.json`

      ​
### /validate service
1. **Endpoint** - `/validate/<namespace>/<docType>/<version>`
    Pulls up the psuedo file upload and validate HTML page.

2. Level-up endpoints redirect to `/schema/<namespace>/[<docType>]` endpoints. 


### Hindsight Pipeline Ingestion integration CLI ideas

1.  Having inlining in service:
    1. Have a `/schema/telemetry/<docType>/<version>?inline=true` service option. 
    2. telemetry-schema-service commons to have [ref-resolver](https://github.com/purukaushik/ref-resolver/blob/master/ref_resolver.py) to resolve $refs and inlining
    3. Recursively wget all *.json from `/schema/telemetry/`
2.  Having inlining in pipeline side script:
    1. Grab all schema jsons by hitting the `/file/` endpoint

    2. Run [ref-resolver](https://github.com/purukaushik/ref-resolver/blob/master/ref_resolver.py) and inline each schema obtained.

       ​

## Hindsight/Pipeline integration ##

**Note**: This is for development purposes only. The schema_grabber.py will be upgraded to be used in production once all the integration code is reviewed and tested out.

#### Prerequisites

1. A version of telemetry-schema-service with this [commit](https://github.com/mozilla/telemetry-schema-service/pull/5/commits/1052ece320ecf129797ac81991a450e33a580ddd) must be running a server, either prod or dev.

2. Get `schema_grabber.py` installed to pull schemas down to the hindsight schema path.

   ```shell
   git clone https://github.com/purukaushik/schema_grabber.git
   ```

   ​

**Pulling schemas**

On the machine running hindsight

1. `cd /path/to/hindsight/schema-path`
2. `python /path/to/schema_grabber/schema_grabber.py`

This pulls down schemas with version numbers.

#### Lua Sandbox Extensions todo

Current sandbox extension can only validate schemas without version numbers.

In order to validate JSON pings with versioned schemas, the sandbox extension [code](https://github.com/mozilla-services/lua_sandbox_extensions/blob/master/moz_telemetry/modules/moz_telemetry/extract_dimensions.lua#L127) must be updated to:

1. Update schemas dictionary to have everything in the schemas_path -> [L127](https://github.com/mozilla-services/lua_sandbox_extensions/blob/98065e7627ebf7440363ad73024968b01a1d5c53/moz_telemetry/modules/moz_telemetry/extract_dimensions.lua#L127)
2. Grab version number from JSON ping -> [L224](https://github.com/mozilla-services/lua_sandbox_extensions/blob/98065e7627ebf7440363ad73024968b01a1d5c53/moz_telemetry/modules/moz_telemetry/extract_dimensions.lua#L224)
3. Grab schema from dictionary with this number -> [L273](https://github.com/mozilla-services/lua_sandbox_extensions/blob/98065e7627ebf7440363ad73024968b01a1d5c53/moz_telemetry/modules/moz_telemetry/extract_dimensions.lua#L273)
4. Validation proceeds then as before.