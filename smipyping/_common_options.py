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
Defines click options that are used for multiple subcommands and that have
the same definition throughout the environment.  This allows the characteristics
and help to be defined once and used multiple times.
"""
from __future__ import absolute_import

import click


def add_options(options):
    """
    Accumulate multiple options into a list. This list can be referenced as
    a click decorator @att_options(name_of_list)

    The list is reversed because of the way click processes options

    Parameters:

      options: list of click.option definitions

    Returns:
        Reversed list

    """
    def _add_options(func):
        """ Reverse options list"""
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options


# Common options
sort_option = [                            # pylint: disable=invalid-name
    click.option('-s', '--sort', is_flag=True, required=False,
                 help='Sort into alphabetical order by classname.')]

namespace_option = [                     # pylint: disable=invalid-name
    click.option('-n', '--namespace', type=str,
                 required=False, metavar='<name>',
                 help='Namespace to use for this operation. If not defined '
                      'all namespaces are used')]
