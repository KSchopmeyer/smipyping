#!/usr/bin/env python2

# vim: tabstop=4 shiftwidth=4 softtabstop=4
from __future__ import print_function
import csv
import argparse

"""
    Manage the user information data base.  Currently that base is created
    from the csv file provided by SMI staff and is in csv format
"""
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
        #csv_dict = cvs.DictReader(cvsfile)
        for row in csv_line:
            print(','. join(row))
        #for row in csv_dict:
        #    print(row['CompanyName'])

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
#cimcli ec -l 10.1.134.212 -n interop -s -u smilab -p foosball -v
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


