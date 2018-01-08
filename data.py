#!/usr/bin/env python

import individual

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
def get_data(service):

    result = service.spreadsheets().values().get(spreadsheetId = SHEET_ID, range = RANGE).execute()

    values = result.get('values', []) #what in the world does this do??

    if not values: 
        raise ValueError('no data found')
    else:
        return values

#values is a list of lists
#returns a map of column names to row indices
def set_columns(values):
    output = {}

    for i, cell in enumerate(values[0]):
        if cell == 'First Name':
            output[cell] = i
        elif cell == 'Last Name':
            output[cell] = i
        elif cell == 'Birth Month':
            output[cell] = i
        elif cell == 'Birth Day':
            output[cell] = i
        elif cell == 'Birth Year':
            output[cell] = i
        elif cell == 'Apartment':
            output[cell] = i
        elif cell == 'Phone Number':
            output[cell] = i
        elif cell == 'Email Address':
            output[cell] = i
        elif cell == 'Records Pulled':
            output[cell] = i
        elif cell == 'MRN':
            output[cell] = i
        elif cell == 'Former Bishop':
            output[cell] = i
        elif cell == 'Former Bishop Email':
            output[cell] = i
        elif cell == 'Gender':
            output[cell] = i
        else:
            continue

    return output

def parse_birthday(birthday):

    fields = birthday.split('/')
    output = fields[2]#year
   
    if len(fields[0]) == 1: 
        output += '0'

    output += fields[0]

    if len(fields[1]) == 1:
        output += '0'

    output += fields[1]

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

