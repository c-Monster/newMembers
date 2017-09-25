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


def main():

    cprint('Starting LDS Tools Automator...', 'green', attrs=['bold'])

    cprint('\tFetching data from Google Sheets...', 'cyan')

    try:
        values = data.get_data()
    except ValueError:
        cprint('Error: no data in spreadsheet!', 'red', attrs = ['bold'])

    members = data.parse_data(values) 

    cprint('\tPulling records...', 'cyan')

    username = raw_input(colored('\tLDS Username: ', 'yellow'))
    password = getpass.getpass(colored('\tLDS Password: ', 'yellow'))

    decoded = json.loads(members)

    session = requests.session()
    credentials = tools.login(session, username, password)

    mrns = []
    for member in decoded:
    
        try:
            result = records.pull(member, credentials, session)
            mrns.append(result)
            cprint('\tsuccess!', 'green')
            
        except AssertionError:
            result = {
                    'error': 'non-200 response',
                    'row': member['id']
                    }
            cprint('\terror', 'red', attrs = ['bold'])
        except (ValueError, KeyError, TypeError):
            result = {
                    'error': 'unable to parse JSON',
                    'row': member['id']
                    }
            cprint('\terror', 'red', attrs = ['bold'])

        row = data.build_pulled_row(result)
        data.update_row(row, result['row'])
    
    cprint('\tFetching former bishops...', 'cyan')

    count = 0
    for member in mrns:

        try: 
            result = bishops.fetch(member, credentials, session)
            cprint('\tsuccess!', 'green')
            count += 1

        except AssertionError:
            result = {
                    'error': 'non-200 response',
                    'row': member['row']
                    }
            cprint('\terror', 'red', attrs = ['bold'])

        except (ValueError, KeyError, TypeError):
            result = {
                    'error': 'unable to parse JSON',
                    'row': member['row']
                    }
            cprint('\terror', 'red', attrs = ['bold'])
            
        row = data.build_bishop_row(result)
        data.update_row(row, result['row'])
    

    msg = 'moved %d records' % len(mrns)
    cprint(msg, 'green', attrs = ['bold'])
    msg = 'found %d bishops' % count
    cprint(msg, 'green', attrs = ['bold'])

if __name__ == '__main__':
    main()
