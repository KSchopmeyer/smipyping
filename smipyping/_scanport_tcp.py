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
Scan port function using the TCP connect.  This scans a single port to determine
if it is open

This code does NOT require privileged mode
"""
import os
import socket

__all__ = ['check_port_tcp']


def check_port_tcp(dst_ip, dst_port, verbose, logger):
    """
    Test for open port using TCP connect.

    Returns tuple (Boolean Result, result errno or exception)
    This method does not require privileged mode to execute.

    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    try:
        result = sock.connect_ex((dst_ip, dst_port))
        if result:
            logger.debug('PORTSCAN_TCP: ERROR_RTN: ip=%s, port=%s, '
                         'erno=%s:%s', dst_ip, dst_port, result,
                         os.strerror(result))
        if verbose and result:
            print('ERROR RTN: ip=%s, port=%s, erno=%s:%s' %
                  (dst_ip, dst_port, result, os.strerror(result)))
        sock.close()
        if result == 0:
            return (True, result, None)
        return (False, result, os.strerror(result))

    except (KeyboardInterrupt, SystemExit):
        raise

    except Exception as ex:  # pylint: disable=broad-except
        logger.debug('PORTSCAN_TCP: Connect exception %s', ex)
        print('TCP Connect exception %s' % ex)
        return (False, 1000, ex)
