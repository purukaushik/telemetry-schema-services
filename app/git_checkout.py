#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import git, os
import json
import datetime
import logging
import sys
from mozilla_cloud_services_logger.formatters import JsonLogFormatter



def gitcheckout(logger):
    checkout(get_config(), logger)
    
def checkout(config, logger):
    """
    Checkout from git with values from branch=config['branch'], remote_url=config['remote_url']
    """
    if os.path.isdir(config['os_dir']):
        logger.debug('directory exists. will pull instead of clone...')
        fetch_branch(config, logger)
    else:
        logger.debug('cloning '+ config['remote_url'])
        try:
            os.mkdir(config['os_dir'])
            git.Git().clone(config['remote_url'], config['os_dir'])
            fetch_branch(config, logger)
        except git.exc.GitCommandError as err:
            logger.error(err)
            logger.warn('Git error while cloning. Using local')
            pass
        
def fetch_branch(config, logger):

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
        pass
    except git.exc.GitCommandError:
        logger.warn("Git error while pulling latest. using local")
        pass
        
def get_config():
    curr_dir = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    config = json.load(open(os.path.join(curr_dir, 'git_config.json')))
    if os.path.isfile(config['os_dir']):
        config['os_dir'] = os.path.abspath(os.path.join(os.getcwd(), os.path.dirname(config['os_dir'])))
        print config
    return config

if __name__ == '__main__':

    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)
    handler.setFormatter(JsonLogFormatter(logger_name=__name__))
    logger.addHandler(handler)
    gitcheckout(logger)
