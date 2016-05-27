#!/usr/bin/env python
import git, os

#REMOTE_URL = 'git@github.com:mozilla-services/mozilla-pipeline-schemas.git'
REMOTE_URL = 'https://github.com/purukaushik/mozilla-pipeline-schemas.git'

# TODO : periodically do this to get updated schemas
def gitcheckout():
    if os.path.isdir('./mozilla-pipeline-schemas'):
        print 'DEBUG: directory exists. skipping cloning...'
        pass
    else:
        print 'DEBUG: cloning '+ REMOTE_URL
        git.Git().clone(REMOTE_URL)


if __name__ == '__main__':
    gitcheckout()
