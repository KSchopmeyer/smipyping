"""
Provides the components for a utility to test a WBEM server.

The Simpleping class that executed a simplistic test on a server defined by
the cmd input arguments.

This tests a wbem server against a class defined in the configuration. If
that class is found, it returns success. Otherwise it returns a fail code.

If successul, the program returns exit code 0 and the text "Running"

Otherwise it returns an exit code that is defines the error and a non-zero
exit code.

This  file includes the cmd line parser, and functions to test the connection.
Returns exit code of 0 if the server is found and the defined class exists.


This module is the component of the script simpleping. It is assembled in a
separate python file for testability
"""

from __future__ import print_function, absolute_import

import argparse as _argparse
import re
from textwrap import fill
import datetime

from urlparse import urlparse
from collections import namedtuple

from pywbem import WBEMConnection, ConnectionError, Error, TimeoutError, \
    CIMError

from smipyping._configfile import read_config
from ._cliutils import SmiSmartFormatter

from ._ping import ping_host

from .config import PING_TEST_CLASS, PING_TIMEOUT, DEFAULT_CONFIG_FILE, \
    DEFAULT_DBTYPE


from ._targetdata import TargetsData

__all__ = ['SimplePing', 'TestResult']

TestResult = namedtuple('TestResult', ['code',
                                       'type',
                                       'exception',
                                       'execution_time'])


