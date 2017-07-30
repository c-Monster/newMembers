#!/usr/bin/env python

import requests
import json
import tools
import recordRequest


username = raw_input('LDS Username:')
password = raw_input('LDS Password:')

session = requests.session()
credentials = tools.login(session, username, password)

name = raw_input('Name of member:')
birthday = raw_input('Birthday of member (YYYYMMDD):')

payload = {
        'mrnOrName':name,
        'name':name,
        'birthDate':birthday
        }

recordsAddress = 'https://www.lds.org/mls/mbr/services/records/request/find-member?lang=eng'
pullAddress = 'https://www.lds.org/mls/mbr/services/records/request/move-household?lang=eng'
#TODO verify that we only need the accept application/json header
headers = {
        'accept':'application/json, text/plain, */*', 
        'accept-encoding':'gzip, dseflate, br',
        'accept-language':'en-US,en;q=0.8',
        'content-type':'application/json;charset=UTF-8',
        'origin':'https://www.lds.org',
        'referer':'https://www.lds.org/mls/mbr/records/request/find-member',
        'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        


response = session.post(url = recordsAddress, data = json.dumps(payload), cookies = credentials, headers = headers)

try:
    decoded = json.loads(response.text)

except (ValueError, KeyError, TypeError):
    print "Error parsing JSON response"


#build request body with apt number
request = recordRequest.buildRequestBody(response.text, '188')

#this is new
headers['dnt'] = '1'
pullResponse = session.put(url = pullAddress, data = json.dumps(request), cookies = credentials, headers = headers)

print pullResponse.status_code

try:
    decoded2 = json.loads(pullResponse.text)

except (ValueError, KeyError, TypeError):
    print "Error parsing JSON response"
