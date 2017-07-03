import json

def buildRequestBody(text, apt):

    try:
        decoded = json.loads(text)

    except (ValueError, KeyError, TypeError):
        print "Could not parse JSON response"

    member = { #same as individual in this case
            'age': decoded['singleResultMoveHousehold']['individual']['age'],
            'birthDate': decoded['singleResultMoveHousehold']['individual']['birthDate'],
            'gender': decoded['singleResultMoveHousehold']['individual']['gender'],
            'hqMoveRestricted': decoded['singleResultMoveHousehold']['individual']['hqMoveRestricted'],
            'id': decoded['singleResultMoveHousehold']['individual']['id'],
            'moveRestricted':decoded['singleResultMoveHousehold']['individual']['moveRestricted'],
            'mrn': decoded['results'][0]['mrn'],
            'name': decoded['singleResultMoveHousehold']['individual']['name'],
            'oouMember': decoded['singleResultMoveHousehold']['individual']['oouMember'],
            'secured': decoded['singleResultMoveHousehold']['individual']['secured'],
            'ysa': True,
            }

#TODO be neater about literals
    address = {
            'city': 'Provo',
            'country': 251,
            'formattedLines': json.dumps(["1565 N University Ave", "Apt 188", "Provo, Utah 84604-2631"]),
            'geocodeToUnits': False,
            'postalCode': '84604-2631',
            'state': 44,
            'street1': '1565 N University Ave',
            'street2': 'Apt ' + apt,
            }

    address['standardized'] = json.dumps(address)


    residential = {
            'address': json.dumps(address),
            'selection': 'suggested',
            }
    
    unitAddressConfig = {
            'addressFields': json.dumps(['country', 'street1', 'street2', 'city', 'state', 'postalCode']),
            'countries': json.dumps({
                'United States': 251
                }),
            'defaultCountry': 251,
            'defaultState': 44,
            'geoCodeEnabled': True,
            'states': json.dumps({ 
                251: json.dumps({
                    'Utah': 44
                    })
                })
            }



    body = {
            'bypassStandardized': True,
            'confirmStandardized': json.dumps(residential),
            'contactPriorLeader': False,
            'defaultNewHoh': json.dumps(member),
            'email': decoded['singleResultMoveHousehold']['email'],
            'entireHouseholdMoving': True, #TODO compare head and individual MRNs to see if the entire household moves or not
            'formattedMrnsToMove': [decoded['results'][0]['formattedMrn']], #TODO figure out how to initialize a list here 
            'head': json.dumps(member),
            'individual': json.dumps(member),
            'joiningExistingHousehold': False,
  #          'mailingAddress': #TODO can I just leave this blank?
            'mailingIsDifferent': False,
            'mrnsToMove': [decoded['results'][0]['mrn']],
            'newHohMrn': decoded['results'][0]['mrn'],
            'phone':decoded['singleResultMoveHousehold']['phone'],
            'promptStandardized': True,
            'residentialAddress': json.dumps(residential),#TODO see if we can null 'standardized'
            'unitAddressConfig': json.dumps(unitAddressConfig),
            'errors': {},
            'members': [],
            }
            
    return body
