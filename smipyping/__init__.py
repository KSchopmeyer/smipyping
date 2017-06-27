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

The smipyping library API consists of the following elements:

* :ref:`Package version` - Provides access to the version of the ``smipyping``
  package.

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
from ._asciitable import *  # noqa: F401, F403
from ._targetdata import *  # noqa: F401, F403
from ._common import *  # noqa: F401, F403

# TODO should _cliutils
from ._cliutils import *  # noqa: F401, F403
from ._scanport import *  # noqa: F401, F403

# support for particular script cmds
from ._simpleping import *  # noqa: F401, F403
from ._explore import *  # noqa: F401, F403
from ._serversweep import *  # noqa: F401, F403
from ._targetdatacli import *  # noqa: F401, F403


# smicli support libraries
from .smicli import *  # noqa: F401, F403
from ._click_context import *  # noqa: F401, F403
from ._cmd_targets import *  # noqa: F401, F403
from ._cmd_provider import *  # noqa: F401, F403
from ._cmd_explorer import *  # noqa: F401, F403

from ._click_configfile import *  # noqa: F401, F403

from ._version import __version__  # noqa: F401, F403gy

_python_m = sys.version_info[0]  # pylint: disable=invalid-name
_python_n = sys.version_info[1]  # pylint: disable=invalid-name

if _python_m == 2 and _python_n < 7:
    raise RuntimeError('On Python 2, smipyping requires Python 2.7 or higher')
elif _python_m == 3 and _python_n < 4:
    raise RuntimeError('On Python 3, smipyping requires Python 3.4 or higher')
