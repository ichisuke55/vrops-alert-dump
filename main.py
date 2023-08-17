import os
import json
import csv
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning


def session_request(session, headers, path):
    response = session.get(
            f"https://{os.environ['VROPS_FQDN']}{path}", timeout=10, headers=headers, verify=False)
    return response.json()
    

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
session = requests.Session()

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json' # if default */* set, return xml
}

# get token
auth_data = {
        "username": f"{os.environ['VROPS_USERNAME']}",
        "password": f"{os.environ['VROPS_PASSWORD']}"
        }
auth_response = session.post(
        f"https://{os.environ['VROPS_FQDN']}/suite-api/api/auth/token/acquire", timeout=5, headers=headers, verify=False, data = json.dumps(auth_data))

headers.update({"Authorization": f"vRealizeOpsToken {auth_response.json()['token']}"})

origin_data = session_request(session, headers, '/suite-api/api/alertdefinitions')

headers.update({'Accept-Language': 'ja'})
jp_data = session_request(session, headers, '/suite-api/api/alertdefinitions')

with open('./dump.csv', 'w') as f:
    writer = csv.writer(f, delimiter='\t')
    header = ['ID', 'NAME(EN)', 'NAME(JP)', 'DESCRIPTION(EN)', 'DESCRIPTION(JP)', 'ADAPTER_KIND', 'RESOURCE_KIND']
    writer.writerow(header)
    for _, o in enumerate(origin_data['alertDefinitions']):
        for _, j in enumerate(jp_data['alertDefinitions']):
            if o['id'] == j['id']:
                # some object's `description` key is not defined, so use x.get('key')
                writer.writerow([o['id'], o['name'], j['name'],
                    o.get('description'), j.get('description'), o['adapterKindKey'], o['resourceKindKey']])
