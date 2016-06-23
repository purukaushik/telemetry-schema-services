import os, json, logging

CWD = os.path.dirname(os.path.realpath(__file__))

def get_schema(fileName, logger):
    logger.debug('json schema full path :' + fileName)
    schema_file = open(fileName)
    #  _. jsonify and return schema file
    return schema_file

def get_schema_json(namespace,docType,version,logger):

    git_url_suffix = namespace + '/' + docType
    # HOTFIX: until we include version number in schema file
    if version == '0':
        git_url_suffix= git_url_suffix+ '.' + 'schema.json'
    else:
        git_url_suffix= git_url_suffix+ '.' + version +'.'+ 'schema.json'
    fiFile = CWD + '/mozilla-pipeline-schemas/'+git_url_suffix

    logger.debug("fetching and reading file: "+ fiFile)
    schema_json = get_schema(fiFile,logger)
    return schema_json
