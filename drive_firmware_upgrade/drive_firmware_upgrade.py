#!/usr/bin/env python

"""
Demonstrate a drive firmware upgrade using the Embedded Web Services API or Web Services Proxy
"""

import logging
import time
from pprint import pformat

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
LOG = logging.getLogger(__name__)

# Configurable Parameters

# An absolute path to a firmware file:
path_to_firmware_file = 'EXAMPLE_DRIVE_FILE_PATH.dlp'

# A list of controller addresses
controller_addresses = ["https://example-b.ict.englab.netapp.com:8443",
                        "https://example-b.ict.englab.netapp.com:8443"]

# Authentication information for the array
auth = ('admin', 'admin')


# End Configurable Parameters

def get_session():
    """Define a re-usable Session object"""
    session = requests.Session()
    session.auth = auth
    session.verify = False
    return session


API = {
    'drives': '/devmgr/v2/storage-systems/{systemId}/drives',
    'compatibilities': '/devmgr/v2/storage-systems/{systemId}/firmware/drives',
    'drive_file_upload': '/devmgr/v2/files/drive/',
    'drive_files': '/devmgr/v2/files/drive/{filename}',
    'firmware_drives_initiate_upgrade': '/devmgr/v2/storage-systems/{systemId}/firmware/drives/initiate-upgrade',
    'firmware_drives_state': '/devmgr/v2/storage-systems/{systemId}/firmware/drives/state'
}


def optimal_drives(rest_client, api, drives=None):
    """Returns a list of all optimal drives from the array.

    :param rest_client: the rest client for which we pull the drives
    :param api: urls
    :param drives: an optional list of drive objects we want to check optimal status with.
    :returns: A list of optimal drive IDs from the array's rest client
    """
    """
    """
    drives_ref_list = []

    if not drives:
        drives_ret = rest_client.get(api.get('drives').format(systemId='1'))
        drives_ret.raise_for_status()
        drives = drives_ret.json()

    if isinstance(drives, dict):
        if drives['status'] == 'optimal':
            drives_ref_list.append(drives['driveRef'])
            LOG.debug("Drive id:{} is optimal.".format(drives['id']))
        else:
            LOG.debug("Drive id:{} is not optimal.".format(drives['id']))

    if isinstance(drives, list):
        for drive in drives:
            if drive['status'] == 'optimal':
                drives_ref_list.append(drive['driveRef'])
                LOG.debug("Drive id:{} is optimal.".format(drive['id']))
            else:
                LOG.debug("Drive id:{} is not optimal.".format(drive['id']))

    return drives_ref_list


def drive_firmware_upgrade(session, api, filename, drives=None):
    """Function to upgrade drive firmware

    :param session: client for which we use to initiate the upgrade
    :param api: urls
    :param filename: firmware filename
    :param drives: optional list of drives we want to specifically upgrade
    :return: rest response
    """
    with open(filename, 'rb') as firmware_file:

        # upload the fw file to the controller
        file_multipart = {
            'file': firmware_file
        }
        ret = session.post(api.get('drive_file_upload'), files=file_multipart)
        ret.raise_for_status()

        # Upgrade all compatible drives
        if drives is None:
            compatible_drives = fw_compatible_drives(session, api, filename)
        else:
            compatible_drives = fw_compatible_drives(session, api, filename, drives)

        # Update all drives
        if len(compatible_drives) is not 0:
            LOG.debug("Updating compatible drives...")
            response = session.post(api.get('firmware_drives_initiate_upgrade').format(systemId='1'),
                                    json={'filename': filename,
                                          'driveRefList': compatible_drives})

            # Wait until all drives are finished downloading
            while session.get(api.get('firmware_drives_state').format(systemId='1')).json()['overallStatus'] \
                    == 'downloadInProgress':
                time.sleep(2)
            LOG.debug('Drive firmware was updated successfully!')
        else:
            LOG.debug("Chosen firmware was not compatible with any drives in this array.")
            return None
        return response


def fw_compatible_drives(rest_client, api, filename, drives=None):
    """Runs a check of drives in the array for compatibility with firmware.

    :param rest_client: rest_client for which we use to get the drives.
    :param api: urls
    :param drives: drives for which we want to check the compatibility with.
    :param filename: the filename of the firmware to check compatibility.
    :return: a list of compatible drives to upgrade.
    """
    LOG.debug('Checking drive compatibility...')
    # we do not want to upgrade non-optimal drives
    if drives is None:
        drives = optimal_drives(rest_client, api)
    else:
        drives = optimal_drives(rest_client, api, drives)

    comp_drives = []
    compatibilities = rest_client.get(api.get('compatibilities').format(systemId='1')).json()['compatibilities']
    for firmware in compatibilities:
        compatible = firmware['compatibleDrives']
        if filename == firmware['filename']:
            for drive in drives:
                for compatible_drive in compatible:
                    if drive in compatible_drive['driveRef']:
                        comp_drives.append(drive)
                if drive not in comp_drives:
                    LOG.debug("Drive ref {} was not compatible with chosen firmware.".format(drive))
    return comp_drives


def main():
    api_a = {key: controller_addresses[0] + API[key] for key in API}
    api_b = {key: controller_addresses[1] + API[key] for key in API}

    # We'll re-use this session
    session = get_session()

    response = drive_firmware_upgrade(session, api_a, path_to_firmware_file)
    LOG.info("Returned: {}".format(pformat(response)))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
    main()
