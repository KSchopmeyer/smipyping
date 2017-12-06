#!/usr/bin/python
"""
Remove entries from ping table for a particular program.  Also,
Display number of ping entries per day for particular program
"""
from __future__ import print_function, absolute_import

import argparse
from configparser import ConfigParser
from sqlalchemy import inspect
import pprint  # noqa: F401

try:
    from sqlalchemy.orm import class_mapper, object_mapper
except ImportError:
    from sqlalchemy.orm.util import class_mapper, object_mapper

from _sql_alchemy_decls import create_sqlalchemy_session, \
    create_sqlalchemy_engine, Company, Target, User, Ping, PreviousScan, \
    LastScan, Program, Notification

# from mysql.connector import MySQLConnection, Error


CONFIG_FILE = 'dbconfig.ini'
DBTYPE = 'mysql'


def read_db_config(filename=CONFIG_FILE, section=DBTYPE):
    """ Read database configuration file and return a dictionary object
    :param filename: name of the configuration file
    :param section: section of database configuration
    :return: a dictionary of configuration parameters
    """
    # create parser and read ini configuration file
    parser = ConfigParser()
    parser.read(filename)

    # get section, default to mysql
    db_dict = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db_dict[item[0]] = item[1]
    else:
        raise Exception('{0} not found in the {1} file'.format(section,
                                                               filename))

    return db_dict


def get_dbconfig(configfile, section=DBTYPE, connector='mysql+mysqlconnector'):
    """
    Create a url for the database connection from the config file  section
    defined in the call.

    Returns the url
    """
    db_config = read_db_config(filename=configfile, section=section)
    user = db_config['user']
    password = db_config['password']
    host = db_config['host']
    database = db_config['database']

    db_config = '%s://%s:%s@%s/%s' % (connector, user, password, host, database)
    print('db_config  %s' % db_config)

    return db_config


def print_table_info(session, table, verbose):
    # TODO, doing count with session.query(Segment.id).count() is much faster
    print('Table %s; count = %s' % (table.__table__,
                                    session.query(table).count()))


def print_program(session, verbose=False):

    print_table_info(session, Program, verbose)

    for row in session.query(Program, Program.ProgramID).all():
        print(row)

def get_programs_list(session):
    programlist = []
    pgm_id = []
    for row in session.query(Program, Program.ProgramID).all():
        # print('row %s, type %s' % (row, type(row)))
        rad = row.__dict__
        pgm = rad['Program']
        start_date = pgm.StartDate
        end_date = pgm.EndDate
        pgm_name = pgm.ProgramName
        id = pgm.ProgramID
        programlist.append('%s: %s: %s' % (pgm_name, start_date, end_date))
        pgm_id.append(id)

    index = pick_from_list(programlist, "pick a progam")

    return pgm_id[index]

def pick_from_list(options, title):
    """
    Interactive component that displays a set of options (strings) and asks
    the user to select one.  Returns the item and index of the selected string.

    Parameters:
      options:
        List of strings to select

      title:
        Title to display before selection

    Retries until either integer within range of options list is input
    or user enter no value. Ctrl_C ends even the REPL.

    Returns: Index of selected item

    Exception: Returns ValueError if Ctrl-c input from console.

    TODO: This could be replaced by the python pick library that would use
    curses for the selection process.
    """
    print(title)
    index = -1
    for str_ in options:
        index += 1
        print('%s: %s' % (index, str_))
    selection_txt = None
    while True:
        try:
            selection_txt = input(
                'Select an entry by index or enter Ctrl-C to exit >')
            if isinstance(selection_txt, int):
                return selection_txt
            if selection_txt.isdigit():
                selection = int(selection_txt)
                if selection >= 0 and selection <= index:
                    return selection
        except ValueError:
            pass
        except KeyboardInterrupt:
            raise ValueError
        print('%s Invalid. Input integer between 0 and %s or Ctrl-C to '
              'exit.' % (selection_txt, index))

def display_pings(session, program_id, args):
    """
    Display number of pings for a program
    """

    query = session.query(Program).filter(Program.ProgramID == program_id)

    result = query.first()
    if result is None:
        raise ValueError('Program_ID %s not in table' % program_id)
    start_date = result.StartDate
    end_date = result.EndDate
    pgm_name = result.ProgramName

    query = session.query(Ping).filter(
        Ping.Timestamp.between(start_date, end_date))

    result = query.all()
    print('program %s start %s end %s record count %s' % (pgm_name, start_date,
                                                          end_date,
                                                          len(result)))

def test_program_valid(session, program_id):
    """Test if program id in program table"""
    # print('testvalid program_id %s type=%s' % (program_id, type(program_id)))
    # rtn = session.query(Program).get(program_id)

    query = session.query(Program).filter(Program.ProgramID == program_id)

    if query.first() is None:
        raise ValueError('Program_ID %s not in table' % program_id)


def main():
    parser = argparse.ArgumentParser(description='Get config file.')
    parser.add_argument('configfile', metavar='CONFIGFILE', type=str,
                        nargs='?', default='localconfig',
                        help='Config file to use. Default = "localconfig"')

    parser.add_argument('-p', '--programs', action='store_true',
                        help='List programs.')
    parser.add_argument('-d', '--display', action='store_true',
                        help='Display pings per day for a program. Program selected from list ')
    parser.add_argument('-D', '--delete', action='store_true',
                        help='Delete pings for a program')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='If True show sql, etc.')
    args = parser.parse_args()

    if args.verbose:
        print(args)

    configfile = args.configfile + '.ini'

    db_config = get_dbconfig(configfile, section=DBTYPE)
    session = create_sqlalchemy_session(db_config, echo=args.verbose)

    if args.programs:
        print_program(session)

    elif args.display:
        program = get_programs_list(session)
        display_pings(session, program, args)
    else:
        print('whoops')


if __name__ == '__main__':
    main()
