#!/usr/bin/env python
from utils import login, get, post
import logging
import sys
import json
import time
logging.captureWarnings(True)
#logging.basicConfig(level=logging.DEBUG)

def get_status(dnac, serial):
    url = "onboarding/pnp-device?serialNumber={}".format(serial)
    response = get(dnac,url)
    try:
        return response.json()[0]['deviceInfo']['onbState']
    except IndexError:
        return None
'''
{
    "lastStateTransitionTime": "2015-09-21 10:31:58.000418",
    "platformId": "ISR4451-X/K9",
    "hostName": "Router",
    "id": "e2d3ff68-87d7-412d-a2c7-1e30e726d5c1",
    "pnpProfileAutoCreated": false,
    "authType": "Unsupported",
    "pnpProfileUsedAddr": "10.10.10.140",
    "configReg": "0x2102",
    "fileDestination": "bootflash",
    "state": "LOCATION_TAG_FILLED",
    "deviceDetailsLastUpdate": "2015-09-21 10:31:58.384",
    "slotNumber": "1",
    "firstContact": "2015-09-21 10:31:54.000815",
    "attributeInfo": {},
    "imageFile": "bootflash:/isr4400-universalk9.03.16.00c.S.155-3.S0c-ext.SPA.bi",
    "versionString": "15.5(3)S0c",
    "apCount": "0",
    "pkiEnabled": true,
    "stateDisplay": "Getting Device Info",
    "returnToRomReason": "reload",
    "serialNumber": "FTX1743ANS9",
    "sudiRequired": false,
    "filesystemInfo": "fileSystem: name=bootflash type=disk size=7451738112 freespace=5350199296;\nfileSystem: name=nvram type=nvram size=33554432 freespace=33348556;\n",
    "mainMemSize": "6295128",
    "authStatus": "None",
    "lastContact": "2015-09-21 10:31:58.000418",
    "isMobilityController": "false"
}
'''
def watch_status(dnac, serial, last_status):
    onbstate = get_status(dnac, serial)
    #print json.dumps(status, indent=2)

    if onbstate is None:
        print("No site status for device")
        sys.exit(1)

    this_status = onbstate

    return this_status

def main(argv):


    if len(argv) != 1:
        print("Error: Usage %s serial" % sys.argv[0])
        sys.exit(1)
    else:
        serial = argv[0]
    dnac = login()

    FINAL_STATUS="Provisioned"
    print("Watching unclaimed for serial:%s" % serial)
    starttime = time.time()
    status_detail = "EMPTY"
    last_status = "first"
    last_time = starttime
    while status_detail != FINAL_STATUS:
        status_detail = watch_status(dnac, serial, last_status)
        if status_detail != last_status:
            now = time.time()
            print("%s: Duration (%d) %s" % (time.strftime("%H:%M:%S"), now - starttime, status_detail))
            last_status = status_detail
            last_time = now
        elif now - last_time > 300:
            print("waiting 5 mins")
            last_time = now
        time.sleep(2)


    print("%s: Completed (%d): %s" % (time.strftime("%H:%M:%S"), now - starttime, status_detail))

    if status_detail == FINAL_STATUS:
        sys.exit(0)
    else:
        sys.exit(3)


if __name__ == "__main__":
    main(sys.argv[1:])
