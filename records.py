#!/usr/bin/env python

import requests
import json
import copy

def login(session, username, password):

    meta = session.get('https://ident.lds.org/sso/UI/Login?service=credentials')
    tokens = meta.cookies
    
    payload = {
              'IDToken1':username,
              'IDToken2':password,
              'IDButton':'Log In',
              'goto':'',
              'gotoOnFail':'',
              'SunQueryParamsString':'c2VydmljZT1jcmVkZW50aWFscw==',
              'encoded':'false',
              'gx_charset':'UTF-8'
              }
    
    response = session.post(
            'https://ident.lds.org/sso/UI/Login?service=credentials', 
            data = payload, 
            allow_redirects = False,
            cookies = tokens
            )

    assert response.status_code == 302
    assert 'lds-id' in response.cookies
    return response.cookies

def buildRequestBody(text, apt):

    try:
        decoded = json.loads(text)

    except (ValueError, KeyError, TypeError):
        print "Could not parse JSON response"


    member = decoded['singleResultMoveHousehold']['individual']
    member['ysa'] = True

    #figure out if member is head of household or not
    if decoded['results'][0]['hohMrn'] == decoded['results'][0]['mrn']:
        #not head of household
        head = decoded['singleResultMoveHousehold']['head']
        spouse = decoded['singleResultMoveHousehold']['spouse']
        entireHouseholdMoving = False
    else:
        #head of household
        head = copy.deepcopy(member)
        head['isMoving'] = True
        entireHouseholdMoving = True
        spouse = None

    address = {
            'city': "Provo",
            'country': 251,
            'formattedLines': ["1565 N University Ave", "Apt 188", "Provo, Utah 84604-2631"],
            'geocodeToUnits': False,
            'postalCode': '84604-2631',
            'state': 44,
            'street1': '1565 N University Ave',
            'street2': 'Apt ' + apt,
            }

    standardized = copy.deepcopy(address)
    standardized['standardized'] = address


    residential = {
            'address': standardized,
            'selection': "suggested"
            }
    
    unitAddressConfig = {
            'addressFields': ['country', 'street1', 'street2', 'city', 'state', 'postalCode'],
            'countries': {
                'United States': 251
                },
            'defaultCountry': 251,
            'defaultState': 44,
            'geocodeEnabled': True,
            'states': { 
                251: {
                    'Utah': 44
                    }
                }
            }


    emptyAddress = {
            'formattedLines': [],
            'geocodeToUnits': False,
            }

    body = {
            'bypassStandardized': True,
            'confirmStandardized': residential,
            'contactPriorLeader': False,
            'defaultNewHoh': member,
            'email': decoded['singleResultMoveHousehold']['email'],
            'entireHouseholdMoving': entireHouseholdMoving,
            'formattedMrnsToMove': [decoded['results'][0]['formattedMrn']],
            'head': head,
            'spouse': spouse,
            'members': [],
            'individual': member,
            'joiningExistingHousehold': False,
            'mailingAddress': emptyAddress, 
            'mailingIsDifferent': False,
            'mrnsToMove': [decoded['results'][0]['mrn']],
            'newHohMrn': decoded['results'][0]['mrn'],
            'phone':decoded['singleResultMoveHousehold']['phone'],
            'promptStandardized': True,
            'residentialAddress': address,
            'unitAddressConfig': unitAddressConfig,
            'errors': {},
            }
            
    return body

def pullRecords(name, row, birthday, apartment, credentials, debug):

    if debug == "true":
        debug == True
    else:
        debug == False
        
    if debug: print "Pulling records for %s" % name

    payload = {
            'mrnOrName':name,
            'name':name,
            'birthDate':birthday
            }
    
    RECORDS_ADDRESS = 'https://www.lds.org/mls/mbr/services/records/request/find-member?lang=eng'
    PULL_ADDRESS = 'https://www.lds.org/mls/mbr/services/records/request/move-household?lang=eng'

    headers = {
            'accept':'application/json, text/plain, */*',
            'content-type':'application/json;charset=UTF-8',
            }
    response = session.post(url = RECORDS_ADDRESS, data = json.dumps(payload), cookies = credentials, headers = headers)
    if debug: 
        print response.status_code

    assert (response.status_code == 200)

    decoded = json.loads(response.text)
    mrn = decoded['singleResultMoveHousehold']['individual']['mrn']
    name = decoded['singleResultMoveHousehold']['individual']['name']

    if debug: 
        print decoded['singleResultMoveHousehold']['individual']['mrn']
        print decoded['singleResultMoveHousehold']['individual']['name']

    request = buildRequestBody(response.text, apartment)
    response = session.put(url = PULL_ADDRESS, data = json.dumps(request), cookies = credentials, headers = headers)
    if debug: print response.status_code
    assert (response.status_code == 200)

    output = {
            "name": name,
            "mrn": mrn,
            "row": row
            }

def getRecords(task):

    data = json.loads(task)

    username = data['username']
    password = data['password']
    debug = data['debug']
    names = data['names']
    
    
    session = requests.session()
    credentials = login(session, username, password)
    
    output = []
    
    for line in names:
    
        individual = line.rstrip().split(', ')
        name = individual[0]
        birthday = individual[1]
        apartment = individual[2]
        row = individual[3]
    
        try:
            result = pull_records(name, row, birthday, apartment, credentials, debug)
    
        except(AssertionError, ValueError, KeyError, TypeError):
            result = {
                    "name": name,
                    "mrn": "error",
                    "row": row
                    }
            
        output.append(result)
    
    return json.dumps(output)
