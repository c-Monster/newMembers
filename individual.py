#!/usr/bin/env python

import copy 
import json
import requests
import tools
import data
from termcolor import colored, cprint

class Birthday:

    def __init__(self, day, month, year):
        #convert month from string to int
        self.month = {
                'January': '01',
                'February': '02',
                'March': '03',
                'April': '04',
                'May': '05',
                'June': '06',
                'July': '07',
                'August': '08',
                'September': '09',
                'October': '10',
                'November': '11',
                'December': '12'
                }[month]
        self.day = day
        self.year = year

    #returns string in format YYYYMMDD
    def toString(self):
        return ''.join([self.year, self.month, self.day])

class Name:

    def __init__(self, firstName, lastName):
        self.firstName = firstName
        self.lastName = lastName

    def toString(self):
        return ' '.join([self.firstName, self.lastName])

class Bishop:

    def __init__(self, name, email):
        self.Name = Name('', name);
        self.email = email


class Individual:
    #same records and pull addresses for all members
    RECORDS_ADDRESS = 'https://www.lds.org/mls/mbr/services/records/request/find-member?lang=eng'
    PULL_ADDRESS = 'https://www.lds.org/mls/mbr/services/records/request/move-household?lang=eng'
    
    MRN_ADDRESS = 'https://www.lds.org/mls/mbr/services/records/request/find-member?lang=eng'
    UNIT_ADDRESS = 'https://www.lds.org/mls/mbr/services/cdol/details/unit/%(unit)s?lang=eng'
    PROFILE_ADDRESS = 'https://www.lds.org/mls/mbr/records/member-profile/service/M00%(mrn)s?lang=eng'
    HEADERS = {
            'accept':'application/json, text/plain, */*',
            }
    MAX_MRN = 11

    #object is initialized with basic attributes
    def __init__(self, ID, firstName, lastName, birthMonth, birthDay, birthYear, phone, email, apartment, gender):
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
        member['phone'] = self.phone
        member['email'] = self.email

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
            'mrnOrName': self.Name.toString(),
            'name': self.Name.toString(),
            'birthDate': self.Birthday.toString()
            }

        headers = {
            'accept':'application/json, text/plain, */*',
            'content-type':'application/json;charset=UTF-8',
            }
            
        #search for potential record
        print '\tsearching for record...'
        response = session.post(url = self.RECORDS_ADDRESS, data = json.dumps(payload), cookies = credentials, headers = headers)
    
        print '\tresponse code: ', colored(response.status_code, 'yellow')
        assert (response.status_code == 200)

        decoded = json.loads(response.text)
        self.mrn = decoded['singleResultMoveHousehold']['individual']['mrn']
        self.Name = decoded['singleResultMoveHousehold']['individual']['name']

        print '\tMRN: ', colored(self.mrn, 'yellow')
        print '\tmaking request...'
        request = self.buildRecordRequestBody(response.text)#build JSON body for final pull request
        response = session.put(url = self.PULL_ADDRESS, data = json.dumps(request), cookies = credentials, headers = headers)
        print '\tresponse code: ', colored(response.status_code, 'yellow')
        assert (response.status_code == 200)
        self.pulled = 'done'
        
        cprint('\tsucess!', 'green')

    def fetch_former_bishop(self, credentials, session):

        try:
            if len(self.mrn) > self.MAX_MRN: #groom mrn
               self.mrn = self.mrn[len(self.mrn)-MAX_MRN:]
    
        except AttributeError:
            cprint('\tmissing MRN', 'red')
            return

        print "\tfinding former bishop of %s...", colored(self.name, 'yellow')
        address = PROFILE_ADDRESS % {'mrn': self.mrn}
        response = session.get(url = address, cookies = credentials, headers = HEADERS)
        print '\tresponse code: ', response.status_code
        assert response.status_code == 200

        decoded = json.loads(response.text)
        print '\tformer bishop: ', colored(decoded['leaderName'], 'yellow')
        print '\tformer bishop email: ', colored(decoded['leaderEmail'], 'yellow')

        leader = decoded['leaderName'].split(' ')
        print '\tmost recent unit: ', colored(decoded['individual']['priorUnits'][0]['unitName'], 'yellow')
                
        address = UNIT_ADDRESS % {'unit': decoded['individual']['priorUnits'][0]['unitNumber']}
        response = session.get(url = address, cookies = credentials, headers = HEADERS)
        assert response.status_code == 200
                
        decoded = json.loads(response.text)
        self.bishop = Bishop(leader[len(leader)-1], decoded['leaderEmail'])
         
    def update_sheet(self, service):

        service = data.build_service()
        index = self.id + 1
        range_name = 'New Members 2017!%d%d' % (index, index)

        row = []
        for i in range(LENGTH):
            row.append(None)

        for n, i in enumerate(row):
            if n == MRN:
                row[n] = self.mrn
            elif n == PULLED:
                row[n] = self.pulled
            elif n == BISHOP:
                row[n] = self.Bishop.Name.toString()
            elif n == EMAIL:
                row[n] = self.Bishop.email




