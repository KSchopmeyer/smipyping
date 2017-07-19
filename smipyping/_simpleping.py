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
"""

from __future__ import print_function, absolute_import


import re
from textwrap import fill
import datetime

from urlparse import urlparse
from collections import namedtuple

from pywbem import WBEMConnection, ConnectionError, Error, TimeoutError, \
    CIMError
from ._ping import ping_host
from .config import PING_TEST_CLASS, PING_TIMEOUT, DEFAULT_USERNAME, \
    DEFAULT_PASSWORD

from ._logging import CIMPING_LOGGER_NAME, get_logger, SmiPypingLoggers


__all__ = ['SimplePing', 'TestResult']

TestResult = namedtuple('TestResult', ['code',
                                       'type',
                                       'exception',
                                       'execution_time'])


class SimplePing(object):
    """Simple ping class. Contains all functionality to handle simpleping."""

    def __init__(self, server=None, namespace=None, user=None, password=None,
                 timeout=None, target_id=None, ping=True,
                 certfile=None, keyfile=None, verify_cert=False,
                 debug=False, verbose=None, logfile=None, log_level=None):
        """Initialize instance attributes."""
        print('SimplePing server %s, target_id %s' % (server, target_id))
        if server:
            self.url = self.server_url_validate(server)
        else:
            self.url = None
        if server is None and target_id is None:
            raise ValueError('SimplePing must define server or target_id')
        if server and target_id:
            raise ValueError('Use either server or target_id, not both')
        self.namespace = namespace
        self.timeout = timeout
        self.user = user
        self.password = password
        self.ping = ping
        self.debug = debug
        self.verbose = verbose
        self.certfile = certfile
        self.keyfile = keyfile
        self.verify_cert = verify_cert
        self.target_id = target_id
        log_dest = 'file' if log_level else None
        SmiPypingLoggers.create_logger(log_component='cimping',
                                       log_dest=log_dest,
                                       log_filename=logfile,
                                       log_level=log_level)
        self.logger = get_logger(CIMPING_LOGGER_NAME)

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

    def __repr__(self):
        """Return url."""
        return 'url=%s ns=%s user=%s password=%s timeout=%s ping=%s debug=' \
               '%s verbose=%s target_id=%s' % (self.url, self.namespace,
                                               self.user, self.password,
                                               self.timeout, self.ping,
                                               self.debug, self.verbose,
                                               self.target_id)

    def __str__(self):
        """Return some attributes."""
        return 'url=%s namespace=%s ping=%s user=%s, pw=%sdebug=%s ' \
               'verbose=%s' % \
               (self.url, self.namespace, self.ping, self.user, self.password,
                self.debug, self.verbose)

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

    def server_url_validate(self, server):
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
        self.logger.debug('ping result=%s' % (result_code))
        if ping_result:
            print('cimping url=%s, ns=%s, principal=%s, cred=%s' %
                  (self.url, self.namespace, self.user, self.password))
            # connect to the server and execute the cim operation test
            conn = self.connect_server(self.url, verify_cert=verify_cert)

            result, exception = self.execute_cim_test(conn)

            result_code = self.get_result_code(result)
        if self.verbose:
            print('result=%s, exception=%s, resultCode %s'
                  % (result, exception, result_code))
        self.logger.debug('result=%s, exception=%s, resultCode %s'
                          % (result, exception, result_code))

        # Return namedtuple with results
        return TestResult(
            code=result_code,
            type=result,
            exception=exception,
            execution_time=str(datetime.datetime.now() - start_time))

    # TODO: ks move this and corresponding simple_ping into ping iteslf.
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
            self.logger.info('Test server %s namespace %s creds %s class %s' %
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
            rtn_code = ("WBEMException", ce, ce.status_code_name,
                        ce.status_description)
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
        self.logger.info('SimplePing Result %s' % (rtn_tuple,))
        return rtn_tuple

    def set_param_from_targetdata(self, target_id, target_data):
        """
        Set the required fields from data in the target_data base

        Get the connection information from the target_data base and save in
        the SimplePing instance
        """

        target_record = target_data[target_id]
        self. set_param_from_targetrecord(target_record, target_id)

    def set_param_from_targetrecord(self, target_record, target_id):
        """
        Set the required fields from the provided target_record in the
        target_database

        This sets the fields from either the database or defaults if the
        fields do not exist in the database
        """

        self.url = '%s://%s' % (target_record['Protocol'],
                                target_record['IPAddress'])

        if self.verbose:
            print(
                'DB target id %s; Using url=%s, user=%s, pw=%s namespace=%s' %
                (target_id, self.url,
                 target_record['Principal'],
                 target_record['Credential'],
                 target_record['Namespace']))

        self.namespace = target_record['Namespace']

        if 'Principal' in target_record:
            self.user = target_record['Principal']
        else:
            self.user = DEFAULT_USERNAME

        if 'Credential' in target_record:
            self.password = target_record['Credential']
        else:
            self.password = DEFAULT_PASSWORD

        if self.verbose:
            print('Target id %s; Using url=%s, user=%s, pw=%s namespace=%s' %
                  (target_id, self.url,
                   self.user,
                   self.password,
                   self.namespace))