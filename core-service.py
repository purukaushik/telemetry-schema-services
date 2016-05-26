from flask import Flask, url_for, jsonify, Response
app = Flask(__name__)
import git, os

#periodically do this to get updated schemas
def gitcheckout():
    if os.path.isdir('./mozilla-pipeline-schemas'):
        pass
    else:
        git.Git().clone('git@github.com:mozilla-services/mozilla-pipeline-schemas.git')


@app.route('/')
def api_root():
    #Possibly set usage kinda thing here
    return ''

@app.route('/schema/<namespace>/<docType>/<version>', methods=['GET'])
def api_get_schema(namespace,docType,version):
    # 1. assemble payload from the parameters
    print "DEBUG: api_get_schema method start"
    if version == None:
        git_url_suffix  = namespace + '/' + docType + '.' + version + '.' + 'schema.json'
    #print 'DEBUG: git_url_suffix: '.append(git_url_suffix)
    # 2. git checkout from the url in the payload
    # alternatively read file from local git repo for now
    gitcheckout()
    fiFile ='./mozilla-pipeline-schemas/'+git_url_suffix
    schema_file = open(fiFile)
    
    # 3. jsonify and return schema file
    schema_json  = schema_file.read()
    resp = Response(schema_json, status = 200, mimetype='applciation/json')
    return resp

if not app.debug:
    import logging
    from logging import FileHandler
    #handle backing server.log file in a deploy script ??
    file_handler = FileHandler('server.log')
    app.logger.addHandler(file_handler)

    
    

if __name__ == '__main__':
    app.run()
