#!/usr/bin/env python2
# (C) Copyright 2017 Inova Development Inc.
# All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# vim: tabstop=4 shiftwidth=4 softtabstop=4
"""
    Manage the user information data base.  Currently that base is created
    from the csv file provided by SMI staff and is in csv format
"""
from __future__ import print_function, absolute_import

import csv
import argparse


def select_company(testname, expected_name):
    if expected_name is None:
        return True
    else:
        return testname == expected_name


description = 'TBD'
parser = argparse.ArgumentParser(description='TBD')

parser.add_argument('cvsfile', help='CVS input file name. Reuired')
parser.add_argument('--output', '-o', help='display, cimcli, smipyping')
parser.add_argument('--company', '-co', help='display, cimcli, smipyping')

parser.add_argument('--verbose', '-v', help='verbose')

args = parser.parse_args()

if args.output == 'displaypld':
    with open(args.cvsfile) as csvfile:
        csv_line = csv.reader(csvfile)
        # ##csv_dict = cvs.DictReader(cvsfile)
        for row in csv_line:
            print(','. join(row))
        # ##for row in csv_dict:
        # ##    print(row['CompanyName'])

if args.output == 'display':
    input_file = csv.DictReader(open(args.csvfile))
    for row in input_file:
        print(row)
        print(row['CompanyName'], row['IPAddress'], row['Principal'],
              row['Credential'])

if args.output == 'smipyping':
    input_file = csv.DictReader(open(args.cvsfile))
    for row in input_file:
        print('./smipyping.py  %s -u %s -p %s -n %s -i %s -c \"%s\"' %
              (row['IPAddress'], row['Principal'], row['Credential'],
               row['Namespace'], row['InteropNamespace'], row['CompanyName']))
# ##cimcli ec -l 10.1.134.212 -n interop -s -u smilab -p foosball -v
if args.output == 'cimcli':
    input_file = csv.DictReader(open(args.cvsfile))
    if args.verbose:
        verbose_param = '-v'
    else:
        verbose_param = ''
    for row in input_file:
        if select_company(row['CompanyName'], args.company):
            print('cimcli nc -l %s -u %s -p %s -n %s %s -s' %
                  (row['IPAddress'], row['Principal'], row['Credential'],
                   row['InteropNamespace'], verbose_param))
else:
    print('Error in output def %s' % args.output)
