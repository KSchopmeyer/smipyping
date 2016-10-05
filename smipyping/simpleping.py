#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Provides the components for a simple utility to test a single
    wbem server against fixed information.  This includes
    the cmd line parser, and funcitons to test the connection.Returns
    exit code of 0 if the server is found and the defined class exists.

    Otherwise returns exit code 1.

    This module is the components of the tool. It is assembled in a separate
    script
"""

from __future__ import print_function, absolute_import

import sys as _sys
import logging
import argparse as _argparse
import re
from textwrap import fill

from pywbem import WBEMConnection, Error, \
                   ConnectionError, TimeoutError, CIMError
from ._cliutils import SmartFormatter as _SmartFormatter

TEST_CLASS = 'CIM_ComputerSystem'


def get_connection_info(conn):
    """Return a string with the connection info."""

    info = 'Connection: %s,' % conn.url
    if conn.creds is not None:
        info += ' userid=%s,' % conn.creds[0]
    else:
        info += ' no creds,'

    info += ' cacerts=%s,' % ('sys-default' if conn.ca_certs is None \
                                            else conn.ca_certs)

    info += ' verifycert=%s,' % ('off' if conn.no_verification else 'on')

    info += ' default-namespace=%s' % conn.default_namespace
    if conn.x509 is not None:
        info += ', client-cert=%s' % conn.x509['cert_file']
        try:
            kf = conn.x509['key_file']
        except KeyError:
            kf = "none"
        info += ":%s" % kf

    if conn.timeout is not None:
        info += ', timeout=%s' % conn.timeout

    return fill(info, 78, subsequent_indent='    ')

def connect(server, opts, argparser_):
    """
    Build connection parameters and issue WBEMConnection to the
    WBEMServer defined by the input options.

    returns completed connection
    """

    if server[0] == '/':
        url = server

    elif re.match(r"^https{0,1}://", server) is not None:
        url = server

    elif re.match(r"^[a-zA-Z0-9]+://", server) is not None:
        argparser_.error('Invalid scheme on server argument.' \
                        ' Use "http" or "https"')

    else:
        url = '%s://%s' % ('https', server)

    creds = None

    #if opts.user is not None and opts.password is None:
        #opts.password = _getpass.getpass('Enter password for %s: ' \
                                        #% opts.user)

    if opts.user is not None or opts.password is not None:
        creds = (opts.user, opts.password)

    if opts.timeout is not None:
        if opts.timeout < 0 or opts.timeout > 300:
            argparser_.error('timeout option(%s) out of range' % opts.timeout)

    conn = WBEMConnection(url, creds, default_namespace=opts.namespace,
                          no_verification=not opts.verify_cert,
                          timeout=opts.timeout)

    conn.debug = opts.debug

    if opts.verbose:
        print(get_connection_info(conn))

    return conn


def test_server(conn, opts):
    """
    Issue the test operation. Returns with system exit code.
    """
    try:
        insts = conn.EnumerateInstances(TEST_CLASS)

        if opts.verbose:
            print('Successful host=%s. Returned %s instance(s)' % (conn.url,
                                                                   len(insts)))
        rtn_code = 0

    except CIMError as ce:
        rtn_code = 1
        if opts.verbose:
            print('Operation Failed: CIMError %s '% ce)
    except TimeoutError as to:
        rtn_code = 4
        if opts.verbose:
            print('Operation Failed: CTimeout %s '% to)
    except Error as er:
        if opts.verbose:
            print('PyWBEM Error %s' % er)
        rtn_code = 2
    except Exception as ex:
        print('General Error %s' % ex)
        rtn_code = 3

    if opts.debug:
        last_request = conn.last_request or conn.last_raw_request
        print('Request:\n\n%s\n' % last_request)
        last_reply = conn.last_reply or conn.last_raw_reply
        print('Reply:\n\n%s\n' % last_reply)

    return rtn_code

def create_parser(prog):
    """
    Create the parser to parse cmd line arguments
    """

    usage = '%(prog)s [options] server'
    desc = 'Provide an interactive shell for issuing operations against' \
           ' a WBEM server.'
    epilog = """
Examples:
  %s https://localhost:15345 -n interop -u sheldon -p penny
          - (https localhost, port=15345, namespace=i user=sheldon
         password=penny)

  %s http://[2001:db8::1234-eth0] -(http port 5988 ipv6, zone id eth0)
