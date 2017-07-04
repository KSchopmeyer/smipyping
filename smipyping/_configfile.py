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
Read the config file.. This is a temporary tool for some of the command line
tools.  It will be replaced with the common config for the click based tools
"""
from __future__ import print_function, absolute_import

from configparser import ConfigParser


def read_config(filename, section, verbose=False):
    """
    Read configuration file for section and return a dictionary object if that
    section is found. If the section is not found, a TypeError is raised

    :param filename: name of the configuration file
    :param section: name of the section (ex. mysql)
    :return: a dictionary of parameters in that section

    Exception: Returns ValueError if the section defined not in config file

    """
    # create parser and read ini configuration file
    if verbose:
        print('read_configfile name %s, section %s' % (filename, section))
    parser = ConfigParser()
    parser.read(filename)

    # get section
    result = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            result[item[0]] = item[1]
    else:
        raise ValueError('{0} not found in the {1} file'.format(section,
                                                                filename))
    return result
