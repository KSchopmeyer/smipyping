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
from __future__ import print_function, absolute_import

import sys
import logging
import inspect
from decorator import decorate
from .config import LOG_OPS_CALLS_NAME, LOG_HTTP_NAME

# from ._constants import API_LOGGER_NAME
API_LOGGER_NAME = 'smipyping.api'

# possible log output destinations
LOG_DESTINATIONS = ['file', 'stderr', 'none']

def get_logger(name):
    """
    Return a :class:`~py:logging.Logger` object with the specified name.

    A :class:`~py:logging.NullHandler` handler is added to the logger if it
    does not have any handlers yet. This prevents the propagation of log
    requests up the Python logger hierarchy, and therefore causes this package
    to be silent by default.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.addHandler(logging.NullHandler())
    return logger
