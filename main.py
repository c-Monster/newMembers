#!/usr/bin/env python

import sys
import json
import requests

from termcolor import colored, cprint
import getpass

import data
import tools
import bishops
import records
import individual


def main():
    
    cprint('      __  ___              __           ', 'green')
    cprint(' ____/  |/  /__  ___  ___ / /____ ____', 'green')
    cprint('/ __/ /|_/ / _ \/ _ \(_-</ __/ -_) __/', 'green')
    cprint('\__/_/  /_/\___/_//_/___/\__/\__/_/   ', 'green')
                                      
    cprint('Starting LDS Tools Automator...', 'green', attrs=['bold'])

    cprint('\tFetching data from Google Sheets...', 'cyan')

    try: #prep the google sheets data
        service = data.build_service()
        values = data.get_data(service)
        data.set_columns(values) 

    except ValueError:
        cprint('unable to retrieve data', 'red', attrs = ['bold'])

    #build LDS sign-on
    username = raw_input(colored('\tLDS Username: ', 'yellow'))
    password = getpass.getpass(colored('\tLDS Password: ', 'yellow'))
    session = requests.session()
    credentials = tools.login(session, username, password)

    recordCount = 0
    bishopCount = 0
    
    for i, row in enumerate(values):

        if i == 0 or len(row) == 0:
            continue
        
        try:
            member = individual.Individual(i, row[data.FIRST], row[data.LAST],
                    row[data.BMONTH], row[data.BDAY], row[data.BYEAR], row[data.PHONE],
                    row[data.PERSONAL_EMAIL], row[data.APT], row[data.GENDER])

        except IndexError: # bad data
            msg = '\tError building object: invalid data in row %d' % i 
            cprint(msg, 'red',  attrs = ['bold'])

        try:
            member.pullRecords(credentials, session)
            recordCount += 1

        except AssertionError:
            cprint("\tunable to pull record", 'red', attrs = ['bold'])
            member.pulled = 'error'
            recordCount -= 1

        try:
            member.fetch_former_bishop(credentials, session)
            bishopCount += 1

        except AssertionError:
            cprint("\tformer bishop not found", 'red', attrs = ['bold'])
            member.bishop = individual.Bishop('error', 'error')
            bishopCount -= 1

        member.update_sheet(service)

    cprint("\tpulled %s records" % recordCount, 'green')
    cprint("\tfound %s bishops" % bishopCount, 'green')


    

if __name__ == '__main__':
    main()
