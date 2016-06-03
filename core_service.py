#!/usr/bin/env python
from flask import Flask, request, Response, redirect
import os, json
from jsonschema import validate, ValidationError
from git_checkout import gitcheckout
import gzip, StringIO

CWD = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = os.path.dirname(os.path.realpath(__name__))+ '/uploads/'
ALLOWED_EXTENSIONS= set(['json'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def throw_validation_error(validationError):
    print str(validationError)
    return Response(validationError,status=400, mimetype='text/html')    

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

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

def get_schema_json(namespace,docType,version):

    git_url_suffix = namespace + '/' + docType
    # HOTFIX: until we include version number in schema file
    if version == '0':
        git_url_suffix= git_url_suffix+ '.' + 'schema.json'
    else:
        git_url_suffix= git_url_suffix+ '.' + version +'.'+ 'schema.json'
    fiFile = CWD + '/mozilla-pipeline-schemas/'+git_url_suffix

    print "DEBUG: fetching and reading file: "+ fiFile
    schema_json = get_schema(fiFile)
    return schema_json

@app.route('/')
def api_root():
    return Response(open('README.md').read(), status=200, mimetype='text/plain')

@app.route('/schema/<namespace>/<docType>/<version>', methods=['GET'])
def api_get_schema(namespace,docType,version):
    resp = Response(get_schema_json(namespace,docType,version), status = 200, mimetype='application/json')
    return resp

@app.route('/validate/<namespace>/<docType>/<version>', methods=['GET', 'POST'])
def api_get_schema_w_version(namespace,docType,version):
    # _. assemble payload from the parameters
    print "DEBUG: api_get_schema method start"
    print "DEBUG: assembling fileName from route"
    # construct file name from GET uri and search for schema in cwd/mozilla-pipeline-schemas/
    # assumes git clones into cwd 
    schema_json = get_schema_json(namespace,docType,version)
    if request.method == 'POST':
        main_schema = json.load(schema_json)
        print "DEBUG: request is POST"
        # handle POST - i.e validation of json
        if request.headers['Content-Type'] == 'application/json':
            try:
                print "DEBUG: try'na validate"
                validate(request.json, main_schema)
                resp_str = {
                    "status" : 200,
                    "message" : "json ok!"
                }
                return Response(json.dumps(resp_str), status=200, mimetype='application/json')
            except ValidationError as e:
                return throw_validation_error(e)
        elif request.headers['Content-Type'] == 'application/x-gzip':
            print "DEBUG: Gzip option"
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
                flash('No file part')
                return redirect(request.url)

            file = request.files['file']
            if file.filename == '' :
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                try:
                    print "before checking request json"
                    validate(json.load(file), main_schema)
                    print "after checking request.json"
                    resp_str = {
                        "status" : 200,
                        "message" : "json ok!"
                    }
                    print "JSON Ok!"
                    return Response(json.dumps(resp_str), status=200, mimetype='application/json')
                except ValidationError as e:
                    return throw_validation_error(e)
            else:
                 message={
                     "status": 400,
                     "message": "File not a json"
                 }
                 print "Not a JSON"
                 return Response(json.dumps(message), status = 400, mimetype='application/json')
    elif request.method == 'GET':
        # handle GET - i.e return schema requested
        # File handler here
        return '''
        <!doctype html>
        <title>Upload new file</title>
        <h1>Upload new file</h1>
        <form action="" method=post enctype=multipart/form-data>
        <p><input type =file name=file><input type=submit value="upload and validate"></form>'''



@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: '+ request.url,
    }
    return Response(json.dumps(message), status=404, mimetype='application/json')
if __name__ == '__main__':
    gitcheckout()
    app.run()
