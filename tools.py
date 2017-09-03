#!/usr/bin/env python

import requests
import json
import copy


#logs returns LDS Tools credentials
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


#builds POST body used to move records
def build_request_body(text, apt, phone):

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
            'formattedLines': ["1565 N University Ave", apt, "Provo, Utah 84604-2631"],
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
            'phone': phone,
            'promptStandardized': True,
            'residentialAddress': address,
            'unitAddressConfig': unitAddressConfig,
            'errors': {},
            }
            
    return body
