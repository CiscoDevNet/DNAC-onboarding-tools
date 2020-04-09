import requests
import json
import logging
from dnac_config import DNAC, DNAC_PORT, DNAC_USER, DNAC_PASSWORD
from requests.auth import HTTPBasicAuth
requests.packages.urllib3.disable_warnings()

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Custom exception definitions
# -------------------------------------------------------------------
class TaskTimeoutError(Exception):
    pass

class TaskError(Exception):
    pass

# API ENDPOINTS
ENDPOINT_TICKET = "ticket"
ENDPOINT_TASK_SUMMARY ="task/%s"
RETRY_INTERVAL=2

# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------
def create_url(path, controller_ip=DNAC):
    """ Helper function to create a DNAC API endpoint URL
    """

    if "dna/" in path:
        return "https://%s:%s/%s" % (controller_ip, DNAC_PORT, path)
    else:
        return "https://%s:%s/api/v1/%s" % (controller_ip, DNAC_PORT, path)


def get_auth_token(controller_ip=DNAC, username=DNAC_USER, password=DNAC_PASSWORD):
    """ Authenticates with controller and returns a token to be used in subsequent API invocations
    """

    #login_url = "https://{0}:{1}/api/system/v1/auth/token".format(controller_ip, DNAC_PORT)
    login_url = "https://{0}:{1}/dna/system/api/v1/auth/token".format(controller_ip, DNAC_PORT)
    result = requests.post(url=login_url, auth=HTTPBasicAuth(DNAC_USER, DNAC_PASSWORD), verify=False, timeout=20)
    result.raise_for_status()

    token = result.json()["Token"]
    return {
        "controller_ip": controller_ip,
        "token": token
    }

def get(dnac, url):
    geturl = create_url(url)
    headers = {'x-auth-token': dnac['token']}
    response = requests.get(geturl, headers=headers, verify=False)
    response.raise_for_status()
    return response

def post(dnac, url, payload):
    posturl = create_url(url)
    logger.debug(posturl)
    logger.debug(json.dumps(payload,indent=2))
    headers = {'x-auth-token': dnac['token'], "content-type" : "application/json"}
    response = requests.post(posturl, headers=headers, data=json.dumps(payload), verify=False)
    response.raise_for_status()
    return response

def put(dnac, url, payload):
    puturl = create_url(url)

    headers = {'x-auth-token': dnac['token'], "Content-Type" : "application/json"}
    response = requests.put(puturl, headers=headers, data=payload, verify=False)
    response.raise_for_status()
    return response

def delete(dnac, url):
    deleteurl = create_url(url)
    headers = {'x-auth-token': dnac['token']}
    response = requests.delete(deleteurl, headers=headers, verify=False)

    # response.text has the error message for deleting a device in onboarding that is in the inventory.
    if response.status_code == 400 and response.text:
        return response
    response.raise_for_status()

    return response

def login():
    return get_auth_token()
