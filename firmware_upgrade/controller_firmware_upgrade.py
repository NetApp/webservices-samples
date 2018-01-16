#!/usr/bin/env python
"""
Demonstrate a controller firmware upgrade using the Embedded Web Services API.
"""
import json
import logging
import sys
import time
from pprint import pformat

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configurable Parameters

# An absolute path to a firmware file:
path_to_firmware_file = '/home/example/RCB_08.40.00.00_280x.dlp'

# A list of controller addresses
controller_addresses = ["https://example-a.ict.englab.netapp.com:8443",
                        "https://example-b.ict.englab.netapp.com:8443"]

# If true, we want to ignore the results of the health check
IGNORE_HEALTH_CHECK = False

# Authentication information for the array
auth = ('admin@local', '****')


# End Configurable Parameters

def get_session():
    """Define a re-usable Session object"""
    session = requests.Session()
    session.auth = auth
    session.verify = False
    return session


API = {
    'embedded_firmware': '/devmgr/v2/firmware/embedded-firmware',
    'system': '/devmgr/v2/storage-systems/1',
    'health_check': '/devmgr/v2/health-check',
}


def health_check(session, health_url):
    """Validates that we *should* run a firmware upgrade operation on this storage-system.
    :param session a persistent session for making HTTP requests
    :param health_url the url of the API to call
    :return True if we are okay to proceed, false if a problem was found
    """
    LOG = logging.getLogger(__name__)
    result = session.post(health_url, headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
                          data=json.dumps({"storageDeviceIds": ["1"]}))

    result.raise_for_status()
    finished = False
    while not finished:
        time.sleep(1)
        result = session.get(health_url, headers={'Accept': 'application/json'})
        result.raise_for_status()
        result = result.json()
        if result['healthCheckRunning']:
            continue

        if not result['results'][0]['successful']:
            LOG.error("The healthCheck has failed: %s", pformat(result))
            if not IGNORE_HEALTH_CHECK:
                return False
            else:
                return True
        else:
            LOG.debug("The healthCheck has passed: %s", pformat(result))
            LOG.info("The healthCheck was successful.")
            finished = True

    return True


def upload_firmware_file(session, firmware_url):
    """Upload and activate the firmware file (it will activate on both controllers)
        :param session a persistent session for making HTTP requests
        :param firmware_url the url of the API to call
        :raise HTTPError if the request returned a failure status
    """
    LOG = logging.getLogger(__name__)
    LOG.info('Uploading file %s', path_to_firmware_file)
    with open(path_to_firmware_file, 'rb') as firmware_file:
        file_multipart = {
            'dlpfile': firmware_file
        }
        response = session.post(firmware_url, files=file_multipart, verify=False)
        LOG.info("Received %s from the upgrade process.", response.status_code)

        LOG.debug(response.headers)
        if response.status_code < 300:
            if response.headers.get('Content-Type') == 'application/json':
                LOG.debug(response.json())
        else:
            LOG.warn(response.text)
        response.raise_for_status()


def wait_for_availability(session, system_urls):
    """Wait for the controllers to reboot before returning.
        :param session a persistent session for making HTTP requests
        :param system_urls a list of urls we can call to ensure that the controller[s] are up
        :raise HTTPError if the request returned a failure status
    """
    LOG = logging.getLogger(__name__)
    # At this point, the API will temporarily become unavailable. Let's ping the API on both controllers
    #  until we get a response.

    for system_url in system_urls:
        retry_max = 1000
        retries = 0
        offline = True
        # It'll take a few moments for the upgrade to start and the device to go offline.
        # Let's make sure we don't check for availability too soon.
        LOG.info("Sleeping for 10s...")
        time.sleep(10)
        while offline and retries < retry_max:
            time.sleep(1)
            if retries % 60 == 0:
                LOG.info("Been waiting for %s minutes.", retries / 60)
            try:
                response = session.get(system_url, verify=False,
                                       headers={'Content-Type': 'application/json', 'Accept': 'application/json'})
                LOG.info("Received a successful response, the device is now online again.")
                offline = False
                if response.status_code < 300:
                    LOG.info("New firmware version: %s", response.json()['fwVersion'])
                elif response.headers.get('Content-Type') == 'application/json':
                    LOG.warn("Received an error fetching the device: status_code=%s, response=%s",
                             response.status_code,
                             response.json())

            except requests.exceptions.ConnectionError:
                LOG.debug("Received a connection error. Retry on count %s...", retries)
                # This is expected
                pass
            retries += 1


def main():
    LOG = logging.getLogger(__name__)
    api_a = {key: controller_addresses[0] + API[key] for key in API}
    api_b = {key: controller_addresses[1] + API[key] for key in API}

    # We'll re-use this session
    session = get_session()

    health_url = api_a.get('health_check')
    healthy = health_check(session, health_url)
    if not healthy:
        sys.exit(1)

    firmware_url = api_a.get('embedded_firmware')

    upload_firmware_file(session, firmware_url)

    system_urls = [api_a.get('system'), api_b.get('system')]
    wait_for_availability(session, system_urls)
    LOG.info("Upgrade operation is complete.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
    main()
