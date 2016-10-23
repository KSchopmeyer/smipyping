
from __future__ import absolute_import
import platform
import subprocess
import re

__all__=['ping_host']

def ping_host(hostname, timeout):
    """ Simple ping of a defined hostname.
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
        command = "ping " + hostname + " -n 1 -w " + str(timeout * 1000)
    else:
        command = "ping -i " + str(timeout) + " -c 1 " + hostname
    proccess = subprocess.Popen(command, stdout=subprocess.PIPE)
    matches = re.match('.*time=([0-9]+)ms.*', proccess.stdout.read(), re.DOTALL)
    if matches:
        return matches.group(1)
    else:
        return False

