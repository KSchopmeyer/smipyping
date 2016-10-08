#!/usr/bin/env python

"""
    TODO
"""

from __future__ import print_function, absolute_import
import sys
import traceback
import logging
import argparse as _argparse
from collections import namedtuple
from terminaltables import SingleTable

from pywbem import WBEMConnection, WBEMServer, ValueMapping, Error, \
                   ConnectionError, TimeoutError
from _cliutils import SmartFormatter as _SmartFormatter
from _cliutils import check_negative_int
from userdata import CsvUserData
from functiontimeout import FunctionTimeoutError, functiontimeout

class smiWBEMServer(WBEMServer):
    pass


# named tuple for the info about opened servers.
server_info_tuple = namedtuple('server_info_tuple',
                               ['url', 'server', 'entry', 'status'])
logger = None
# @functiontimeout(45)
def explore_server(server_url, principal, credential, args):
    """ Explors a cim server for characteristics defined by
        the server class including namespaces, brand, version, etc. info.
    """

    if args.verbose:
        print("WBEM server:  %s, principal=%s, credential=%s" % (server_url,
                                                                 principal,
                                                                 credential))

    conn = WBEMConnection(server_url, (principal, credential),
                          no_verification=True, timeout=20)

    server = WBEMServer(conn)

    if args.verbose:
        print('Brand:%s, Version:%s, Interop namespace:%s' % (server.brand,
                                                              server.version,
                                                              server.interop_ns))
        print("All namespaces: %s" % server.namespaces)
    else:
        # force access to test server connection
        _ = server.interop_ns

    return server

def smi_version(server, args):
    """
    Get the smi version used by this server from the SNIA profile information
    on the server
    """

    global logger
    org_vm = ValueMapping.for_property(server, server.interop_ns,
                                       'CIM_RegisteredProfile',
                                       'RegisteredOrganization')
    snia_server_profiles = server.get_selected_profiles('SNIA', 'SMI-S')
    versions = []
    for inst in snia_server_profiles:
        org = org_vm.tovalues(inst['RegisteredOrganization'])
        name = inst['RegisteredName']
        vers = inst['RegisteredVersion']
        ####print("  %s %s Profile %s" % (org, name, vers))
        versions.append(vers)
    return versions

def explore_server_profiles(server, args, short_explore=True):

    global logger

    def print_profile_info(org_vm, inst):
        """Print the registered org, name, version for the profile defined by
           inst
        """
        org = org_vm.tovalues(inst['RegisteredOrganization'])
        name = inst['RegisteredName']
        vers = inst['RegisteredVersion']
        if args.verbose:
            print("  %s %s Profile %s" % (org, name, vers))

    #logger.info("Advertised management profiles:")
    org_vm = ValueMapping.for_property(server, server.interop_ns,
                                       'CIM_RegisteredProfile',
                                       'RegisteredOrganization')
    #for inst in server.profiles:
    #    print_profile_info(org_vm, inst)

    if short_explore:
        return server

    indication_profiles = server.get_selected_profiles('DMTF', 'Indications')

    logger.info('Profiles for DMTF:Indications')
    for inst in indication_profiles:
        print_profile_info(org_vm, inst)

    server_profiles = server.get_selected_profiles('SNIA')

    logger.info('SNIA Profiles:')
    for inst in server_profiles:
        print_profile_info(org_vm, inst)

    # get Central Instances
    for inst in indication_profiles:
        org = org_vm.tovalues(inst['RegisteredOrganization'])
        name = inst['RegisteredName']
        vers = inst['RegisteredVersion']
        logger.info("Central instances for profile %s:%s:%s (component):",
                    org, name, vers)
        try:
            ci_paths = server.get_central_instances(
                inst.path,
                "CIM_IndicationService", "CIM_System", ["CIM_HostedService"])
        except Exception as exc:
            logger.error("Error: Central Instances%s", str(exc))
            ci_paths = []
        for ip in ci_paths:
            logger.error("  %s", str(ip))

    for inst in server_profiles:
        org = org_vm.tovalues(inst['RegisteredOrganization'])
        name = inst['RegisteredName']
        vers = inst['RegisteredVersion']
        logger.info("Central instances for profile %s:%s:%s(autonomous):",
                    org, name, vers)

        try:
            ci_paths = server.get_central_instances(inst.path)
        except Exception as exc:
            print("Exception: %s" % str(exc))
            ci_paths = []
        for ip in ci_paths:
            logger.info("  %s", str(ip))
    return server