class SimplePing(object):
    """Simple ping class. Contains all functionality to handle simpleping."""

    def __init__(self, prog):
        """Initialize instance attributes."""
        self.prog = prog
        self.debug = False,
        self.verbose = False,
        self.ping = True
        self.argparser = None
        self.namespace = None
        self.user = None
        self.password = None
        self.url = None
        self.timeout = None

        # Error code keys and corresponding exit codes
        self.error_code = {
            'Running': 0,
            'WBEMException': 1,
            'PyWBEM Error': 2,
            'General Error': 3,
            'TimeoutError': 4,
            'ConnectionError': 5,
            'Ping Fail': 6,
            'Disabled': 0}

    def __str__(self):
        """Return url."""
        return 'url %s prog %s ' % (self.url, self.prog)

    def __repr__(self):
        """Return some attributes."""
        return 'prog %s debug %s verbose %s ping %s namespace %s' % \
               (self.prog, self.debug, self.verbose, self.ping,
                self.namespace)

    def get_connection_info(self, conn):
        """Return a string with the connection info."""
        info = 'Connection: %s,' % conn.url

        if conn.creds is not None:
            info += ' targetid=%s,' % conn.creds[0]
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

        Returns url including scheme and saves it in the class object

        Exception: ValueError Error if url scheme is invalid
        """
        if server[0] == '/':
            url = server

        elif re.match(r"^https{0,1}://", server) is not None:
            url = server

        elif re.match(r"^[a-zA-Z0-9]+://", server) is not None:
            raise ValueError('SimplePing: Invalid scheme on server argument %s.'
                             ' Use "http" or "https"', server)

        else:
            url = '%s://%s' % ('https', server)
        self.url = url
        return url

    def get_result_code(self, result_type):
        """Get the result code corresponding to the result_type."""
        return self.error_code[result_type]

    def test_server(self, verify_cert=False):
        """
        Execute the simpleping tests against the defined server.

        This method executes all of the required tests against the server
        and returns the namedtuple TestResults
        """
        start_time = datetime.datetime.now()
        # execute the ping test if required
        ping_result = True
        result_code = 0
        exception = ''
        if self.ping:
            ping_result, result = self.ping_server()
            if ping_result is False:
                result_code = self.get_result_code(result)
                exception = 'Ping failed'
        if ping_result:
            # connect to the server and execute the cim operation test
            conn = self.connect_server(self.url, verify_cert=verify_cert)

            result, exception = self.execute_cim_test(conn)

            result_code = self.get_result_code(result)
        if self.verbose:
            print('result=%s, exception=%sm resultCode %s'
                  % (result, exception, result_code))

        # Return namedtuple with results
        return TestResult(
            code=result_code,
            type=result,
            exception=exception,
            execution_time=str(datetime.datetime.now() - start_time))

    # TODO move this and corresponding simple_ping into ping iteslf.
    def ping_server(self):
        """
        Get the netloc from the url and ping the server.


        Returns the result text that must match the defined texts.

        """
        netloc = urlparse(self.url).netloc
        target_address = netloc.split(':')
        if self.verbose:
            print('Ping network address %s' % target_address[0])
        if ping_host(target_address[0], PING_TIMEOUT):
            return(True, 'running')
        return(False, 'Ping Fail')

    def connect_server(self, url, verify_cert=False):
        """
        Build connection parameters and issue WBEMConnection to the WBEMServer.

        The server is defined by the input options.

        Returns completed connection or exception of connection fails
        """
        creds = None

        if self.user is not None or self.password is not None:
            creds = (self.user, self.password)

        conn = WBEMConnection(url, creds, default_namespace=self.namespace,
                              no_verification=not verify_cert,
                              timeout=self.timeout)

        conn.debug = self.debug

        if self.verbose:
            print(self.get_connection_info(conn))

        return conn

    def execute_cim_test(self, conn):
        """
        Issue the test operation. Returns with system exit code.

        Returns a tuple of code and reason text.  The code is ne 0 if there was
        an error.
        """
        try:
            if self.verbose:
                print('Test server %s namespace %s creds %s class %s' %
                      (conn.url, conn.default_namespace, conn.creds,
                       PING_TEST_CLASS))
            insts = conn.EnumerateInstances(PING_TEST_CLASS)

            if self.verbose:
                print('Running host=%s. Returned %s instance(s)' %
                      (conn.url, len(insts)))
            rtn_code = ("Running", "")

        except CIMError as ce:
            print('CIMERROR %r %s %s %s' % (ce,
                                            ce.status_code,
                                            ce.status_code_name,
                                            ce.status_description))
            rtn_reason = '%s:%s:%s:%s' % (ce, ce.status_code,
                                          ce.status_code_name,
                                          ce.status_description)
            rtn_code = ("WBEMException", ce.status_code_name)
        except ConnectionError as co:
            rtn_code = ("ConnectionError", co)
        except TimeoutError as to:
            rtn_code = ("TimeoutError", to)
        except Error as er:
            rtn_code = ("PyWBEM Error", er)
        except Exception as ex:  # pylint: disable=broad-except
            rtn_code = ("General Error", ex)

        if self.debug:
            last_request = conn.last_request or conn.last_raw_request
            print('Request:\n\n%s\n' % last_request)
            last_reply = conn.last_reply or conn.last_raw_reply
            print('Reply:\n\n%s\n' % last_reply)

        # rtn_tuple = [rtn_code[0], rtn_code[1]]
        rtn_tuple = tuple(rtn_code)
        if self.verbose:
            print('rtn_tuple %s' % (rtn_tuple,))
        return rtn_tuple

    def create_parser(self):
        """Create the parser to parse cmd line arguments."""
        usage = '%(prog)s [options] server'
        desc = """
