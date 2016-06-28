import os, json, logging
from os.path import isfile,join
from git_checkout import gitcheckout, get_config, checkout
import re
CWD = os.path.dirname(os.path.realpath(__file__))

def get_schema(fileName, logger):
    """ Locate and return the schema specified by full path in fileName.
        Returns: a file object of the schema. 
    """
    logger.debug('json schema full path :' + fileName)
    schema_file = open(fileName)
    #  _. jsonify and return schema file
    return schema_file

def get_schema_json(namespace,docType,version,logger):
    """ Construct full path of schema requested at /namespace/docType/version to /namespace/docType.version.schema.json and return the json file.
        Returns: a file object of the schema
    """
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

def get_doctypes_versions(namespace, docType,logger):
    """ Provided a namespace and docType, it scans the filesystem and returns a list - either all doctypes under namespace/ or all versions under a namespace/doctype
    """
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
            logger.debug( " looking at : " + file)
            m = re.search('^' + docType+'\.'+'([0-9])\.',file)
            if m is not None:
                version = m.group(1).replace('.','')
                schema = '/schema/'+namespace+'/'+ docType +'/'+version
                minify = schema + '?minify=true'
                lst_item = (version, schema, '/validate/'+namespace+"/"+docType+"/"+version, minify)
                
                lst.append(lst_item)
    return lst

def checkout_branch(branch):
    config = get_config()
    config['branch'] = branch
    checkout(config)

if __name__ == "__main__" :
    branch  = 'sandbox'
    print "checking out branch \'"+branch+"\' "
    checkout_branch(branch)
