#!/usr/bin/env python

import httplib2
import os
import json

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from termcolor import cprint

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
SECRET = 'records_auth.json'
APP_NAME = 'ward_members_auth'
SHEET_ID = '13zdxFnJLJ_7IfWQxOBm0sZPkIL5bHZ0RE29o_T27Hd0'
RANGE='New Members 2017'

FIRST = -1
LAST = -1
DOB  = -1 
APT = -1
PHONE = -1
PULLED = -1
MRN = -1
BISHOP = -1
EMAIL = -1
CONTACTED = -1
BIRTH_DAY = -1
BIRTH_MONTH = -1
BIRTH_YEAR = -1

LENGTH = -1

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()

except ImportError:
    flags = None

def get_credentials():

    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')

    if not os.path.exists(credential_dir):
        os.mkdirs(credential_dir)

    credential_path = os.path.join(credential_dir, 'sheets.googleapis.com-new-members.json')

    store = Storage(credential_path)
    credentials = store.get()

    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(SECRET, SCOPES)
        flow.user_agent = APP_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        print 'storing credentials to', credential_path

    return credentials

def build_service():

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())

    discovery_url = ('https://sheets.googleapis.com/$discovery/rest?' 'version=v4')

    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discovery_url)

    return service

#gets a dump of what's in Google Sheets
def get_data():

    service = build_service()

    result = service.spreadsheets().values().get(spreadsheetId = SHEET_ID, range = RANGE).execute()

    values = result.get('values', []) #what in the world does this do??

    if not values: 
        raise ValueError('no data found')
    else:
        return values

#values is a list of lists
def set_columns(values):

    global LENGTH
    LENGTH = len(values[0])

    for i, cell in enumerate(values[0]):
        if cell == 'First Name':
            global FIRST
            FIRST = i
        elif cell == 'Last Name':
            global LAST
            LAST = i
        elif cell == 'Birth Month':
            global BIRTH_MONTH
            BIRTH_MONTH = i
        elif cell == 'Birth Day':
            global BIRTH_DAY
            BIRTH_DAY = i
        elif cell == 'Birth Year':
            global BIRTH_YEAR
            BIRTH_YEAR = i
        elif cell == 'Apartment':
            global APT
            APT = i
        elif cell == 'Phone Number':
            global PHONE
            PHONE = i
        elif cell == 'Email Address':
            global PERSONAL_EMAIL
            PERSONAL_EMAIL = i
        elif cell == 'Records Pulled':
            global PULLED
            PULLED = i
        elif cell == 'MRN':
            global MRN
            MRN = i
        elif cell == 'Former Bishop':
            global BISHOP
            BISHOP = i
        elif cell == 'Former Bishop Email':
            global EMAIL
            EMAIL = i
        else:
            continue

    
#returns a JSON object full of records to be pulled
#assumes values is a list of lists
def parse_data(values):

    set_columns(values) 
    
    output = []
    for i, row in enumerate(values):

        if i == 0 or len(row) == 0:
            continue
        
        try: 
            if row[PULLED] == 'done':
                continue
        except IndexError:#row[PULLED] comes back as null
            print '\t\t[identified record to pull]'

        try:
            name = "%s %s" % (row[FIRST], row[LAST])
            member = {
                'name': name,
                'birthday': parse_birthday(row[BIRTH_DAY], row[BIRTH_MONTH], row[BIRTH_YEAR]),
                'apartment': row[APT],
                'phone': row[PHONE],
                'email': row[PERSONAL_EMAIL],
                'id': i
                    }

            output.append(member)

        except IndexError:
            msg = '\tError building member object: index out of range in row %d' % i

            cprint(msg, 'red', attrs = ['bold'])
            member = {
                    'error': msg,
                    'id': i
                    }
            #TODO make an error appear in the sheet

    return json.dumps(output)



def parse_birthday(day, month, year):

    output = year
   
    if month == 'January':
        output += '01'
    elif month == 'February':
        output += '02'
    elif month == 'March':
        output += '03'
    elif month == 'April':
        output += '04'
    elif month == 'May':
        output += '05'
    elif month == 'June':
        output += '06'
    elif month == 'July':
        output += '07'
    elif month == 'August':
        output += '08'
    elif month == 'September':
        output += '09'
    elif month == 'October':
        output += '10'
    elif month == 'November':
        output += '11'
    elif month == 'December':
        output += '12'


    if len(day) == 1:
        output += '0'

    output += day

    return output

def build_pulled_row(member):

    row = []

    for i in range(LENGTH):
        row.append(None)

    try:
        mrn = member['mrn']

        for n, i in enumerate(row):
            if n == MRN:
                row[n] = mrn
            elif n == PULLED:
                row[n] = 'done'

    except KeyError: #we now know it's reporting an error

        try:
            index = member['row']

            for n, i in enumerate(row):
                if n == PULLED:
                    row[n] = member['error']

        except KeyError:
            cprint('\t\tcould not find row nor mrn when building pulled row', 'red', attrs=['bold'])
    
    return row

def build_bishop_row(member):

    row = []

    for i in range(LENGTH):
        row.append(None)

    try:
        bishop = member['bishop']

        for n, i in enumerate(row):
            if n == BISHOP:
                row[n] = bishop

        email = member['email']

        for n, i in enumerate(row):
            if n == EMAIL:
                row[n] = email

    except KeyError: #we now know it's reporting an error
        try:
            index = member['row']

            for n, i in enumerate(row):
                if n == BISHOP:
                    row[n] = member['error']

        except KeyError:
            cprint('\t\tcould not find row nor bishop info when building pulled row', 'red', attrs=['bold'])
    
    return row


#@param row - list of values that goes in the row
#@param index - int representing the row
def update_row(row, index):

    index += 1

    #Can we build the service more than one time?
    service = build_service()

    range_name = 'New Members 2017!%d:%d' % (index, index)
    values = [row]
    body = {
            'values': values
            }
    service.spreadsheets().values().update(spreadsheetId = SHEET_ID, range = range_name, body = body, valueInputOption = 'RAW').execute() 



#this is an example
def ex():

    service = build_service()

    range_name = 'New Members 2017!B2:C4'

    result = service.spreadsheets().values().get(spreadsheetId=SHEET_ID, range = range_name).execute()

    values = result.get('values', [])

    if not values:
        print 'no data found'
    else:
        print range_name
        for row in values:
            print row[0], row[1]

    values = [
            ['c', 'Monster'],
            ['e', 'Monster']
            ]

    body = {
            'majorDimension': 'ROWS',
            'values': values
            }

    result = service.spreadsheets().values().update(spreadsheetId=SHEET_ID, range = range_name, valueInputOption='RAW', body=body).execute()


    

