#!/usr/bin/env python
from flask import Flask, request, Response, redirect, render_template, flash, send_from_directory, jsonify
import os, json
from os.path import isfile,join
from jsonschema import validate, ValidationError
from git_checkout import gitcheckout
import gzip, StringIO
import re
import logging


CWD = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = os.path.dirname(os.path.realpath(__name__))+ '/uploads/'
ALLOWED_EXTENSIONS= set(['json'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def throw_validation_error(validationError):
    print str(validationError)
    return Response(str(validationError),status=400, mimetype='text/html')    

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

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

def get_doctypes_versions(namespace, docType):
    path_of_namespace = CWD + '/mozilla-pipeline-schemas/' + namespace
    files = [f for f in os.listdir(path_of_namespace) if isfile(join(path_of_namespace,f))]
    lst = list()

    if docType== None:
        for file in files:
            m = re.search('^[A-Za-z]*\.', file)
            docType = m.group().replace('.','')
            lst_item = (docType, '/schema/'+namespace+'/'+docType, None)
            lst.append(lst_item)
    else:
        for file in files:
            print "DEBUG: looking at : " + file
            m = re.search('^' + docType+'\.'+'([0-9])\.',file)
            if m is not None:
                version = m.group(1).replace('.','')
                lst_item = (version,'/schema/'+namespace+'/'+ docType +'/'+version, '/validate/'+namespace+"/"+docType+"/"+version)
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

    return jsonify(json.load(get_schema_json(namespace,docType,version)))

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
        return render_template('file_upload.html')


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: '+ request.url,
    }
    return Response(json.dumps(message), status=404, mimetype='application/json')

if __name__ == '__main__':
    logging.basicConfig(filename='core_service.log', filemode='a', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s',datefmt='%a, %d %b %Y %H:%M:%S',)
    gitcheckout()
    app.run(host='0.0.0.0', port=8080)
