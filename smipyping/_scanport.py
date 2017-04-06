"""
Scan port function.  This scans a single port to determine if it is open

This is the code that is privilege aware.
"""
# required to turn off  IP v6 warning message from scapy in import
import logging
SCPY_LOG = logging.getLogger("scapy.runtime")
SCPY_LOG.setLevel(49)

from scapy.all import *  # noqa: E402, F403
__all__ = ['check_port_syn']


def check_port_syn(dst_ip, dst_port, verbose):
    """
    Check a single address with SYN for open port.

    Uses scapy function to execute SYN on dst_ip and port.
    This is one way to test for open https ports.

    Using SYN allows us to test for open port but in Python requires that
    the code execute in admin mode.
    """
    SYNACK = 0x12
    RSTACK = 0x14

    conf.verb = 0  # Disable verbose in sr(), sr1() methods  #noqa: F405
    port_open = False
    src_port = RandShort()
    p = IP(dst=dst_ip) / TCP(sport=src_port, dport=dst_port, flags='S')
    resp = sr1(p, timeout=2)  # Sending packet
    if str(type(resp)) == "<type 'NoneType'>":
        if verbose:
            print('%s Closed. response="none"' % dst_ip)
    elif resp.haslayer(TCP):
        if resp.getlayer(TCP).flags == SYNACK:
            send_rst = sr(IP(dst=dst_ip) / TCP(sport=src_port, dport=dst_port,
                                             flags='AR'), timeout=1)
            port_open = True
            if verbose:
                print('check_port:%s:%s Open' % (dst_ip, dst_port))
        elif resp.getlayer(TCP).flags == RSTACK:
            if verbose:
                print('%s:%s Closed. response="RSTACK"' % (dst_ip, dst_port))
    else:
        if verbose:
            print('%s is Down' % dst_ip)

    sys.stdout.flush()
    return port_open
