#!/usr/bin/env python
import git, os

#REMOTE_URL = 'git@github.com:mozilla-services/mozilla-pipeline-schemas.git'
REMOTE_URL = 'https://github.com/purukaushik/mozilla-pipeline-schemas.git'

# TODO : periodically do this to get updated schemas
def gitcheckout():
    if os.path.isdir('./mozilla-pipeline-schemas'):
        print 'DEBUG: directory exists. will pull instead of clone...'
        repo = git.Repo.init('./mozilla-pipeline-schemas')
        origin = repo.remotes.origin
        fetch_info = origin.fetch()
        origin.pull()
        print 'DEBUG: done pulling'
        headcommit = repo.head.commit
        import datetime
        commit_msg = repr(headcommit.author) + "  " + datetime.datetime.fromtimestamp(int(headcommit.authored_date)).strftime('%Y-%m-%d %H:%M:%S') +  "  " + headcommit.message
        print 'DEBUG: latest commit: ' + commit_msg
        pass
    else:
        print 'DEBUG: cloning '+ REMOTE_URL
        git.Git().clone(REMOTE_URL)


if __name__ == '__main__':
    gitcheckout()