def create_parser(prog):
    """Create the cmd line parser for the explore functions"""
    
    usage = '%(prog)s [options] server'
    desc = 'Sweep possible WBEMServer ports across a range of IP addresses.'
    epilog = """
Examples:
  %s 10.1.134.25
  %s 10.1.134
  %s TODO entry_id list or nothing or all.

""" % (prog, prog, prog)

    argparser = _argparse.ArgumentParser(
        prog=prog, usage=usage, description=desc, epilog=epilog,
        formatter_class=_SmartFormatter)

    pos_arggroup = argparser.add_argument_group(
        'Positional arguments')
    pos_arggroup.add_argument(
        'wbemserver', metavar='server', nargs='?',
        help='Optional ip addresss of wbem servers to explore schema:address:')

    general_arggroup = argparser.add_argument_group(
        'General options')
    general_arggroup.add_argument(
        '--csvfile', '-c', default='userdata_example.csv',
        help='Use csv input file')
    general_arggroup.add_argument(
        '--verbose', '-v', action='store_true', default=False,
        help='Verbosity level')
    general_arggroup.add_argument(
        '--debug', '-d', action='store_true',
        help='Display detailed connection information')

    return argparser

def main():
    prog = "explore"  # Name of the script file invoking this module

    argparser = create_parser(prog)

    args = argparser.parse_args()

    if args.verbose:
        print('args %s' % args)

        #logging.basicConfig(stream=sys.stderr, level=logging.INFO,
                        #format='%(asctime)s %(levelname)s %(message)s)')

    global logger
    logger = logging.getLogger('Explore')
    hdlr = logging.FileHandler('explore.log')
    ##formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)     
    logger.addHandler(ch)
    
    filtered_hosts = []

    #####print('args %s' % args.wbemserver)
    
    user_data = CsvUserData(args.csvfile)
    hosts = user_data.get_hostid_list()
      
    # TODO make this list comprehension
    if args.wbemserver is not None:
        for host in hosts:
            if host == args.wbemserver:
                filtered_hosts.append(host)
        if len(filtered_hosts) == 0:
            print('Ip address %s not in data base' % args.wbemserver)
            sys.exit(1)
    else:
        filtered_hosts = hosts

    servers = []
    for host_addr in filtered_hosts:
        entry = user_data.get_dict_for_host(host_addr)
        if not entry:
            raise ValueError('Error with host %s getting from userdata' %
                             host_addr)

        url = '%s://%s' % (entry['Protocol'], entry['IPAddress'])
        credential = entry['Credential']
        principal = entry['Principal']

        logger.info('Open %s Company=%s'% (url, entry['CompanyName']))
        
        server = None
        try:
            server = explore_server(url, principal, credential, args)
            # TODO change to named tuple.
            s = [url, server, 'OK', entry]
            servers.append(s)

        except FunctionTimeoutError as fte:

            logger.error('Timeout decorator exception:%s company %s'%
                         (url, entry['CompanyName']))
            err = 'FunctTo'
            servers.append([url, server, '  FunctTo', entry])
            traceback.format_exc()

        except ConnectionError as ce:
            logger.error('ConnectionError exception:%s company %s'%
                         (url, entry['CompanyName']))
            err = 'ConnErr'
            servers.append([url, server, 'ConnErr', entry])
            traceback.format_exc()

        except TimeoutError as to:
            logger.error('Timeout Error exception:%s company %s'%
                         (url, entry['CompanyName']))

            err = 'Timeout'
            servers.append([url, server, 'Timeout', entry])
            traceback.format_exc()

        except Error as er:
            logger.error('PyWBEM Error exception:%s company %s'%
                         (url, entry['CompanyName']))
            err = 'PyWBMEr'
            servers.append([url, server, 'PyWBMErr', entry])
            traceback.format_exc()

        except Exception as ex:
            logger.error('General Error exception:%s company %s'%
                         (url, entry['CompanyName']))

            err = 'GenErr'
            servers.append([url, server, 'GenErr', entry])
            traceback.format_exc()

    # print results
    print_format = '%-20.20s %-11.11s %-15.15s %-8.8s %-12.12s %-6.6s'
    print(print_format % \
          ('Url', 'Brand', 'Company', 'Version', 'Interop_ns', 'Status'))
    print('==================================================================')
    for server_tuple in servers:
        url = server_tuple[0]
        server = server_tuple[1]
        entry = server_tuple[3]
        status = server_tuple[2]
        brand = ''
        version = ''
        interop_ns = ''
        if server is not None and status == 'OK':
            brand = server.brand
            version = server.version
            interop_ns = server.interop_ns

        print(
            '%-20.20s %-11.11s %-15.15s %-8.8s %-12.12s %-6.6s' % \
            (url, brand, entry['CompanyName'], version, interop_ns,
             server_tuple[2]))

    # repeat to get smi info.
    print('\n\n%-20.20s %-15.15s %-15.15s %s' % (
          'Url', 'Brand', 'Company', 'SMI Profiles'))
    print('==================================================================')
    for server_tuple in servers:
        if server_tuple[2] == 'OK':
            entry = server_tuple[3]
            try:
                versions = smi_version(server_tuple[1], args)
            except Exception as ex:
                print('Exception in smi_versions %s' % server_tuple)
                continue
            if versions is not None:
                print('%-20.20s %-15.15s %-15.15s %s' % \
                      (s[0],entry['CompanyName'], entry['Product'], \
                       ", ". join(versions)))

    return 0

if __name__ == '__main__':
    sys.exit(main())
