#!/usr/bin/env python
import git, os
import json
import datetime
import logging

#logging.basicConfig(filename='git_checkout.log', filemode='a', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s',datefmt='%a, %d %b %Y %H:%M:%S',)
#logger = logging.getLogger('git_checkout')

def gitcheckout(logger):
    checkout(get_config(), logger)
    
def checkout(config, logger):
    """
    Checkout from git with values from branch=config['branch'], remote_url=config['remote_url']
    """
    if os.path.isdir(config['os_dir']):
        fetch_branch(config, logger)
    else:
        logger.debug('cloning '+ config['remote_url'])
        try:
            git.Git().clone(config['remote_url'])
            fetch_branch(config, logger)
        except git.exc.GitCommandError:
            logger.warn('Git error. using local')
            pass
        
def fetch_branch(config, logger):
    logger.debug('directory exists. will pull instead of clone...')
    repo = git.Repo.init("./" + config['os_dir'])
    origin = repo.remotes.origin
    try:
        logger.debug("Fetching branch: " + config['branch'])
        origin.fetch(config['branch'])
        # git checkout branch
        git.Git('./' + config['os_dir']).checkout(config['branch'])
        # git pull origin branch
        fetch_info =origin.pull(config['branch'])
        
        logger.debug('done pulling ' + config['branch'])
        headcommit = fetch_info[0].ref.commit
        commit_msg = repr(headcommit.author) + "  " + datetime.datetime.fromtimestamp(int(headcommit.authored_date)).strftime('%Y-%m-%d %H:%M:%S') +  "  " + headcommit.message 
        logger.debug('latest commit: ' + commit_msg)
        pass
    except git.exc.GitCommandError:
        logger.warn("Git error. using local")
        pass
        
def get_config():
    return json.load(open('git_config.json'))

if __name__ == '__main__':
    gitcheckout()
