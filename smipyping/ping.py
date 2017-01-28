
from __future__ import absolute_import
import os
import platform
import subprocess
import re

__all__=['ping_host']

def ping_host(hostname, timeout):
    """ Simple ping of a defined hostname.
    Calls system ping in a subprocess.
    This works in user mode whereas ICMP pings in Python only work in
    admin mode.

    Parameters:

      hostname:
        Address of the host to ping

      timeout:
        Timeout in seconds for the ping

    Returns:

        Returns True if Ping succeeded
    """
    
    if platform.system() == "Windows":
        command = "ping " + hostname + " -q -n 1 -w " + str(timeout * 1000)
    else:
        command = "ping -i " + str(timeout) + " -c 1 " + hostname

    #  TODO the following failed with Python 2.7
    # proccess = subprocess.Popen(command, stdout=subprocess.PIPE)
    # matches = re.match('.*time=([0-9]+)ms.*', proccess.stdout.read(), re.DOTALL)
    #if matches:
    #    return matches.group(1)
    #else:
    #    return False
    need_sh = False if  platform.system().lower()=="windows" else True

    # execute the ping command and discard text response
    FNULL = open(os.devnull, 'w')
    return subprocess.call(
        command, shell=need_sh, stdout=FNULL, stderr=subprocess.STDOUT) == 0

