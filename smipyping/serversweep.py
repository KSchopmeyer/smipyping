#!/usr/bin/env python

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

"""
    cimping access the availability of simlab servers either a single
    server or the known list from a csv input file
"""

from __future__ import print_function, absolute_import
import socket
import sys
import os
import time
import argparse as _argparse
import threading

from scapy.all import *

from _cliutils import SmartFormatter as _SmartFormatter
from _cliutils import check_negative_int
from userdata import CsvUserData

DEFAULT_TEST_PORT = 5989

results = []
def check_port_syn(dst_ip, dst_port, verbose):
    """Check a single address consiting of host_ip and port using the
        SYN and ack.  This is one way to test for open https ports
    """

    SYNACK = 0x12
    RSTACK = 0x14

    conf.verb = 0 # Disable verbose in sr(), sr1() methods
    port_open = False
    src_port = RandShort()
    p = IP(dst=dst_ip)/TCP(sport=src_port, dport=dst_port, flags='S')
    resp = sr1(p, timeout=2) # Sending packet
    if str(type(resp)) == "<type 'NoneType'>":
        if verbose:
            print('%s Closed. response="none"' % dst_ip)
    elif resp.haslayer(TCP):
        if resp.getlayer(TCP).flags == SYNACK:
            send_rst = sr(IP(dst=dst_ip)/TCP(sport=src_port, dport=dst_port,
                                             flags='AR'), timeout=1)
            port_open = True
            if verbose:
                print('check_port:%s Open' % dst_ip)
        elif resp.getlayer(TCP).flags == RSTACK:
            if verbose:
                print('%s Closed. response="RSTACK"' % dst_ip)
    else:
        if verbose:
            print('%s is Down' % dst_ip)
    result_key = '%s:%s' % (dst_ip, dst_port)
    if port_open:
        results.append(result_key)
    sys.stdout.flush()
    return port_open


def scan_subnets(subnets, start_ip, end_ip, port, verbose):
    """ Scan a subnet and return list of hosts found with port open
        subnet can be either a specific subnet or a list of subnets
        Ports can be either single port or list of ports
        Returns Dictionary of hosts that have defined port open.
    """
    open_hosts = []

    # if subnets or port is list, recursively call with each entry
    if isinstance(subnets, list):
        for subnet in subnets:
            rtn = scan_subnets(subnet, start_ip, end_ip, port, verbose)
            if rtn is not None:
                open_hosts.extend(rtn)
        return open_hosts

    if isinstance(port, list):
        for p in port:
            rtn = scan_subnets(subnets, start_ip, end_ip, p, verbose)
            if rtn is not None:
                open_hosts.extend(rtn)
        return open_hosts

    for ip in range(start_ip, end_ip + 1):
        test_ip = subnets + '.' + str(ip)
        test_host_id = '%s:%s' % (test_ip, port)

        result = check_port_syn(test_ip, port, verbose) # Test one ip:port

        print('test %s %s result %s' % (test_ip, port, result))

        if verbose:
            response_txt = 'Exists' if result else 'None'
            print('test address=%s, %s' % (test_host_id, response_txt))
        else:
            sys.stdout.flush()
            sys.stdout.write(test_host_id)
            if not test_ip == end_ip:
                sys.stdout.write('\b' * (len(test_host_id) + 4))

        if result: # Port exists
            open_hosts.append(test_host_id) # Append to list

    return open_hosts

def scan_subnets_threaded(subnets, start_ip, end_ip, port, verbose):

    tests = bld_test_list(subnets, start_ip, end_ip, port, verbose)
    open_hosts = []
    threads_ = []

    for test in tests:
        process = threading.Thread(target=check_port_syn, args=(test[0],
                                   test[1], verbose))
        threads_.append(process)

    for process in threads_:
        process.start()
    for process in threads_:
        process.join()
    for result in results:
        open_hosts.append(result)
    return open_hosts

def bld_test_list(subnets, start_ip, end_ip, port, verbose):
    """ Scan a subnet and return list of hosts found with port open
        subnet can be either a specific subnet or a list of subnets
        Ports can be either single port or list of ports
        Returns Dictionary of hosts that have defined port open.
    """
    test_list = []

    if isinstance(subnets, list):
        subnetlist = subnets
    else:
        subnetlist = [subnets]

    if isinstance(port, list):
        ports = port
    else:
        ports = [port]

    for subnet in subnetlist:
        for port_ in ports:
            for ip in range(start_ip, end_ip + 1):
                test_ip = '%s.%s' % (subnet, ip)
                #test_host_id = '%s:%s' % (test_ip, port_)
                test_list.append((test_ip, port_))

    return test_list

