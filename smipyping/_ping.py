
from __future__ import absolute_import
import os
import platform
import subprocess
import urlparse
from .config import PING_TIMEOUT

__all__ = ['ping_host', 'ping_uri']

def ping_uri(uri, timeout):
    """
    Strip the uri to its hostname/ipaddress and call the ping_host function

    Parameters:
        uri:
            Uri to ping including hostname

    Returns:
        True if timed out
    """
    netloc = urlparse.urlparse(url).netloc
    target_address = netloc.split(':')
    result = ping_host(target_address[0], PING_TIMEOUT)
    return result    

def ping_host(hostname, timeout):
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

    if platform.system() == "Windows":
        command = "ping " + hostname + " -q -n 1 -w " + str(timeout * 1000)
    else:
        command = "ping -i " + str(timeout) + " -c 1 " + hostname

    need_sh = False if platform.system().lower() == "windows" else True

    # execute the ping command and discard text response
    FNULL = open(os.devnull, 'w')
    return subprocess.call(
        command, shell=need_sh, stdout=FNULL, stderr=subprocess.STDOUT) == 0
