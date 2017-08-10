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
Common functions to implement logging and logginf configuration using the
python logging module.

This code uses named loggers to separate logging into separate functionality
Each component can implement a separate logger with separate logging
capabilities.

"""
from __future__ import print_function, absolute_import

import logging
# import inspect
# from decorator import decorate

# from ._constants import API_LOGGER_NAME
API_LOGGER_NAME = 'smipyping.api'
EXPLORE_LOGGER_NAME = 'smicli.explore'
CIMPING_LOGGER_NAME = 'smicli.cimping'
SWEEP_LOGGER_NAME = 'smicli.sweep'

LOG_COMPONENTS = ['explore', 'cimping', 'sweep', 'all']

# possible log output destinations
LOG_DESTINATIONS = ['file', 'stderr', 'none']
DEFAULT_LOG_LEVEL = 'debug'

LOG_LEVELS = ['error', 'warning', 'info', 'debug']
__all__ = ['SmiPypingLoggers', 'LOG_DESTINATIONS', 'LOG_LEVELS',
           'API_LOGGER_NAME', 'EXPLORE_LOGGER_NAME', 'CIMPING_LOGGER_NAME',
           'DEFAULT_LOG_LEVEL', 'SWEEP_LOGGER_NAME']


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


class SmiPypingLoggers(object):
    """
    Create named loggers for smipyping
    """
    loggers = {}
    prog = 'smicli'

    @classmethod
    def __repr__(cls):
        return 'PywbemLoggers(loggers={s.loggers!r})'.format(s=cls)

    @classmethod
    def reset(cls):
        """Reset the logger dictionary. Used primarily in unittests"""
        cls.loggers = {}

    @classmethod
    def create_logger(cls, log_component, log_dest=None,
                      log_filename=None, log_level='debug'):
        """
        Create a named logger

        parameters:
          log_component - Name of the logging component. The logger is
          created with smipyping/log_component as its name

          log_dest - For now only file is allowed

          log_filename - name of the log output file

          log_level - Log level at which this named component is to be
          logged

          Exceptions:
            ValueError if there is an issue with any of the input parameters
        """
        if log_dest == 'stderr':
            handler = logging.StreamHandler()
            format_string = '%(asctime)s-%(name)s-%(message)s'
        elif log_dest == 'file':
            if not log_filename:
                raise ValueError('Filename required if log destination '
                                 'is "file"')
            handler = logging.FileHandler(log_filename)
            format_string = '%(asctime)s-%(name)s-%(message)s'
        else:
            # TODO reinsert this test ks assert(log_dest == 'none')
            handler = None
            format_string = None

        # Set the log level based on the log_level input
        if log_level:
            level = getattr(logging, log_level.upper(), None)
            # check logging log_level_choices have not changed from expected
            assert isinstance(level, int)
            if level is None:
                raise ValueError('Invalid log level %s specified. Must be one '
                                 'of %s.' % (log_level, LOG_LEVELS))
        else:
            handler = None

        logger_name = '%s.%s' % (cls.prog, log_component)
        # create named logger
        if handler:
            handler.setFormatter(logging.Formatter(format_string))
            logger = logging.getLogger(logger_name)
            logger.addHandler(handler)
            logger.setLevel(level)

        # save the detail level in the dict that is part of this class.
        # All members of this tuple are just viewing except detail
        # that is used by individual loggers
        cls.loggers[logger_name] = (log_level, log_dest, log_filename)
