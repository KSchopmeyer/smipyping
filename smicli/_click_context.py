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
Click context file. Used to communicate between click commands.

This defines the context object that is passed to each click command.
"""

from __future__ import absolute_import, unicode_literals

import click_spinner
import click
import smipyping


def xstr(s):  # pylint: disable=invalid-name
    """returns the input or 'None' to allow printing None"""
    return 'None' if s is None else s


class ClickContext(object):
    """
        Manage the click context object
    """

    def __init__(self, ctx, config_file, db_type, db_info, log, log_file,
                 log_components, targets_tbl, output_format, verbose):
        self._config_file = config_file
        self._db_type = db_type
        self._db_info = db_info
        self._verbose = verbose
        self._log = log
        # TODO fix log level
        self._log_level = None
        self._log_file = log_file
        self._log_components = log_components
        self._targets_tbl = targets_tbl
        self._output_format = output_format
        self._spinner = click_spinner.Spinner()

    def __repr__(self):
        return 'config_file=%s, db_type=%s, db_info=%s log_level=%s ' \
               'log_file=%s output_format=%s verbose=%s' % \
               (xstr(self.config_file), xstr(self.db_type), self.db_info,
                xstr(self.log_level), xstr(self.log_file),
                xstr(self.output_format), self.verbose)

    @property
    def config_file(self):
        """
        :term:`string`: Name of the config file used.
        """
        return self._config_file

    @property
    def db_type(self):
        """
        :term:`string`: Type of db used. This must be one of the strings
        defined by :data:`~smipyping.config.DB_POSSIBLE_TYPES`
        """
        return self._db_type

    @property
    def db_info(self):
        """
        :term:`dict`: Detailed info on db used. Varies by db type. This
        defines the configuration parameters for opening the db defined by
        db_type and the directory containing the directory for the
        config file.
        """
        # TODO this should have been named db_config
        return self._db_info

    @property
    def verbose(self):
        """
        :class:`py:bool`: verbose display flag
        """
        return self._verbose

    @property
    def log_level(self):
        """
        :class:`py:string`: string defining the log level
        """
        return self._log_level

    @property
    def log_file(self):
        """
        :class:`py:string`: Nname of file if log to file is specified
        """
        return self._log_file

    @property
    def log_components(self):
        """
        :class:`py:bool`: verbose display flag
        """
        return self._log_components

    @property
    def output_format(self):
        """
        :term:`string`: Output format defined for displaying data.
        """
        return self._output_format

    @property
    def targets_tbl(self):
        """
        :term:`targets_tbl file`: Handle of the Targets table.

        This is initialized late to allow help commands to execute without
        any database.
        """
        if self._targets_tbl:
            return self._targets_tbl
        try:
            targets_tbl = smipyping.TargetsTable.factory(
                self.db_info, self.db_type, self.verbose,
                output_format=self.output_format)
            self._targets_tbl = targets_tbl
            return self._targets_tbl
        except ValueError as ve:
            raise click.ClickException("Invalid database. Targets table "
                                       "load fails. Exception %s" % ve)

    @property
    def spinner(self):
        """
        :class:`~click_spinner.Spinner` object.
        """
        return self._spinner

    def execute_cmd(self, cmd):
        """
        Call the cmd executor defined by cmd with the spinner
        """
        self.spinner.start()
        try:
            cmd()
        finally:
            self.spinner.stop()
