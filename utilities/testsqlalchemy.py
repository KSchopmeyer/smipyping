#!/usr/bin/python
"""
Test using sqlalchemy to manage database
"""

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


def create_dburl(configfile, section=DBTYPE, connector='mysql+mysqlconnector'):
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

    dburl = '%s://%s:%s@%s/%s' % (connector, user, password, host, database)
    print('dburl  %s' % dburl)

    return dburl


def create_sql_engine(configfile, section, echo=None):
    """
    Create the sql_alchemy engine and return the handle of the engine.

    Parameters:
        echo: Boolean. Set to true to show sql generated.

    Returns:
        configured "Session" class
    """
    Session = sessionmaker()
    engine = create_engine(create_dburl(configfile, section=DBTYPE), echo=echo)
    Session.configure(bind=engine)  # once engine is available
    return Session()


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
        return("<Companies(CompanyName='%s id %s')>" % (self.CompanyName,
                                                        self.CompanyID))


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
    company = relationship("Company", backref="targets")

    def __repr__(self):
        return('<Targets(TargetID=%s IPAddress=%s CompanyID=%s, Namespace=%s'
               ' SMIVersion=%s Product=%s Principal=%s Credential=%s'
               ' CimomVersion=%s InteropNamespace=%s Notify=%s NotifyUsers=%s'
               ' ScanEnabled=%s Protocol=%s Port=%s)>' %
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

    def __repr__(self):
        return('<Users(UserID=%s, Firstname=%s, Lastname=%s, Email=%s'
               'CompanyID=%s Active=%s,Notify=%s>' %
               (self.UserID, self.Firstname, self.Lastname, self.Email,
                self.CompanyID, self.Active, self.Notify))


class Ping(Base):
    __tablename__ = 'Pings'
    PingID = Column(Integer(11), primary_key=True)
    TargetID = Column(Integer(11), ForeignKey("Targets.TargetID"))
    Timestamp = Column(DateTime,  nullable=False)
    Status = Column(String(255), nullable=False)

    def __repr__(self):
        return('<Ping(PingID=%s, TargetID=%s, Timestamp=%s, Status=%s>' %
               (self.PingID, self.TargetID, self.Timestamp, self.Status))


class PreviousScan(Base):
    __tablename__ = 'PreviousScans'
    ScanID = Column(Integer, primary_key=True)
    TimeStamp = Column(DateTime, nullable=False)

    def __repr__(self):
        return('<PreviousScan(ScanID=%s, Timestamp=%s>' % (self.ScanID,
                                                           self.TargetID))


class LastScan(Base):
    __tablename__ = 'LastScan'
    ScanID = Column(Integer, primary_key=True)
    LastScan = Column(DateTime, nullable=False)

    def __repr__(self):
        return('<LastScan(ScanID=%s, LastScan=%s>' % (self.ScanID,
                                                      self.LastScan))


class Program(Base):
    __tablename__ = 'Program'
    ProgramID = Column(Integer, primary_key=True)
    ProgramName = Column(String(15), nullable=False)
    StartDate = Column(Date, nullable=False)
    EndDate = Column(Date, nullable=False)

    def __repr__(self):
        return(
            '<Program(ProgramID=%s, ProgramName=%s StartDate=%s '
            ' EndDate>' % (self.ProgramID,
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
            '<Notification(NotificationID=%s, NotificationID=%s UserID=%s '
            ' TargetID=% Message=%s>>' % (self.NotificationID,
                                          self.NotificationID,
                                          self.UserID,
                                          self.TargetID,
                                          self.Message))


# for instance in session.query(Company).order_by(Company.ID):
#    print(instance.CompanyName)

def print_company(session):
    print('Table %s' % Company.__table__)
    print('Companies count = %s' % session.query(Company).count())
    for row in session.query(Company, Company.CompanyName).all():
        print(row.Company)

def print_targets(session):
    print('Table %s' % Target.__table__)
    print('Targets count = %s' % session.query(Target).count())
    for row in session.query(Target, Target.TargetID).all():
        print('companyId %s' % row.Target.CompanyID)
        company = session.query(Company).filter(Company.CompanyID == row.Target.CompanyID).first()
        print('Company = %s' % company)
        print row.Target, company.CompanyName

def print_previous_scans(session):
    print('Table %s' % 'Table %s' % PreviousScan.__table__)
    print('PreviousScan count = %s' % session.query(PreviousScan).count())
    for row in session.query(PreviousScan, PreviousScan.ScanID).all():
        print row.PreviousScan

def print_lastscan(session):
    print('Table %s' % LastScan.__table__)
    print('LastScan count = %s' % session.query(LastScan).count())
    for row in session.query(LastScan, LastScan.ScanID).all():
        print row.LastScan

def print_users(session):

    print('Table %s' % User.__table__)
    print('Users count = %s' % session.query(User).count())
    for row in session.query(User, User.UserID).all():
        print row.User

def print_pings(session):

    print('Table %s' % Ping.__table__)
    print('Users count = %s' % session.query(Ping).count())
    for row in session.query(Ping, Ping.PingID).all():
        print row.User

def test_tables(configfile, args):
    """
    Test the defined tables and database
    """

    session = create_sql_engine(configfile, section=DBTYPE)

    for table in args.tables:
        if table == 'Companies':
            print_company(session)
        elif table == 'Targets':
            print_targets(session)
        elif table == 'Users':
            print('Table %s' % User.__table__)

        elif table == 'PreviousScans':
            print_previous_scans(session)

        elif table == 'LastScans':
            print_lastscan(session)

        elif table == 'Pings':
            print_Pings(session)            

        elif table == "all":
            print_company(session)
            print_targets(session)
            print_previous_scans(session)
            print_lastscan(session)
            print_pings(session)


        else:
            print('Table %s Not found' % table)
            raise ValueError('Table %s Not found' % table)


def main():
    parser = argparse.ArgumentParser(description='Get config file.')
    parser.add_argument('configfile', metavar='CONFIGFILE', type=str,
                        nargs='?', default='localconfig',
                        help='Config file to use. Default = "localconfig"')
    parser.add_argument('-t', '--tables', nargs='*',
                        default=['Companies'],
                        help='One or more table names. Default is Companies')
    parser.add_argument('-s', '--showtablenames', action='store_true',
                        help='List the names of all tables in the database.')
    parser.add_argument('-c', '--showcolumnnames', action='store_true',
                        help='List the names of all columns in each table.')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    if args.verbose:
        print(args)
    configfile = args.configfile + '.ini'
    test_tables(configfile, args)


if __name__ == '__main__':
    main()
