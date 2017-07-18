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

import logging
import inspect
from decorator import decorate

# from ._constants import API_LOGGER_NAME
API_LOGGER_NAME = 'smipyping.api'
EXPLORE_LOGGER_NAME = 'smipyping.explore'
CIMPING_LOGGER_NAME = 'smipyping.cimping'

LOG_COMPONENTS = ['explore', 'cimping', 'all']

# possible log output destinations
LOG_DESTINATIONS = ['file', 'stderr', 'none']
DEFAULT_LOG_LEVEL = 'debug'

LOG_LEVELS = ['error', 'warning', 'info', 'debug']
__all__ = ['SmiPypingLoggers', 'LOG_DESTINATIONS', 'LOG_LEVELS',
           'API_LOGGER_NAME', 'EXPLORE_LOGGER_NAME', 'CIMPING_LOGGER_NAME',
           'DEFAULT_LOG_LEVEL']


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

    @classmethod
    def __repr__(cls):
        return 'PywbemLoggers(loggers={s.loggers!r})'.format(s=cls)

    @classmethod
    def reset(cls):
        """Reset the logger dictionary. Used primarily in unittests"""
        cls.loggers = {}

    @classmethod
    def create_logger(cls, log_component, log_dest='file',
                      log_filename=None, log_level='debug'):

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
            assert(log_dest == 'none')
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

        logger_name = 'smipyping' + log_component
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


def logged_api_call(func):
    """
    Function decorator that causes the decorated API function or method to log
    calls to itself to a logger.

    The logger's name is the dotted module name of the module defining the
    decorated function (e.g. 'zhmcclient._cpc').

    Parameters:

      func (function object): The original function being decorated.

    Returns:

      function object: The function wrappering the original function being
        decorated.

    Raises:

      TypeError: The @logged_api_call decorator must be used on a function or
        method (and not on top of the @property decorator).
    """

    # Note that in this decorator function, we are in a module loading context,
    # where the decorated functions are being defined. When this decorator
    # function is called, its call stack represents the definition of the
    # decorated functions. Not all global definitions in the module have been
    # defined yet, and methods of classes that are decorated with this
    # decorator are still functions at this point (and not yet methods).

    module = inspect.getmodule(func)
    if not inspect.isfunction(func) or not hasattr(module, '__name__'):
        raise TypeError("The @logged_api_call decorator must be used on a "
                        "function or method (and not on top of the @property "
                        "decorator)")

    try:
        # We avoid the use of inspect.getouterframes() because it is slow,
        # and use the pointers up the stack frame, instead.

        this_frame = inspect.currentframe()  # this decorator function here
        apifunc_frame = this_frame.f_back  # the decorated API function

        apifunc_owner = inspect.getframeinfo(apifunc_frame)[2]

    finally:
        # Recommended way to deal with frame objects to avoid ref cycles
        del this_frame
        del apifunc_frame

    # TODO: For inner functions, show all outer levels instead of just one.

    if apifunc_owner == '<module>':
        # The decorated API function is defined globally (at module level)
        apifunc_str = '{func}()'.format(func=func.__name__)
    else:
        # The decorated API function is defined in a class or in a function
        apifunc_str = '{owner}.{func}()'.format(owner=apifunc_owner,
                                                func=func.__name__)

    logger = get_logger(API_LOGGER_NAME)

    def log_api_call(func, *args, **kwargs):
        """
        Log entry to and exit from the decorated function, at the debug level.

        Note that this wrapper function is called every time the decorated
        function/method is called, but that the log message only needs to be
        constructed when logging for this logger and for this log level is
        turned on. Therefore, we do as much as possible in the decorator
        function, plus we use %-formatting and lazy interpolation provided by
        the log functions, in order to save resources in this function here.

        Parameters:

          func (function object): The decorated function.

          *args: Any positional arguments for the decorated function.

          **kwargs: Any keyword arguments for the decorated function.
        """

        # Note that in this function, we are in the context where the
        # decorated function is actually called.

        try:
            # We avoid the use of inspect.getouterframes() because it is slow,
            # and use the pointers up the stack frame, instead.

            this_frame = inspect.currentframe()  # this function here
            apifunc_frame = this_frame.f_back  # the decorated API function
            apicaller_frame = apifunc_frame.f_back  # caller of API function
            apicaller_module = inspect.getmodule(apicaller_frame)
            if apicaller_module is None:
                apicaller_module_name = "<unknown>"
            else:
                apicaller_module_name = apicaller_module.__name__
        finally:
            # Recommended way to deal with frame objects to avoid ref cycles
            del this_frame
            del apifunc_frame
            del apicaller_frame
            del apicaller_module

        # Log only if the caller is not from our package
        log_it = (apicaller_module_name.split('.')[0] != 'zhmcclient')

        if log_it:
            logger.debug("==> %s, args: %.500r, kwargs: %.500r",
                         apifunc_str, args, kwargs)
        result = func(*args, **kwargs)
        if log_it:
            logger.debug("<== %s, result: %.1000r", apifunc_str, result)
        return result

    return decorate(func, log_api_call)
