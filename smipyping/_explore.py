#!/usr/bin/env python

"""
    SMIWBEMServer class extends WBEMServer class
"""

from __future__ import print_function, absolute_import

import os
import sys as _sys
import traceback
import logging
import time
import argparse as _argparse
from collections import namedtuple
from urlparse import urlparse

from pywbem import WBEMConnection, WBEMServer, ValueMapping, Error, \
    ConnectionError, TimeoutError
from ._cliutils import SmartFormatter as _SmartFormatter
# TODO from ._cliutils import check_negative_int
from ._targetdata import TargetsData
from ._functiontimeout import FunctionTimeoutError
from ._terminaltable import print_terminal_table, fold_cell
from ._ping import ping_host
from .config import DEFAULT_CONFIG_FILE, PING_TIMEOUT

__all__ = ['Explorer', ]


# named tuple for information about opened servers.
ServerInfoTuple = namedtuple('ServerInfoTuple',
                             ['url', 'server', 'target_id', 'status', 'time'])


class Explorer(object):

    def __init__(self, prog, logfile=None,debug=None, ping=None, verbose=None,
                 target_data=None):
        """Initialize instance attributes."""

        self.debug = debug
        self.verbose = verbose
        self.ping = ping
        self.target_data = target_data
        self.timeout = None
        self.prog = prog
        self.logfile = logfile
        self.create_logger(self.prog, self.logfile)

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
                    versions = smi_version(server_tuple.server)
                except Exception as ex:
                    print('Exception %s in smi_versions %s' % (ex, server_tuple))
                    continue

                line = [entry['TargetID'],
                        server_tuple.url,
                        entry['CompanyName'],
                        entry['Product']]
                if versions is not None:
                    cell_str = ", ". join(sorted(versions))
                    line.append(fold_cell(cell_str, 14))
                table_data.append(line)
        print_terminal_table("Display SMI Profile Information", table_data)

    def print_server_info(self, servers, user_data):
        """ Display a table of info from the server scan
        """

        table_data = []
        tbl_hdr = ['Id', 'Url', 'Brand', 'Company', 'Vers', 'Interop_ns',
                   'Status', 'time']
        table_data.append(tbl_hdr)
        for server_tuple in servers:
            url = server_tuple.url
            server = server_tuple.server
            status = server_tuple.status
            target_id = server_tuple.target_id
            entry = user_data.get_dict_record(target_id)
            brand = ''
            version = ''
            interop_ns = ''
            if server is not None and status == 'OK':
                brand = server.brand
                version = server.version
                interop_ns = server.interop_ns
            disp_time = None
            if server_tuple.time <= 60:
                disp_time = "%.2f s" % (round(server_tuple.time, 1))
            else:
                disp_time = "%.2f m" % (server_tuple.time / 60)
            line = [target_id,
                    url,
                    brand,
                    entry['CompanyName'],
                    version,
                    interop_ns,
                    server_tuple.status,
                    disp_time]

            table_data.append(line)

        print_terminal_table("Server Basic Information", table_data)

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
        servers = []
        # #### TODO move this all back to IDs and stop mapping host to id.
        for target_id in target_list:
            target = target_data[target_id]

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
            if target_data.disabled_target(target):
                s = ServerInfoTuple(url=url, server=None, status='DISABLE',
                                    target_id=target_id, time=0)
                servers.append(s)
                logger.info('Disabled %s ' % (log_info))

            else:
                if self.ping:
                    start_time = time.time()   # Scan start time
                    ping_result = self.ping_server(url, self.verbose)
                    if ping_result is False:
                        cmd_time = time.time() - start_time
                        s = ServerInfoTuple(url=url, server=None,
                                            status='PING_FAIL',
                                            target_id=target_id, time=cmd_time)
                        servers.append(s)
                        continue
                svr_tuple = explore_server(url, target, principal, credential,
                                           args, logger)
                servers.append(svr_tuple)

        return servers

    def explore_server(self, url, target, principal, credential):
        """ Explore a cim server for characteristics defined by
            the server class including namespaces, brand, version, etc. info.

            Return: The ServerInfoTuple object
        """
        credential = target['Credential']
        principal = target['Principal']
        log_info = 'id=%s Url=%s Product=%s Company=%s' \
                % (target['TargetID'], url,
                   target['Product'],
                   target['CompanyName'])

        if self.verbose:
            print("WBEM server:  %s, principal=%s, credential=%s"
                  % (url, principal, credential))
        cmd_time = 0
        start_time = time.time()   # Scan start time
        try:
            self.logger.info('Open %s' % log_info)
            # start_time = time.time()   # Scan start time
            conn = WBEMConnection(url, (principal, credential),
                                  no_verification=True, timeout=20)
            server = WBEMServer(conn)

            # Access the server since the creation of the connection and
            # server constructors do not actually contact the WBEM server
            if args.verbose:
                print('Brand:%s, Version:%s, Interop namespace:%s' %
                      (server.brand, server.version, server.interop_ns))
                print("All namespaces: %s" % server.namespaces)
            else:
                # force access to test server connection
                _ = server.interop_ns  # noqa: F841

            cmd_time = time.time() - start_time
            svr_tuple = ServerInfoTuple(url=url, server=server,
                                        target_id=target_id, status='OK',
                                        time=cmd_time)
            self.logger.info('OK %s time %s' % (log_info, cmd_time))
        except FunctionTimeoutError as fte:
            cmd_time = time.time() - start_time
            self.logger.error('Timeout decorator exception:%s %s time %s' %
                         (fte, log_info, cmd_time))
            err = 'FunctTo'
            svr_tuple = ServerInfoTuple(url, server, target_id, err, cmd_time)
            traceback.format_exc()

        except ConnectionError as ce:
            cmd_time = time.time() - start_time
            self.logger.error('ConnectionError exception:%s %s time %s' %
                         (ce, log_info, cmd_time))
            err = 'ConnErr'
            svr_tuple = ServerInfoTuple(url, server, target_id, err, cmd_time)
            traceback.format_exc()

        except TimeoutError as to:
            cmd_time = time.time() - start_time
            self.logger.error('Timeout Error exception:%s %s,'
                         ' time %s' % (to, log_info, cmd_time))

            err = 'Timeout'
            svr_tuple = ServerInfoTuple(url, server, target_id, err, cmd_time)
            traceback.format_exc()

        except Error as er:
            cmd_time = time.time() - start_time
            self.logger.error('PyWBEM Error exception:%s %s time %s' %
                         (er, log_info, cmd_time))
            err = 'PyWBMEr'
            svr_tuple = ServerInfoTuple(url, server, target_id, err, cmd_time)
            traceback.format_exc()

        except Exception as ex:
            cmd_time = time.time() - start_time
            self.logger.error('General Error: exception:%s %s time %s' %
                         (ex, log_info, cmd_time))

            err = 'GenErr'
            svr_tuple = ServerInfoTuple(url, server, target_id, err, cmd_time)
            traceback.format_exc()

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
        Get the smi version used by this server from the SNIA profile information
        on the server
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
            # ###print("  %s %s Profile %s" % (org, name, vers))
            versions.append(vers)
        return versions

    def explore_server_profiles(self, server, args, short_explore=True):

        def print_profile_info(org_vm, inst):
            """Print the registered org, name, version for the profile defined by
               inst
            """
            org = org_vm.tovalues(inst['RegisteredOrganization'])
            name = inst['RegisteredName']
            vers = inst['RegisteredVersion']
            if args.verbose:
                print("  %s %s Profile %s" % (org, name, vers))

        # ##logger.info("Advertised management profiles:")
        org_vm = ValueMapping.for_property(server, server.interop_ns,
                                           'CIM_RegisteredProfile',
                                           'RegisteredOrganization')
        # for inst in server.profiles:
        #    print_profile_info(org_vm, inst)

        if short_explore:
            return server

        indication_profiles = server.get_selected_profiles('DMTF', 'Indications')

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
                    "CIM_IndicationService", "CIM_System", ["CIM_HostedService"])
            except Exception as exc:
                self.logger.error("Error: Central Instances%s", str(exc))
                ci_paths = []
            for ip in ci_paths:
                self.logger.error("  %s", str(ip))

        for inst in server_profiles:
            org = org_vm.tovalues(inst['RegisteredOrganization'])
            name = inst['RegisteredName']
            vers = inst['RegisteredVersion']
            self.logger.info("Central instances for profile %s:%s:%s(autonomous):",
                        org, name, vers)

            try:
                ci_paths = server.get_central_instances(inst.path)
            except Exception as exc:
                print("Exception: %s" % str(exc))
                ci_paths = []
            for ip in ci_paths:
                logger.info("  %s", str(ip))
        return server


    def create_logger(prog, logfile):
        """ Build logger instance"""

        # logging.basicConfig(stream=sys.stderr, level=logging.INFO,
        # format='%(asctime)s %(levelname)s %(message)s)')

        self.logger = logging.getLogger(prog)
        hdlr = logging.FileHandler(logfile)
        # formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
        logger.setLevel(logging.INFO)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)


