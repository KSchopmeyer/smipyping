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
import time
import datetime
from smipyping._configfile import read_config
from mysql.connector import MySQLConnection

__all__ = ['PingTable', 'CsvPingTable']


class PingTable(object):
    """
    `PingID` int(11) unsigned NOT NULL AUTO_INCREMENT,
    `TargetID` int(11) unsigned NOT NULL,
    `Timestamp` datetime NOT NULL,
    `Status` varchar(255) NOT NULL,
    """

    def __init__(self, db_dict, db_type, verbose):
        """Constructor for PingTable"""
        self.db_dict = db_dict
        self.verbose = verbose
        self.db_type = db_type

    @classmethod
    def factory(cls, db_dict, db_type, verbose):
        """Factory method to select subclass based on database type.
           Currently the types sql and csv are supported.

           Returns instance object of the defined type.
        """

        inst = None
        if verbose:
            print('targetdata factory datafile %s dbtype %s verbose %s'
                  % (db_dict,
                     db_type,
                     verbose))
        if db_type == ('csv'):
            inst = CsvPingTable(db_dict, db_type, verbose)

        elif db_type == ('mysql'):
            inst = SQLPingTable(db_dict, db_type, verbose)
        else:
            ValueError('Invalid pingtable factory db_type %s' % db_type)

        if verbose:
            print('Resulting pingtable factory inst %r' % inst)

        return inst

    def __str__(self):
        """String info on tpingtable. TODO. Put more info her"""
        return ('count=%s' % len(self.targets_dict))

    def __repr__(self):
        """Rep of target data"""
        return ('Pingtable db_type %s, db_dict %s rep count=%s' %
                (self.db_type, self.db_dict))


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
            while f.read(1) != b"\n":  # Until EOL is found...
                f.seek(-2, 1)         # ...jump back, read byte plus one more.
            last = f.readline()       # Read last line.
            return last

    def append(self, target_id, status):
        """ Write a single record into the table"""
        ping_id = self.get_last_ping_id()
        with open(self.filename, 'a') as ping_file:
            print("%s,%s,%s,'%s'" % (ping_id, target_id,
                                     datetime.datetime.now(),
                                     status), file=ping_file)


class SQLPingTable(PingTable):
    def __init(self, filename, args):
        super(CsvPingTable, self).__init__(filename, args)

        self.connection = None

    def __init__(self, db_dict, dbtype, verbose):
        """Read the input file into a dictionary."""

        print('SQL Database type %s  verbose=%s' % (db_dict, verbose))
        super(SQLTargetsData, self).__init__(db_dict, dbtype, verbose)

        try:
            connection = MySQLConnection(host=db_dict['host'],
                                         database=db_dict['database'],
                                         user=db_dict['user'],
                                         password=db_dict['password'])

            if connection.is_connected():
                print('sql db connection established. host %s, db %s' %
                      (db_dict['host'], db_dict['database']))
            else:
                print('SQL database connection failed. host %s, db %s' %
                      (db_dict['host'], db_dict['database']))
                raise ValueError('Connection to database failed')
            self.connection = connection
        except Exception as ex:
            raise ValueError('Could not connect to sql database %r. '
                             ' Exception: %r'
                             % (db_dict, ex))

    def get_last_ping_id(self):
        return 9999

    def append(self, target_id, status):
        """
        Write a new record to the database
        """
        cursor = self.connection.cursor()
        try:
            ts = time.time()
            timestamp = \
                datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            add_record = ("Insert INOT Pings "
                          "(TargetID, Timestamp, Status) "
                          "VALUES (%s %s %s")
            data = (target_id, timestamp, status)
            cursor.execute(add_record, data)
            # cur.execute("INSERT INTO Pings VALUES (%s,%s)",(188,90))
            self.connection.commit()
        except:
            self.connection.rollback()
        cursor.close()
