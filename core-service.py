from flask import Flask, url_for, jsonify, Response
app = Flask(__name__)
import git, os

CWD = os.path.dirname(os.path.realpath(__file__))
#REMOTE_URL = 'git@github.com:mozilla-services/mozilla-pipeline-schemas.git'
REMOTE_URL = 'https://github.com/purukaushik/mozilla-pipeline-schemas.git'

if not app.debug:
    import logging
    from logging import FileHandler
    #handle backing server.log file in a deploy script ??
    file_handler = FileHandler('server.log')
    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)

# TODO : periodically do this to get updated schemas
def gitcheckout():
    if os.path.isdir('./mozilla-pipeline-schemas'):
        print 'DEBUG: directory exists. skipping cloning...'
        pass
    else:
        print 'DEBUG: cloning '+ REMOTE_URL
        git.Git().clone(REMOTE_URL)


@app.route('/')
def api_root():
    # TODO : Possibly set usage kinda thing here
    return ''

@app.route('/schema/<namespace>/<docType>/<version>', methods=['GET'])
def api_get_schema(namespace,docType,version):
    # 1. assemble payload from the parameters
    print "DEBUG: api_get_schema method start"

    #if version == None:
    git_url_suffix  = namespace + '/' + docType  + '.' + 'schema.json'

    #TODO : add version logic once gitpython checkout branch is done
    #else:    
    #    git_url_suffix = namespace + '/' + docType + '.'+ version +'.' + 'schema.json'
    #    app.logger.debug( git_url_suffix: '.append(git_url_suffix)


    # 2. git checkout from the url in the payload
    gitcheckout()

    fiFile = CWD + '/mozilla-pipeline-schemas/'+git_url_suffix
    print 'DEBUG: json schema full path :' + fiFile
    schema_file = open(fiFile)
    
    # 3. jsonify and return schema file
    schema_json  = schema_file.read()
    resp = Response(schema_json, status = 200, mimetype='applciation/json')
    return resp
    

if __name__ == '__main__':
    app.run()
