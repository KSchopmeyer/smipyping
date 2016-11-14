#!/usr/bin/env python
##

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
        return 9999

    def append(self, target_id, status):
        """ Write a single record into the table"""
        ping_id = self.get_last_ping_id()
        with open(self.filename, 'a') as ping_file:
            print("%s,%s,%s,'%s'" %(ping_id, target_id,
                                    datetime.datetime.now(),
                                    status), file=ping_file)



