#!/usr/bin/env python
from __future__ import print_function
import json
from utils import login, get, create_url

import time

def msec_to_time(msec):
    epoc = msec /1000
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoc))


def process(workflows):
    for workflow in workflows:
        print("Name:{}, Type:{}, InUse:{} updated {} id:{}".format(workflow['name'],
                                                           workflow['type'],
                                                        workflow['useState'],
                                                           msec_to_time(workflow['lastupdateOn']),
                                                           workflow['id']))
        print (json.dumps(workflow['tasks']))
        print()

if __name__ == "__main__":
    dnac = login()

    data = get(dnac, 'dna/intent/api/v1/onboarding/pnp-workflow')
    process(data.json())