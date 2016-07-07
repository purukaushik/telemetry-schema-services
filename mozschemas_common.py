import os, json, logging
from os.path import isfile,join
from git_checkout import gitcheckout, get_config, checkout
import re

CWD = os.path.dirname(os.path.realpath(__file__))

def get_schema(fileName, logger):
    """ Locate and return the schema specified by full path in fileName.
        Returns: a file object of the schema. 
    """
    logger.debug('Fetching file from :' + fileName)
    return open(fileName)

def get_schema_json(namespace, docType, version, logger):
    """ Construct full path of schema requested at /namespace/docType/version to /namespace/docType.version.schema.json and return the json file.
        Returns: a file object of the schema
    """
    git_url_suffix = namespace + '/' + docType + '.' + version + '.' + 'schema.json'
    schema_file = CWD + '/mozilla-pipeline-schemas/' + git_url_suffix

    logger.debug("Fetching and reading file: " + schema_file)
    schema_json = get_schema(schema_file, logger)
    return schema_json

def get_doctypes_versions(namespace, docType, logger):
    """ Provided a namespace and docType, it scans the filesystem and returns a list - either all doctypes under namespace/ or all versions under a namespace/doctype
    """
    path_of_namespace = CWD + '/mozilla-pipeline-schemas/' + namespace
    files = [f for f in os.listdir(path_of_namespace) if isfile(join(path_of_namespace, f))]
    version_list = list()

    if docType is None:
        for file in files:
            m = re.search('^[A-Za-z]*\.', file)
            docType = m.group().replace('.', '')
            lst_item = (docType, '/schema/' + namespace + '/' + docType, None, None)
            version_list.append(lst_item)
    else:
        for file in files:
            logger.debug( " looking at : " + file)
            m = re.search('^' + docType+'\.'+'([0-9])\.',file)
            if m is not None:
                version = m.group(1).replace('.','')
                schema = '/schema/' + namespace + '/' + docType + '/' + version
                minify = schema + '?minify=true'
                lst_item = (version, schema, '/validate/' + namespace + "/" + docType + "/" + version, minify)
                
                version_list.append(lst_item)
    return version_list

def checkout_branch(branch):
    config = get_config()
    config['branch'] = branch
    checkout(config)

if __name__ == "__main__" :
    branch  = 'sandbox'
    print "checking out branch \'"+branch+"\' "
    checkout_branch(branch)
