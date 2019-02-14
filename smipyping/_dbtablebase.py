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
Table base common defines elements that apply to all of the database tables

This includes the magic functions, and common elements for accessing,
iterating, etc. the dictionaries that contain the elements.
"""


import six


class DBTableBase(object):
    """
        Common methods that apply to all of the db tables
    """

    table_name = ""  # name of the table db table that defines the class

    def __init__(self, db_dict, db_type, verbose):
        """
        Constructor for table


        Parameters:
          db_dict (:term: `dictionary')
            Dictionary containing all of the parameters to open the database
            defined by the db_dict attribute.

          db_type (:term: `string`)
            String defining one of the allowed database types for the
            target database.

          verbose (:class:`py:bool`)
            Boolean. If true detailed info is displayed on the processing
            of the TargetData class
        """
        self.db_dict = db_dict
        self.verbose = verbose
        self.db_type = db_type
        self.data_dict = {}

    def __str__(self):
        """String info on table. TODO. Put more info here"""
        return ('% len %s' % (self.table_name, len(self.data_dict)))

    def __repr__(self):
        """Rep of table data info. displays table name, length, etc."""
        return ('%s db_type %s db len %s' %
                (self.table_name, self.db_type, len(self.data_dict)))

    def __contains__(self, record_id):
        """Determine if record_id is in data dictionary."""
        return record_id in self.data_dict

    def __iter__(self):
        """iterator for table."""
        return six.iterkeys(self.data_dict)

    def iteritems(self):
        """
        Iterate through the property names (in their original lexical case).

        Returns key and value
        """
        for key, val in self.data_dict.iteritems():
            yield (key, val)

    def keys(self):
        """get all of the keys (normally the id field) as a list"""
        return list(self.data_dict.keys())

    def __getitem__(self, record_id):
        """Return the record for the defined record_id."""
        return self.data_dict[record_id]

    def __delitem__(self, record_id):
        """
        Delete an item from the current table. NOTE: We should not be
        using this.  Our approach is to delete the record in the database
        and reload the table.
        """
        del self.data_dict[record_id]

    def __len__(self):
        """Return number of items in the database dictionary"""
        return len(self.data_dict)