""" % (prog, prog)

    argparser = _argparse.ArgumentParser(
        prog=prog, usage=usage, description=desc, epilog=epilog,
        add_help=False, formatter_class=_SmartFormatter)

    pos_arggroup = argparser.add_argument_group(
        'Positional arguments')
    pos_arggroup.add_argument(
        'server', metavar='server', nargs='?',
        help='R|Host name or url of the WBEM server in this format:\n' \
             '    [{scheme}://]{host}[:{port}]\n' \
             '- scheme: Defines the protocol to use;\n'  \
             '    - "https" for HTTPs protocol\n'    \
             '    - "http" for HTTP protocol.\n' \
             '  Default: "https".\n' \
             '- host: Defines host name as follows:\n' \
             '     - short or fully qualified DNS hostname,\n' \
             '     - literal IPV4 address(dotted)\n' \
             '     - literal IPV6 address (RFC 3986) with zone\n' \
             '       identifier extensions(RFC 6874)\n' \
             '       supporting "-" or %%25 for the delimiter.\n' \
             '- port: Defines the WBEM server port to be used\n' \
             '  Defaults:\n' \
             '     - HTTP  - 5988\n' \
             '     - HTTPS - 5989\n')

    server_arggroup = argparser.add_argument_group(
        'Server related options',
        'Specify the WBEM server namespace and timeout')
    server_arggroup.add_argument(
        '-n', '--namespace', dest='namespace', metavar='namespace',
        default='interop',
        help='R|Default namespace in the WBEM server for operation\n' \
             'requests when namespace option not supplied with\n' \
             'operation request.\n'
             'Default: %(default)s')
    server_arggroup.add_argument(
        '-t', '--timeout', dest='timeout', metavar='timeout', type=int,
        default=20,
        help='R|Timeout of the completion of WBEM Server operation\n' \
             'in seconds(integer between 0 and 300).\n' \
             'Default: 20 seconds')

    security_arggroup = argparser.add_argument_group(
        'Connection security related options',
        'Specify user name and password or certificates and keys')
    security_arggroup.add_argument(
        '-u', '--user', dest='user', metavar='user',
        help='R|User name for authenticating with the WBEM server.\n' \
             'Default: No user name.')
    security_arggroup.add_argument(
        '-p', '--password', dest='password', metavar='password', \
        help='R|Password for authenticating with the WBEM server.\n' \
             'Default: Will be prompted for, if user name\nspecified.')
    security_arggroup.add_argument(
        '-V', '--verify-cert', dest='verify_cert',
        action='store_true',
        help='Client will verify certificate returned by the WBEM' \
             ' server (see cacerts). This forces the client-side' \
             ' verification of the server identity, Normally it would' \
             ' be important to verify the server certificate but in the smi' \
             ' test environment where certificates are largely unknown' \
             ' the default is to not verify.')
    security_arggroup.add_argument(
        '--cacerts', dest='ca_certs', metavar='cacerts',
        help='R|File or directory containing certificates that will be\n' \
             'matched against a certificate received from the WBEM\n' \
             'server. Set the --no-verify-cert option to bypass\n' \
             'client verification of the WBEM server certificate.\n')
             # 'Default: Searches for matching certificates in the\n' \
             # 'following system directories:\n'
             # + ("\n".join("%s" % p for p in get_default_ca_cert_paths())))

    security_arggroup.add_argument(
        '--certfile', dest='cert_file', metavar='certfile',
        help='R|Client certificate file for authenticating with the\n' \
             'WBEM server. If option specified the client attempts\n' \
             'to execute mutual authentication.\n'
             'Default: Simple authentication.')
    security_arggroup.add_argument(
        '--keyfile', dest='key_file', metavar='keyfile',
        help='R|Client private key file for authenticating with the\n' \
             'WBEM server. Not required if private key is part of the\n' \
             'certfile option. Not allowed if no certfile option.\n' \
             'Default: No client key file. Client private key should\n' \
             'then be part  of the certfile')

    general_arggroup = argparser.add_argument_group(
        'General options')
    general_arggroup.add_argument(
        '-v', '--verbose', dest='verbose',
        action='store_true', default=False,
        help='Print more messages while processing')
    general_arggroup.add_argument(
        '-d', '--debug', dest='debug',
        action='store_true', default=False,
        help='Display XML for request and response')
    general_arggroup.add_argument(
        '-h', '--help', action='help',
        help='Show this help message and exit')

    return argparser

def parse_cmdline(argparser_):
    """ Parse the command line.  This test for any required args"""
    
    opts = argparser_.parse_args()
    
    if not opts.server:
        argparser_.error('No WBEM server specified')
        return None
    return opts
    
# TODO remove all of the following
#def main():
    #""" Main function executes the test.
        #TODO. Remove this completely to use the script code
    #"""

    #prog = "simpleping"  # Name of the script file invoking this module

    #argparser_ = create_parser(prog)
    
    #opts = argparser_.parse_args()

    #opts = parse_cmdline(argparser_)

    #conn = connect(opts.server, opts, argparser_)

    #rtn_code = test_server(conn, opts)

    #return rtn_code


#if __name__ == '__main__':
    #_sys.exit(main())
