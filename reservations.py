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

# Send a request to get all subnets in '147.188.0.0/16'
response = requests.get(ADDRESS + 'network', params=params, verify=False, auth=('USERNAME', 'PASSWORD'))

# If the request returns error exit the program
if response.status_code != requests.codes.ok:
    exit_msg = 'Error {} script terminated: {}'
    sys.exit(exit_msg.format(r.status_code, r.reason))

# Store cookie for consecutive requests
ibapauth_cookie = response.cookies['ibapauth']
cookies = {'ibapauth': ibapauth_cookie}

# jsonify the response which now is a dictionary of all the entries
r = response.json()

headers = {
    'content-type': 'application/json',
}

params = (
    ('_function', 'next_available_ip'),
    ('_return_as_object', '1'),
)

data = '{"num":1}'

# For every network in the /16 find the next available IP
for dict in r:
    response = requests.post(ADDRESS + dict['_ref'], headers=headers, params=params, data=data, verify=False, cookies=cookies)
    innerr = response.json()

    if 'result' in innerr:
        # If the next available's IP forth octet is between 1 and 10 then query infoblox for that IP
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
                    # If the IP doesn't have a record that is equal to fixedaddress, ipv4address, a, prt, host record, reserve it
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

                        # Currently reservation request is commented out and only printing with as per the print statement above the addresses that are to be added
                        #response = requests.post(ADDRESS+'fixedaddress', headers=headers, params=params, data=data, verify=False, cookies=cookies)