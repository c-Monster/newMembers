#!/usr/bin/env python

import requests
import sys
import json
import tools

from termcolor import colored, cprint

#TODO figure out the correct number of digits in MRN --> str.zfill() 
MRN_ADDRESS = 'https://www.lds.org/mls/mbr/services/records/request/find-member?lang=eng'
UNIT_ADDRESS = 'https://www.lds.org/mls/mbr/services/cdol/details/unit/%(unit)s?lang=eng'
PROFILE_ADDRESS = 'https://www.lds.org/mls/mbr/records/member-profile/service/M00%(mrn)s?lang=eng'
HEADERS = {
        'accept':'application/json, text/plain, */*',
        }

def fetch(member, credentials, session):
    
    name = member['name']
    mrn = member['mrn']
    
    print "\tfinding former bishop and email of %s..." % colored(name, 'yellow')
    
            
    address = PROFILE_ADDRESS % {'mrn': mrn}
    response = session.get(url = address, cookies = credentials, headers = HEADERS)
    print response.status_code
   
    assert response.status_code == 200
    decoded = json.loads(response.text)
            
    print '\tmost recent unit: ', colored(decoded['individual']['priorUnits'][0]['unitName'], 'yellow')
            
    address = UNIT_ADDRESS % {'unit': decoded['individual']['priorUnits'][0]['unitNumber']}
    response = session.get(url = address, cookies = credentials, headers = HEADERS)
    assert response.status_code == 200
            
    decoded = json.loads(response.text)
            
    print '\tformer bishop: ', colored(decoded['leaderName'], 'yellow')
    print '\tformer bishop email: ', colored(decoded['leaderEmail'], 'yellow')
            
    leader = decoded['leaderName'].split(' ')

    
    output = {
        'bishop': leader[len(leader)-1],
        'email': decoded['leaderEmail'],
        'row': member['row']
            }
        
    return output
    
        

