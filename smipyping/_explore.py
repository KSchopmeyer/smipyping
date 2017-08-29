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
    Defines an explorer that does a general inspection of wbem servers
    to determine information like namespace, etc.
"""

from __future__ import print_function, absolute_import

import traceback
import time
from collections import namedtuple
from urlparse import urlparse
import threading

from pywbem import WBEMConnection, WBEMServer, ValueMapping, Error, \
    ConnectionError, TimeoutError, AuthError
from ._tableoutput import TableFormatter
from ._ping import ping_host
from .config import PING_TIMEOUT, DEFAULT_USERNAME, DEFAULT_PASSWORD
from ._logging import EXPLORE_LOGGER_NAME, get_logger, SmiPypingLoggers

__all__ = ['Explorer', ]


# named tuple for information about opened servers.
ServerInfoTuple = namedtuple('ServerInfoTuple',
                             ['url', 'server', 'target_id', 'status', 'time'])


RESULTS = []


class Explorer(object):
    """
    The Explorer class provides a general capability to explore providers
    defined in a database including getting information on server branding,
    namespaces, interop namespaces, profiles, etc.

    It is designed to explore a number of servers and provide a report of
    the results with logging to capture information on each individual
    WBEM Server
    """

    def __init__(self, prog, target_data, logfile=None, log_level=None,
                 debug=None, ping=None, verbose=None, threaded=False,
                 output_format='simple'):
        """Initialize instance attributes."""
        self.verbose = verbose
        self.ping = ping
        self.target_data = target_data
        self.timeout = None
        self.prog = prog
        self.debug = debug
        self.threaded = threaded
        self.explore_time = None
        self.output_format = output_format
        log_dest = 'file' if log_level else None
        SmiPypingLoggers.create_logger(log_component='explore',
                                       log_dest=log_dest,
                                       log_filename=logfile,
                                       log_level=log_level)
        self.logger = get_logger(EXPLORE_LOGGER_NAME)

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
                entry = user_data.get_target(target_id)
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
                    line.append(TableFormatter.fold_cell(cell_str, 14))
                table_data.append(line)
        table = TableFormatter(table_data, headers=table_hdr,
                               title='Display SMI Profile Information',
                               table_format=self.output_format)
        table.print_table()

    def report_server_info(self, servers, target_data, table_format='table',
                           columns=None, report='full'):
        """ Display a table of info from the server scan
        """

        rows = []
        if report == 'full':
            headers = ['Id', 'Url', 'Company', 'Product', 'Vers',
                       'SMI Profiles', 'Interop_ns', 'Status', 'time']
        else:
            headers = ['Id', 'Url', 'Company', 'Product',
                       'Status', 'time']
        servers.sort(key=lambda tup: int(tup.target_id))
        for server_tuple in servers:
            url = server_tuple.url
            server = server_tuple.server
            status = server_tuple.status
            target_id = server_tuple.target_id
            target = target_data.get_target(target_id)
            version = ''
            interop_ns = ''
            smi_profiles = ''
            if server is not None and status == 'OK':
                version = server.version
                interop_ns = server.interop_ns
                smi_profile_list = self.smi_version(server_tuple.server)
                if smi_profile_list is not None:
                    cell_str = ", ". join(sorted(smi_profile_list))
                    smi_profiles = (TableFormatter.fold_cell(cell_str, 14))
            disp_time = None
            if server_tuple.time <= 60:
                disp_time = "%.2fs" % (round(server_tuple.time, 1))
            else:
                disp_time = "%.2fm" % (server_tuple.time / 60)
            row = []
            if 'Id' in headers:
                row.append(target_id)
            if 'Url' in headers:
                row.append(url)
            if 'Company' in headers:
                row.append(TableFormatter.fold_cell(target['CompanyName'], 11),)
            if 'Product' in headers:
                row.append(TableFormatter.fold_cell(target['Product'], 8),)
            if 'Vers' in headers:
                row.append(version)
            if 'SMI Profiles' in headers:
                row.append(smi_profiles)
            if 'Interop_ns' in headers:
                row.append(interop_ns)
            if 'Status' in headers:
                row.append(server_tuple.status)
            if 'time' in headers:
                row.append(disp_time)

            rows.append(row)

        table = TableFormatter(rows, headers=headers,
                               title='Server Explorer Report:',
                               table_format=self.output_format)
        table.print_table()

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

        principal = target.get('Principal', DEFAULT_USERNAME)
        credential = target.get('Credential', DEFAULT_PASSWORD)

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
            self.logger.error('Pywbem Client Timeout Error exception:%s %s '
                              'time %.2f s', to, log_info, cmd_time)

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

        except AuthError as ae:
            cmd_time = time.time() - start_time
            self.logger.error('PyWBEM AuthEr exception:%s %s time %.2f s',
                              ae, log_info, cmd_time)
            err = 'AuthErr'
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
