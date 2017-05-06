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
    smicli config file manager
"""

from __future__ import print_function, absolute_import

from click_configfile import ConfigFileReader, Param, SectionSchema
from click_configfile import matches_section
import click

from .config import DEFAULT_SMI_CLI_CONFIG_FILES


class ConfigSectionSchema(object):
    """Describes all config sections of this configuration file."""

    @matches_section("general")
    class General(SectionSchema):
        """ General info Section schema.
        TODO Clean this one up
        """
        name = Param(type=str)
        flag = Param(type=bool, default=True)
        numbers = Param(type=int, multiple=True)
        filenames = Param(type=click.Path(), multiple=True)
        dbtype = Param(type=str)

    @matches_section("csv")
    class Csv(SectionSchema):
        """ Database config section schema """
        filename = Param(type=str)

    @matches_section("mysql")
    class Mysql(SectionSchema):
        """ Database config section schema """
        host = Param(type=str)
        database = Param(type=str)
        user = Param(type=str)
        password = Param(type=str)

    @matches_section("logging")
    class Logging(SectionSchema):
        """ Logging config section schema"""
        name = Param(type=str)
        loglevel = Param(type=str)


class ConfigFileProcessor(ConfigFileReader):
    config_files = DEFAULT_SMI_CLI_CONFIG_FILES
    config_section_schemas = [
        ConfigSectionSchema.General,     # PRIMARY SCHEMA
        ConfigSectionSchema.Csv,
        ConfigSectionSchema.Mysql,
        ConfigSectionSchema.Logging
    ]

    # -- ALTERNATIVES: Override ConfigFileReader methods:
    #  * process_config_section(config_section, storage)
    #  * get_storage_name_for(section_name)
    #  * get_storage_for(section_name, storage)


# -- COMMAND:
CONTEXT_SETTINGS = dict(default_map=ConfigFileProcessor.read_config())

# @click.command(context_settings=CONTEXT_SETTINGS)
# @click.option("-n", "--number", "numbers", type=int, multiple=True)
# @click.pass_context
# def command_with_config(ctx, numbers):
#     # -- ACCESS ADDITIONAL DATA FROM CONFIG FILES: Using ctx.default_map
#     for person_data_key in ctx.default_map.keys():
#         if not person_data_key.startswith("person."):
#             continue
#         person_data = ctx.default_map[person_data_key]
#         process_person_data(person_data)    # as dict.
