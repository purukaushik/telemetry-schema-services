#!/usr/bin/env python
"""Schema Service Core.
Starts the core python schema hosting/validation web service API.
Usage:
core_service.py [-p <port>] [--host=<host>]
core_service.py (-h | --help)
    
Options:
-h --help       Show this screen.
--host=<host>   Hostname [default: 127.0.0.1]
-p <port>       Port number to run flask on [default: 5000]
"""
from flask import Flask, request, Response, redirect, render_template, flash, jsonify,send_from_directory
import os, json
from os.path import isfile,join
from jsonschema import validate, ValidationError
from git_checkout import gitcheckout
from service_commons import get_schema, get_schema_json
import gzip, StringIO
import re
import logging
from docopt import docopt


UPLOAD_FOLDER = os.path.dirname(os.path.realpath(__name__))+ '/uploads/'
ALLOWED_EXTENSIONS= set(['json'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def throw_validation_error(validationError):
    app.logger.error(str(validationError))
    return Response(str(validationError),status=400, mimetype='text/html')    

# check for file in allowed extensions
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS


def get_doctypes_versions(namespace, docType):
    path_of_namespace = CWD + '/mozilla-pipeline-schemas/' + namespace
    files = [f for f in os.listdir(path_of_namespace) if isfile(join(path_of_namespace,f))]
    lst = list()

    if docType== None:
        for file in files:
            m = re.search('^[A-Za-z]*\.', file)
            docType = m.group().replace('.','')
            lst_item = (docType, '/schema/'+namespace+'/'+docType, None, None)
            lst.append(lst_item)
    else:
        for file in files:
            app.logger.debug( " looking at : " + file)
            m = re.search('^' + docType+'\.'+'([0-9])\.',file)
            if m is not None:
                version = m.group(1).replace('.','')
                schema = '/schema/'+namespace+'/'+ docType +'/'+version
                minify = schema + '?minify=true'
                lst_item = (version, schema, '/validate/'+namespace+"/"+docType+"/"+version, minify)
                
                lst.append(lst_item)
    return lst
@app.route('/')
def api_root():
    return Response(open('README.md').read(), status=200, mimetype='text/plain')


@app.route('/file/<path:path>', methods=['GET'])
def api_get_file(path):
    return send_from_directory(CWD+ '/mozilla-pipeline-schemas/', path)

@app.route('/schema/<namespace>', methods=['GET'])
def api_get_doctypes(namespace):
    lst = get_doctypes_versions(namespace, None)    
    return render_template('links.html', duct_tape=lst, listing='docTypes under '+ namespace)

@app.route('/schema/<namespace>/<docType>', methods=['GET'])
def api_get_versions(namespace,docType):
    lst = get_doctypes_versions(namespace,docType)
    return render_template('links.html', duct_tape=lst, listing='versions of '+ docType)

@app.route('/schema/<namespace>/<docType>/<version>', methods=['GET'])
def api_get_schema(namespace,docType,version):
    # MINIFY
    if len(request.args) !=0:
        if request.args.get('minify')== 'true':
            app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

    return jsonify(json.load(get_schema_json(namespace,docType,version,app.logger)))

@app.route('/validate/<namespace>/<docType>/<version>', methods=['GET', 'POST'])
def api_get_schema_w_version(namespace,docType,version):
    # _. assemble payload from the parameters
    app.logger.debug(" api_get_schema method start")
    app.logger.debug(" assembling fileName from route")
    # construct file name from GET uri and search for schema in cwd/mozilla-pipeline-schemas/
    # assumes git clones into cwd 
    schema_json = get_schema_json(namespace,docType,version,app.logger)
    if request.method == 'POST':
        main_schema = json.load(schema_json)
        app.logger.debug(" request is POST")
        # handle POST - i.e validation of json
        if request.headers['Content-Type'] == 'application/json':
            try:
                app.logger.debug(" try'na validate")
                validate(request.json, main_schema)
                resp_str = {
                    "status" : 200,
                    "message" : "json ok!"
                }
                return Response(json.dumps(resp_str), status=200, mimetype='application/json')
            except ValidationError as e:
                return throw_validation_error(e)
        elif request.headers['Content-Type'] == 'application/x-gzip':
            app.logger.debug(" Gzip option")
            file = StringIO.StringIO(request.data)
            ungzip = gzip.GzipFile(fileobj = file,mode ='rb')
            file_content = ungzip.read()
            try:
                validate(json.loads(file_content),main_schema)
                resp_str = {
                    "status": 200,
                    "message" : "json ok!"
                }
                return Response(json.dumps(resp_str), status=200, mimetype='application/json')
            except ValidationError as e:
                return throw_validation_error(e)
        else:
            if 'file' not in request.files:
                error = 'There was an error processing your file. Please try again.'
                return render_template('file_upload.html',error=error)
            file = request.files['file']
            if file.filename == '' :
                error = 'No file uploaded. Please select a json file to continue.'
                return render_template('file_upload.html', error=error)
            if file and allowed_file(file.filename):
                try:
                    print "before checking request json"
                    validate(json.load(file), main_schema)
                    print "after checking request.json"
                    resp_str = {
                        "status" : 200,
                        "message" : "json ok!"
                    }
                    app.logger.debug( "JSON Ok!")
                    return Response(json.dumps(resp_str), status=200, mimetype='application/json')
                except ValidationError as e:
                    return throw_validation_error(e)
            else:
                 message={
                     "status": 400,
                     "message": "File not a json"
                 }
                 app.logger.debug("Not a JSON")
                 return Response(json.dumps(message), status = 400, mimetype='application/json')
    elif request.method == 'GET':
        # handle GET - i.e return schema requested
        # File handler here
        return render_template('file_upload.html')


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: '+ request.url,
    }
    return Response(json.dumps(message), status=404, mimetype='application/json')

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Schema service v0.1')
    print arguments
    host = '127.0.0.1'
    port = 5000
    if '--host' in arguments:
        host = arguments['--host']
    if '-p' in arguments:
        port = arguments['-p']
        
    logging.basicConfig(filename='core_service.log', filemode='a', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s',datefmt='%a, %d %b %Y %H:%M:%S',)
    gitcheckout()
    app.run(host=host, port=port, threaded=True)
