#!/usr/bin/env python
# encoding: utf-8

import requests
import sys
import os
import re
import getpass
import json
import string

def reserve(innerr, subnet, size):
    if 'result' in innerr:
        # If the next available's IP forth octet is less than subnet+number of IPs we want to reserve then query infoblox
        if int(innerr['result']['ips'][0].split('.')[3]) > subnet and int(innerr['result']['ips'][0].split('.')[3]) < subnet+11:
            for i in range(int(innerr['result']['ips'][0].split('.')[3]), subnet+size):
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

                        ''' Currently reservation request is commented out and only printing with as the print statement above the addresses that are to be added
                        response = requests.post(ADDRESS + 'fixedaddress', headers=headers, params=innerparams2, data=innerdata, verify=False, cookies=cookies)
                        
                        # If the request returns error exit the program
                        if response.status_code != requests.codes.ok:
                            exit_msg = 'Error {} script terminated: {}'
                            sys.exit(exit_msg.format(r.status_code, r.reason))'''


def reservelast(dict):
    params = (
        ('_return_fields+', 'ipv4addr,mac'),
        ('_return_as_object', '1'),
    )

    network = dict['network'].split('.')
    for i in range (250, 255):
        address = network[0] + '.' + network[1] + '.' + network[2] + '.' + str(i)

        r = requests.get(ADDRESS + 'search?address=' + address, cookies=cookies, verify=False)

        response = r.json()

        if len(response) < 3:
            data = '{"ipv4addr":' + address + ' ,"mac":"00:00:00:00:00:00"}'
            print(innerdata)

        '''    response = requests.post(ADDRESS + 'fixedaddress', headers=headers, params=params, data=data,
                                     verify=False, cookies=cookies)
            
            
            # If the request returns error exit the program
            if response.status_code != requests.codes.ok:
                exit_msg = 'Error {} script terminated: {}'
                sys.exit(exit_msg.format(r.status_code, r.reason))
            '''

cookies = ''

# Set parameters to access the NIOS WAPI.
ADDRESS = 'https://URL/wapi/v2.5/'  # Version varies
valid_cert = False  # False since GM uses self-signed certificate
JSON = 'application/json'

params = (
    ('network_container', '147.188.0.0/16'),
)

# Send a request to get all subnets in '147.188.0.0/16'
response = requests.get(ADDRESS + 'network', params=params, verify=False, auth=('USER', 'PASS'))

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

for dict in r:

    # For every network in the /16 find the next available IP
    response = requests.post(ADDRESS + dict['_ref'], headers=headers, params=params, data=data, verify=False, cookies=cookies)
    innerr = response.json()


    # For /24 reserve the first 10 for greater prefixes the first 4
    if dict['network'].split('/')[1] == '24':
        reservelast(dict)
        if 'result' in innerr:
            reservefirst(innerr, 0, 10)
    else:
        # The number of subnets is calculated as 2 exponsed to the difference on /24 - more specific prefix
        exponent = 2 ** (int(dict['network'].split('/')[1]) - 24)

        # Calculate the subnet IP
        for i in range(0, exponent):
            subnet = int((i * (256 / exponent+1)) - i)

            print(dict['network'], subnet)
            reserve(innerr, subnet, 5)
