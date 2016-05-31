#!/usr/bin/env python
from flask import Flask, url_for, jsonify,request, Response
import os, json
from jsonschema import validate, ValidationError

app = Flask(__name__)
CWD = os.path.dirname(os.path.realpath(__file__))


if not app.debug:
    import logging
    from logging import FileHandler
    #TODO : change to rotating file handler thing
    file_handler = FileHandler('server.log')
    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)

def get_schema(fileName):
    print 'DEBUG: json schema full path :' + fileName
    schema_file = open(fileName)
    #  _. jsonify and return schema file
    return schema_file


@app.route('/')
def api_root():
    # TODO : Possibly set usage kinda thing here
    return ''

# TODO: Unmessify
@app.route('/schema/<namespace>/<docType>', methods=['GET'])
def api_get_schema(namespace,docType):
    print "DEBUG: api_get_schema method start"
    print "DEBUG: assembling fileName from route"

    git_url_suffix  = namespace + '/' + docType  + '.' + 'schema.json'
    fiFile = CWD + '/mozilla-pipeline-schemas/'+git_url_suffix

    print "DEBUG: fetching and reading file: "+ fiFile
    schema_json = get_schema(fiFile)
    resp = Response(schema_json, status = 200, mimetype='application/json')
    return resp

@app.route('/schema/<namespace>/<docType>/<version>', methods=['GET', 'POST'])
def api_get_schema_w_version(namespace,docType,version):
    # _. assemble payload from the parameters
    print "DEBUG: api_get_schema method start"
    print "DEBUG: assembling fileName from route"
    
    git_url_suffix = namespace + '/' + docType + '.'+ version +'.' + 'schema.json'
    fiFile = CWD + '/mozilla-pipeline-schemas/'+git_url_suffix

    print "DEBUG: fetching and reading file: "+ fiFile
    schema_json = get_schema(fiFile)

    if request.method == 'POST':
        main_schema = json.load(schema_json)
        # handle POST - i.e validation of json
        if request.headers['Content-Type'] == 'application/json':
            try:
                validate(request.json, main_schema)
                resp_str = {
                    "status" : 200,
                    "message" : "json ok!"
                }
                return Response(resp_str, status=200, mimetype='application/json')
            except ValidationError:
                message = {
                    "status": 500,
                    "message": "Invalid Json payload"
                }
                return Response(message,status=500, mimetype='application/json')
        else:
            return Response('Error: Gzip not handled yet', status=500, mimetype='application/text')
        # TODO : handle GZIP
    elif request.method == 'GET':
        # handle GET - i.e return schema requested
        resp = Response(schema_json, status = 200, mimetype='application/json')
        return resp



@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: '+ request.url,
    }

if __name__ == '__main__':
    app.run()
