"""
Retrieving the job data for a Webservices AutoSupport bundle request example.

Usage:
    retrieveAutoSupportJob [--job_id=<id>]
    retrieveAutoSupportJob -h
Options:
    --job_id=id the job id of a prior AutoSupport bundle request. When ommitted, this
    command will default to retrieve a list of all jobs.
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

def retrieveAutoSupportJob(job_id):
    # Setup the appropriate url based on the given job id
    request_url = None
    user_message_jobs = None
    if (job_id is None) or not str(job_id):
        user_message_jobs = 'all jobs'
        request_url = 'http://{server}/devmgr/v2/auto-support/jobs'
    else:
        user_message_jobs = 'job id [%s]' % str(job_id)
        request_url = 'http://{server}/devmgr/v2/auto-support/jobs/{job_id}'.format(
            server=PROPS.server, job_id=job_id)

    # Get a connection
    connection = get_session()

    LOG.info("Retieving job data for %s." % (user_message_jobs))

    result = connection.get(request_url.format(server=PROPS.server))

    if result.status_code != 200:
        LOG.error("AutoSupport job retrieval request failed")
    else:
        LOG.info("AutoSupport job retrieval request succeeded")

    result.raise_for_status()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
        format='%(relativeCreated)dms %(levelname)s %(module)s.%(funcName)s:%(lineno)d\n %(message)s')
    args = docopt.docopt(__doc__)
    retrieveAutoSupportJob(args.get('--job_id'))