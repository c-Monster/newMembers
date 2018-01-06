#!/usr/bin/env python

import requests
import json
import copy


#logs returns LDS Tools credentials
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


#builds POST body used to move records
def build_request_body(text, apt, phone, email):

    try:
        decoded = json.loads(text)

    except (ValueError, KeyError, TypeError):
        print "Could not parse JSON response"


