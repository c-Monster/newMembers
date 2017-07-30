#!/usr/bin/env python

import tools
import requests
import sys
import json

#TODO figure out the correct number of digits in MRN
MRN_ADDRESS = 'https://www.lds.org/mls/mbr/services/records/request/find-member?lang=eng'
UNIT_ADDRESS = 'https://www.lds.org/mls/mbr/services/cdol/details/unit/%(unit)s?lang=eng'
PROFILE_ADDRESS = 'https://www.lds.org/mls/mbr/records/member-profile/service/M00%(mrn)s?lang=eng'
HEADERS = {
        'accept':'application/json, text/plain, */*',
        'accept-encoding':'gzip, dseflate, br',   
        'accept-language':'en-US,en;q=0.8',
        'content-type':'application/json;charset=UTF-8',
        'origin':'https://www.lds.org',                                                                                   
        'referer':'https://www.lds.org/mls/mbr/records/request/find-member',
        }

username = sys.argv[1]
password = sys.argv[2]

mrn = raw_input("MRN: ")

session = requests.session()
credentials = tools.login(session, username, password)

address = PROFILE_ADDRESS % {'mrn': mrn}
print address
response = session.get(url = address, cookies = credentials, headers = HEADERS)
print response.status_code
assert response.status_code == 200

try:
    decoded = json.loads(response.text)

except(ValueError, KeyError, TypeError):
    print "Error parsing json reponse to profile request"

print decoded['individual']['priorUnits'][0]['unitName']
print decoded['individual']['priorUnits'][0]['unitNumber']

address = UNIT_ADDRESS % {'unit': decoded['individual']['priorUnits'][0]['unitNumber']}
response = session.get(url = address, cookies = credentials, headers = HEADERS)
assert response.status_code == 200

try:
    decoded = json.loads(response.text)
    
except(ValueError, KeyError, TypeError):
    print "Error parsing json response to unit request"

print decoded['leaderName']
print decoded['leaderEmail']


