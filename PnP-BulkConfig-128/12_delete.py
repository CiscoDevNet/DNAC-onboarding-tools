#!/usr/bin/env python
from __future__ import print_function
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
        print ("Cannot find serial:{}".format(deviceSerial))

def delete_device(dnac, deviceId):
    response = delete(dnac, "onboarding/pnp-device/{}".format(deviceId))
    if response.status_code == 400:
        message = json.loads(response.text)
        return message['response']['message']
    return response.json()['deviceInfo']['state']

def find_and_delete(dnac, devices):

    f = open(devices, 'rt')
    try:
        reader = csv.DictReader(f)
        for device_row in reader:
            #print ("Variables:",device_row)

            deviceId = find_device(dnac, device_row['serial'])
            if deviceId is not None:
                print ("deleting:{}: {} Status:".format(device_row['serial'], deviceId),end='')
                status = delete_device(dnac, deviceId)
                print (status)

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

