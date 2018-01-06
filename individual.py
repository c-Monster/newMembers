#!/usr/bin/env python

import copy 
import json
import requests
import tools
from termcolor import colored, cprint

class Birthday:

    def _init_(self, day, month, year):
        #convert month from string to int
        self.month = {
                'January': 1,
                'February': 2,
                'March': 3,
                'April': 4,
                'May': 5,
                'June': 6,
                'July': 7,
                'August': 8,
                'September': 9,
                'October': 10,
                'November': 11,
                'December': 12
                }[month]
        self.day = day
        self.year = year

    def toString(self):

class Name:

    def _init_(self, firstName, lastName):
        self.firstName = firstName
        self.lastName = lastName

    def toString(self):
        return ' '.join([self.firstName, self.lastName])

class Individual:
    #same records and pull addresses for all members
    RECORDS_ADDRESS = 'https://www.lds.org/mls/mbr/services/records/request/find-member?lang=eng'
    PULL_ADDRESS = 'https://www.lds.org/mls/mbr/services/records/request/move-household?lang=eng'
    
    #object is initialized with basic attributes
    def _init_(self, ID, firstName, lastName, birthMonth, birthDay, birthYear, phone, email, apartment, gender):
        self.ID = ID
        self.Name = Name(firstName, lastName)
        self.Birthday = Birthday(birthDay, birthMonth, birthYear)
        self.phone = phone
        self.email = email
        self.apartment = apartment

    def buildRecordRequestBody(self, searchResult):

        try:
            decoded = json.loads(searchResult)

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
                'formattedLines': ["1565 N University Ave", self.apartment, "Provo, Utah 84604-2631"],
                'geocodeToUnits': False,
                'postalCode': '84604-2631',
                'state': 44,
                'street1': '1565 N University Ave',
                'street2': 'Apt ' + self.apartment,
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
                'email': self.email,
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
                'phone': self.phone,
                'promptStandardized': True,
                'residentialAddress': address,
                'unitAddressConfig': unitAddressConfig,
                'errors': {},
                }
                
        return body

    #pulls records
    def pullRecords(self, credentials, session):

        print "\tpulling records of %s..." % colored(self.Name.toString(), 'yellow')

        payload = {
            'mrnOrName': self.Name.toString()
            'name': self.Name.toString()
            'birthDate': self.Name.toString()
            }

        headers = {
            'accept':'application/json, text/plain, */*',
            'content-type':'application/json;charset=UTF-8',
            }
            
        #search for potential record
        print '\tsearching for record...'
        response = session.post(url = RECORDS_ADDRESS, data = json.dumps(payload), cookies = credentials, headers = headers)
    
        print '\tresponse code: ', colored(response.status_code, 'yellow')
        assert (response.status_code == 200)

        decoded = json.loads(response.text)
        self.mrn = decoded['singleResultMoveHousehold']['individual']['mrn']
        self.Name = decoded['singleResultMoveHousehold']['individual']['name']

        print '\tMRN: ', colored(self.mrn, 'yellow')
        print '\tmaking request...'
        request = self.buildRecordRequestBody(response.text)#build JSON body for final pull request
        response = session.put(url = PULL_ADDRESS, data = json.dumps(request), cookies = credentials, headers = headers)
        print '\tresponse code: ', colored(response.status_code, 'yellow')
        assert (response.status_code == 200)
    



