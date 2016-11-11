#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Provides the components for a utility to test a WBEM server.

This tests a wbem server against a class defined in the configuration. If
that class is found, it returns success. Otherwise it returns a fail code.

This includes the cmd line parser, and funcitons to test the connection.
Returns exit code of 0 if the server is found and the defined class exists.

Otherwise returns exit code 1.

In addition, it returns an empty string if successful or a string with
error code if in error.

This module is the components of the tool. It is assembled in a separate
script
"""

from __future__ import print_function, absolute_import

import logging
import argparse as _argparse
import re
from textwrap import fill
import datetime

from pywbem import WBEMConnection, ConnectionError, Error, TimeoutError, \
    CIMError
from ._cliutils import SmartFormatter as _SmartFormatter

from .ping import ping_host

from .userdata import CsvUserData

from. config import USERDATA_FILE, PING_TEST_CLASS

class SmiCustomFormatter(_SmartFormatter,
                         _argparse.RawDescriptionHelpFormatter):
    """
    Define a custom Formatter to allow formatting help and epilog.

    argparse formatter specifically allows multipleinheritance for the
    formatter customization and actually recommends this in a discussion
    in one of the issues.

    http://bugs.python.org/issue13023

    Also recommended in a StackOverflow discussion:

    http://stackoverflow.com/questions/18462610/argumentparser-epilog-and-description-formatting-in-conjunction-with-argumentdef


    """

    pass

class SimplePing(object):
    """Simple ping class. Contains all functionality to handle simpleping"""
    def __init__(self, prog):
        self.conn = None
        self.prog = prog
        self.debug = False,
        self.verbose = False,
        self.ping = False
        self.argparser = None
        self.namespace = None
        self.namespace = None
        self.user = None
        self.credential = None
        self.url = None
        self.timeout = None
        self.server = None

    def get_connection_info(self, conn):
        """Return a string with the connection info."""
        info = 'Connection: %s,' % conn.url

        if conn.creds is not None:
            info += ' userid=%s,' % conn.creds[0]
        else:
            info += ' no creds,'

        info += ' cacerts=%s,' % ('sys-default' if conn.ca_certs is None
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

    def server_to_url(self, server):
        """
        Confirm that the server url is correct or fix it.

        Returns url including scheme and saves it in the class

        Exception: argparser Error if url scheme is invalid
        """
        if server[0] == '/':
            url = server

        elif re.match(r"^https{0,1}://", server) is not None:
            url = server

        elif re.match(r"^[a-zA-Z0-9]+://", server) is not None:
            self.argparser.error('Invalid scheme on server argument.'
                             ' Use "http" or "https"')

        else:
            url = '%s://%s' % ('https', server)

        self.url = url
        return url


    def connect_server(self, url, user=None, password=None,
                       timeout=None, verify_cert=False):
        """
        Build connection parameters and issue WBEMConnection to the WBEMServer.

        The server is defined by the input options.

        Returns completed connection or exception of connection fails
        """
        creds = None

        if self.user is not None or self.password is not None:
            creds = (user, password)

        conn = WBEMConnection(url, creds, default_namespace=self.namespace,
                              no_verification=not verify_cert,
                              timeout=self.timeout)

        conn.debug = self.debug

        if self.verbose:
            print(self.get_connection_info(conn))

        return conn

    def test_server(self, conn, ip_address,):
        """
        Issue the test operation. Returns with system exit code.

        Returns a tuple of code and reason text.  The code is ne 0 if there was
        an error.
        """
        start_time = datetime.datetime.now()
        ping_timeout = 2
        if self.ping:
            if not ping_host(ip_address, ping_timeout):
                end_time = datetime.datetime.now() - start_time
                return(6, 'Ping Failed', "", end_time)
        try:
            insts = conn.EnumerateInstances(PING_TEST_CLASS)

            if verbose:
                print('Success host=%s. Returned %s instance(s)' % (conn.url,
                                                                    len(insts)))
            rtn_code = (0, "Success", "")

        except CIMError as ce:
            rtn_code = (1, "CIMError", ce)
            if self.verbose:
                print('Operation Failed: CIMError %s ' % ce)

        except ConnectionError as co:
            rtn_code = (5, "ConnectionError", co)
            if self.verbose:
                print('Operation Failed: ConnectionError %s ' % co)
        except TimeoutError as to:
            rtn_code = (4, "TimeoutError", to)
            if self.verbose:
                print('Operation Failed: TimeoutError %s ' % to)
        except Error as er:
            if self.verbose:
                print('PyWBEM Error %s' % er)
            rtn_code = (2, "PyWBEM Error", er)
        except Exception as ex:
            print('General Error %s' % ex)
            rtn_code = (3, "General Error", ex)

        if self.debug:
            last_request = conn.last_request or conn.last_raw_request
            print('Request:\n\n%s\n' % last_request)
            last_reply = conn.last_reply or conn.last_raw_reply
            print('Reply:\n\n%s\n' % last_reply)

        end_time = datetime.datetime.now() - start_time
        # TODO this fails if we make it a tuple. not all args cvtd
        #      in the print function
        rtn_tuple = [rtn_code[0], rtn_code[1], rtn_code[2], str(end_time)]
        # print('rtn_tuple %s' % rtn_tuple)
        return rtn_tuple

    def create_parser(self):
        """Create the parser to parse cmd line arguments."""
        usage = '%(prog)s [options] server'
        desc = """
