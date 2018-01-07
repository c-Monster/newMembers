#!/usr/bin/env python

import requests
import sys
import json
import tools

from termcolor import colored, cprint

#TODO figure out the correct number of digits in MRN --> str.zfill() 

def fetch(member, credentials, session):
    
    name = member['name']
    mrn = member['mrn']

    if len(mrn) > MAX:
        mrn = mrn[len(mrn)-MAX:]
    
    print "\tfinding former bishop and email of %s..." % colored(name, 'yellow')
    
            
    address = PROFILE_ADDRESS % {'mrn': mrn}
            
            

    
    output = {
        'bishop': leader[len(leader)-1],
        'email': decoded['leaderEmail'],
        'row': member['row']
            }
        
    return output
    
        

