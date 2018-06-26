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
Table base common elements that apply to all of the tables
"""


import six


class DBTableBase(object):
    """
        Common methods that apply to all of the db tables
    """
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
        del self.data_dict[record_id]

    def __len__(self):
        """Return number of programs"""
        return len(self.data_dict)
