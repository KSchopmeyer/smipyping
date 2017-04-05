
"""
Functions to support pinging a system either by uri or hostname
"""
from __future__ import absolute_import

import os
import platform
import subprocess
import urlparse
import shlex
from .config import PING_TIMEOUT

__all__ = ['ping_host', 'ping_uri']


def ping_uri(uri, timeout=None):
    """
    Strip the uri to its hostname/ipaddress and call the ping_host function

    Parameters:
        uri:
            Uri to ping including hostname

    Returns:
        True if ping ok
    """
    netloc = urlparse.urlparse(uri).netloc
    target_address = netloc.split(':')
    ping_timeout = timeout if timeout else PING_TIMEOUT
    result = ping_host(target_address[0], ping_timeout)
    return result


def ping_host(hostname, timeout=None):
    """ Simple ping of a defined hostname.
    Calls system ping in a subprocess.
    This works in user mode whereas ICMP pings in Python only work in
    admin mode.

    Parameters:

      hostname:
        Address of the host to ping

      timeout:
        True if ping succeeds.

    Returns:

        Returns True if Ping succeeded
    """
    ping_timeout = timeout if timeout else PING_TIMEOUT
    if platform.system() == "Windows":
        command = "ping " + hostname + " -q -n 1 -w " + str(ping_timeout * 1000)
    else:
        command = "ping -i 2 -W " + str(ping_timeout) + " -c 1 " + hostname

    need_sh = False if platform.system().lower() == "windows" else True

    # execute the ping command and discard text response
    FNULL = open(os.devnull, 'w')
    return subprocess.call(
        command, shell=need_sh, stdout=FNULL, stderr=subprocess.STDOUT) == 0

    # execute the ping command and discard text response
    try:
        subprocess.check_call(shlex.split(command), shell=need_sh)
        return True

    except subprocess.CalledProcessError as e:
        print('ping exception %s' % e)
        return False

    return

    # p = subprocess.Popen(shelex.split(command), stdin=PIPE, stdout=PIPE,
    #                      stderr=PIPE)
    # output, err = p.communicate(b"input data that is passed to subprocess' stdin")
    # rc = p.returncode
    # if rc != 0:
