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
Declarations of the smipyping database tables in SQLAlchemy, ORM
This declares 5 tables
    Company
    Target
    User
    Ping
    Program
    LastScan
    PreviousScan
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.types import Enum, DateTime, Date
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
# from sqlalchemy import inspect

try:
    from sqlalchemy.orm import class_mapper, object_mapper
except ImportError:
    from sqlalchemy.orm.util import class_mapper, object_mapper


def create_sqlalchemy_session(db_config, echo=None):
    """
    Create the sql_alchemy session and return the session.

    Parameters:

        echo: Boolean. Set to true to show sql generated.

    Returns:
        configured "Session" class
    """
    session = sessionmaker()
    engine = create_engine(db_config, echo=echo)
    session.configure(bind=engine)  # once engine is available
    return session()


def create_sqlalchemy_engine(db_config, echo=None):
    """Create and return an sqlalchemy enging"""
    engine = create_engine(db_config, echo=echo)
    return engine


Base = declarative_base()

#
#   Define the tables used which corresponds to the tables in the
#   database
#


class Company(Base):
    __tablename__ = 'Companies'
    CompanyID = Column(Integer(11), primary_key=True)
    CompanyName = Column(String(30), nullable=False)

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

    # Relationship to company table
    company = relationship("Company", backref="Targets")

    def __repr__(self):
        return('TargetID=%s; IPAddress=%s; CompanyID=%s; Namespace=%s;'
               ' SMIVersion=%s; Product=%s; Principal=%s; Credential=%s;'
               ' CimomVersion=%s; InteropNamespace=%s; Notify=%s;'
               ' NotifyUsers=%s; ScanEnabled=%s; Protocol=%s; Port=%s;'
               ' company=%s' %
               (self.TargetID, self.IPAddress, self.CompanyID, self.Namespace,
                self.SMIVersion, self.Product, self.Principal, self.Credential,
                self.CimomVersion, self.InteropNamespace, self.Notify,
                self.NotifyUsers, self.ScanEnabled, self.Protocol,
                self.Port, self.company))


class User(Base):
    __tablename__ = 'Users'
    UserID = Column(Integer(11), primary_key=True)
    Firstname = Column(String(30), nullable=False)
    Lastname = Column(String(30), nullable=False)
    Email = Column(String(50), nullable=False)
    CompanyID = Column(Integer, ForeignKey("Companies.CompanyID"))
    Active = Column(Enum('Active', 'Inactive'), nullable=False)
    Notify = Column(Enum('Enabled', 'Disabled'), nullable=False)

    # Relationship to Company
    company = relationship("Company", backref="Users")

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

    # relationship to the target that caused this ping. Note that we do
    # not use the backref on this one.
    target = relationship("Target")

    def __repr__(self):
        return('PingID=%s; TargetID=%s; Timestamp=%s; Status=%s' %
               (self.PingID, self.TargetID, self.Timestamp, self.Status))


class PreviousScan(Base):
    __tablename__ = 'PreviousScans'
    ScanID = Column(Integer, primary_key=True)
    TimeStamp = Column(DateTime, nullable=False)

    def __repr__(self):
        return('ScanID=%s, Timestamp=%s' % (self.ScanID, self.TargetID))


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
    NotifyID = Column(Integer, primary_key=True)
    NotifyTime = Column(DateTime, nullable=False)
    UserID = Column(Integer, ForeignKey("Users.UserID"))
    TargetID = Column(Integer(11), ForeignKey("Targets.TargetID"))
    Message = Column(String(100), nullable=False)

    # target = relationship("Target", backref="Notifications")
    # user = relationship("User", backref="Notifications")

    def __repr__(self):
        return(
            'NotificationID=%s, NotificationID=%s; UserID=%s; '
            ' TargetID=%s; Message=%s' % (self.NotificationID,
                                          self.NotificationID,
                                          self.UserID,
                                          self.TargetID,
                                          self.Message))
