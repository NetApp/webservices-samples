"""
Updating the Webservices AutoSupport configuration example.

Usage:
    update_auto_support_configuration
    update_auto_support_configuration -h
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

def update_auto_support_configuration():
    # Get a connection
    connection = get_session()

    # Set the desired AutoSupport configuration
    data = {
        "autoSupportEnabled": True
    }

    try:
        LOG.info("Updating the AutoSupport configuration.")
        result = connection.post('http://{server}/devmgr/v2/auto-support/configuration'.format(server=PROPS.server), data=json.dumps(data))
        try:
            result.raise_for_status()
        except requests.HTTPError as e:
            LOG.error("Update AutoSupport configuration attempt failed || http status code: %s" % str(e.response.status_code))
            raise
        else:
            LOG.info("Update AutoSupport configuration attempt succeeded")

        LOG.info("Retrieving current AutoSupport configuration")
        result = connection.get('http://{server}/devmgr/v2/auto-support/configuration'.format(server=PROPS.server))
        try:
            result.raise_for_status()
        except requests.HTTPError as e:
            LOG.error("AutoSupport configuration retrieval attempt failed || http status code: %s" % str(e.response.status_code))
            raise
    except Exception as e:
        LOG.error("Server connection failured")
        raise

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
        format='%(relativeCreated)dms %(levelname)s %(module)s.%(funcName)s:%(lineno)d\n %(message)s')
    args = docopt.docopt(__doc__)
    update_auto_support_configuration()
