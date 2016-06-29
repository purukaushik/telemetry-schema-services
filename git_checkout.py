#!/usr/bin/env python
import git, os
import json
#REMOTE_URL = 'git@github.com:mozilla-services/mozilla-pipeline-schemas.git'
#REMOTE_URL = 'https://github.com/purukaushik/mozilla-pipeline-schemas.git'
#REMOTE_URL = 'https://github.com/mreid-moz/mozilla-pipeline-schemas.git'
# TODO : periodically do this to get updated schemas

#-----GIT CONFIG-----


def gitcheckout():
    checkout(get_config())
    
def checkout(config):
    """
    Checkout from git with values from branch=config['branch'], remote_url=config['remote_url']
    """
    if os.path.isdir(config['os_dir']):
        fetch_branch(config)
    else:
        print 'DEBUG: cloning '+ config['remote_url']
        try:
            git.Git().clone(config['remote_url'])
            fetch_branch(config)
        except git.exc.GitCommandError:
            print "Git error. using local"
            pass
        
def fetch_branch(config):
    print 'DEBUG: directory exists. will pull instead of clone...'
    repo = git.Repo.init('./mozilla-pipeline-schemas')
    origin = repo.remotes.origin
    try:
        print "DEBUG: Fetching branch: " + config['branch']
        origin.fetch(config['branch'])
        # git checkout branch
        git.Git('./mozilla-pipeline-schemas').checkout(config['branch'])
        # git pull origin branch
        fetch_info =origin.pull(config['branch'])
        
        print 'DEBUG: done pulling ' + config['branch']
        headcommit = fetch_info[0].ref.commit
        import datetime
        commit_msg = repr(headcommit.author) + "  " + datetime.datetime.fromtimestamp(int(headcommit.authored_date)).strftime('%Y-%m-%d %H:%M:%S') +  "  " + headcommit.message 
        print 'DEBUG: latest commit: ' + commit_msg
        pass
    except git.exc.GitCommandError:
        print "Git error. using local"
        pass
        
def get_config():
    return json.load(open('git_config.json'))

if __name__ == '__main__':
    gitcheckout()
