#!/usr/bin/env python
from __future__ import print_function, absolute_import

import argparse
import sys
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import make_url


def make_session(connection_string):
    engine = create_engine(connection_string, echo=False, convert_unicode=True)
    Session = sessionmaker(bind=engine)
    return Session(), engine


def pull_data(from_db, to_db, tables):
    source, sengine = make_session(from_db)
    smeta = MetaData(bind=sengine)
    destination, dengine = make_session(to_db)

    for table_name in tables:
        print('Processing %s' % table_name)
        print('Pulling schema from source server')
        table = Table(table_name, smeta, autoload=True)
        print('Creating table on destination server')
        table.metadata.create_all(dengine)
        NewRecord = quick_mapper(table)
        columns = table.columns.keys()
        print('Transferring records')
        for record in source.query(table).all():
            data = dict(
                [(str(column), getattr(record, column)) for column in columns]
            )
            destination.merge(NewRecord(**data))
    print('Committing changes')
    destination.commit()


def print_usage():
    print("""

"MYSQL://username:password@host:port/database_name"
Usage: %s -f source_server -t destination_server table [table ...]
    -f, -t = driver://user[:password]@host[:port]/database

Example: %s -f oracle://someuser:PaSsWd@db1/TSH1 \\
    -t mysql://root@db2:3307/reporting table_one table_two
    """ % (sys.argv[0], sys.argv[0]))


def quick_mapper(table):
    Base = declarative_base()

    class GenericMapper(Base):
        __table__ = table
    return GenericMapper


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get config file.')
    #parser.add_argument('configfile', metavar='CONFIGFILE', type=str,
    #                    nargs='?', default='localconfig',
    #                    help='Config file to use. Default = "localconfig"')

    parser.add_argument('-f', '--fromdb', type=str, required=True,
                        help='From database url')
    parser.add_argument('-t', '--todb', type=str, required=True,
                        help='To Database url')
    parser.add_argument('-T', '--tables', nargs='+', required=True,
                        help='Tables to duplicate')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='If True show sql, etc.')
    args = parser.parse_args()

    # if '-f' not in options or '-t' not in options or not tables:
    #if not args.from or not args.to or not args.tables
    #    print_usage()
    #    raise SystemExit, 1
    print('args %s' % args)
    from_url = make_url(args.fromdb)
    print('from_url %s' % from_url)

    pull_data(
        args.fromdb,
        args.todb,
        args.tables)

# from sqlalchemy.engine.url import make_url
# In [2]: url = make_url("urlstring")
#