def create_explore_parser(prog):
    """Create the cmd line parser for the explore functions"""

    usage = '%(prog)s [options] server'
    desc = 'Explore WBEM servers in the defined database for general ' \
           'information about each server.'
    epilog = """
Examples:
  %s -u 10.1.134.25
  %s -T 4
  %s        # explores all servers in the base

""" % (prog, prog, prog)

    argparser = _argparse.ArgumentParser(
        prog=prog, usage=usage, description=desc, epilog=epilog,
        formatter_class=_SmartFormatter)

    pos_arggroup = argparser.add_argument_group(
        'Positional arguments')

    server_arggroup = argparser.add_argument_group(
        'Server related options',
        'Specify the server either by host address or database targetID')
    pos_arggroup.add_argument(
        '-u', '--uri', metavar='URI', nargs='?',
        help='Optional host name or ip address of wbem servers to explore '
             'schema:address:')
    server_arggroup.add_argument(
        '-T', '--target_id', dest='target_id',
        metavar='TargetId',
        type=int,
        help='R|If this argument is set, the value is a user id\n'
             'instead of an server url as the source for the test. In\n'
             'this case, namespace, user, and password arguments are\n'
             'derived from the user data rather than cli input')
    server_arggroup.add_argument(
        '-t', '--timeout', dest='timeout', metavar='timeout', type=int,
        default=20,
        help='R|Timeout of the completion of WBEM Server operation\n'
             'in seconds(integer between 0 and 300).\n'
             'Default: 20 seconds')

    general_arggroup = argparser.add_argument_group(
        'General options')
    argparser.add_argument(
        '-f', '--config_file', metavar='CONFIG_FILE',
        default=DEFAULT_CONFIG_FILE,
        help=('Configuration file to use for config information. '
              'Default=%s' % DEFAULT_CONFIG_FILE))
    general_arggroup.add_argument(
        '--no_ping', '-n', action='store_true', default=False,
        help='R|Do not ping for server as first test. Executing the\n'
             'ping often shortens the total response time.')
    general_arggroup.add_argument(
        '--verbose', '-v', action='store_true', default=False,
        help='Verbosity level')
    general_arggroup.add_argument(
        '--debug', '-d', action='store_true',
        help='Display detailed connection information')

    return argparser


