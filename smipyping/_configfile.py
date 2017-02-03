"""
Read the config file
"""
from __future__ import print_function, absolute_import

from configparser import ConfigParser
import six
from smipyping._terminaltable import print_terminal_table, fold_cell

__all__ = ['TargetsData']


def read_config(filename, section):
    """
    Read configuration file for section and return a dictionary object if that
    section is found. If the section is not found, a TypeError is raised

    :param filename: name of the configuration file
    :param section: name of the section (ex. mysql)
    :return: a dictionary of parameters in that section
    
    """
    # create parser and read ini configuration file
    parser = ConfigParser()
    parser.read(filename)

    # get section, default to mysql
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise TypeError('{0} not found in the {1} file'.format(section,
                                                               filename))

    return db
