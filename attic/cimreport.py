#!/usr/bin/python
"""
Test using sqlalchemy to manage database
"""
from __future__ import print_function, absolute_import, division

import argparse
from configparser import ConfigParser
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
# from mysql.connector import MySQLConnection, Error
from sqlalchemy import Column, ForeignKey, Integer, String, cast
from sqlalchemy.types import Enum, DateTime, Date
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy import inspect

from _sql_alchemy_decls import create_sqlalchemy_session, \
    create_sqlalchemy_engine, Company, Target, User, Ping, PreviousScan, \
    LastScan, Program, Notification

#import smipyping


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
    print('Table %s; count = %s' % (table.__table__,
                                    session.query(table).count()))


def print_companies(session, verbose=False):
    print_table_info(session, Company, verbose)
    if verbose:
        for row in session.query(Company, Company.CompanyID).all():
            print(row.Company)
            for target in row.Company.targets_:
                print(' TargetID=%s, IP=%s product=%s' % (target.TargetID,
                                                          target.IPAddress,
                                                          target.Product))


def row_as_dict(row):
    print('inspect row %s' % inspect(row).mapper)
    return {c.key: getattr(row, c.key)
            for c in inspect(row).mapper.column_attrs}


def row2dict(row):
    """Map a single row of an sqlalchemy declarative class query to
       a dictionary. NOTE: maps everything to string.  Does not account
       for types
    """
    dict_ = {}
    for column in row.__table__.columns:
        dict_[column.name] = getattr(row, column.name)

    return dict_


def table2dict(table, session, id_field, rel=None):
    """
    Convert the sqlalchemy table defined  to a dictionary with the
    dictionary keys being identified by the id_field.

    Parameters:
        table - sqlalchemy declarative table class
        session - sqlalchemy session
        id_field - Name of the key_field in the table
        rel - TODO
    returns: Dictionary of dictionary for each target.  The TargetID is the
      key in the top level dictionary
    """
    dict_ = {}
    for row in session.query(table).all():
        value = row_as_dict(row)
        key = value[id_field]
        # TODO this one does not work
        #if rel:
        #    rel[0] = row.Target.CompanyName
        dict_[key] = value
    return dict_


def get_target_table(session, only_enabled=False, verbose=False):
    """
    Get the complete target table or only the enabled entries
    """
    # TODO why does it not expand the company????
    dict_ = table2dict(Target, session, 'TargetID', ["Company", "CompanyName"])

    return dict_

def get_company_table(session):
    """
        Get dictionary of companies
    """
    dict_ = table2dict(Company, session, 'CompanyID')

    return dict_

def count_pings_by_target_day(session, date, verbose=False):
    """
    """
    print_table_info(session, Ping, verbose)

    if verbose:
        print('Get pings for date %s' % date)
    counts_dict = {}
    # query for date provided
    for ping in session.query(Ping).filter(cast(Ping.Timestamp, Date) == date):
        p_int = 1 if ping.Status == 'OK' else 0

        if ping.TargetID in counts_dict.keys():
            counts_dict[ping.TargetID][0] += 1
            counts_dict[ping.TargetID][1] += p_int
        else:
            counts_dict[ping.TargetID] = [1, p_int]
    #convert to list and compute percentage
    rtn_list = []
    for key, value in counts_dict.items():
        percent = 0 if value[0] == 0 else (value[1] * 100) / value[0]
        list_ = [key, value[0], value[1], percent]
        rtn_list.append(list_)

    return rtn_list


def count_pings_by_target(session, start_date, end_date, verbose=False):
    """
    Count total and OK pings for date range provided by targetID.

    Creates a list containing a list of lists where each sublist entry
    contains
        [TargetID, Total for this targetId, OK for this target ID, percentage]
    """
    if verbose:
        print('Get pings for start_date %s end_date %s' %
              (start_date, end_date))

    # create dictionary by TargetID of the total count and OK count of pings
    counts_dict = {}
    for ping in session.query(Ping).filter(
            cast(Ping.Timestamp, Date).between(start_date, end_date)):
        p_int = 1 if ping.Status == 'OK' else 0
        if ping.TargetID in counts_dict.keys():
            counts_dict[ping.TargetID][0] += 1
            counts_dict[ping.TargetID][1] += p_int
        else:
            counts_dict[ping.TargetID] = [1, p_int]

    #convert to list and compute percentage
    rtn_list = []
    for key, value in counts_dict.items():
        list_ = [key, value[0], value[1], ((value[1] / value[0]) * 100)]
        rtn_list.append(list_)
    return rtn_list


def get_program_dates(session, program_id, verbose=False):
    """
        Get program start and end date for provided ProgramID
    """
    if verbose:
        print('Get Program for program id %s' % program_id)
    record = session.query(Program).filter(
        Program.ProgramID == program_id).first()

    if verbose:
        print('Program record %s' % record.StartDate)

    return (record.StartDate, record.EndDate)


def get_CompanyName(TargetID):
    """Get the company name for a defined TargetID"""
    pass


def main():
    parser = argparse.ArgumentParser(description='Print cim weekly report.')
    parser.add_argument('configfile', metavar='CONFIGFILE', type=str,
                        nargs='?', default='localconfig',
                        help='Config file to use. Default = "localconfig"')
    parser.add_argument('-e', '--email', action='store',
                        help='Email address to which report is maile. '
                             '(.e.g smilab\@snia.org')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output. Shows diagnostics')
    args = parser.parse_args()

    if args.verbose:
        print(args)
    configfile = args.configfile + '.ini'

    db_config = get_dbconfig(configfile, section=DBTYPE)
    session = create_sqlalchemy_session(db_config, echo=args.verbose)

    program_id = 11
    program_name = "SMI Lab 16"

    start_date, end_date = get_program_dates(session, program_id, args.verbose)
    print('Program start %s, end %s' % (start_date, end_date))

    target_counts = count_pings_by_target(session, start_date, end_date,
                                          args.verbose)

    # Add information on CompanyName, Product, SMIVersion, IP Address, Contacts

    targets_dict = get_target_table(session)
    company_dict = get_company_table(session)


    # sort by CompanyName
    list2 = []
    # add ipaddress, product contact
    for t in target_counts:
        if t[0] in targets_dict:
            target_record = targets_dict[t[0]]
            co_id = target_record['CompanyID']
            list2.append([company, t])
        else:
            print('id %s not in targets_dict' % t[0])

    list2.sort(key=lambda x: x[0])

    # do today and 7 day report

    # create html report
    for l in list2:
        print('%-20s %06.1f %6d' % (l[0], l[1][3], l[1][2],))


if __name__ == '__main__':
    main()
