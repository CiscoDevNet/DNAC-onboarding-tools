#!/usr/bin/env python
from __future__ import print_function
import csv
import json
import requests
import os
import os.path
import logging
from netaddr import IPNetwork, IPAddress
from argparse import ArgumentParser
from utils import login, get, post, delete


def get_file_id(dnac, file_name):
    response = get(dnac, "dna/intent/api/v1/file/namespace/config")
    for file in response.json()['response']:
        if file['name'] == file_name:
            return file['id']
    raise ValueError("Cannot find file:{}".format(file_name))


def parse_file(mappingfile):
    '''
    takes a mapping file and parses it.  ipsubnet -> configfile
    Validates the ip range, and also the config file exists in DNAC.
    :param mappingfile:
    :return:
    '''
    mapping = {}
    f = open(mappingfile, 'rt')
    try:
        reader = csv.DictReader(f)
        for ip_row in reader:
            print(ip_row)
            file_id = get_file_id (dnac, ip_row['configFile'])
            print (file_id)
            # validate the IP
            ip = IPNetwork(ip_row['subnet'])
            mapping[ip_row['subnet']+","+ip_row['upLink']] = file_id
    finally:
        f.close()
    return mapping

def find_workflow(dnac,name):
    response = get(dnac, 'dna/intent/api/v1/onboarding/pnp-workflow?name={}'.format(name))
    return response.json()

def create_workflow(dnac, device_ip, interface, file_id):
    print('creating workflow')


    if interface == "*":
        interface = ""
    safe_interface = interface.replace("/","-")
    name = '{}:{}'.format(device_ip, safe_interface)
    old_workflow = find_workflow(dnac, name)
    if old_workflow != []:
        response = delete(dnac, "dna/intent/api/v1/onboarding/pnp-workflow/{}".format(old_workflow[0]['id']))
        print ("Deleting Old workflow")
        logging.debug(json.dumps(response.json()))
    payload = {
    "name": name,
    "description": "",
    "currTaskIdx": 0,
    "tasks": [
        {
            "configInfo": {
                "saveToStartUp": True,
                "connLossRollBack": True,
                "fileServiceId": file_id
            },
            "type": "Config",
            "currWorkItemIdx": 0,
            "name": "Config Download",
            "taskSeqNo": 0
        }
    ],
    "addToInventory": True
}
    logging.debug(json.dumps(payload))
    response = post(dnac, "dna/intent/api/v1/onboarding/pnp-workflow", payload)
    print(json.dumps(response.json()))
    workflow_id=response.json()['id']

    return workflow_id

def claim_device(dnac, device_id, file_id, workflow_id):
    print('claim device')
    payload = {
  "workflowId": workflow_id,
  "deviceClaimList": [
    {
      "configList": [
        {
          "configId": "",
          "configParameters": [
          ]
        }
      ],
      "deviceId": device_id
    }
  ],
  "populateInventory": True,
  "imageId": None,
  "projectId": None,
  "configId": file_id
}

    logging.debug(json.dumps(payload))
    response = post(dnac, "dna/intent/api/v1/onboarding/pnp-device/claim", payload)
    print(json.dumps(response.json()))

def claim(dnac, device_ip, interface, device_id, file_id):
    print ("Claiming {} with file {}".format(device_ip, file_id))
    workflow_id = create_workflow(dnac, device_ip, interface, file_id)
    claim_device(dnac, device_id, file_id, workflow_id)

def poll_and_wait(dnac, mapping):
    devices = get(dnac, "dna/intent/api/v1/onboarding/pnp-device?source=Network&onbState=Initialized")

    for device in devices.json():
        ip_address = device['deviceInfo']['httpHeaders'][0]['value']
        ip = IPAddress(ip_address)

        cdp_links = [ link['remoteInterfaceName'] for link in device['deviceInfo']['neighborLinks']]

        print("Trying to find mapping for {}".format(ip))
        for network_cdp in mapping.keys():
            network = network_cdp.split(',')[0]
            cdp = network_cdp.split(',')[1]
            if IPAddress(ip_address) in IPNetwork(network):
                if cdp == "*"  or cdp in cdp_links:
                    print ("{}:{}:{}:{}".format(device['id'],network,cdp, mapping[network_cdp]))
                    claim(dnac, ip_address, cdp, device['id'],  mapping[network_cdp])
                else:
                    print("No Link match upstream")

if __name__ == "__main__":
    # can we use default workflow? No.  that will keep old configfile.  need to create ta new one.
    # do we put or just create new?
    parser = ArgumentParser(description='Select options.')
    parser.add_argument('-v', action='store_true',
                        help="verbose")
    parser.add_argument( 'mapping', type=str,
            help='mapping file between IP subnet, configfile')
    args = parser.parse_args()

    if args.v:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    dnac = login()
    print ("Using device file:", args.mapping)
    mapping = parse_file(args.mapping)
    print ("##########################")
    poll_and_wait(dnac, mapping)