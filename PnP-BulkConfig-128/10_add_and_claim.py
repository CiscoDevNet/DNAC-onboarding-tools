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

logger = logging.getLogger()

class SiteCache:
    def __init__(self, dnac):
        self._cache = {}
        response = get(dnac, "group?groupType=SITE")
        sites = response.json()['response']
        for s in sites:
            self._cache[s['groupNameHierarchy']] =  s['id']
    def lookup(self, fqSiteName):
        if fqSiteName in self._cache:
            return self._cache[fqSiteName]
        else:
            raise ValueError("Cannot find site:{}".format(fqSiteName))

class ImageCache:
    def __init__(self, dnac):
        self._cache = {}
        response = get(dnac, "image/importation")
        sites = response.json()['response']
        for s in sites:
            self._cache[s['name']] =  s['imageUuid']
    def lookup(self, imagename):
        if imagename in self._cache:
            return self._cache[imagename]
        else:
            raise ValueError("Cannot find image:{}".format(imagename))

def add_device(dnac, name, serial, pid, top_of_stack):
    if top_of_stack is None:
        stack = False
    else:
        stack = True
    payload = [{
	"deviceInfo": {
		"hostname": name,
		"serialNumber": serial,
		"pid": pid,
		"sudiRequired": False,
		"userSudiSerialNos": [],
		"stack": stack,
		"aaaCredentials": {
			"username": "",
			"password": ""
		}
	}
}]
    logger.debug(json.dumps(payload))
    device = post(dnac, "onboarding/pnp-device/import", payload)
    try:
        deviceId = device.json()['successList'][0]['id']
    except IndexError as e:
        print ('##SKIPPING device:{},{}:{}'.format(name, serial, device.json()['failureList'][0]['msg']))
        deviceId = None

    return deviceId

# other options.
# type="stackSwitch"
# "licenseLevel":"",
# "topOfStackSerialNumber":"",
def claim_device(dnac,deviceId, configId, siteId, top_of_stack, imageId, params):
    # if image is not None and image is not "":
    #     logging.debug("looking for imageid for {}".format(image))
    #     response = get(dnac, 'image/importation?name={0}'.format(image))
    #     try:
    #         imageid = response.json()['response'][0]['imageUuid']
    #     except IndexError:
    #         print("Image:{} not found".format(image))
    #         return {"Error" : "Imnage:{} nmot found".format(image)}
    # else:
    #     imageid =''

    payload = {
        "siteId": siteId,
         "deviceId": deviceId,
         "type": "Default",
         "imageInfo": {"imageId": imageId, "skip": False},
         "configInfo": {"configId": configId, "configParameters": params}
}
    if top_of_stack is not None:
        payload['type'] = "StackSwitch"
        payload['topOfStackSerialNumber'] = top_of_stack
    logger.debug(json.dumps(payload, indent=2))

    claim = post(dnac,"onboarding/pnp-device/site-claim", payload)

    return claim.json()['response']

def find_template_name(data, templateName):
    # the order of attributes is random.  need to search the children.
    for attr in data:
        logger.debug("ATTR:" +json.dumps(attr, indent=2) )
        if 'key' in attr:
            if attr['key'] == 'day0.templates':
                for dev in attr['attribs']:
                    # DeviceFamily/DeviceSeries/DeviceType
                    #template = dev['attribs'][0]['attribs'][0]['attribs'][0]
                    for template in dev['attribs'][0]['attribs'][0]['attribs']:
                        logger.debug(json.dumps(template, indent=2))
                        if template['key'] == 'template.id':
                            for templ_attrs in template['attribs']:
                                if templ_attrs['key'] == 'template.name' and templ_attrs['value'] == templateName:
                                    return template['value']

                    #if template['attribs'][1]['value'] == templateName:
                       #return template['value']
    raise ValueError("Cannot find template named:{}".format(templateName))

def find_site_template(dnac, siteId, templateName):

    response = get(dnac,"siteprofile/site/{}".format(siteId))

    logger.debug("siteprofile {} returned:".format(siteId))
    logger.debug(json.dumps(response.json(), indent=2))

    if response.json()['response'] == []:
        raise ValueError("Cannot find Network profile for siteId:{}".format(siteId))

    # need to be careful here.  WLAN profiles also apply to a site.  need to filter them
    wired_site_profile = [ site for site in response.json()['response'] if site['namespace'] != "wlan" and site['namespace'] != "routing"]

    # now need to find the template
    data = wired_site_profile[0]['profileAttributes']
    return find_template_name(data, templateName)


def get_template(dnac, configId, supplied_params):
    params=[]
    response = get(dnac, "template-programmer/template/{}".format(configId))
    logger.debug("template {} returned:".format(configId))
    logger.debug(json.dumps(response.json(),indent=2))
    for vars in response.json()['templateParams']:
        name = vars['parameterName']
        params.append({"key": name, "value": supplied_params[name]})
    #print params
    return params

def create_and_upload(dnac, site_cache, image_cache, devices):

    f = open(devices, 'rt')
    try:
        reader = csv.DictReader(f)
        for device_row in reader:
            #print ("Variables:",device_row)

            try:
                siteId = site_cache.lookup(device_row['siteName'])
                #image is optional
                if 'image' in device_row and device_row['image'] != '':
                    imageId = image_cache.lookup(device_row['image'])
                else:
                    imageId = ''

            except ValueError as e:
                print("##ERROR {},{}: {}".format(device_row['name'],device_row['serial'], e))
                continue
            # need to get templateId from Site..
            configId = find_site_template(dnac, siteId, device_row['templateName'])
            params = get_template(dnac, configId, device_row)

            if 'topOfStack' in device_row:
                top_of_stack = device_row['topOfStack']
            else:
                top_of_stack = None

            # add device to PnP
            deviceId = add_device(dnac, device_row['name'], device_row['serial'], device_row['pid'], top_of_stack)
            if deviceId is not None:
                #claim the device if sucessfully added
                claim_status = claim_device(dnac, deviceId, configId, siteId, top_of_stack, imageId, params)
                if "Claimed" in claim_status:
                    status = "PLANNED"
                else:
                    status = "FAILED"
                print ('Device:{} name:{} siteName:{} Status:{}'.format(device_row['serial'],
                                                                    device_row['name'],
                                                                    device_row['siteName'],
                                                                    status))
    finally:
        f.close()

if __name__ == "__main__":
    parser = ArgumentParser(description='Select options.')
    parser.add_argument( 'devices', type=str,
            help='device inventory csv file')
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
    site_cache = SiteCache(dnac)
    image_cache = ImageCache(dnac)


    print ("Using device file:", args.devices)

    print ("##########################")
    create_and_upload(dnac, site_cache, image_cache, devices=args.devices)
