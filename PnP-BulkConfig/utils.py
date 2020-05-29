import requests
import json
from dnac_config import DNAC, DNAC_PORT, DNAC_USER, DNAC_PASSWORD
from requests.auth import HTTPBasicAuth
requests.packages.urllib3.disable_warnings()

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

    return "https://%s:%s/api/v1/%s" % (controller_ip, DNAC_PORT, path)


def get_auth_token(controller_ip=DNAC, username=DNAC_USER, password=DNAC_PASSWORD):
    """ Authenticates with controller and returns a token to be used in subsequent API invocations.
    v 1.3.3.x /dna/system/api/v1/auth/token
    v 1.2.x.x /api/system/v1/auth/token
    """

    login_url = "https://{0}:{1}/dna/system/api/v1/auth/token".format(controller_ip, DNAC_PORT)
    print("You're logging into: ", login_url)
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
    response.raise_for_status()
    return response

def login():
    return get_auth_token()
