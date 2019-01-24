"""
Retrieve current Webservices AutoSupport configuration example.

Usage:
    retrieveAutoSupportConfiguration
    retrieveAutoSupportConfiguration -h
Options:
    -h --help Show this screen.
    --version Show version.
"""

import docopt
import json
import logging
import requests

from base import Properties, get_session

PROPS = Properties()
LOG = logging.getLogger(__name__)

def retrieveAutoSupportConfiguration():
    # Get a connection
    connection = get_session()

    LOG.info("Retieving current AutoSupport configuration")

    result = connection.get('http://{server}/devmgr/v2/auto-support/configuration'.format(server=PROPS.server))

    if result.status_code != 200:
        LOG.error("AutoSupport configuration retrieval request failed")
    else:
        LOG.info("AutoSupport configuration retrieval succeeded")

    result.raise_for_status()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
        format='%(relativeCreated)dms %(levelname)s %(module)s.%(funcName)s:%(lineno)d\n %(message)s')
    args = docopt.docopt(__doc__)
    retrieveAutoSupportConfiguration()