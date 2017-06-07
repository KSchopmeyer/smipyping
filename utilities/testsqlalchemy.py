#!/usr/bin/python
"""
Test using sqlalchemy to manage database
"""
from __future__ import print_function, absolute_import

import argparse
from configparser import ConfigParser
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
# from mysql.connector import MySQLConnection, Error
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.types import Enum, DateTime, Date
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship

CONFIG_FILE = 'dbconfig.ini'
DBTYPE = 'mysql'


def read_db_config(filename=CONFIG_FILE, section=DBTYPE):
    """ Read database configuration file and return a dictionary object
    :param filename: name of the configuration file
    :param section: section of database configuration
    :return: a dictionary of database parameters
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
        raise Exception('{0} not found in the {1} file'.format(section,
                                                               filename))

    return db


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


def create_sql_engine(configfile, section, echo=None):
    """
    Create the sql_alchemy session and return the session.

    Parameters:

        echo: Boolean. Set to true to show sql generated.

    Returns:
        configured "Session" class
    """
    Session = sessionmaker()
    engine = create_engine(get_dbconfig(configfile, section=DBTYPE), echo=echo)
    Session.configure(bind=engine)  # once engine is available
    return Session()


def create_sqlalchemy_engine(configfile, section, echo=None):
    engine = create_engine(get_dbconfig(configfile, section=DBTYPE), echo=echo)
    return engine


Base = declarative_base()

#
#   Define the tables used
#

# NOTES: for mysql it automatically sets auto_incrment


class Company(Base):
    __tablename__ = 'Companies'

    CompanyID = Column(Integer(11), primary_key=True)
    CompanyName = Column(String(30), nullable=False)

    targets_for_company = relationship("Target")

    def __repr__(self):
        return("CompanyID=%s; CompanyName='%s'" % (self.CompanyID,
                                                   self.CompanyName))


class Target(Base):
    __tablename__ = 'Targets'

    TargetID = Column(Integer(11), primary_key=True)
    IPAddress = Column(String(15), nullable=False)
    CompanyID = Column(Integer(11), ForeignKey("Companies.CompanyID"))
    Namespace = Column(String(30), nullable=False)
    SMIVersion = Column(String(15), nullable=False)
    Product = Column(String(30), nullable=False)
    Principal = Column(String(30), nullable=False)
    Credential = Column(String(30), nullable=False)
    CimomVersion = Column(String(30), nullable=False)
    InteropNamespace = Column(String(30), nullable=False)
    Notify = Column(Enum('Enabled', 'Disabled'), default='Disabled')
    NotifyUsers = Column(String(12), nullable=False)
    ScanEnabled = Column(Enum('Enabled', 'Disabled'), default='Enabled')
    Protocol = Column(String(10), default='http')
    Port = Column(String(10), nullable=False)

    # TODO what is diff between backref and back_populates.
    company = relationship("Company")

    def __repr__(self):
        return('TargetID=%s; IPAddress=%s; CompanyID=%s; Namespace=%s;'
               ' SMIVersion=%s; Product=%s; Principal=%s; Credential=%s;'
               ' CimomVersion=%s; InteropNamespace=%s; Notify=%s;'
               ' NotifyUsers=%s; ScanEnabled=%s; Protocol=%s Port=%s' %
               (self.TargetID, self.IPAddress, self.CompanyID, self.Namespace,
                self.SMIVersion, self.Product, self.Principal, self.Credential,
                self.CimomVersion, self.InteropNamespace, self.Notify,
                self.NotifyUsers, self.ScanEnabled, self.Protocol,
                self.Port))


class User(Base):
    __tablename__ = 'Users'
    UserID = Column(Integer(11), primary_key=True)
    Firstname = Column(String(30), nullable=False)
    Lastname = Column(String(30), nullable=False)
    Email = Column(String(50), nullable=False)
    CompanyID = Column(Integer, ForeignKey("Companies.CompanyID"))
    Active = Column(Enum('Active', 'Inactive'), nullable=False)
    Notify = Column(Enum('Enabled', 'Disabled'), nullable=False)

    # TODO what is diff between backref and back_populates.
    company = relationship("Company", backref="targets")

    def __repr__(self):
        return('UserID=%s; Firstname=%s; Lastname=%s; Email=%s;'
               'CompanyID=%s; Active=%s; Notify=%s' %
               (self.UserID, self.Firstname, self.Lastname, self.Email,
                self.CompanyID, self.Active, self.Notify))


class Ping(Base):
    __tablename__ = 'Pings'
    PingID = Column(Integer(11), primary_key=True)
    TargetID = Column(Integer(11), ForeignKey("Targets.TargetID"))
    Timestamp = Column(DateTime, nullable=False)
    Status = Column(String(255), nullable=False)

    # TODO what is diff between backref and back_populates.
    target = relationship("Target", backref="targets")

    def __repr__(self):
        return('PingID=%s; TargetID=%s; Timestamp=%s; Status=%s' %
               (self.PingID, self.TargetID, self.Timestamp, self.Status))


class PreviousScan(Base):
    __tablename__ = 'PreviousScans'
    ScanID = Column(Integer, primary_key=True)
    TimeStamp = Column(DateTime, nullable=False)

    def __repr__(self):
        return('ScanID=%s,\; Timestamp=%s' % (self.ScanID, self.TargetID))


class LastScan(Base):
    __tablename__ = 'LastScan'
    ScanID = Column(Integer, primary_key=True)
    LastScan = Column(DateTime, nullable=False)

    def __repr__(self):
        return('ScanID=%s, LastScan=%s' % (self.ScanID, self.LastScan))


class Program(Base):
    __tablename__ = 'Program'
    ProgramID = Column(Integer, primary_key=True)
    ProgramName = Column(String(15), nullable=False)
    StartDate = Column(Date, nullable=False)
    EndDate = Column(Date, nullable=False)

    def __repr__(self):
        return('ProgramID=%s; ProgramName=%s; StartDate=%s;  EndDate=%s' %
               (self.ProgramID,
                self.ProgramName,
                self.StartDate,
                self.EndDate))


class Notification(Base):
    __tablename__ = 'Notifications'
    NotificationID = Column(Integer, primary_key=True)
    NotifyTime = Column(DateTime, nullable=False)
    UserID = Column(Integer, ForeignKey("Userss.UserID"))
    TargetID = Column(Integer(11), ForeignKey("Targets.TargetID"))
    Message = Column(String(100), nullable=False)

    def __repr__(self):
        return(
            'NotificationID=%s, NotificationID=%s; UserID=%s; '
            ' TargetID=%s; Message=%s' % (self.NotificationID,
                                          self.NotificationID,
                                          self.UserID,
                                          self.TargetID,
                                          self.Message))


def print_table_info(session, table, verbose):
    print('Table %s; count = %s' % (table.__table__,
                                    session.query(table).count()))


def print_companies(session, verbose=False):
    print_table_info(session, Company, verbose)
    if verbose:
        for row in session.query(Company, Company.CompanyID).all():
            print(row.Company)
            #print('type row %s, row.Company %s' % (type(row),
            #                                    type(row.Company)))
            print('Target Relationships:')
            for target in row.Company.targets_for_company:
                print('  id=%s, product=%s' % (target.TargetID,
                                               target.Product))
            # print('targets type %s' % type(row.Company.targets_for_company))
            # targets type <class 'sqlalchemy.orm.collections.InstrumentedList'>
            # print('targets %s' % row.Company.targets_for_company)

# <Companies(CompanyName='Tintri id 33')>
# type row <class 'sqlalchemy.util._collections.KeyedTuple'>,
# row.Company <class '__main__.Company'>


def print_targets(session, verbose=False):
    print_table_info(session, Target, verbose)
    if verbose:
        for row in session.query(Target, Target.TargetID).all():
            print('Target: %s\nCompany (%s)' % (row.Target, row.Target.company))
            print(row._asdict())


def print_previous_scans(session, verbose=False):
    print_table_info(session, PreviousScan, verbose)

    if verbose:
        for row in session.query(PreviousScan, PreviousScan.ScanID).all():
            print(row.PreviousScan)


def print_lastscan(session, verbose=False):
    print_table_info(session, LastScan, verbose)
    if verbose:
        for row in session.query(LastScan, LastScan.ScanID).all():
            print(row.LastScan)


def print_users(session, verbose=False):
    print_table_info(session, User, verbose)

    if verbose:
        for row in session.query(User, User.UserID).all():
            print(row.User)


def print_pings(session, verbose=False):
    """
    Display info on Pings

    This does not show full output because of potential size since there
    may be thousands of ping results
    """
    print_table_info(session, Ping, verbose)

    # blocked because produces enormous output
    # if verbose:
    #    for row in session.query(Ping, Ping.PingID).all():
    #        print(row.Ping)

    print('oldest record; %s\nnewest record; %s' %
          (session.query(Ping).first(),
           session.query(Ping).order_by(-Ping.PingID).first()))


def display_tables(configfile, args):
    """
    Test the defined tables and database
    """

    session = create_sql_engine(configfile, section=DBTYPE)

    for table in args.tables:
        if table == 'Companies':
            print_companies(session, verbose=args.verbose)
        elif table == 'Targets':
            print_targets(session, verbose=args.verbose)
        elif table == 'Users':
            print_users(session, verbose=args.verbose)
        elif table == 'PreviousScans':
            print_previous_scans(session, verbose=args.verbose)
        elif table == 'LastScans':
            print_lastscan(session, verbose=args.verbose)
        elif table == 'Pings':
            print_pings(session, verbose=args.verbose)

        elif table == "all":
            print_companies(session, verbose=args.verbose)
            print_targets(session, verbose=args.verbose)
            print_previous_scans(session, verbose=args.verbose)
            print_lastscan(session, verbose=args.verbose)
            print_pings(session, verbose=args.verbose)
            print_users(session, verbose=args.verbose)

        else:
            print('Table %s Not found' % table)
            raise ValueError('Table %s Not found' % table)


def display_table_names(configfile, args):
    engine = create_sqlalchemy_engine(configfile, args)
    print ('Defined Table Names:')
    for name in engine.table_names():
        print('   %s' % name)


def main():
    parser = argparse.ArgumentParser(description='Get config file.')
    parser.add_argument('configfile', metavar='CONFIGFILE', type=str,
                        nargs='?', default='localconfig',
                        help='Config file to use. Default = "localconfig"')
    parser.add_argument('-t', '--tables', nargs='*',
                        default=['Companies'],
                        help='One or more table names. Default is Companies. '
                             '"all" means to show info on all tables.')
    parser.add_argument('-n', '--tablenames', action='store_true',
                        help='List the names of all tables in the database. '
                             'This option lists names and exits ')
    parser.add_argument('-c', '--showcolumnnames', action='store_true',
                        help='List the names of all columns in each table.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='If false, show only overview info on tables in '
                        '-t and database. If True, list entries in tables')
    args = parser.parse_args()

    if args.verbose:
        print(args)
    configfile = args.configfile + '.ini'
    if args.tablenames:
        display_table_names(configfile, args)
    else:
        display_tables(configfile, args)


if __name__ == '__main__':
    main()