def print_open_hosts_report(args, open_hosts, total_time, user_data):
    print('\n')
    print("=" * 50)
    execution_time = ''
    if total_time <= 60:
        execution_time = "%s sec" % (round(total_time, 1))
    else:
        execution_time = "%s min" % (total_time / 60)

    range_txt = '%s:%s' % (args.startip, args.endip)

    if len(open_hosts) != 0:
        print('Open WBEMServers:subnet(s)=%s port(s)=%s range %s, %s count %s' \
                % (args.subnet, args.port, range_txt, execution_time, \
                   len(open_hosts)))

        for host_data in open_hosts:
            if user_data is not None:
                entry = user_data.get_dict_entry(host_data)
                if entry is not None:
                    print('%s %-20s %-18s %-18s' % (host_data,
                                                    entry['CompanyName'],
                                                    entry['Product'],
                                                    entry['SMIVersion']))
                else:
                    print('%s %s' % (host_data, "Not in user data"))
            else:
                print('%s' % (host_data))
    else:
        print('No WBEM Servers:subnet(s)=%s port(s)=%s range %s, %s' \
                % (args.subnet, args.port, range_txt, execution_time))
    print("=" * 50)

def main():
    """
        Port sweep demo program
    """

    prog = "sweep"  # Name of the script file invoking this module
    usage = '%(prog)s [options] server'
    desc = 'Sweep possible WBEMServer ports across a range of IP addresses '\
           'and ports to find existing open WBEM servers.'
    epilog = """
Examples:
  %s 10.1.134 --startip=1 --endip=254
        The above example will scan the subnets 10.1.134 from 1 to 254
  %s 10.1.134
  %s 10.1.132 10.1.134 -p 5989 -p 5988

""" % (prog, prog, prog)

    argparser = _argparse.ArgumentParser(
        prog=prog, usage=usage, description=desc, epilog=epilog,
        formatter_class=_SmartFormatter)

    pos_arggroup = argparser.add_argument_group(
        'Positional arguments')
    pos_arggroup.add_argument(
        'subnet', metavar='subnet', nargs='+',
        help='IP subnets to scan (ex. 10.1.132). Multiple subnets allowed')

    subnet_arggroup = argparser.add_argument_group(
        'Scan related options',
        'Specify parameters of the subnet scan')
    subnet_arggroup.add_argument(
        '--startip', '-s', metavar='Start', nargs='?', default=1,
        type=check_negative_int,
        help='Start scanning from this IP')
    subnet_arggroup.add_argument(
        '--endip', '-e', metavar='End', nargs='?', default=254,
        type=check_negative_int,
        help='Scan to this IP')
    subnet_arggroup.add_argument(
        '--port', '-p', nargs='?', action='append', type=int,
        help='Port(s) to test. This argument may be repeated to test ' \
             'multiple ports')

    general_arggroup = argparser.add_argument_group(
        'General options')
    general_arggroup.add_argument(
        '--csvfile', '-c',
        help='Use csv input file')
    general_arggroup.add_argument(
        '--threaded', '-t', action='store_true', default=False,
        help='If set output detail displays as test proceeds')        
    general_arggroup.add_argument(
        '--verbose', '-v', action='store_true', default=False,
        help='If set output detail displays as test proceeds')

    args = argparser.parse_args()

    if not args.subnet:
        argparser.error('No Subnet specified')

    # set default port if none provided.
    if args.port is None:
        args.port = [DEFAULT_TEST_PORT]

    if args.verbose:
        print('subnet=%s' % args.subnet)
        print('startip=%s' % args.startip)
        print('endip=%s' % args.endip)
        print('port=%s' % args.port)
        print('csvfile=%s' % args.csvfile)
        print('verbose=%s' % args.verbose)
        print('threaded=%s' % args.threaded)
    user_data = None
    if args.csvfile is not None:
        user_data = CsvUserData(args.csvfile)

    start_time = time.time() # Scan start time

    try:
        open_hosts = []

        if args.threaded:
            rtn = scan_subnets_threaded(args.subnet, args.startip,
                                        args.endip, args.port, args.verbose)
        else:
            rtn = scan_subnets(args.subnet, args.startip,
                                        args.endip, args.port, args.verbose)            
        if rtn is not None:
            open_hosts.extend(sorted(rtn))

    except KeyboardInterrupt:
        # Used in case the  user press "Ctrl+C", it will show the
        # following error instead of a python's scary error
        print("\nCtrl+C. Exiting with no output.")
        sys.exit(1)

    total_time = time.time() - start_time

    print_open_hosts_report(args, open_hosts, total_time, user_data)

if __name__ == '__main__':
    main()


