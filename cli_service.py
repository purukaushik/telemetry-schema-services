"""Schema Service CLI.
Schema retrieval command line utility.
Usage:
cli_service.py [-n <namespace>]
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
    if '-n' in arguments:
        namespace = arguments['-n']
        if '-d' in arguments:
            docType = arguments['-d']
            if '-v' in arguments:
                version = arguments['-v']
                import logging
                logger = logging.getLogger(__name__)
                if version is not None:
                    print get_schema_json(namespace,docType,version,logger).read()
                else:
                    lst = get_doctypes_versions(namespace,docType,logger)
                    for needed,u1,u2,u3 in lst:
                        print needed
