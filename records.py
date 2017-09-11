#!/usr/bin/env python

import requests
import json
import tools

from termcolor import colored, cprint

RECORDS_ADDRESS = 'https://www.lds.org/mls/mbr/services/records/request/find-member?lang=eng'
PULL_ADDRESS = 'https://www.lds.org/mls/mbr/services/records/request/move-household?lang=eng'

def pull(member, credentials, session):

    print "\tpulling records of %s..." % colored(member['name'], 'yellow')

    payload = {
            'mrnOrName': member['name'],
            'name': member['name'],
            'birthDate': member['birthday']
            }
    

    headers = {
            'accept':'application/json, text/plain, */*',
            'content-type':'application/json;charset=UTF-8',
            }

    print '\tsearching for record...'
    response = session.post(url = RECORDS_ADDRESS, data = json.dumps(payload), cookies = credentials, headers = headers)

    print '\tresponse code: ', colored(response.status_code, 'yellow')
    assert (response.status_code == 200)

    decoded = json.loads(response.text)
    mrn = decoded['singleResultMoveHousehold']['individual']['mrn']
    name = decoded['singleResultMoveHousehold']['individual']['name']

    print '\tMRN: ', colored(mrn, 'yellow')

    request = tools.build_request_body(response.text, member['apartment'], member['phone'])

    print '\tmaking request...'
    response = session.put(url = PULL_ADDRESS, data = json.dumps(request), cookies = credentials, headers = headers)
    print '\ttresponse code: ', colored(response.status_code, 'yellow')
    assert (response.status_code == 200)

    output = {
            "name": name,
            "mrn": mrn,
            "row": member['id']
            }

    return output

            
    
