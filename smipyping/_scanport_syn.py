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
Scan port function using the SYN packet.  This scans a single port to determine
if it is open

This is the code that is privilege aware because it uses raw tcp and that
requires admin privileges in the Python interpreter.
"""
# required to turn off  IP v6 warning message from scapy in import
import sys
import logging
from scapy.all import IP, TCP, sr1, sr, conf, RandShort
SCPY_LOG = logging.getLogger("scapy.runtime")
SCPY_LOG.setLevel(49)

__all__ = ['check_port_syn']


def check_port_syn(dst_ip, dst_port, verbose, logger):
    """
    Check a single address with SYN for open port.

    Uses scapy function to execute SYN on dst_ip and port.
    This is one way to test for open https ports.

    Using SYN allows us to test for open port but in Python requires that
    the code execute in admin mode.

    Returns tuple (Boolean result, None, None)
    """
    SYNACK = 0x12
    RSTACK = 0x14

    conf.verb = 0  # Disable verbose in sr(), sr1() methods  #noqa: F405
    result = False
    src_port = RandShort()
    response = None
    p = IP(dst=dst_ip) / TCP(sport=src_port, dport=dst_port, flags='S')
    resp = sr1(p, timeout=2)  # Sending packet
    if str(type(resp)) == "<type 'NoneType'>":
        response = 'none'
        logger.debug('PORTSCAN_SYN: %s Closed. response="none"', dst_ip)
        if verbose:
            print('%s Closed. response="none"' % dst_ip)
    elif resp.haslayer(TCP):
        if resp.getlayer(TCP).flags == SYNACK:
            # pylint: disable=bad-continuation
            sr(IP(dst=dst_ip) / TCP(sport=src_port, dport=dst_port,
               flags='AR'), timeout=1)
            result = True
            response = 'Open, SYNACK'
            logger.debug('PORTSCAN_SYN:check_port:%s:%s Open', dst_ip,
                         dst_port)
            if verbose:
                print('check_port:%s:%s Open' % (dst_ip, dst_port))
        elif resp.getlayer(TCP).flags == RSTACK:
            logger.debug('PORTSCAN_SYN: %s:%s Closed. response="RSTACK"',
                         dst_ip, dst_port)
            response = 'Closed, RSTACK'
            if verbose:
                print('%s:%s Closed. response="RSTACK"' % (dst_ip, dst_port))
    else:
        response = 'Down, no TCP'
        if verbose:
            print('%s is Down' % dst_ip)

    sys.stdout.flush()
    # Returns tuple of
    return (result, None, response)
