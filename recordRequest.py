import json
import copy

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

    head = copy.deepcopy(member)
    head['isMoving'] = True

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
            'entireHouseholdMoving': True, #TODO compare head and individual MRNs to see if the entire household moves or not
            'formattedMrnsToMove': [decoded['results'][0]['formattedMrn']],
            'head': head,
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
            'members': [],
            }
            
    return body
