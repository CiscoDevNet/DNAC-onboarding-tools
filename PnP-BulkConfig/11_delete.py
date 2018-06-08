#!/usr/bin/env python

import csv
import json
import requests
import os
import os.path
from argparse import ArgumentParser
from utils import login, get, post, delete


def find_device(dnac,deviceSerial):
    response = get (dnac, "onboarding/pnp-device?serialNumber={}".format(deviceSerial))

    try:
        return response.json()[0]['id']
    except IndexError as e:
        print "Cannot find serial:{}".format(deviceSerial)

def delete_device(dnac, deviceId):
    response = delete(dnac, "onboarding/pnp-device/{}".format(deviceId))
    print response.json()

def find_and_delete(dnac, devices):

    f = open(devices, 'rt')
    try:
        reader = csv.DictReader(f)
        for device_row in reader:
            print ("Variables:",device_row)

            deviceId = find_device(dnac, device_row['serial'])
            if deviceId is not None:
                print "deleting:{}:{}".format(device_row['serial'], deviceId)
                delete_device(dnac, deviceId)

    finally:
        f.close()

if __name__ == "__main__":
    parser = ArgumentParser(description='Select options.')
    parser.add_argument( 'devices', type=str,
            help='device inventory csv file')
    args = parser.parse_args()

    dnac = login()

    print ("Using device file:", args.devices)

    print ("##########################")
    find_and_delete(dnac, devices=args.devices)
