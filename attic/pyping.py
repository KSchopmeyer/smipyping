#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4

"""
    cimping access the availability of simlab servers either a single
    server or the known list from a csv input file
"""

from __future__ import print_function
import argparse
import csv
import os
import platform
from pywbem import WBEMConnection
from pywbem.cim_operations import CIMError, ConnectionError


FILE_NAME = 'cimoms-2015-10-30.2.csv'

def get_csvfile(csv_filename):
    """Open a cvs file containing the following
    TODO
        return the internal list of cvs rows.
    """
    return csv.DictReader(open(csv_filename))

def get_cvsfile_iplist(cvs_file):
    """PROBABLY NOT NEEDED"""

    print('type %s' % type(cvs_file))
    for row in cvs_file:
        row['pinged'] = None
        if ping_host(row['IPAddress'], args.verbose):
            if args.verbose:
                print('Found %s ip=%s' % (row['IPAddress'],
                                          row['CompanyName']))
            row['pinged'] = True
            output_list.append(row)

        else:
            if args.verbose:
                print('Not Found %s ip=%s' % (row['IPAddress'],
                                              row['CompanyName']))
            row['pinged'] = False
            output_list.append(row)
    return output_list

def ping_hosts(rows, verbose):
    """Ping hosts defined by cvs_rows table and return new list
       that adds status to the table
    """

    rtn_list = []
    for row in rows:

        row['pinged'] = ping_host(row['IPAddress'], verbose)

        if verbose:
            print('%sound ip=%s ip=%s' % (('F' if row['pinged'] else 'Not f'),
                                          row['IPAddress'],
                                          row['CompanyName']))
        rtn_list.append(row)
    return rtn_list

def ping_host(hostname, verbose):
    """ Ping a host and return true if found"""
    ###response = os.system("ping -c 1 " + hostname)

    # Ping parameters as function of OS
    # TODO windows parameters not tested.

    ping_str = "-n 1" if  platform.system().lower() == "windows" else "-c 1 -w2 -q"
    print('hostname %s pingstr %s' % (hostname, ping_str))

    # Ping
    response = os.system("ping " + ping_str + " " + hostname + " > /dev/null 2>&1")
    #response = os.system("ping " + ping_str + " " + hostname) == 0

    if verbose:
        if response == 0:
            print('%s is up!' % hostname)
        else:
            print('%s is down!' % hostname)

    return True if response == 0 else False

def gen_report(rows):
    """Generate report of info in the cvs_rows table"""

    # print table of results.
    #print('len2 %s' % len(input_list))
    # why could I not use the input_file again here.
    print('Company              IPAddress      Ping\n' \
          '----------------------------------------')
    for row in rows:
        if row['pinged'] is not None:
            pinged = "OK" if row['pinged'] else 'Fail'
        print('{:20} {:14} {:6}'.format(row['CompanyName'],
                                        row['IPAddress'],
                                        pinged))
    print('\n')

def access_host(hostname, user, cred, ns, verbose):
    try:
        conn = WBEMConnection('https://' + hostname, (user, cred),
                              no_verification=True, timeout=5)
    except CIMError as ce:
        print('Error on host get class %s' % hostname)
        print(ce.args[0])
    except exception:
        print('Internal error in socket')
        return False
    try:
        clas = conn.GetClass('CIM_ManagedElement', namespace=ns)
    except ConnectionError as ce:
        print('Connection Failed on host get class %s' % hostname)
        print(ce.args[0])
        return False        
    except CIMError as ce:
        print('Error on host get class %s' % hostname)
        print(ce.args[0])
        return False
    print('Good access for host %s' % hostname)
    return True

