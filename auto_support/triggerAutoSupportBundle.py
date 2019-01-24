"""
Triggering a Webservices AutoSupport bundle example.

Usage:
    triggerAutoSupportBundle <operation_type> <dispatch_type>
    triggerAutoSupportBundle -h
Arguments:
    operation_type the AutoSupport operation type
    dispatch_type the AutoSupport dispatch type
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

def triggerAutoSupportBundle(operation_type, dispatch_type):
    # Get a connection
    connection = get_session()

    # Setup the request body with the desired operation and dispatch types
    request_data = {
        'operationType': operation_type,
        'dispatchType': dispatch_type
    }

    LOG.info("Triggering an AutoSupport bundle with an operation type of [%s] and a dispatch type of [%s]." %
        (operation_type, dispatch_type))

    result = connection.post('http://{server}/devmgr/v2/auto-support'.format(server=PROPS.server), data=json.dumps(request_data))

    if result.status_code != 200:
        LOG.error("Trigger AutoSupport bundle attempt failed")
    else:
        LOG.info("Trigger AutoSupport bundle attempt succeeded")

    result.raise_for_status()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
        format='%(relativeCreated)dms %(levelname)s %(module)s.%(funcName)s:%(lineno)d\n %(message)s')
    args = docopt.docopt(__doc__)
    triggerAutoSupportBundle(str(args.get('<operation_type>')), str(args.get('<dispatch_type>')))