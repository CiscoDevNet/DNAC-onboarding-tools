#!/usr/bin/env python
from __future__ import print_function
import csv
import json

from argparse import ArgumentParser
from utils import login, get, put


def get_config(dnac,templateId, params):
    body = {
             "templateId": templateId,
            "params": params
                }
    response = put(dnac, "template-programmer/template/preview", payload=json.dumps(body))
    print (response.json()['cliPreview'])

def get_device(dnac, serial):
    params = {}
    response = get(dnac, "onboarding/pnp-device?serialNumber={}".format(serial))
    try:
        device = response.json()[0]['workflowParameters']['configList']
        templateId = device[0]['configId']
        for p in device[0]['configParameters']:
            params[p['key']] = p['value']
        return templateId, params
    except KeyError:
        print("Cannot find tempate for device serial {}".format(serial))
        raise KeyError

if __name__ == "__main__":
    parser = ArgumentParser(description='Select options.')
    parser.add_argument( 'serial', type=str,
            help='device serial number')
    args = parser.parse_args()

    dnac = login()
    print ("looking for serial number:", args.serial)


    templateId, params = get_device(dnac, args.serial)
    get_config(dnac, templateId, params)