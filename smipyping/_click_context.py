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
"""

from __future__ import absolute_import, unicode_literals

import click_spinner
import click


class ClickContext(object):
    """
        Manage the click context object
    """

    def __init__(self, ctx, config_file, target_data, verbose):
        self._config_file = config_file
        self._verbose = verbose
        self._target_data = target_data
        self._spinner = click_spinner.Spinner()

    @property
    def config_file(self):
        """
        :term:`string`: Name of the config file used.
        """
        return self._config_file

    @property
    def verbose(self):
        """
        :term:`bool`: verbose display flag
        """
        return self._verbose

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
