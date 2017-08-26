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
from __future__ import absolute_import

from .config import *  # noqa: F401,F403
# core classes and functions
from ._ping import *  # noqa: F401,F403
from ._tableoutput import *  # noqa: F401,F403

from ._common import *  # noqa: F401,F403
from ._logging import *  # noqa: F401,F403
from ._common_options import *  # noqa: F401,F403

# Database data sources
from ._targetdata import *  # noqa: F401,F403
from ._lastscantable import *  # noqa: F401,F403
from ._pingstable import *  # noqa: F401,F403
from ._companiestable import *  # noqa: F401,F403
from ._userstable import *  # noqa: F401,F403
from ._notificationstable import *  # noqa: F401,F403
from ._previousscanstable import *  # noqa: F401,F403
from ._programstable import *  # noqa: F401,F403

# TODO should drop _cliutils
from ._cliutils import *  # noqa: F401,F403
from ._scanport_syn import *  # noqa: F401,F403
from ._scanport_tcp import *  # noqa: F401,F403

# support for particular script cmds
from ._simpleping import *  # noqa: F401,F403
from ._explore import *  # noqa: F401,F403
from ._serversweep import *  # noqa: F401,F403
from ._targetdatacli import *  # noqa: F401,F403

from ._cimreport import *  # noqa: F401,F403


# smicli support libraries
from .smicli import *  # noqa: F401,F403
from ._click_context import *  # noqa: F401,F403
from ._cmd_targets import *  # noqa: F401,F403
from ._cmd_provider import *  # noqa: F401,F403
from ._cmd_explorer import *  # noqa: F401,F403
from ._cmd_cimping import *  # noqa: F401,F403
from ._cmd_sweep import *  # noqa: F401,F403

from ._click_configfile import *  # noqa: F401,F403

from ._version import *  # noqa: F401,F403
