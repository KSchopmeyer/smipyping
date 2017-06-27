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
    SMIWBEMServer class extends WBEMServer class
"""

from __future__ import print_function, absolute_import

import traceback
import logging
import time
from collections import namedtuple
from urlparse import urlparse
import threading

from pywbem import WBEMConnection, WBEMServer, ValueMapping, Error, \
    ConnectionError, TimeoutError
from ._asciitable import print_ascii_table, fold_cell
from ._csvtable import write_csv_table
from ._ping import ping_host
from .config import PING_TIMEOUT

__all__ = ['Explorer', ]


# named tuple for information about opened servers.
ServerInfoTuple = namedtuple('ServerInfoTuple',
                             ['url', 'server', 'target_id', 'status', 'time'])


RESULTS = []


class Explorer(object):

    def __init__(self, prog, target_data, logfile=None, debug=None, ping=None,
                 verbose=None, threaded=False):
        """Initialize instance attributes."""

        self.verbose = verbose
        self.ping = ping
        self.target_data = target_data
        self.timeout = None
        self.prog = prog
        self.logfile = logfile
        self.debug = debug
        self.threaded = threaded
        self.create_logger(self.prog, self.logfile)
        self.explore_time = None

    def print_smi_profile_info(self, servers, user_data):
        """
        Generates a table of smi profile information listing the smi profiles

        Parameters:

          servers: list of ServerInfoTuple entries
        """

        table_data = []
        table_hdr = [' Id', 'Url', 'Company', 'Product', 'SMI Profiles']
        table_data.append(table_hdr)
        for server_tuple in servers:
            if server_tuple.status == 'OK':
                target_id = server_tuple.target_id
                entry = user_data.get_dict_record(target_id)
                try:
                    versions = self.smi_version(server_tuple.server)
                except Exception as ex:
                    print('Exception %s in smi_versions %s' % (ex,
                                                               server_tuple))
                    continue

                line = [entry['TargetID'],
                        server_tuple.url,
                        entry['CompanyName'],
                        entry['Product']]
                if versions is not None:
                    cell_str = ", ". join(sorted(versions))
                    line.append(fold_cell(cell_str, 14))
                table_data.append(line)
        print_ascii_table("Display SMI Profile Information", table_hdr,
                          table_data)

    def report_server_info(self, servers, user_data, table_type='report'):
        """ Display a table of info from the server scan
        """

        table_data = []
        tbl_hdr = ['Id', 'Url', 'Brand', 'Company', 'Product', 'Vers',
                   'SMI Profiles', 'Interop_ns', 'Status', 'time']
        table_data.append(tbl_hdr)
        servers.sort(key=lambda tup: int(tup.target_id))
        for server_tuple in servers:
            url = server_tuple.url
            server = server_tuple.server
            status = server_tuple.status
            target_id = server_tuple.target_id
            entry = user_data.get_dict_record(target_id)
            brand = ''
            version = ''
            interop_ns = ''
            smi_profiles = ''
            if server is not None and status == 'OK':
                brand = server.brand
                version = server.version
                interop_ns = server.interop_ns
                smi_profile_list = self.smi_version(server_tuple.server)
                if smi_profile_list is not None:
                    cell_str = ", ". join(sorted(smi_profile_list))
                    smi_profiles = (fold_cell(cell_str, 14))
            disp_time = None
            if server_tuple.time <= 60:
                disp_time = "%.2f s" % (round(server_tuple.time, 1))
            else:
                disp_time = "%.2f m" % (server_tuple.time / 60)
            line = [target_id,
                    url,
                    brand,
                    entry['CompanyName'],
                    entry['Product'],
                    version,
                    smi_profiles,
                    interop_ns,
                    server_tuple.status,
                    disp_time]

            table_data.append(line)

        if table_type == 'report':
            print_ascii_table("Server Basic Information", table_data)
        elif table_type == 'csv':
            write_csv_table(table_data)
        else:
            TypeError('table type invalid %s' % table_type)

    def explore_servers(self, target_list):
        """
        Explore the basic characteristics of a list of servers including
        existence, branding, etc.

        Parameters:

          target_list - List of target_ids to explore

        Returns:
            List of namedtuple ServerInfoTuple representing the results of
            the explore
        """
        self.explore_time = time.time()
        if self.threaded:
            servers = self.explore_threaded(target_list)
        else:
            servers = self.explore_non_threaded(target_list)

        self.explore_time = time.time() - self.explore_time
        self.logger.info('Explore Threaded=%s time=%.2f s', self.threaded,
                         self.explore_time)
        return servers

    def explore_non_threaded(self, target_list):

        servers = []
        # #### TODO move this all back to IDs and stop mapping host to id.
        for target_id in target_list:
            target = self.target_data[target_id]

            # get variables for the connection and logs
            url = '%s://%s' % (target['Protocol'], target['IPAddress'])
            credential = target['Credential']
            principal = target['Principal']
            product = target['Product']
            company_name = target['CompanyName']
            log_info = 'id=%s Url=%s Product=%s Company=%s' % (target_id, url,
                                                               product,
                                                               company_name)

            # TODO too much swapping between entities.
            # TODO need a target class since this goes back to top dict to
            # get info
            if self.target_data.disabled_target(target):
                s = ServerInfoTuple(url=url, server=None, status='DISABLE',
                                    target_id=target_id, time=0)
                servers.append(s)
                self.logger.info('Disabled %s ', log_info)

            else:
                svr_tuple = self.explore_server(url, target, principal,
                                                credential)
                servers.append(svr_tuple)

        return servers

    def explore_threaded(self, target_list):
        """
        Threaded scan of IP Addresses for open ports.

        Scan the IP address defined by the input and return a list of open
        IP addresses. This function creates multiple processes and executes
        each call in a process for speed.
        """
        servers = []
        # #### TODO move this all back to IDs and stop mapping host to id.
        threads_ = []
        for target_id in target_list:
            target = self.target_data[target_id]

            # get variables for the connection and logs
            url = '%s://%s' % (target['Protocol'], target['IPAddress'])
            credential = target['Credential']
            principal = target['Principal']
            product = target['Product']
            company_name = target['CompanyName']
            log_info = 'id=%s Url=%s Product=%s Company=%s' % (target_id, url,
                                                               product,
                                                               company_name)

            # TODO too much swapping between entities.
            # TODO need a target class since this goes back to top dict to
            # get info
            if self.target_data.disabled_target(target):
                s = ServerInfoTuple(url=url, server=None, status='DISABLE',
                                    target_id=target_id, time=0)
                servers.append(s)
                self.logger.info('Disabled %s ', log_info)
            else:
                process = threading.Thread(target=self.explore_server,
                                           args=(url, target, principal,
                                                 credential))
                threads_.append(process)

        for process in threads_:
            process.start()

        for process in threads_:
            process.join()

        for result in RESULTS:
            servers.append(result)

        return servers

    def explore_server(self, url, target, principal, credential):
        """ Explore a cim server for characteristics defined by
            the server class including namespaces, brand, version, etc. info.

            Return: The ServerInfoTuple object
        """
        cmd_time = 0
        start_time = time.time()   # Scan start time
        target_id = target['TargetID']
        credential = target['Credential']
        principal = target['Principal']
        log_info = 'id=%s Url=%s Product=%s Company=%s' \
            % (target['TargetID'], url,
               target['Product'],
               target['CompanyName'])
        svr_tuple = None
        if self.ping:
            ping_result = self.ping_server(url, self.verbose)
            if ping_result is False:
                cmd_time = time.time() - start_time
                self.logger.error('PING_FAIL %s time %.2f s', log_info,
                                  cmd_time)
                svr_tuple = ServerInfoTuple(url=url, server=None,
                                            status='PING_FAIL',
                                            target_id=target_id,
                                            time=cmd_time)
                RESULTS.append(svr_tuple)
                return svr_tuple
        try:
            self.logger.info('Open %s', log_info)
            conn = WBEMConnection(url, (principal, credential),
                                  no_verification=True, timeout=20)
            server = WBEMServer(conn)

            # Access the server since the creation of the connection
            # and server constructors do not actually contact the
            # WBEM server
            if self.verbose:
                print('Brand:%s, Version:%s, Interop namespace:%s' %
                      (server.brand, server.version, server.interop_ns))
                print("All namespaces: %s" % server.namespaces)
            else:
                # force access to test server connection
                _ = server.interop_ns  # noqa: F841
                _ = server.profiles  # noqa: F841

            cmd_time = time.time() - start_time

            svr_tuple = ServerInfoTuple(url=url, server=server,
                                        target_id=target_id,
                                        status='OK',
                                        time=cmd_time)
            self.logger.info('OK %s time %.2f s', log_info, cmd_time)

        except ConnectionError as ce:
            cmd_time = time.time() - start_time
            self.logger.error('ConnectionError exception:%s %s time %.2f s',
                              ce, log_info, cmd_time)
            err = 'ConnErr'
            svr_tuple = ServerInfoTuple(url, server, target_id, err,
                                        cmd_time)
            traceback.format_exc()

        except TimeoutError as to:
            cmd_time = time.time() - start_time
            self.logger.error('Timeout Error exception:%s %s time %.2f s',
                              to, log_info, cmd_time)

            err = 'Timeout'
            svr_tuple = ServerInfoTuple(url, server, target_id, err,
                                        cmd_time)
            traceback.format_exc()

        except Error as er:
            cmd_time = time.time() - start_time
            self.logger.error('PyWBEM Error exception:%s %s time %.2f s',
                              er, log_info, cmd_time)
            err = 'PyWBMEr'
            svr_tuple = ServerInfoTuple(url, server, target_id, err,
                                        cmd_time)
            traceback.format_exc()

        except Exception as ex:
            cmd_time = time.time() - start_time
            self.logger.error('General Error: exception:%s %s time %.2f s',
                              ex, log_info, cmd_time)

            err = 'GenErr'
            svr_tuple = ServerInfoTuple(url, server, target_id, err,
                                        cmd_time)
            traceback.format_exc()

        RESULTS.append(svr_tuple)
        return svr_tuple

    def ping_server(self, url, verbose):
        """
        Get the netloc from the url and ping the server.

        Returns the result text that must match the defined texts.

        """
        netloc = urlparse(url).netloc
        target_address = netloc.split(':')
        result = ping_host(target_address[0], PING_TIMEOUT)
        if verbose:
            print('Ping host=%s, result=%s' % (target_address[0], result))
        return result

    def smi_version(self, server):
        """
        Get the smi version used by this server from the SNIA profile
        information on the server
        """

        org_vm = ValueMapping.for_property(server, server.interop_ns,
                                           'CIM_RegisteredProfile',
                                           'RegisteredOrganization')
        snia_server_profiles = server.get_selected_profiles('SNIA', 'SMI-S')
        versions = []
        for inst in snia_server_profiles:
            org = org_vm.tovalues(inst['RegisteredOrganization'])  # noqa: F841
            name = inst['RegisteredName']  # noqa: F841
            vers = inst['RegisteredVersion']
            versions.append(vers)
        return versions

    def explore_server_profiles(self, server, args, short_explore=True):

        def print_profile_info(org_vm, inst):
            """
            Print the registered org, name, version for the profile
            defined by inst
            """
            org = org_vm.tovalues(inst['RegisteredOrganization'])
            name = inst['RegisteredName']
            vers = inst['RegisteredVersion']
            if args.verbose:
                print("  %s %s Profile %s" % (org, name, vers))

        org_vm = ValueMapping.for_property(server, server.interop_ns,
                                           'CIM_RegisteredProfile',
                                           'RegisteredOrganization')

        if short_explore:
            return server

        indication_profiles = server.get_selected_profiles('DMTF',
                                                           'Indications')

        self.logger.info('Profiles for DMTF:Indications')
        for inst in indication_profiles:
            print_profile_info(org_vm, inst)

        server_profiles = server.get_selected_profiles('SNIA')

        self.logger.info('SNIA Profiles:')
        for inst in server_profiles:
            print_profile_info(org_vm, inst)

        # get Central Instances
        for inst in indication_profiles:
            org = org_vm.tovalues(inst['RegisteredOrganization'])
            name = inst['RegisteredName']
            vers = inst['RegisteredVersion']
            self.logger.info(
                "Central instances for profile %s:%s:%s (component):",
                org, name, vers)
            try:
                ci_paths = server.get_central_instances(
                    inst.path,
                    "CIM_IndicationService", "CIM_System",
                    ["CIM_HostedService"])
            except Exception as exc:
                self.logger.error("Error: Central Instances%s", str(exc))
                ci_paths = []
            for ip in ci_paths:
                self.logger.error("  %s", str(ip))

        for inst in server_profiles:
            org = org_vm.tovalues(inst['RegisteredOrganization'])
            name = inst['RegisteredName']
            vers = inst['RegisteredVersion']
            self.logger.info(
                "Central instances for profile %s:%s:%s(autonomous):",
                org, name, vers)

            try:
                ci_paths = server.get_central_instances(inst.path)
            except Exception as exc:
                print("Exception: %s" % str(exc))
                ci_paths = []
            for ip in ci_paths:
                self.logger.info("  %s", str(ip))
        return server

    def create_logger(self, prog, logfile):
        """ Build logger instance"""

        # logging.basicConfig(stream=sys.stderr, level=logging.INFO,
        # format='%(asctime)s %(levelname)s %(message)s)')

        if logfile:
            self.logger = logging.getLogger(prog)
            hdlr = logging.FileHandler(logfile)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            hdlr.setFormatter(formatter)
            self.logger.addHandler(hdlr)
            self.logger.setLevel(logging.INFO)

            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)
        else:
            self.logger = logging.getLogger(prog)
            hdlr = logging.NullHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            hdlr.setFormatter(formatter)
            self.logger.addHandler(hdlr)
            self.logger.setLevel(logging.INFO)

            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)