Script for doing a simple CIM ping against a WBEM server defined by
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

  % s -T 4

  test providerid 4 from the default provider database

  %s http://[2001:db8::1234-eth0] -n interop -(http port 5988 ipv6, zone id eth0)
    """ % (self.prog, self.prog, self.prog)  # noqa: E501

        argparser = _argparse.ArgumentParser(
            prog=self.prog, usage=usage, description=desc, epilog=epilog,
            add_help=False, formatter_class=SmiSmartFormatter)

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
            '-n', '--namespace', dest='namespace', metavar='Namespace',
            help='R|Namespace in the WBEM server for the test request.\n'
            'Default: %(default)s')
        server_arggroup.add_argument(
            '-t', '--timeout', dest='timeout', metavar='timeout', type=int,
            default=20,
            help='R|Timeout of the completion of WBEM Server operation\n'
                 'in seconds(integer between 0 and 300).\n'
                 'Default: 20 seconds')
        server_arggroup.add_argument(
            '-T', '--target_id', dest='target_id',
            metavar='TargetUserId',
            type=int,
            help='R|If this argument is set, the value is a user id\n'
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
            help='R|Client will verify certificate returned by the WBEM\n'
                 'server (see cacerts). This forces the client-side\n'
                 'verification of the server identity, Normally it would\n'
                 'smi be important to verify the server certificate but in\n'
                 'the test environment where certificates are largely\n'
                 'unknown the default is to not verify.')
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
            '--no_ping', '-x', action='store_true', default=False,
            help='R|Do not ping for server as first test. Executing the\n'
                 'ping often shortens the total response time.')
        argparser.add_argument(
            '-f', '--config_file', metavar='CONFIG_FILE',
            default=DEFAULT_CONFIG_FILE,
            help=('Configuration file to use for config information. '
                  'Default=%s' % DEFAULT_CONFIG_FILE))
        argparser.add_argument(
            '-D', '--dbtype', metavar='DBTYPE',
            default=DEFAULT_DBTYPE,
            help=('DBTYPE to use. Default=%s' % DEFAULT_DBTYPE))
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
        return argparser  # used for unittests

    def parse_cmdline(self, input_params=None):
        """
        Parse the command line.

        This function  creates the argparser and uses it to parse the
        command line or the list of arguments in input_params

        It returns the parsed options or generates an exception.
        """
        if input_params:
            opts = self.argparser.parse_args(input_params)
        else:
            opts = self.argparser.parse_args()

        # save cli options for use in subsequent functions.
        self.verbose = opts.verbose
        self.debug = opts.debug
        self.ping = False if opts.no_ping else True
        self.namespace = opts.namespace if opts.namespace else 'None'
        self.timeout = opts.timeout

        if opts.verbose:
            print('opts %s' % opts)

        if not opts.server:
            if opts.target_id is None:
                self.argparser.error('No WBEM server specified and no '
                                     'target_id')
            else:
                if (opts.user is not None or opts.password is not None or
                        opts.namespace is not None):
                    self.argparser.error('-u, -n, or -p not used with'
                                         '-i option')
        elif opts.server and opts.target_id:
            self.argparser.error('Server argument and -T option are mutually '
                                 'exclusive. Chose one or the other')
        elif opts.server and not opts.namespace:
            self.argparser.error('Namespace required when server specified')
        else:
            self.server_to_url(opts.server)
            self.namespace = opts.namespace
            self.user = opts.user
            self.password = opts.password
        if opts.target_id:
            # TODO is there optionality on the config_file here
            db_config = read_config(opts.config_file, opts.dbtype, self.verbose)
            target_data = TargetsData.factory(db_config, opts.dbtype,
                                              opts.verbose)
            if opts.target_id in target_data:
                self.set_from_userrecord(opts.target_id, target_data)
            else:
                self.argparser.error('Id %s not in user data base' %
                                     opts.target_id)

        if opts.timeout is not None:
            if opts.timeout < 0 or opts.timeout > 300:
                self.argparser.error('timeout option(%s) out of range' %
                                     opts.timeout)
        return opts

    def set_from_userrecord(self, target_id, target_data):
        """
        Set the required fields from the user record.

        Get the connection information from the user record and save in
        the SimplePing instance
        """

        target_record = target_data[target_id]
        self.url = '%s://%s' % (target_record['Protocol'],
                                target_record['IPAddress'])

        if self.verbose:
            print(
                'User id %s; Using url=%s, user=%s, pw=%s namespace=%s' %
                (target_id, self.url,
                 target_record['Principal'],
                 target_record['Credential'],
                 target_record['Namespace']))
        self.namespace = target_record['Namespace']
        self.user = target_record['Principal']
        self.password = target_record['Credential']
