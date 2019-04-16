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
# TODO the following should be standardized in report module
from textwrap import fill
import datetime
from threading import Thread
import Queue

from urlparse import urlparse
from collections import namedtuple

from pywbem import WBEMConnection, ConnectionError, Error, TimeoutError, \
    CIMError
from ._ping import ping_host
from .config import PING_TEST_CLASS, PING_TIMEOUT, DEFAULT_USERNAME, \
    DEFAULT_PASSWORD

from .config import MAX_THREADS
from ._logging import CIMPING_LOGGER_NAME, get_logger, SmiPypingLoggers

from ._pingstable import PingsTable


__all__ = ['SimplePing', 'SimplePingList', 'TestResult']

LOG = get_logger(__name__)

TestResult = namedtuple('TestResult', ['code',
                                       'type',
                                       'exception',
                                       'execution_time'])


class SimplePingList(object):
    """
        Ping a list of target_ids using a work queue to speed up the process.
        Uses the SimplePing class to execute pings against a list of servers.
        If no list is provided, it scans all servers in the Targets Table
        of thedatabase.

    """
    def __init__(self, targets_tbl, target_ids=None, verbose=None, logfile=None,
                 timeout=None, log_level=None, threaded=True,
                 include_disabled=False):
        """
        Saves the input parameters and sets up local variables for the
        execution of the scan.

        Parameters:

            targets_tbl(:class:`~smipyping.TargetsTbl`)
               Instance of the TargetData class with the targets from the
               database.

            target_ids(:term:`list` of :term:`integer`)
                database Ids of targets that are to be pinged. If this is
                None, the entire set of enabled targets is pinged.

            verbose(:class:`py:bool`):
                Optional flag that when enabled outputs additional diagnostic
                information to the console.

            threaded(:class: `py:bool`):
                Optional flag that allows running this operation single
                threaded rather than the default multi-thread.

            logfile(:term:`string`):
                Optional string defining a file name for a log file
                TODO change this

            log_level(:term:`string`)
                TODO clean this up

            timeout(:term: `integer` or None)
                If this is an integer it is the timeout in seconds that will
                be passed on to  the test connection

            include_disabled(:class:`py:bool`):
                If true, include disabled targets.

        Exceptions:
            KeyError if a target_id is not in the database.
        """
        self.targets_tbl = targets_tbl
        self.include_disabled = include_disabled

        if include_disabled:
            self.target_ids = target_ids if target_ids else \
                targets_tbl.keys()
        else:
            self.target_ids = target_ids if target_ids else \
                targets_tbl.get_enabled_targetids()

        self.verbose = verbose
        self.logfile = logfile
        self.log_level = log_level
        self.kill_threads = False
        self.threaded = threaded
        self.timeout = timeout

    def __repr__(self):
        """
        Return string with class status
        """
        return "SimplePingList(" \
               "target_ids={}, " \
               "include_disabled={}, " \
               "verbose = {}, "  \
               "threaded={}, " \
               "timeout={}" \
               "log_level={})".format(self.target_ids,
                                      self.include_disabled,
                                      self.verbose, self.threaded,
                                      self.timeout,
                                      self.log_level)

    def ping_servers(self):
        """
        Execute SimplePing on the servers defined. Returns a list of
        results. If self.threaded is True, call the threaded executor.
        Otherwise call the single-thread method

        return:
            list of TestResult named tuples with results of test.

        Exceptions:
            KeyboardInterrupt:

        """
        print("SELF %s" % self)

        if self.threaded:
            return self.ping_servers_threaded()

        return self.ping_servers_not_threaded()

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
            # check_result, error = self.check_port(work[0])
            simpleping = SimplePing(target_id=work[0],
                                    targets_tbl=self.targets_tbl,
                                    timeout=self.timeout)
            test_result = simpleping.test_server()
            # append target_id and results to results list.
            results.append((work[0], test_result))
            queue.task_done()
        return

    def ping_servers_threaded(self):
        """
        Execute SimplePing on the servers defined. Returns a list of
        results. If self.threaded is True, call the threaded executor.
        Otherwise call the single-thread method

        return:
            list of TestResult named tuples with results of test.

        Exceptions:
            KeyboardInterrupt:

        """
        # set up queue to hold all call info
        queue = Queue.Queue(maxsize=0)
        num_threads = MAX_THREADS

        results = []

        # put all targets into work queue
        for target_id in self.target_ids:
            queue.put((target_id, results))

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

    def ping_servers_not_threaded(self):
        """
        Threaded cimping of servers.

        Execute SimplePing on the servers defined without multithreading.
        Executes each test in a single thread.  NOTE: THis is probably
        most useful  for debugging.
        Returns a list of results

        return:
            list of TestResult named tuples with results of test.

        Exceptions:
            KeyboardInterrupt:

        """
        results = []
        for targetid in self.target_ids:
            simpleping = SimplePing(target_id=targetid,
                                    targets_tbl=self.targets_tbl,
                                    timeout=self.timeout)
            test_result = simpleping.test_server()
            # append target_id and results to results list.
            results.append((targetid, test_result))

        # returns list of ip addresses that were were found
        return results

    def create_fake_results(self, result=None):
        """
        Test functionality to create a fake result list from either the
        ids in the list or all ids.  If the result is none, generate result
        by rotating through possible results. Otherwise use result indicated.

        This is a test tool only.

        Return list of tuples where each tuple contains
            (targetdata id, TestResult)
        """
        rtn_list = []
        for id_ in self.target_ids:
            result = 'OK'
            result_code = SimplePing.get_result_code(result)
            exception = None
            execution_time = .01
            rtn_list.append((id_, TestResult(
                code=result_code,
                type=result,
                exception=exception,
                execution_time=str(execution_time))))
        return rtn_list


