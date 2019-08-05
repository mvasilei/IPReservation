#!/usr/bin/env python
# encoding: utf-8

import requests
import sys
import os
import re
import getpass
import json
import string

cookies = ''

# Set parameters to access the NIOS WAPI.
ADDRESS = 'https://gmcc01.bham.ac.uk/wapi/v2.5/'  # Version varies
valid_cert = False  # False since GM uses self-signed certificate
JSON = 'application/json'

params = (
    ('network_container', '147.188.0.0/16'),
)

response = requests.get(ADDRESS + 'network', params=params, verify=False, auth=('USERNAME', 'PASSWORD'))

if response.status_code != requests.codes.ok:
    exit_msg = 'Error {} logging out: {}'
    sys.exit(exit_msg.format(r.status_code, r.reason))

ibapauth_cookie = response.cookies['ibapauth']
cookies = {'ibapauth': ibapauth_cookie}

r = response.json()

headers = {
    'content-type': 'application/json',
}

params = (
    ('_function', 'next_available_ip'),
    ('_return_as_object', '1'),
)

data = '{"num":1}'

for dict in r:
    response = requests.post(ADDRESS + dict['_ref'], headers=headers, params=params, data=data, verify=False, cookies=cookies)
    innerr = response.json()

    if 'result' in innerr:
        if int(innerr['result']['ips'][0].split('.')[3]) < 11:
            for i in range(int(innerr['result']['ips'][0].split('.')[3]), 11):
                address = innerr['result']['ips'][0].split('.')[0]+'.' \
                     + innerr['result']['ips'][0].split('.')[1]+'.'\
                     +innerr['result']['ips'][0].split('.')[2]+'.'\
                     + str(i)

                innerparams = (
                    ('address', address),
                    ('_return_as_object', '1'),
                )

                response = requests.get(ADDRESS + 'search', headers=headers, params=innerparams, verify=False, cookies=cookies)

                innerr2 = response.json()

                if 'result' in innerr2:
                    if innerr2['result'][0]['_ref'].split('/')[0] == 'fixedaddress' or \
                            innerr2['result'][0]['_ref'].split('/')[0] == 'ipv4address' or \
                            innerr2['result'][0]['_ref'].split('/')[0] == 'record:a' or \
                            innerr2['result'][0]['_ref'].split('/')[0] == 'record:ptr' or \
                            innerr2['result'][0]['_ref'].split('/')[0] == 'record:host':

                        pass
                    else:

                        innerparams2 = (
                            ('_return_fields+', 'ipv4addr,mac'),
                            ('_return_as_object', '1'),
                        )

                        innerdata = '{"ipv4addr":' + address + ' ,"mac":"00:00:00:00:00:00"}'
                        print(innerdata)

                        #response = requests.post(ADDRESS+'fixedaddress', headers=headers, params=params, data=data, verify=False, cookies=cookies)