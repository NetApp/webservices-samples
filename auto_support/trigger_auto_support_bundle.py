"""
Triggering a Webservices AutoSupport bundle example.

Usage:
    trigger_auto_support_bundle <operation_type> <dispatch_type>
    trigger_auto_support_bundle -h
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

def trigger_auto_support_bundle(operation_type, dispatch_type):
    # Get a connection
    connection = get_session()

    # Setup the request body with the desired operation and dispatch types
    # The operation type determines whether the bundle will be collected and availble
    # for local retrieval or if the bundle will be dispatched to the AutoSupport
    # backend server. The dispatch type indicates what type of bundle will be collected.
    # Refer to the Webservices API documentation for further information.
    request_data = {
        'operationType': operation_type,
        'dispatchType': dispatch_type
    }

    response_data = None
    try:
        LOG.info("Triggering an AutoSupport bundle with an operation type of [%s] and a dispatch type of [%s]." %
            (operation_type, dispatch_type))
        result = connection.post('http://{server}/devmgr/v2/auto-support'.format(server=PROPS.server), data=json.dumps(request_data))
        try:
            result.raise_for_status()
            LOG.info("Trigger AutoSupport bundle attempt succeeded")
            response_data = result.json()
        except Exception as e:
            LOG.error("Trigger AutoSupport bundle attempt failed")
            raise

        LOG.info("Retrieving job data for %s." % (response_data['jobId']))
        result = connection.get('http://{server}/devmgr/v2/auto-support/jobs/{id}'.format(server=PROPS.server, id=response_data['jobId']))
        try:
            result.raise_for_status()
            response_data = result.json()
            LOG.info("AutoSupport job retrieval request succeeded")
            LOG.info("Job data:\n%s" % str(response_data))
        except Exception as e:
            LOG.error("AutoSupport job retrieval request failed")
            raise
    except Exception as e:
        LOG.error("Server connection failure")
        raise

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
        format='%(relativeCreated)dms %(levelname)s %(module)s.%(funcName)s:%(lineno)d\n %(message)s')
    args = docopt.docopt(__doc__)
    trigger_auto_support_bundle(str(args.get('<operation_type>')), str(args.get('<dispatch_type>')))
