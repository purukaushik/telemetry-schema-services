#!/usr/bin/env python
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Schema Service CLI.
Schema retrieval command line utility.
Usage:
mozschemas_cli.py [(-n <namespace>)]
mozschemas_cli.py [(-n <namespace>  -d <doctype>)]
mozschemas_cli.py [(-n <namespace>  -d <doctype> -v <version>)]
mozschemas_cli.py (-h | --help)
    
Options:
-h --help       Show this screen.
-n namespace    List all docTypes under namespace
-n namespace -d doctype List versions under namespace and docType
-n namespace -d doctype -v version Show schema @ namespace/docType/version
"""

import logging
import sys

from docopt import docopt
from mozilla_cloud_services_logger.formatters import JsonLogFormatter

import git_checkout
from mozschemas_common import SchemasLocalFilesHelper

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    arguments = docopt(__doc__, version = 'CLI version v0.0')

    # defaults
    namespace = 'telemetry'
    docType = 'main'

    handler = logging.StreamHandler(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)
    handler.setFormatter(JsonLogFormatter(logger_name=__name__))
    logger.addHandler(handler)
    git_checkout.gitcheckout(logger)

    schelper = SchemasLocalFilesHelper()

    if arguments['-n'] is not None:
        namespace = arguments['-n']
        
        docType = arguments['-d']
        version = arguments['-v']
        lst = schelper.get_doctypes_versions(namespace, docType, logger)
        versions = list()
        for doctype_version, u1, u2, u3 in lst:
            versions.append(doctype_version)
        if version is not None:
            if version in versions:
                print schelper.get_schema_json(namespace, docType, version, logger).read()
            else:
                print "No such version. Try one of these:\n"
                print versions
        else:
            if len(versions)==0:
                print "No such docType. Try one of these:\n"
                lst = schelper.get_doctypes_versions(namespace, None, logger)
                for doctype_version, u1, u2, u3 in lst:
                    print doctype_version
            else:
                print versions
    else:
        print "ERROR! Specify Namespace."
        print __doc__