class SimplePing(object):
    """Simple ping class. Contains all functionality to handle simpleping."""

    # class level attributes
    # Error code keys and corresponding exit codes
    error_code = {
        'OK': 0,
        'WBEMError': 1,
        'PyWBEMError': 2,
        'GeneralError': 3,
        'TimeoutError': 4,
        'ConnectionError': 5,
        'PingFail': 6,
        'Disabled': 7}

    @classmethod
    def get_result_code(cls, result_type):
        """Get the result code corresponding to the result_type."""
        return cls.error_code[result_type]

    def __init__(self, server=None, namespace=None, user=None, password=None,
                 timeout=None, target_id=None, targets_tbl=None, ping=True,
                 certfile=None, keyfile=None, verify_cert=False,
                 debug=False, verbose=None, logfile=None, log_level=None):
        """
        Initialize instance attributes.

          Parameters:

            server(:term:`string`):
                url of a server to cimping. This is optional however either
                the url or target_id must exist and they cannot both exist

            namespace(:term:`string`):
                namespace of the server if url is defined. Otherwise ignored.

            user

            password

            timeout

            target_id

            targets_tbl

            ping

            certfile

            keyfile

            verify_cert

            debug

            verbose

            logfile

            log_level

          Exceptions:
            ValueError if invalid input parameters.

        """
        if server:
            self.url = self.server_url_validate(server)
        else:
            self.url = None
        if server is None and target_id is None:
            raise ValueError('SimplePing must define server or target_id')
        if server and target_id:
            raise ValueError('Use either server or target_id, not both')
        if target_id and not targets_tbl:
            raise ValueError('targets_tbl required to use target_id')
        self.targets_tbl = targets_tbl
        self.target_id = target_id

        if verbose:
            if server:
                print('SimplePing server %s' % self.url)
            else:
                print('SimplePing id %s' % target_id)

        if self.target_id:
            target_record = self.targets_tbl[self.target_id]
            self.url = '%s://%s' % (target_record['Protocol'],
                                    target_record['IPAddress'])

            self.namespace = target_record['Namespace']
            self.user = target_record.get('Principal', DEFAULT_USERNAME)
            self.password = target_record.get('Credential', DEFAULT_PASSWORD)
        else:
            self.namespace = namespace
            self.user = user
            self.password = password

        self.timeout = timeout
        self.ping = ping
        self.debug = debug
        self.verbose = verbose
        self.certfile = certfile
        self.keyfile = keyfile
        self.verify_cert = verify_cert
        log_dest = 'file' if log_level else None
        SmiPypingLoggers.create_logger(log_component='cimping',
                                       log_dest=log_dest,
                                       log_filename=logfile,
                                       log_level=log_level)
        self.logger = get_logger(CIMPING_LOGGER_NAME)

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

    def get_connection_info(self, conn):  # pylint: disable=no-self-use
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
                             ' Use "http" or "https"' % server)
        else:
            url = '%s://%s' % ('https', server)
        self.url = url
        return url

    def ping_log_result(self, result, db_dict, dbtype):
        """
            Write the ping result to the ping_log destination.
            Uses the PingTable to output the results of a ping to
            the destination defined by the dbtype.

            The output log consists of the ping target id and status.
        """
        pingtable = PingsTable.factory(db_dict, dbtype, self.verbose)

        pingtable.append(self.target_id, result)
        # TODO Finish this. NOTE: Do I really need this???

    def test_server(self, verify_cert=False):
        """
        Execute the simpleping tests against the defined server.

        This method executes all of the required tests against the server
        and returns the namedtuple TestResults

          Returns:
             tuple of
        """
        start_time = datetime.datetime.now()
        # execute the ping test if required
        ping_result = True
        result_code = 0
        exception = None
        if self.ping:
            ping_result, result = self.ping_server()
            if ping_result is False:
                result_code = self.get_result_code(result)
                exception = None
        if ping_result:
            # connect to the server and execute the cim operation test
            conn = self.connect_server(verify_cert=verify_cert)
            result, exception = self.execute_cim_test(conn)
            result_code = self.get_result_code(result)
        if self.verbose:
            print('result=%s, exception=%s, resultCode %s'
                  % (result, exception, result_code))
        execution_time = datetime.datetime.now() - start_time
        execution_time = '%.2fs' % execution_time.total_seconds()
        if self.url:
            id_ = 'url=%s' % self.url
        else:
            id_ = 'target_id=%s' % self.target_id
        self.logger.info('Test %s result=%s, exception=%s, resultCode=%s,'
                         ' time=%s',
                         id_, result, exception, result_code,
                         str(execution_time))

        # Return namedtuple with results
        return TestResult(
            code=result_code,
            type=result,
            exception=exception,
            execution_time=str(execution_time))

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
            return(True, 'OK')
        return(False, 'PingFail')

    def connect_server(self, verify_cert=False):
        """
        Build connection parameters and issue WBEMConnection to the WBEMServer.

        The server is defined by the input options.

        Returns completed connection or exception of connection fails
        """

        creds = None

        if self.user is not None or self.password is not None:
            creds = (self.user, self.password)

        conn = WBEMConnection(self.url, creds, default_namespace=self.namespace,
                              no_verification=not verify_cert,
                              timeout=self.timeout)
        conn.debug = self.debug
        if self.verbose:
            print(self.get_connection_info(conn))

        return conn

    def execute_cim_test(self, conn):
        """
        Issue the test operation. Returns with system exit code.

        Returns a tuple of code and reason text or exception if an exception
        occurred.  The code is ne 0 if there was an error.

          Return:
            tuple of result code (:term:`string`) and exception object if
            there was an exception (otherwise None).

        """
        try:
            if self.verbose:
                print('Test server %s namespace %s creds %s class %s' %
                      (conn.url, conn.default_namespace, conn.creds,
                       PING_TEST_CLASS))
            self.logger.info('Test server %s namespace %s creds %s class %s',
                             conn.url, conn.default_namespace, conn.creds,
                             PING_TEST_CLASS)
            insts = conn.EnumerateInstances(PING_TEST_CLASS)

            if self.verbose:
                print('Running host=%s. Returned %s instance(s)' %
                      (conn.url, len(insts)))
            rtn_tuple = ('OK', None)

        except CIMError as ce:
            # TODO make this a named tuple for clarity
            rtn_tuple = ("WBEMError", ce)
        except ConnectionError as co:
            rtn_tuple = ("ConnectionError", co)
        except TimeoutError as to:
            rtn_tuple = ("TimeoutError", to)
        except Error as er:
            rtn_tuple = ("PyWBEMError", er)
        except Exception as ex:  # pylint: disable=broad-except
            rtn_tuple = ("GeneralError", ex)

        if self.debug:
            last_request = conn.last_request or conn.last_raw_request
            print('Request:\n\n%s\n' % last_request)
            last_reply = conn.last_reply or conn.last_raw_reply
            print('Reply:\n\n%s\n' % last_reply)

        if self.verbose:
            print('Execute_cim_test %s rtn_tuple %s' % (conn.url, (rtn_tuple,)))
        self.logger.info('SimplePing Result  ip=%s return=%s', conn.url,
                         (rtn_tuple,))
        return rtn_tuple

    def set_connect_from_targetrecord(self, target_record, target_id):
        """
        Set the required fields from the provided target_record in the
        targets_tbl

        This sets the fields from either the database or defaults if the
        fields do not exist in the database
        """

        self.url = '%s://%s' % (target_id.get_url.str())

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
