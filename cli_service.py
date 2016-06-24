"""Schema Service CLI.
Schema retrieval command line utility.
Usage:
cli_service.py [(-n <namespace>)]
cli_service.py [(-n <namespace>  -d <doctype>)]
cli_service.py [(-n <namespace>  -d <doctype> -v <version>)]
cli_service.py (-h | --help)
    
Options:
-h --help       Show this screen.
-n namespace    List all docTypes under namespace
-n namespace -d doctype List versions under namespace and docType
-n namespace -d doctype -v version Show schema @ namespace/docType/version
"""

from service_commons import get_schema, get_schema_json, get_doctypes_versions
from docopt import docopt
import json
if __name__ == "__main__":
    arguments = docopt(__doc__, version='CLI version v0.0')
    
    namespace = 'telemetry'
    docType = 'main'
    if arguments['-n'] is not None:
        namespace = arguments['-n']
        
        docType = arguments['-d']
        version = arguments['-v']
        import logging
        logger = logging.getLogger(__name__)
        lst = get_doctypes_versions(namespace,docType,logger)
        versions = list()
        for needed,u1,u2,u3 in lst:
            versions.append(needed)    
        if version is not None:
            if version in versions:
                print get_schema_json(namespace,docType,version,logger).read()
            else:
                print "No such version. Try one of these:\n"
        else:
            
            if len(versions)==0:
                print "No such docType. Try one of these:\n"
                lst = get_doctypes_versions(namespace,None,logger)
                for needed,u1,u2,u3 in lst:
                    print needed
            else:
                print versions
    else:
        print "ERROR! Specify Namespace."

        