def main(prog):
    """ Main call during test. Creates logger, executes explore and
        table generate
    """


    argparser = create_explore_parser(prog)
    args = argparser.parse_args()

    if args.verbose:
        print('args %s' % args)

    # logfile = '%s.log' % prog
    # logger = create_explore_logger(prog, logfile)

    target_data = TargetsData.factory(args.config_file, 'csv', args.verbose)

    # create list of valid hosts and filter by wbemserver arg.
    hosts = target_data.get_hostid_list()

    filtered_hosts = []

    # TODO make this list comprehension
    if args.wbemserver is not None:
        for host in hosts:
            if host == args.wbemserver:
                filtered_hosts.append(host)
        if len(filtered_hosts) == 0:
            raise ValueError('Ip address %s not in data base' % args.wbemserver)
    else:
        filtered_hosts = hosts

    targets = []
    for host in filtered_hosts:
        targets.append()

    # Now map hosts back to target_ids.

    ping = False if args.no_ping else True

    explore = explorer(prog, logfile, target_data, target_list=targets,
                       verbose=verbose, ping=ping, args=args,
                       debug=debug)

    servers = explore.explore_servers(target_list=targets)

    # print results
    explore.print_server_info(servers, target_data)

    # repeat to get smi info.

    explore.print_smi_profile_info(servers, target_data)

    return 0


if __name__ == '__main__':
    prog_name = os.path.basename(_sys.argv[0])
    _sys.exit(main(prog_name))