def access_hosts(rows, verbose):
    """access each hosts defined by cvs_rows table and return new list
       that adds status to the table
    """

    rtn_list = []
    for row in rows:
        print('call access_host host=%s u=%s p=%s, ns=%s' % (row['IPAddress'],
                                                             row['Principal'],
                                                             row['Credential'],
                    row['InteropNamespace']))
        access_host(row['IPAddress'], row['Principal'], row['Credential'],
                    row['InteropNamespace'], args.verbose)

        if verbose:
            pinged = False
            try:
                if row['pinged']:
                    pinged = True
            except KeyError as ke:
                print('row[pinged] exception')
                pinged=False
            print('%sound %s ip=%s' % (('F' if pinged else 'Not f'),
                                       row['IPAddress'],
                                       row['CompanyName']))
        rtn_list.append(row)
    return rtn_list


# TODO modify this so we create multiple groups representing input
#  csv, single
#  TODO: add a parameter to represent tests to execute.

parser = argparse.ArgumentParser(description='Execute a' \
                                             ' cimping request.')
parser.add_argument('--cvsfile', '-c',
                    help='Use cvs input file')

parser.add_argument('--access', '-a', action='store_true',
                    help='Test acccess rather than ping')

parser.add_argument('--verbose', '-v', action='store_true',
                    help='Verbose output flag. Display additional info about'
                         ' request and response')

parser.add_argument('--hostname', '-ho',
                    help='Target host name or IP address for request')

parser.add_argument('--user', '-u', default=None,
                    help='Client user name if required for the operation')

parser.add_argument('--password', '-p', default=None,
                    help='Client password if required for the operation')

parser.add_argument('--namespace', '-n', default='interop',
                    help='User namespace. Defaults to interop.')

parser.add_argument('--interop', '-i', default='interop',
                    help='Interop namespace. Defaults to interop.')


parser.add_argument('--company', '-co', default='None',
                    help='Name of company.')

args = parser.parse_args()

if args.verbose:
    print(args)

if args.access:
    if args.cvsfile:
        cvs_rows = get_cvsfile(FILE_NAME)
        output_list = access_hosts(cvs_rows, args.verbose)
    ##gen_report(output_list)
    else:
        # connect to single server
        not_found_list = []
        found_list = []

        if access_host(args.hostname, args.user, args.password,
                       args.ns, args.verbose):
            print('Found %s ip=%s' % (args.company, args.hostname))
            found_list.append((args.hostname, args.company))

        else:
            print('Not Found %s ip=%s' % (args.company, args.hostname))
            not_found_list.append((args.hostname, args.company))

if args.cvsfile:
    cvs_rows = get_csvfile(FILE_NAME)
    output_list = ping_hosts(cvs_rows, args.verbose)
    gen_report(output_list)
else:
    # connect to single server
    not_found_list = []
    found_list = []

    if ping_host(args.hostname, args.verbose):
        print('Found %s ip=%s' % (args.company, args.hostname))
        found_list.append((args.hostname, args.company))

    else:
        print('Not Found %s ip=%s' % (args.company, args.hostname))
        not_found_list.append((args.hostname, args.company))


#### need output dictionary
#output_list = []
#if args.cvsfile:
    #input_file = csv.DictReader(open(FILE_NAME))
    #print('type %s' % type(input_file))
    #for row in input_file:
        #row['pinged'] = None
        #if ping_host(row['IPAddress'], args.verbose):
            #if args.verbose:
                #print('Found %s ip=%s' % (row['IPAddress'],
                                          #row['CompanyName']))
            #row['pinged'] = True
            #output_list.append(row)

        #else:
            #if args.verbose:
                #print('Not Found %s ip=%s' % (row['IPAddress'],
                                              #row['CompanyName']))
            #row['pinged'] = False
            #output_list.append(row)

    ## print table of results.
    ##print('len2 %s' % len(input_list))
    ## why could I not use the input_file again here.
    #print('Company              IPAddress      Ping\n' \
          #'----------------------------------------')
    #for row in output_list:
        #if row['pinged'] is not None:
            #pinged = "OK" if row['pinged'] else 'Fail'
        #print('{:20} {:14} {:6}'.format(row['CompanyName'],
                                        #row['IPAddress'],
                                        #pinged))
    #print('\n')
#else:






