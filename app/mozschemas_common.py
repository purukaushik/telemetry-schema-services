# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import re
from os.path import isfile,join

import mozschemas_logging
from git_checkout import get_config, checkout
from ref_resolver.ref_resolver import RefResolver
import json

class SchemasLocalFilesHelper:

    def __init__(self):
        self.git_config = get_config()
        self.schema_base_path = self.git_config['os_dir']
        self.logger = mozschemas_logging.getLogger(__name__)

    def get_inlined_schema(self, filename):
        """ Resolve $refs recursively and return an inlined schema.
        :param filename: schema to be resolved
        :return: json dictionary
        """
        self.logger.debug('Inlining ' + filename)
        json_file = json.load(open(filename))
        id = None
        if 'id' in json_file:
            id = json_file['id']
            RefResolver(id).resolve(json_file)
        return json_file

    def get_schema(self, fileName):
        """ Locate and return the schema specified by full path in fileName.
            Returns: a file object of the schema.
        """
        self.logger.debug('Fetching file from :' + fileName)
        return open(fileName)

    def get_schema_json(self, namespace, docType, version, inline=False):
        """ Construct full path of schema requested at /namespace/docType/version to /namespace/docType.version.schema.json and return the json file.
            Returns: a file object of the schema
        """
        git_url_suffix = namespace + '/' + docType + '.' + version + '.schema.json'
        schema_file = self.schema_base_path + git_url_suffix

        self.logger.debug("Fetching and reading file: " + schema_file)
        if inline:
            schema_json = self.get_inlined_schema(schema_file)
        else:
            schema_json = self.get_schema(schema_file)
        return schema_json

    def get_doctypes_versions(self, namespace, docType):
        """ Returns one of two lists:
            1. If both namespace and docType is provided returns list of versions of schemas under namespace/docType
                The list contains tuples of the form-  ( <version:Int>, <URI-endpoint-to-schema:String>, <URI-endpoint-to-validate-page:String>, <URI-endpoint-to-minify-schema:String  )
            2. If only namespace is provided, lists all docTypes under namespace
                The list contains tuples of the form-  ( <docType:String> , <URI-endpoint-to-docType:String> , None, None)
        """
        path_of_namespace = self.schema_base_path + namespace
        files = [f for f in os.listdir(path_of_namespace) if isfile(join(path_of_namespace, f)) and f.__contains__('.schema.json')]
        version_list = list()

        if docType is None:
            for file in files:
                m = re.search('^[A-Za-z]*\.', file)
                docType = m.group().replace('.', '')
                lst_item = (docType, '/schema/' + namespace + '/' + docType, None, None)
                version_list.append(lst_item)
        else:
            for file in files:
                self.logger.debug( " looking at : " + file)
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
