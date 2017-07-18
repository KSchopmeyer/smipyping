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


def xstr(s):
    return 'None' if s is None else s


class ClickContext(object):
    """
        Manage the click context object
    """

    def __init__(self, ctx, config_file, db_type, db_info, log_level, log_file,
                 target_data, verbose):
        self._config_file = config_file
        self._db_type = db_type
        self._db_info = db_info
        self._verbose = verbose
        self._log_level = log_level
        self._log_file = log_file
        self._target_data = target_data
        self._spinner = click_spinner.Spinner()

    def __repr__(self):
        return 'config_file=%s, db_type=%s, db_info=%s log_level=%s ' \
               'log_file=%s verbose=%s' % \
               (xstr(self.config_file), xstr(self.db_type), self.db_info,
                xstr(self.log_level), xstr(self.log_file),
                self.verbose)

    @property
    def config_file(self):
        """
        :term:`string`: Name of the config file used.
        """
        return self._config_file

    @property
    def db_type(self):
        """
        :term:`string`: Type of db used.
        """
        return self._db_type

    @property
    def db_info(self):
        """
        :term:`dict`: Detailed info on db used. Varies by db type.
        """
        return self._db_info

    @property
    def verbose(self):
        """
        :term:`bool`: verbose display flag
        """
        return self._verbose

    @property
    def log_level(self):
        """
        :term:`bool`: verbose display flag
        """
        return self._log_level

    @property
    def log_file(self):
        """
        :term:`bool`: verbose display flag
        """
        return self._log_file

    @property
    def target_data(self):
        """
        :term:`target_data file`: Dictionary of provider data
        """
        return self._target_data

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
        if self._target_data is None:
            raise click.ClickException("No provider targets database defined")
        self.spinner.start()
        try:
            cmd()
        finally:
            self.spinner.stop()
