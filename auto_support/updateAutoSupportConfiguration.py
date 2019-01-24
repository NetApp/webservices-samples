"""
Updating the Webservices AutoSupport configuration example.

Usage:
    updateAutoSupportConfiguration <configuration_file>
    updateAutoSupportConfiguration
Arguments:
    configuration_file the AutoSupport configuration file
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

def updateAutoSupportConfiguration(configuration_file):
    # Get a connection
    connection = get_session()

    LOG.info("Updating the AutoSupport configuration using configuration file [%s]." % (configuration_file))

    data = ""
    with open('configuration_data.json') as f:
        data = json.load(f)

    result = connection.post('http://{server}/devmgr/v2/auto-support/configuration'.format(server=PROPS.server), data=json.dumps(data))

    if result.status_code != 200:
        LOG.error("Update AutoSupport configuration attempt failed")
    else:
        LOG.info("Update AutoSupport configuration attempt succeeded")

    result.raise_for_status()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
        format='%(relativeCreated)dms %(levelname)s %(module)s.%(funcName)s:%(lineno)d\n %(message)s')
    args = docopt.docopt(__doc__)
    updateAutoSupportConfiguration(str(args.get('<configuration_file>')))