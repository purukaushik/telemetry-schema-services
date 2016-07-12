#!/usr/bin/env python
"""Schema Service Core.
Starts the core python schema hosting/validation web service API.
Usage:
mozschemas_service.py [-p <port>] [--host=<host>]
mozschemas_service.py (-h | --help)
    
Options:
-h --help       Show this screen.
--host=<host>   Hostname [default: 0.0.0.0]
-p <port>       Port number to run flask on [default: 8080]
"""
from flask import Flask, request, Response, redirect, render_template, flash, jsonify, send_from_directory, url_for
import os
import json
from jsonschema import validate, ValidationError
from git_checkout import gitcheckout
from mozschemas_common import get_schema_json, get_doctypes_versions
import gzip
import StringIO
import logging
from docopt import docopt


UPLOAD_FOLDER = os.path.dirname(os.path.realpath(__name__))+ '/uploads/'
ALLOWED_EXTENSIONS= set(['json'])
CWD = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def throw_validation_error(validationError):
    app.logger.error("Error in validation.")
    app.logger.error(str(validationError))
    return Response(str(validationError), status=400, mimetype='text/plain')

# check for file in allowed extensions
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
def api_root():
    return Response(open('README.md').read(), status=200, mimetype='text/plain')

@app.route('/file/<path:path>', methods = ['GET'])
def api_get_file(path):
    return send_from_directory(CWD + '/mozilla-pipeline-schemas/', path)

@app.route('/schema/<namespace>', methods=['GET'])
def api_get_doctypes(namespace):
    try:
        lst = get_doctypes_versions(namespace, None, app.logger)
    except OSError:
        return redirect(url_for('api_get_doctypes', namespace='telemetry'))
    return render_template('links.html', display_list = lst, listing = 'docTypes under ' + namespace)

@app.route('/schema/<namespace>/<docType>', methods = ['GET'])
def api_get_versions(namespace, docType):
    lst = get_doctypes_versions(namespace, docType, app.logger)
    return render_template('links.html', display_list = lst, listing = 'versions of ' + docType)

@app.route('/schema/<namespace>/<docType>/<version>', methods = ['GET'])
def api_get_schema(namespace, docType, version):
    # MINIFY
    if len(request.args) != 0:
        if request.args.get('minify') == 'true':
            app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
        else:
            app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    else:
        app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    return jsonify(json.load(get_schema_json(namespace, docType, version, app.logger)))

@app.route('/validate/<namespace>', methods = ['GET'])
def api_validate_namespace(namespace):
    return redirect(url_for('api_get_doctypes',namespace=namespace))

@app.route('/validate/<namespace>/<docType>', methods = ['GET'])
def api_validate_doctype(namespace, docType):
    return redirect(url_for('api_get_versions',namespace=namespace,docType=docType))

@app.route('/validate/<namespace>/<docType>/<version>', methods = ['GET', 'POST'])
def api_get_schema_w_version(namespace, docType, version):
    # _. assemble payload from the parameters
    app.logger.debug(" api_get_schema method start")
    app.logger.debug(" assembling fileName from route")
    # construct file name from GET uri and search for schema in cwd/mozilla-pipeline-schemas/
    # assumes git clones into cwd 
    schema_json = get_schema_json(namespace, docType, version, app.logger)
    if request.method == 'POST':
        main_schema = json.load(schema_json)
        app.logger.debug(" request is POST")
        # handle POST - i.e validation of json
        if request.headers['Content-Type'] == 'application/json':
            try:
                app.logger.debug(" Validating...")
                resp_str = validate_json(request.json, main_schema)
                return jsonify(resp_str)
            except ValidationError as e:
                return throw_validation_error(e)
        elif request.headers['Content-Type'] == 'application/x-gzip':
            app.logger.debug(" Gzip option")
            uploaded_file = StringIO.StringIO(request.data)
            ungzip = gzip.GzipFile(fileobj = uploaded_file, mode = 'rb')
            file_content = ungzip.read()
            try:
                resp_str = validate_json(json.loads(file_content), main_schema)
                return jsonify(resp_str)
            except ValidationError as e:
                return throw_validation_error(e)
        else:
            if 'file' not in request.files:
                error = 'There was an error processing your file. Please try again.'
                return render_template('file_upload.html', error = error)
            uploaded_file = request.files['file']
            if uploaded_file.filename == '':
                error = 'No file uploaded. Please select a json file to continue.'
                return render_template('file_upload.html', error = error)
            if uploaded_file and allowed_file(uploaded_file.filename):
                try:
                    resp_str = validate_json(json.load(uploaded_file), main_schema)
                    app.logger.debug("JSON is valid!")
                    return jsonify(resp_str)
                except ValidationError as e:
                    return throw_validation_error(e)
            else:
                 message={
                     "status": 400,
                     "message": "File not a json"
                 }
                 app.logger.debug("Not a JSON")
                 return Response(response=json.dumps(message), status=400, mimetype="application/json")
    elif request.method == 'GET':
        # handle GET - i.e return schema requested
        # File handler here
        return render_template('file_upload.html')


def validate_json(json_file, main_schema):
    validate(json_file, main_schema)
    resp_str = {
        "status": 200,
        "message": "JSON is valid."
    }
    return resp_str


@app.errorhandler(404)
def not_found(error = None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    return Response(json.dumps(message), status=404, mimetype='application/json')

if __name__ == '__main__':
    arguments = docopt(__doc__, version = 'Schema service v0.1')
    host = arguments.get('--host', '0.0.0.0')
    port = arguments.get('-p', 8080)

    logging.basicConfig(filename = 'mozschemas_service.log', filemode = 'a', level = logging.DEBUG, format = '%(asctime)s %(levelname)-8s %(message)s', datefmt = '%a, %d %b %Y %H:%M:%S')
    gitcheckout(app.logger)
    app.run(host = host, port = port, threaded = True)
