
"""
The external API ofthis client library is defined by the symbols that
are exported from the ``smipyping`` Python package and its sub-modules via their
``__all__`` variables.

Public symbols that are not listed in the ``__all__`` variables are still
available for compatibility reasons. However, they may change over time.

Consumers of this package that use other symbols than those from the external
API are at the risk of suffering from incompatible changes in future versions
of this package.

The external API is completely available in the ``smipyping`` namespace. That
is the only namespace that needs to be imported by users of the API. The
sub-modules do not need to be imported. It is recommended to use the symbols
in the ``pywbem`` namespace and not those of the sub-modules.

With a few exceptions for tooling reasons, this documentation describes the
symbols of the ``smipyping`` namespace.

The WBEM client library API consists of the following elements:

* :ref:`Package version` - Provides access to the version of the ``smipyping``
  package.
* :ref:`WBEM operations` - Class :class:`WBEMConnection` is the main class of
  the WBEM client library and its methods issue WBEM operations to a WBEM
  server.

.. _`Package version`:

Package version
---------------

The package version can be accessed by programs using the following variable.

Note: For tooling reasons, the variable is shown in the namespace
``smipyping._version``. However, it is also available in the ``smipyping``
namespace and should be used from there.

.. autodata:: smipyping._version.__version__

"""

# There are submodules, but clients shouldn't need to know about them.
# Importing just this module is enough.
# These are explicitly safe for 'import *'

from __future__ import absolute_import

import sys

from .config import *  # noqa: F401, F403
# core classes and functions
from ._ping import *  # noqa: F401, F403
from ._csvtable import *  # noqa: F401, F403
from ._terminaltable import *  # noqa: F401, F403 
from ._targetdata import *  # noqa: F401, F403
from ._simpleping import *  # noqa: F401, F403
from ._explore import *  # noqa: F401, F403
from ._serversweep import *  # noqa: F401, F403
# TODO should not need this
from ._cliutils import *  # noqa: F401, F403
from ._targetdatacli import *  # noqa: F401, F403
from ._scanport import *  # noqa: F401, F403

# smicli support libraries
#from .smicli import *  # noqa: F401, F403
#from ._cmd_database import *  # noqa: F401, F403
#from ._cmd_provider import *  # noqa: F401, F403
#from ._cmd_explorer import *  # noqa: F401, F403
#from ._click_context import *  # noqa: F401, F403

from ._version import __version__  # noqa: F401, F403gy

_python_m = sys.version_info[0]  # pylint: disable=invalid-name
_python_n = sys.version_info[1]  # pylint: disable=invalid-name

if _python_m == 2 and _python_n < 7:
    raise RuntimeError('On Python 2, smipyping requires Python 2.7 or higher')
elif _python_m == 3 and _python_n < 4:
    raise RuntimeError('On Python 3, smipyping requires Python 3.4 or higher')
