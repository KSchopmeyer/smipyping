#!/usr/bin/python
"""
Simple test to acquire the mysql database and get some table info
using sql connector
"""

from mysql.connector import MySQLConnection, Error
import argparse
from configparser import ConfigParser
from collections import OrderedDict
from pprint import pprint as pp  # noqa: F401
from smipyping import SimplePing

def read_db_config(filename, section):
    """
    Read database configuration file and return a dictionary object

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

def get_companies(dbconnection, args):
    """
    Return an ordered dictionary of information from the company table.
    The key is the db key

    """
    print('Companies')
    cursor = dbconnection.cursor()
    cursor.execute('SELECT * FROM Companies')
    row = cursor.fetchone()
    company_dict = OrderedDict()
    row = cursor.fetchone()
    while row is not None:
        company_dict[row[0]] = row[1]
        row = cursor.fetchone()
    # cursor.close()
    return company_dict

def get_company(company_id, company_dict):
    """
    Get the entry for a key from the company table
    """
    return company_dict[company_id]

def fetch_one(cursor):
    row = cursor.fetchone()
    if row is None:
        return None
    cols = [d[0] for d in cursor.description]
    return dict(zip(cols, row))

def get_providers(dbconnection, args):
    """Build dictionary of information from the Targets table"""
    cursor = dbconnection.cursor()
    cursor.execute('SELECT * FROM Targets')
    #target_dict = OrderedDict()
    row = fetch_one(cursor)
    targets_dict = OrderedDict()
    if row is None:
        return None
    while row is not None:
        pp(row)
        target_id = row['TargetID']
        targets_dict[target_id] = row
        row = fetch_one(cursor)

    return targets_dict


def dbconnect(configfile, args):
    """Connect to the database defined by the config file and return the
    connection object
    """
    db_config = read_db_config(configfile, section='mysql')

    try:
        print('Connecting to MySQL database...')
        connection = MySQLConnection(**db_config)

        if connection.is_connected():
            print('connection established.')
        else:
            print('connection failed.')
            raise ValueError('Connection to database failed')
        print('connection %r' % connection)
        return connection
    except Error as error:
        raise ValueError("Db connect failed")

def test_server(target_dict):
    """
    Test a single server. Input is defined by a dictionary of target
    information
    """
    print('Test server target %s' % target_dict['IPAddress'])
    if target_dict['ScanEnabled'] == 'Enabled':
        print('%s to be tested' % target_dict['IPAddress'])
    

def run_test(configfile, args):
    """
        Run test of all servers in the targets database
    """
    connection = dbconnect(configfile, args)

    print("connection established")

    companies = get_companies(connection, args)
    pp(companies)

    targets = get_providers(connection, args)
    # pp.pprint(targets)
    for target_key in targets:
        test_server(targets[target_key])

    connection.close()
    print('Connection closed.')


def main():
    parser = argparse.ArgumentParser(description='Get config file.')
    parser.add_argument('configfile', metavar='CONFIGFILE', type=str,
                        nargs='?', default='localconfig',
                        help='Config file to use. Default = "localconfig"')
    parser.add_argument(
        '-t', '--targets', action='append',
        help='List of target ids that are to be tested')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    if args.verbose:
        print(args)
    configfile = args.configfile + '.ini'
    run_test(configfile, args)


if __name__ == '__main__':
    main()


