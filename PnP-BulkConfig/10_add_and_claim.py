#!/usr/bin/env python
from __future__ import print_function
import csv
import json
import requests
import os
import os.path
from argparse import ArgumentParser
from utils import login, get, post



def add_device(dnac, name, serial, pid):
    payload = [{
	"deviceInfo": {
		"name": name,
		"serialNumber": serial,
		"pid": pid,
		"sudiRequired": False,
		"userSudiSerialNos": [],
		"stack": False,
		"aaaCredentials": {
			"username": "",
			"password": ""
		}
	}
}]
    device = post(dnac, "onboarding/pnp-device/import", payload)
    try:
        deviceId = device.json()['successList'][0]['id']
    except IndexError as e:
        print ('##SKIPPING device:{},{}:{}'.format(name, serial, device.json()['failureList'][0]['msg']))
        deviceId = None

    return deviceId

def claim_device(dnac,deviceId, configId, workflowId, params):
    payload = {
	"deviceClaimList": [{
		"deviceId": deviceId,
		"configList": [{
			"configId": configId,
			"configParameters": params
		}]
	}],
	"projectId": None,
	"workflowId": workflowId,
	"configId": None,
	"imageId": None,
	"populateInventory": True
}
    #print json.dumps(payload, indent=2)

    claim = post(dnac,"onboarding/pnp-device/claim", payload)
    return claim.json()['message']

def get_workflow(dnac,workflowName):
    response = get (dnac, "onboarding/pnp-workflow")
    for workflow in response.json():
        if workflow['name'] == workflowName:
            workflowId = workflow['id']
            #print json.dumps(workflow, indent=4)
            for tasks in workflow['tasks']:
                configId = tasks['configInfo']['configId']
            return workflowId, configId

    raise ValueError("Cannot find template:{}".format(workflowName))

def get_template(dnac, configId, supplied_params):
    params=[]
    response = get(dnac, "template-programmer/template/{}".format(configId))
    for vars in response.json()['templateParams']:
        name = vars['parameterName']
        params.append({"key": name, "value": supplied_params[name]})
    #print params
    return params

def create_and_upload(dnac, devices):

    f = open(devices, 'rt')
    try:
        reader = csv.DictReader(f)
        for device_row in reader:
            #print ("Variables:",device_row)

            try:
                workflowId, configId = get_workflow(dnac, device_row['workflow'])
            except ValueError as e:
                print("##ERROR {},{}: {}".format(device_row['name'],device_row['serial'], e))
                continue

            params = get_template(dnac, configId, device_row)

            deviceId = add_device(dnac, device_row['name'], device_row['serial'], device_row['pid'])
            if deviceId is not None:
                #claim
                claim_status = claim_device(dnac, deviceId, configId, workflowId, params)
                if "Claimed" in claim_status:
                    status = "PLANNED"
                else:
                    status = "FAILED"
                print ('Device:{} name:{} workflow:{} Status:{}'.format(device_row['serial'],
                                                                    device_row['name'],
                                                                    device_row['workflow'],
                                                                    status))
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
    create_and_upload(dnac, devices=args.devices)