Interactive shell for doing a simple CIM ping against a WBEM server defined by
the input parameters. This script connects to the server and test for the
existence of a single class. If the  test fails it exists with non-zero exit
code. It includes an option to ping the server before connecting.

Return:
    Success: return code 0 with empty string
    Failure: return code 1 - 6 and outputs string with error text:
        1. CIMError
        2. PyWBEM Error
        3. General Error
        4. Timeout Error
        5. ConnectionError
        6. Ping error (only return if ping is executed)
    """
        epilog = """
Examples:\n
  %s https://localhost:15345 -n interop -u sheldon -p penny
          - (https localhost, port=15345, namespace=i user=sheldon
         password=penny)

  %s http://[2001:db8::1234-eth0] -(http port 5988 ipv6, zone id eth0)
    """ % (self.prog, self.prog)

        argparser = _argparse.ArgumentParser(
            prog=self.prog, usage=usage, description=desc, epilog=epilog,
            add_help=False, formatter_class=SmiCustomFormatter)

        pos_arggroup = argparser.add_argument_group(
            'Positional arguments')
        pos_arggroup.add_argument(
            'server', metavar='server', nargs='?',
            help='R|Host name or url of the WBEM server in this format:\n'
                 '    [{scheme}://]{host}[:{port}]\n'
                 '- scheme: Defines the protocol to use;\n'
                 '    - "https" for HTTPs protocol\n'
                 '    - "http" for HTTP protocol.\n'
                 '  Default: "https".\n'
                 '- host: Defines host name as follows:\n'
                 '     - short or fully qualified DNS hostname,\n'
                 '     - literal IPV4 address(dotted)\n'
                 '     - literal IPV6 address (RFC 3986) with zone\n'
                 '       identifier extensions(RFC 6874)\n'
                 '       supporting "-" or %%25 for the delimiter.\n'
                 '- port: Defines the WBEM server port to be used\n'
                 '  Defaults:\n'
                 '     - HTTP  - 5988\n'
                 '     - HTTPS - 5989\n')

        server_arggroup = argparser.add_argument_group(
            'Server related options',
            'Specify the WBEM server namespace and timeout')
        server_arggroup.add_argument(
            '-n', '--namespace', dest='namespace', metavar='namespace',
            help='R|Namespace in the WBEM server for the test request.\n'
                 'Default: %(default)s')
        server_arggroup.add_argument(
            '-t', '--timeout', dest='timeout', metavar='timeout', type=int,
            default=20,
            help='R|Timeout of the completion of WBEM Server operation\n'
                 'in seconds(integer between 0 and 300).\n'
                 'Default: 20 seconds')
        server_arggroup.add_argument(
            '--ping', action='store_true', default=False,
            help='Ping for server before trying to connect.')
        server_arggroup.add_argument(
            '-i', '--user-id', dest='user_id', metavar='UserDataId',
            help='R|If this argument is set, the value is a user id to use\n'
                 'instead of an server url as the source for the test. In\n'
                 'this case, namespace, user, and password arguments are\n'
                 'derived from the user data rather than cli input')

        security_arggroup = argparser.add_argument_group(
            'Connection security related options',
            'Specify user name and password or certificates and keys')
        security_arggroup.add_argument(
            '-u', '--user', dest='user', metavar='user',
            help='R|User name for authenticating with the WBEM server.\n'
                 'Default: No user name.')
        security_arggroup.add_argument(
            '-p', '--password', dest='password', metavar='password',
            help='R|Password for authenticating with the WBEM server.\n'
                 'Default: Will be prompted for, if user name\nspecified.')
        security_arggroup.add_argument(
            '-V', '--verify-cert', dest='verify_cert',
            action='store_true',
            help='Client will verify certificate returned by the WBEM'
                 ' server (see cacerts). This forces the client-side'
                 ' verification of the server identity, Normally it would'
                 ' be important to verify the server certificate but in the smi'
                 ' test environment where certificates are largely unknown'
                 ' the default is to not verify.')
        security_arggroup.add_argument(
            '--cacerts', dest='ca_certs', metavar='cacerts',
            help='R|File or directory containing certificates that will be\n'
                 'matched against a certificate received from the WBEM\n'
                 'server. Set the --no-verify-cert option to bypass\n'
                 'client verification of the WBEM server certificate.\n')
        security_arggroup.add_argument(
            '--certfile', dest='cert_file', metavar='certfile',
            help='R|Client certificate file for authenticating with the\n'
                 'WBEM server. If option specified the client attempts\n'
                 'to execute mutual authentication.\n'
                 'Default: Simple authentication.')
        security_arggroup.add_argument(
            '--keyfile', dest='key_file', metavar='keyfile',
            help='R|Client private key file for authenticating with the\n'
                 'WBEM server. Not required if private key is part of the\n'
                 'certfile option. Not allowed if no certfile option.\n'
                 'Default: No client key file. Client private key should\n'
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

        self.argparser = argparser


    def parse_cmdline(self):
        """
        Parse the command line.

        This function  tests for any required arguments.

        It returns the parsed options or generates an exception.
        """
        opts = self.argparser.parse_args()

        if opts.verbose:
            attrs = vars(opts)
            print('cli arguments')
            print('\n'.join("%s: %s" % item for item in attrs.items()))
            print('')
            
        # save cli options for use in subsequent functions.
        self.verbose = opts.verbose
        self.debug = opts.debug
        self.ping = opts.ping
        self.namespace = opts.namespace if opts.namespace else 'None'
        self.timeout = opts.timeout
        
        
        if not opts.server:
            if opts.user_id is None:
                self.argparser.error('No WBEM server specified')
            else:
                if (opts.user is not None or opts.password is not None or
                        opts.namespace is not None):
                    self.argparser.error('-u, -n, or -p not used with'
                                         '-i option')
        if opts.user_id:
            user_data = CsvUserData(USERDATA_FILE)
            if opts.user_id in user_data:
                user_record = user_data(opts.user_id)
                print('Using ip=%s, user=%s, pw=%s namespace=%s' %
                      (user_record['IPAddress'], user_record['Principal'],
                      user_record['Credential'],
                      user_record['Namespace']))
            self.namespace = user_record['Namespace']
            self.user = user_record['Principal']
            self.server = user_record['IPAddress']
        else:
            self.namespace = opts.namespace
            self.user = opts.user
            self.credential = opts.password
            self.server = opts.server           
            
                    

        if opts.timeout is not None:
            if opts.timeout < 0 or opts.timeout > 300:
                self.argparser.error('timeout option(%s) out of range' %
                                     opts.timeout)



        return opts
