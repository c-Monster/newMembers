#!/usr/bin/env python

import requests

def login(session, username, password):

    meta = session.get('https://ident.lds.org/sso/UI/Login?service=credentials')
    tokens = meta.cookies
    
    payload = {
              'IDToken1':username,
              'IDToken2':password,
              'IDButton':'Log In',
              'goto':'',
              'gotoOnFail':'',
              'SunQueryParamsString':'c2VydmljZT1jcmVkZW50aWFscw==',
              'encoded':'false',
              'gx_charset':'UTF-8'
              }
    
    response = session.post(
            'https://ident.lds.org/sso/UI/Login?service=credentials', 
            data = payload, 
            allow_redirects = False,
            cookies = tokens
            )

    assert response.status_code == 302
    assert 'lds-id' in response.cookies
    return response.cookies


username = raw_input('LDS Username:')
password = raw_input('LDS Password:')

session = requests.session()
credentials = login(session, username, password)

name = raw_input('Name of member:')
birthday = raw_input('Birthday of member (YYYYMMDD):')
payload = {
        'mrnOrName':name,
        'name':name,
        'birthdate':birthday
        }

recordsAddress = 'https://www.lds.org/mls/mbr/services/records/request/find-member?lang=eng'
response = session.get(url = recordsAddress, data = payload, cookies = credentials)
print response
responseString = str(response.text).split("platformCallback")[1]
response_as_dict_string = responseString.replace("true", "True").replace("null", "None")
response_dict = eval(response_as_dict_string)
print response_dict['name']
