#!/usr/bin/env python

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

"""
Server sweep functions.

These functions allow sweeping a set of subnets for specific open
ports.

WARNING: Because the sweep uses SYN to test for an open https port this
code must be executed in privileged mode. That is a python requirement.

While  other tests can detect open http ports, we must detect an open
https port so the choices of test are limited.
"""

from __future__ import print_function, absolute_import
import os
import sys
import time
from threading import Thread
import Queue
import itertools
import six

from .config import MAX_THREADS
from ._scanport_syn import check_port_syn
from ._scanport_tcp import check_port_tcp
from ._tableoutput import TableFormatter
from ._logging import SWEEP_LOGGER_NAME, get_logger

__all__ = ['ServerSweep', 'SCAN_TYPES']

SCAN_TYPES = ['tcp', 'syn', 'all']


class ServerSweep(object):
    """
    Class to define the functionality to execute port sweeps of
    IP address and ports to find potential WBEM Servers.
    """
    def __init__(self, net_defs, ports, target_data=None, no_threads=False,
                 min_octet_val=1, max_octet_val=254, verbose=False,
                 scan_type='tcp'):
        """
        Parameters:
          net_defs: list of subnets. Each subnet is defined as a sweep range
          where the sweep range for each component of the ip address is an
          integer (designates a single address), a range (integer:integer),
          or a list (integer,integer,integer)

          ports:(list of integer or integer) one or more ports to be included
          in the scan

          targets_data (todo) The provider data  that defines the known
          providers.  This is optional. If not provided, it is not included
          in the output report.

          no_threads (bool): Flag to indicate whether the threaded
            implementation is to be used

          min_octet_val (integer): integer defining the minimum octet value
          to be used for the expansion of any ip octet not defined in a
          subnet definition. Default = 1

          max_octet_val (integer): integer defining the maximum octet value
          to be used for the expansion of any ip octet not defined in a
          subnet definition. Default = 254

          no_threads: Boolean. Use non-threaded implementation if True. The
          default is to use the threaded implementation

          verbose: detailed display if True
        """
        self.net_defs = net_defs
        self.min_octet_val = min_octet_val
        self.max_octet_val = max_octet_val
        self.ports = ports
        self.no_threads = no_threads
        self.target_data = target_data
        self.verbose = verbose
        self.total_sweep_time = None
        self.total_pings = None
        self.scan_type = scan_type
        self.logger = get_logger(SWEEP_LOGGER_NAME)
        self.kill_threads = False

    def check_port(self, test_address):
        """
        Runs defined test against a single ip/port defined as a tuple in
        test_address

        Parameters:

          test_address: tuple containing ip address and port

          verbose (bool): passed on to the actual port check for possible
            detailed display

        Returns:
            True if port OK

        Exceptions:
            ValueError if self.scan_type invalid
        """
        error = None
        try:
            if self.scan_type == 'syn':
                result, err, str_ = check_port_syn(test_address[0],
                                                   test_address[1],
                                                   self.verbose,
                                                   self.logger)
            elif self.scan_type == 'tcp':
                result, err, str_ = check_port_tcp(test_address[0],
                                                   test_address[1],
                                                   self.verbose,
                                                   self.logger)
                error = str_
            elif self.scan_type == 'all':
                resulttcp, errno, str_ = check_port_tcp(test_address[0],
                                                        test_address[1],
                                                        self.verbose,
                                                        self.logger)
                resultsyn, cd, bl = check_port_syn(test_address[0],
                                                   test_address[1],
                                                   self.verbose, self.logger)
                result = resulttcp
                if resulttcp != resultsyn:
                    self.logger.debug('scanner result differ. addr=%s, syn=%s,'
                                      ' tcp=%s, errno=%s errno=%s',
                                      test_address, resultsyn, resulttcp, errno,
                                      os.strerror(errno))
                    print('Error scanner mismatch addr=%s, syn=%s, tcp=%s,'
                          ' errno=%s:%s' %
                          (test_address, resultsyn, resulttcp, errno,
                           os.strerror(errno)))

            else:
                raise ValueError('Invalid port checker type %s' % type)

        # Just exit program if keyboard interrupt
        except (KeyboardInterrupt, SystemExit):
            print('KeyboardInterrupt CheckPort')
            raise

        return (result, error)

    def list_subnets_to_scan(self):
        """
        show the ip addresses and ports to be scanned as a list and count
        of the totals.  This is primarily a diagnostic tool but helps users
        determine what all will be scanned.
        """
        test_list = [result for result in self.build_test_list()]
        print('scan list count=%s:' % len(test_list))
        index = 0
        for test_addr in test_list:
            index += 1
            print(' %4s %s' % (index, test_addr))

    def scan_subnets(self):
        """
        Nonthreaded scan of IP addresses for open ports.

        Scan a subnet and return list of hosts found with port open.

        Subnet can be either a specific subnet or a list of subnets
        Ports can be either single port or list of ports
        Returns Dictionary of hosts that have defined port open.
        """
        open_hosts = []
        test_count = 0
        for test_addr in self.build_test_list():
            test_count += 1
            result, error = self.check_port(test_addr)  # Test one ip:port
            response_txt = 'Exists' if result else ('None: %s' % error)
            self.logger.info('SCAN Result ip=%s, result=%s',
                             (test_addr,), response_txt)
            if self.verbose:
                print('test address=%s, %s' % ((test_addr,), response_txt))

            if result:  # Port exists
                open_hosts.append(test_addr)  # Append to list
        self.total_pings = test_count

        return open_hosts

    def process_queue(self, queue, results):
        """This is a thread function that processes a queue to do check_port.
        Each queue entry is a tuple of ip_address(with port) and results
        list where the results are appended for each succseful scan.
        """
        while not queue.empty():
            if self.kill_threads:
                return
            work = queue.get()
            results = work[1]   # get results list from work
            check_result, error = self.check_port(work[0])
            # TODO not passing on error information
            if check_result is True:
                # append address info to the results list
                results.append(work[0])
            queue.task_done()
        return

    def scan_subnets_threaded(self):
        """
        Threaded scan of IP Addresses for open ports.

        Scan the IP address defined by the input and return a list of open
        IP addresses. This function creates multiple processes and executes
        each call in a process for speed.
        """

        # set up queue to hold all call info
        queue = Queue.Queue(maxsize=0)
        num_threads = MAX_THREADS

        results = []
        test_count = 0
        for test_addr in self.build_test_list():
            test_count += 1
            queue.put((test_addr, results))
        self.total_pings = test_count

        # Start worker threads.
        threads = []
        for i in range(num_threads):  # pylint: disable=unused-variable
            t = Thread(target=self.process_queue, args=(queue, results))
            t.daemon = True    # allows main program to exit.
            threads.append(t)
            t.start()

        try:
            queue.join()
        except KeyboardInterrupt:
            print("Ctrl-C received! Sending kill to threads...")
            self.kill_threads = True
            for t in threads:
                t.kill_received = True

        # returns list of ip addresses that were were found
        return results

    def expand_subnet_definition(self, net_def):
        """
        Get a list of IP addresses from the net_definition provided in net_def.

        The syntax for the net definition is as follows:

        Defines for octets of an IPV4 address where each octet is one of the
        following:

          Integer representing the octet.

          Range definition for the octet defining the range of values in the
          expansion.  The syntax of the range definition is <nin>-<max> where
          min and max are integers.  Thus, 3:10 expands to all values from 3 to
          10 (inclusive) for that octet of the IP address

          List definition consists of list of values separated by commans. All
          of the values in the list are included in the expansion.

          Any missing octets are expanded to the range definition between
          the input parameters min_val and max_val

          Returns a list of the IP address that make up this expansion

          Parameters:

            net_def: String. See above for syntax

          Returns:  A generator that returns ip addresses until the expansion
          is exhausted.

          Exceptions:
            ValueError if any of the components of the net definition are in
            error.
        """
        octet_max = 255

        try:
            octets = net_def.split('.')
            ipv4_octet_count = 4
            for index in range(ipv4_octet_count):
                try:
                    octets[index]
                except IndexError:
                    octets.append('%d-%d' % (self.min_octet_val,
                                             self.max_octet_val))
        except Exception as ex:
            print('Exception subnet %s Exception %s' % (net_def, ex))
            raise

        octet_lists = []
        try:
            for octet in octets:
                if octet.isdigit():
                    try:
                        octet = int(octet)
                    except Exception as ex:
                        raise ValueError('octet %s not integer' % octet)
                    octet_lists.append([octet])
                elif '-' in octet:
                    range_ = octet.split('-')
                    min_ = int(range_[0])
                    max_ = int(range_[1]) + 1    # range is inclusive
                    if len(range_) != 2:
                        raise ValueError('Range %s invalid. Too many components'
                                         % range_)
                    if min_ < 0:
                        raise ValueError('Value %s in range %s invalid' %
                                         (min_,
                                          range_))
                    if max_ > octet_max:
                        raise ValueError('Value %s in range %s invalid. gt %s'
                                         % (max_, range_, octet_max))
                    if max_ <= min_:
                        raise ValueError('Value %s must be gt %s in  def %s' %
                                         (max_, min_, octet))

                    octect_list = [item for item in six.moves.range(min_, max_)]
                    octet_lists.append(octect_list)
                elif ',' in octet:
                    items = octet.split(',')
                    octet_lists.append([int(x) for x in items])
                else:
                    raise ValueError('Invalid octet %s in net definition %s' %
                                     (octet, net_def))
        except ValueError:
            raise

        # product_get, a generator that iproduces results of merged lists
        for ip in itertools.product(*octet_lists):
            yield '.'.join(map(str, ip))  # pylint: disable=bad-builtin

    def build_test_list(self):
        """
        Create list of IP addresses and ports to scan.

        Create dictionary of IP address: port for all ports in the ranges
        defined by the input parameters and return that dictionary

        Returns:
          Generator that generates a set of the combination of net defs and
          ports until the combinations are exhausted.

          Each call returns a tuple of (IP address, port)
        """

        if isinstance(self.net_defs, tuple):
            self.net_defs = list(self.net_defs)
        if not isinstance(self.net_defs, list):
            self.net_defs = [self.net_defs]

        if not isinstance(self.ports, (list, tuple)):
            self.ports = [self.ports]

        for net_def in self.net_defs:
            for test_ip in self.expand_subnet_definition(net_def):
                # return one tuple of ip address, port for each call
                for port_ in self.ports:
                    yield test_ip, port_

    def write_results(self, open_hosts, output_file='serversweep.txt',
                      unknown_only=True):
        """
        Write the results to an output file for further processing
        """
        with open(output_file, 'w+') as f1:
            # add code to filter
            for open_host in open_hosts:
                ip_address = '%s:%s' % (open_host[0], open_host[1])
                status = ''
                if self.target_data is not None:
                    record_list = self.target_data.get_targets_host(open_host)
                    status = 'known' if record_list else 'unknown'
                if unknown_only and status == 'unknown':
                    print('%s %s' % (ip_address, status), file=f1)
                else:
                    print('%s %s' % (ip_address, status), file=f1)

    def print_open_hosts_report(self, open_hosts):
        """
        Output report of the entries found.

        If userdata is found, include the userdata info including CompanyName,
        Product, etc.
        """
        print('\n')
        if self.total_sweep_time <= 60:
            execution_time = "%.2f sec" % (round(self.total_sweep_time, 1))
        else:
            execution_time = "%.2f min" % (self.total_sweep_time / 60)

        range_txt = '%s:%s' % (self.min_octet_val, self.max_octet_val)

        unknown = 0
        known = 0
        rows = []

        headers = ['IPAddress', 'CompanyName', 'Product', 'Error']

        title = 'Open WBEMServers:subnet(s)=%s\n' \
                'port(s)=%s range=%s, scan_type=%s time=%s\n' \
                '    total pings=%s pings answered=%s' \
                % (self.net_defs, self.ports, range_txt, self.scan_type,
                   execution_time, self.total_pings, len(open_hosts))

        if open_hosts:    # if open_hosts not zero
            # open_hosts.sort(key=lambda ip: map(int, ip.split('.')))
            # TODO this probably requires ordered dict rather than dictionary to
            # keep order. We are not outputing in full order. Note that
            # ip address itself is not good ordering since not all octets are
            # 3 char

            for host_data in open_hosts:
                ip_address = '%s:%s' % (host_data[0], host_data[1])
                if self.target_data is not None:
                    record_list = self.target_data.get_targets_host(host_data)
                    if record_list:
                        # TODO this should be a list since there may be
                        # multiples for single ip address
                        entry = self.target_data.get_target(record_list[0])
                        if entry is not None:
                            known += 1
                            rows.append([ip_address,
                                         entry['CompanyName'],
                                         entry['Product'],
                                         entry['SMIVersion']])
                        else:
                            unknown += 1
                            print('Invalid entry %s %s %s' % (
                                record_list[0], ip_address,
                                "Not in user data"))
                            rows.append([ip_address, "Not in base", "", ""])
                    else:
                        unknown += 1
                        rows.append([ip_address, "Unknown"])
                # no host info requested.
                else:
                    rows.append([ip_address])
        else:
            print('No WBEM Servers found:subnet(s)=%s port(s)=%s range %s, %s' %
                  (self.net_defs, self.ports, range_txt, execution_time))

        if rows:
            table = TableFormatter(rows, headers=headers,
                                   title=title)
            table.print_table()
        # TODO: Should the following  be in the report???
        print('\nScan Results: Found=%s, Unknown=%s, Total=%s Time=%s'
              % (known, unknown, (known + unknown), execution_time))

    def sweep_servers(self):
        """
        Execute the scan on the subnets defined by the class object
        constructor.

          Returns:
              List of hosts results with each entry in the list a tuple
              of (ip, port, error_info) for hosts with open ports in the
              defined range of subnets and ports input
        """
        start_time = time.time()   # Scan start time

        range_txt = '%s:%s' % (self.min_octet_val, self.max_octet_val)
        self.logger.info('Serversweep Scan WBEMServers: subnet(s)=%s '
                         'port(s)=%s range=%s, scan_type=%s ',
                         self.net_defs, self.ports, range_txt, self.scan_type)

        try:
            open_hosts = []

            if self.no_threads:
                scan_results = self.scan_subnets()
            else:
                scan_results = self.scan_subnets_threaded()

            if scan_results is not None:
                open_hosts.extend(sorted(scan_results))

        except KeyboardInterrupt:
            # Used in case the  user press "Ctrl+C", it will show the
            # following error instead of a python scary error
            print("\nCtrl+C. Exiting with no output.")
            sys.exit(1)

        self.total_sweep_time = time.time() - start_time

        return(open_hosts)
