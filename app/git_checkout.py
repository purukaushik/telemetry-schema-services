#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import git, os
import json
import datetime
import mozschemas_logging

logger = mozschemas_logging.getLogger(__name__)

def gitcheckout():
    checkout(get_config())
    
def checkout(config):
    """
    Checkout from git with values from branch=config['branch'], remote_url=config['remote_url']
    """
    if os.path.isdir(config['os_dir']):
        logger.debug('directory exists. will pull instead of clone...')
        fetch_branch(config)
    else:
        logger.debug('cloning '+ config['remote_url'])
        try:
            os.mkdir(config['os_dir'])
            git.Git().clone(config['remote_url'], config['os_dir'])
            fetch_branch(config)
        except git.exc.GitCommandError as err:
            logger.exception('Git error while cloning. Using local')

def fetch_branch(config):

    repo = git.Repo.init(config['os_dir'])
    origin = repo.remotes.origin
    try:
        logger.debug("Fetching branch: " + config['branch'])
        origin.fetch(config['branch'])
        # git checkout branch
        git.Git(config['os_dir']).checkout(config['branch'])
        # git pull origin branch
        fetch_info =origin.pull(config['branch'])
        
        logger.debug('done pulling ' + config['branch'])
        headcommit = fetch_info[0].ref.commit
        commit_msg = repr(headcommit.author) + "  " + datetime.datetime.fromtimestamp(int(headcommit.authored_date)).strftime('%Y-%m-%d %H:%M:%S') +  "  " + headcommit.message 
        logger.debug('latest commit: ' + commit_msg)
    except git.exc.GitCommandError:
        logger.exception('Git error while cloning. Using local')
        
def get_config():
    curr_dir = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    config = json.load(open(os.path.join(curr_dir, 'git_config.json')))
    if os.path.isfile(config['os_dir']):
        config['os_dir'] = os.path.abspath(os.path.join(os.getcwd(), os.path.dirname(config['os_dir'])))
    return config

