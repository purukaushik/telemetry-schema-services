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

### /file service 
**Endpoint** - `/file/<filename>.json` 

Fetches `<filename>.json` from `/telemetry` folder in file system location specified in [`git_config.json`](https://github.com/purukaushik/telemetry-schema-service/blob/master/app/git_config.json#L4). 

### /schema service
1. **Endpoint** - `/schema/<namespace>`
    * HTML page containing `<docType:String>, <URI-endpoint-to-docType:String>`
2. **Endpoint** - `/schema/<namespace>/<docType>`
    * HTML page containing `<version:Int>, <URI-endpoint-to-schema:String>, <URI-endpoint-to-validate-page:String>, <URI-endpoint-to-minify-schema:String`
3. **Endpoint** - `/schema/<namespace>/<docType>/<version>`
    * JSON schema located at `mozilla-pipeline-schemas/telemetry/<docType>.<version>.schema.json` -> same as doing `/file/<docType>.<version>.schema.json`
    
### /validate service
1. **Endpoint** - `/validate/<namespace>/<docType>/<version>`
    Pulls up the psuedo file upload and validate HTML page.
2. Level-up endpoints redirect to `/schema/<namespace>/[<docType>]` endpoints. 