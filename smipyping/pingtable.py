#!/usr/bin/env python
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

"""Define the user base and its data"""

# TODO change ip_address to hostname where host name is name : port

from __future__ import print_function, absolute_import

import datetime
import six


__all__ = ['PingTable', 'CsvPingTable']


class PingTable(object):
    """
    `PingID` int(11) unsigned NOT NULL AUTO_INCREMENT,
    `TargetID` int(11) unsigned NOT NULL,
    `Timestamp` datetime NOT NULL,
    `Status` varchar(255) NOT NULL,
    """

    def __init__(self, filename, args):
        """Constructor for PingTable"""
        self.filename = filename
        self.args = args


class CsvPingTable(PingTable):
    """
        Ping Table functions for csv based table
    """
    def __init(self, filename, args):
        super(CsvPingTable, self).__init__(filename, args)

        print('init csvpingtable %s %s' % (self.filename, self.args))

    def get_last_ping_id(self):
        with open(file, "rb") as f:
            first = f.readline()      # Read the first line.
            f.seek(-2, 2)             # Jump to the second last byte.
            while f.read(1) != b"\n": # Until EOL is found...
                f.seek(-2, 1)         # ...jump back the read byte plus one more.
            last = f.readline()       # Read last line.
            return last

    def append(self, target_id, status):
        """ Write a single record into the table"""
        ping_id = self.get_last_ping_id()
        with open(self.filename, 'a') as ping_file:
            print("%s,%s,%s,'%s'" %(ping_id, target_id,
                                    datetime.datetime.now(),
                                    status), file=ping_file)

class SQLPingTable(PingTable):
    def __init(self, filename, args):
        super(CsvPingTable, self).__init__(filename, args)

    def get_last_ping_id(self):
        return 9999



