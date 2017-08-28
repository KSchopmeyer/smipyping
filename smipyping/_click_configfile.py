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
    smicli config file manager. These classes extend the click_configfile
    imported from click contrib.  They define the characteristics of the
    config file used including sections and parameters.
"""

from __future__ import print_function, absolute_import

from click_configfile import ConfigFileReader, Param, SectionSchema, \
    matches_section

from .config import DEFAULT_SMICLI_CONFIG_FILES


class ConfigSectionSchema(object):  # pylint: disable=too-few-public-methods
    """Describes all config sections of this configuration file."""

    @matches_section("general")  # pylint: disable=too-few-public-methods
    class General(SectionSchema):
        """
        General info Section schema. This is the primary schema and default
        mapping and in the map to dictionary every entry in this group shows
        up as a entry in the top level dictionary
        TODO can we use choices here.
        """
        name = Param(type=str)
        # flag = Param(type=bool, default=True)
        # numbers = Param(type=int, multiple=True)
        # filenames = Param(type=click.Path(), multiple=True)
        dbtype = Param(type=str)
        output_format = Param(type=str)

    @matches_section("csv")  # pylint: disable=too-few-public-methods
    class Csv(SectionSchema):
        """ Database config section schema. Defines the characteristcs of
            the csv file if that database type is specified
        """
        targetsfilename = Param(type=str)    # filename for targets csv file
        pingsfilename = Param(type=str)    # filename for pings csv file
        lastscanfilename = Param(type=str)    # filename for the csv file
        companiesfilename = Param(type=str)    # filename for the csv file
        notificationsfilename = Param(type=str)    # filename for the csv file
        usersfilename = Param(type=str)    # filename for the userscsv file

    @matches_section("mysql")  # pylint: disable=too-few-public-methods
    class Mysql(SectionSchema):
        """ Database config section schema for a mysql database """
        host = Param(type=str)        # host name
        database = Param(type=str)    # database name on the host
        user = Param(type=str)        # user name for db access
        password = Param(type=str)    # user password for db access

    @matches_section("sqlite")  # pylint: disable=too-few-public-methods
    class Sqlite(SectionSchema):
        """ Database config section schema. Defines the characteristcs of
            the csv file if that database type is specified
        """
        filename = Param(type=str)    # filename for the csv file

    @matches_section("log")  # pylint: disable=too-few-public-methods
    class Log(SectionSchema):
        """ Log config section schema"""
        # name = Param(type=str)
        log_file = Param(type=str)
        log_level = Param(type=str)


class ConfigFileProcessor(ConfigFileReader):
    """
    Subclass of ConfigFileReader specializes superclass for items like:
        -- section definitions
        -- config file locations
    """
    config_files = DEFAULT_SMICLI_CONFIG_FILES
    config_section_schemas = [
        ConfigSectionSchema.General,     # PRIMARY SCHEMA
        ConfigSectionSchema.Csv,
        ConfigSectionSchema.Mysql,
        ConfigSectionSchema.Log
    ]

    @classmethod
    def set_config_files(cls, config_files):
        """
        Set the config file from a list of possible config files

        Replaces the original config files defined with the class of
        DEFAULT_SMICLI_CONFIG_FILES.
        """
        cls.config_files = config_files

    @classmethod
    def set_search_path(cls, search_path):
        """
        Set the config file from a list of possible config files.

        A list of search paths.   Replaces the default search path of
        ["."]
        """
        cls.config_searchpath = search_path


def get_config_dict():
    """
    Get the dictionary that represents the config file.

    returns:
        Dictionary containing the mapped config file if the file esists and
        is valid

        None if the file does not exist.

    Exceptions:
        TODO

    """
    return dict(help_option_names=['-h', '--help'],
                default_map=ConfigFileProcessor.read_config())


# -- COMMAND:
CONTEXT_SETTINGS = get_config_dict()
