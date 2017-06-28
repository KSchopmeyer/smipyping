#!/usr/bin/python
"""
Simple test to acquire the mysql database and get some table info
using sql connector
"""

from mysql.connector import MySQLConnection, Error
import argparse
from configparser import ConfigParser


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


# cursor.execute("desc table_name")
# print [columns[0] for column in cursor.fetchall()]

def connect(configfile, args):
    """ Connect to MySQL database """

    db_config = read_db_config(configfile, section='mysql')

    try:
        print('Connecting to MySQL database...')
        connection = MySQLConnection(**db_config)

        if connection.is_connected():
            print('connection established.')
        else:
            print('connection failed.')
            raise ValueError('Connection to database failed')

        if args.showtablenames:
            print('Tables in database:')
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            for (table_name,) in cursor:
                print('  %s' % table_name)
        else:
            print('args.table %s' % args.tables)
            table_list = []
            if args.tables[0] == "all":
                cursor = connection.cursor()
                cursor.execute("SHOW TABLES")
                for (table_name,) in cursor:
                    table_list.append(table_name)
            else:
                table_list.extend(args.tables)
                
            for table in table_list:
                print('Table: %s' % table)
                cursor = connection.cursor()
                if args.showcolumnnames:
                    cursor.execute('SHOW columns from %s' % table)
                    for column in cursor.fetchall():
                        print('   %s:%s:%s' % (column[0], column[1], column[2]))
                    #print([column[0] for column in cursor.fetchall()])
                    #print([column for column in cursor.fetchall()])
                    #   This does not work print(cursor.column_names)

                else:
                    cursor.execute('SELECT COUNT(*) FROM %s' % table)
                    res = cursor.fetchone()
                    total_rows = res[0]
                    print('Rows in table=%s' % total_rows)
                    if table != "Pings":
                        cursor.execute('SELECT * FROM %s' % table)
                        rows = cursor.fetchall()
                        for row in rows:
                            print(row)

    except Error as error:
        print(error)

    finally:
        cursor.close()
        connection.close()
        print('Connection closed.')


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
    connect(configfile, args)


if __name__ == '__main__':
    main()
