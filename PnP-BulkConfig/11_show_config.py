#!/usr/bin/env python
from __future__ import print_function
import csv
import json

from argparse import ArgumentParser
from utils import login, get, put


def get_config(dnac,templateId, params):
    body = {
            "params": params,
             "templateId": templateId
                }
    print(body)
    response = put(dnac, "template-programmer/template/preview", payload=json.dumps(body))
    print(response.json()['cliPreview'])

def get_device(dnac, serial):
    params = {}
    response = get(dnac, "onboarding/pnp-device?{}".format(serial))
    data = response.json()
    print(json.dumps(data, indent=4))
    try:
        device = response.json()[0]['workflowParameters']['configList']
        templateId = device[0]['configId']
        print(templateId)
        for p in device[0]['configParameters']:
            params[p['key']] = p['value']
        print(params)
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
