#!/usr/bin/env python

import tools
import requests
import sys
import json

#TODO dynamically fill filename
PROFILE_ADDRESS = 'https://www.lds.org/mls/mbr/records/member-profile/service/M0000062426036?lang=eng'
HEADERS = {'accept':'application/json, text/plain, */*'}

username = sys.argv[1]
password = sys.argv[2]

session = requests.session()

credentials = tools.login(session, username, password)

response = session.get(url = PROFILE_ADDRESS, cookies = credentials, headers = HEADERS)

assert response.status_code == 200

try:
    decoded = json.loads(response.text)

except(ValueError, KeyError, TypeError):
    print "Error parsing json reponse"

print decoded['individual']['priorUnits'][0]['unitName']

