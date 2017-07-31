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
        }

#data will be a string of MRNs delineated by whitespace
def getFormerBishopInfo(data, session, credentials)
    
    output
    mrnList = data.split(" ")

    for mrn in mrnList:

        session = requests.session()
        credentials = tools.login(session, username, password)
        
        address = PROFILE_ADDRESS % {'mrn': mrn}
        response = session.get(url = address, cookies = credentials, headers = HEADERS)
        assert response.status_code == 200
        
        try:
            decoded = json.loads(response.text)
        
        except(ValueError, KeyError, TypeError):
            print "Error parsing json reponse to profile request"
        
        print decoded['individual']['priorUnits'][0]['unitName']
        
        address = UNIT_ADDRESS % {'unit': decoded['individual']['priorUnits'][0]['unitNumber']}
        response = session.get(url = address, cookies = credentials, headers = HEADERS)
        assert response.status_code == 200
        
        try:
            decoded = json.loads(response.text)
            
        except(ValueError, KeyError, TypeError):
            print "Error parsing json response to unit request"
        
        print decoded['leaderName']
        print decoded['leaderEmail']

        output.join(decoded['leaderName'])
        output.join(',')
        output.join(decoded['leaderEmail'])
        output.join('\n')

    return output

        

username = sys.argv[1]
password = sys.argv[2]
data = sys.stdin.read()

session = requests.session()
credentials = tools.login(session, username, password)

output = getFormerBishopInfo(data, session, credentials)
print output
