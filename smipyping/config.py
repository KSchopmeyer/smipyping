
"""
The :mod:`smipyping.config` module sets configuration variables for smipyping.

These configuration variables are used bysmipyping only after its modules
have been loaded, so they can be modified by the user directly after
importing :mod:`smipyping`. For example:

::

    import smipyping
    pywbem.config.ENFORCE_INTEGER_RANGE = False

Note that the source file of the :mod:`pywbem.config` module should not be
changed by the user. Instead, use the technique described above to modify
the variables.
"""

# This module is meant to be safe for 'import *'.

__all__ = ['ENFORCE_INTEGER_RANGE', 'DEFAULT_SWEEP_PORT', 'USERDATA_FILE',
           'PING_TEST_CLASS', 'SIMPLEPING_OPERATION_DEFAULT_TIMEOUT']

#: Enforce the value range in CIM integer types (e.g. :class:`~pywbem.Uint8`).
#:
#: * True (default): Enforce the value range; Assigning values out of range
#:   causes :exc:`~py:exceptions.ValueError` to be raised.
#: * False: Do not enforce the value range; Assigning values out of range
#:   works.
ENFORCE_INTEGER_RANGE = True

#: The default port used by the serversweep function in case no parameter is
#: provided. This is the DMTF defined https port.
DEFAULT_SWEEP_PORT = 5989

#: File name for user data
USERDATA_FILE = 'userdata_example.csv'

#: The class that is used in ping tests.
PING_TEST_CLASS = 'CIM_ComputerSystem'

PING_TIMEOUT = 2

#: Timeout in seconds for the WBEM operation
SIMPLEPING_OPERATION_DEFAULT_TIMEOUT = 20


