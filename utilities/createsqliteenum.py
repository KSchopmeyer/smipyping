#!/usr/bin/python
from sqlalchemy import create_engine, Enum
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.types import Enum, DateTime, Date

Base = declarative_base()
e = Enum('foo', 'bar')

class Company(Base):
    __tablename__ = 'Companies'
    CompanyID = Column(Integer(11), primary_key=True)
    CompanyName = Column(String(30), nullable=False)
    Notify = Column(Enum('Enabled', 'Disabled'), default='Disabled')

    def __repr__(self):
        return("CompanyID=%s; CompanyName='%s'" % (self.CompanyID,
                                                   self.CompanyName))

engine = create_engine('sqlite:///:memory:', echo=True)
Base.metadata.create_all(bind=engine)
