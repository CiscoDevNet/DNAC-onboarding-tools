#!/usr/bin/env python
from __future__ import print_function
import csv
import json
import requests
import os
import os.path
import logging
from argparse import ArgumentParser
from utils import login, get, post
#from fake import fake
logger = logging.getLogger()

def get_ip(host):
    try:
        ip = host['deviceInfo']['httpHeaders'][0]['value']
    except KeyError:
        ip =""
    return ip
def get_neighbour(host):
    try:
        # change to list comprehension
        links = ",".join([ link['remoteInterfaceName'] for link in host['deviceInfo']['neighborLinks']])
    except KeyError:
        links = ''
    return links
def get_workflow_name(host):
    try:
        workflowname = host['deviceInfo']['workflowName']
    except KeyError:
        workflowname = ""
    return workflowname

def process(data):
    fmt="{:13s}{:17}{:12}{:8}{:16}{:26}{:26}"
    print(fmt.format("Name","PID","State","Source","IP Address","Neighbour Interface","Workflow Name"))
    for host in data:
        logging.debug('Host:{}'.format(json.dumps(host)))
        print(fmt.format(host['deviceInfo']['name'],
                         host['deviceInfo']['pid'],
                         host['deviceInfo']['state'],
                         host['deviceInfo']['source'],
                         get_ip(host),
                         get_neighbour(host),
                         get_workflow_name(host)
                         ))
def process_single(device):
    print(json.dumps(device, indent=2))

if __name__ == "__main__":
    parser = ArgumentParser(description='Select options.')
    parser.add_argument( '--device', type=str,
            help='serial number of device')
    parser.add_argument('-v', action='store_true',
                        help="verbose")
    args = parser.parse_args()

    if args.v:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        # set logger
    logger.debug("Logging enabled")

    dnac = login()

    if args.device:
        # get the device
        device = response = get(dnac, "dna/intent/api/v1/onboarding/pnp-device?name={}".format(args.device))
        process_single(device.json())
    else:
        # show all devices
        response = get(dnac, "dna/intent/api/v1/onboarding/pnp-device")
        process(response.json())
