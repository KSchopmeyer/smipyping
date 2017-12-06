#!/usr/bin/python
"""
Test using sqlalchemy to manage database
"""
from __future__ import print_function, absolute_import

import pprint

import argparse
from configparser import ConfigParser
from sqlalchemy import inspect

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
    print('PrimaryKey %s' % class_mapper(table).primary_key[0].name)
    primary_keys = [key.name for key in inspect(table).primary_key]
    # TODO how do I map the above into the query below. table.primary_key
    print('primary_keys list %s' % primary_keys)
    print('Table %s; count = %s' % (table.__table__,
                                    session.query(table).count()))


def print_companies(session, verbose=False):
    print_table_info(session, Company, verbose)
    if verbose:
        for row in session.query(Company, Company.CompanyID).all():
            print(row.Company)
            for target in row.Company.Targets:
                print(' TargetID=%s, IP=%s product=%s' % (target.TargetID,
                                                          target.IPAddress,
                                                          target.Product))


def row_as_dict(row):
    return {c.key: getattr(row, c.key)
            for c in inspect(row).mapper.column_attrs}


def row2dict(row):
    """Map a single row of an sqlalchemy declarative class query to
       a dictionary. NOTE: maps everything to string.  Does not account
       for types
    """
    d = {}
    for column in row.__table__.columns:
        d[column.name] = getattr(row, column.name)

    return d


def table2dict(table, session, id_field):
    d = {}
    row = session.query(table).first()
    print('row %s type %s' % (row, type(row)))
    value = row_as_dict(row)
    print('Primary key %s input %s' % (
        inspect(table).primary_key[0].name, id_field))
    key = value[id_field]
    d[key] = value
    return d

    for row in session.query(table).all():
        print('row %s type %s' % (row, type(row)))
        value = row_as_dict(row)
        key = value[id_field]
        d[key] = value
    return d


# Despite "doog adibies" answer has been accepted and I upvoted it since has
# been extremely helpful, there are a couple of notable issues in the algorithm:

# The sub-serialization of relationships stops at the first child
# (because of the premature addition to "found")
# It also serializes back relationships, which in most cases are not
#   desiderable (if you have a Father object with a relationship to Son with a
# configured backref, you will generate an extra Father node for each son in it,
# with the same data that the main Father object already provides!)

# To fix these issues, I defined another set() to track undesired back
# relationships and I moved the tracking of visited children later in the code.
# I also deliberately renamed variables in order to make more clear (of course
# IMO) what they represents and how the algorithm works and replaced the map()
# with a cleaner dictionary comprehension.

# The following is my actual working implementation, which has been tested
# against nested objects of 4 dimensions (User -> UserProject ->
# UserProjectEntity -> UserProjectEntityField):
def model_to_dict2(obj, visited_children=None, back_relationships=None):
    if visited_children is None:
        visited_children = set()
    if back_relationships is None:
        back_relationships = set()
    serialized_data = {c.key: getattr(obj, c.key) for c in obj.__table__.columns}
    relationships = class_mapper(obj.__class__).relationships
    visitable_relationships = [(name, rel) for name, rel in relationships.items() if name not in back_relationships]
    for name, relation in visitable_relationships:
        if relation.backref:
            back_relationships.add(relation.backref)
        relationship_children = getattr(obj, name)
        if relationship_children is not None:
            if relation.uselist:
                children = []
                for child in [c for c in relationship_children if c not in visited_children]:
                    visited_children.add(child)
                    children.append(model_to_dict2(child, visited_children,
                                                   back_relationships))
                serialized_data[name] = children
            else:
                serialized_data[name] = model_to_dict2(relationship_children,
                                                       visited_children,
                                                       back_relationships)
    return serialized_data


def object_to_dict(obj, depth=0, found=None):
    """
    Uses the relationships property of the mapper. The code choices depend
    on how you want to map your data and how your relationships look. If you
    have a lot of recursive relationships, you may want to use a max_depth
    counter. My example below uses a set of relationships to prevent a
    recursive loop. You could eliminate the recursion entirely if you only
    plan to go down one in depth, but you did say "and so on".
    """
    # pfound = list(found) if found else 'none'
    #print('object_to_dict %s\nfound: %s' % (obj, pfound))
    if found is None:
        found = set()
    mapper = class_mapper(obj.__class__)
    # columns = [column.key for column in mapper.columns]
    # print('columns %s' % columns)
    # TODO convert this one to something more logical.
    # get_key_value = lambda c: (c, getattr(obj, c).isoformat()) if isinstance(getattr(obj, c), DateTime) else (c, getattr(obj, c))
    # out = dict(map(get_key_value, columns))
    out = {c.key: getattr(obj, c.key)
           for c in inspect(obj).mapper.column_attrs}
    # print('out %s' % out)
    if depth > 0:
        return out
    depth += 1
    x = []
    for name, relation in mapper.relationships.items():
        x.append('%s/%s:%s, ' % (name, relation, (relation in found)))
    for name, relation in mapper.relationships.items():
        if relation not in found:
            found.add(relation)
            related_obj = getattr(obj, name)
            if related_obj is not None:
                if relation.uselist:
                    out[name] = [object_to_dict(child, depth, found) for child in related_obj]
                else:
                    out[name] = object_to_dict(related_obj, depth, found)
    # print('Returns out %s' % out)
    return out


def print_targets(session, verbose=False):
    print_table_info(session, Target, verbose)
    pp = pprint.PrettyPrinter(indent=4)

    # row = session.query(Target).first()
    # print('row: %s' % row)

    # print('ObjectasDict: %s' % row_as_dict(row))
    # row_dict = object_to_dict(row)
    # print('object_to_dict: %s' % object_to_dict(row))
    # print('id %s comp %s' % (row_dict['TargetID'], row_dict['company']['CompanyName']))
    # return

    for row in session.query(Target).all():
        # print('row: %s' % row)
        # print('ObjectasDict: %s' % row_as_dict(row))
        row_dict = object_to_dict(row)
        # print('object_to_dict: %s' % row_dict)
        pp.pprint(row_dict)
        print('id %s comp %s' % (row_dict['TargetID'],
                                 row_dict['company']['CompanyName']))

    return

    # print('targets_as_dict\n%s' % targets_as_dict(session))

    #d = table2dict(Target, session, 'TargetID')
    #pp.pprint(d)

    # for row in session.query(Target, Target.TargetID).all():

    #return d

    if verbose:
        print('Targets Dict\n%s' % session)
        for row in session.query(Target, Target.TargetID).all():
            print('Target: %s\nCompany (%s)' % (row.Target, row.Target.company))
            it = row._asdict()
            row_dict = object_to_dict(row)
            pp.pprint(row_dict)
            # pp = pprint.PrettyPrinter(indent=4)
            # pp.pprint(it)
            # print('Try target %s' % it[Target])


def print_targets_user_pw(session, verbose=False):
    group = []
    for row in session.query(Target, Target.TargetID).all():
        data = row.__dict__['Target']
        print('data %s' % data)
        CompanyName = data.company.CompanyName
        CompanyName = CompanyName.replace(' ', '_')
        Principal = data.Principal
        Credential = data.Credential
        tup = (CompanyName, Principal, Credential)
        group.append(tup)
    group = set(group)
    group = sorted(group, key=lambda tup: tup[0])
    print("Company   User   PW")
    for item in group:
        print('%s %s %s' % (item[0], item[1], item[2]))


def print_previous_scans(session, verbose=False):
    print_table_info(session, PreviousScan, verbose)

    if verbose:
        for row in session.query(PreviousScan, PreviousScan.ScanID).all():
            print(row.PreviousScan)


def print_lastscan(session, verbose=False):
    print_table_info(session, LastScan, verbose)

    for row in session.query(LastScan, LastScan.ScanID).all():
        print(row.LastScan)


def print_users(session, verbose=False):
    print_table_info(session, User, verbose)

    if verbose:
        for row in session.query(User, User.UserID).all():
            print(row.User, row.User.company)


def print_program(session, verbose=False):
    print_table_info(session, Program, verbose)

    if verbose:
        for row in session.query(Program, Program.ProgramID).all():
            print(row)


def print_notifications(session, verbose=False):
    print_table_info(session, Notification, verbose)

    if verbose:
        for row in session.query(Notification,
                                 Notification.NotificationID).all():
            print(row)


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

    print('oldest record; %s' %
          (session.query(Ping).first()))

    print('Newest records')
    rows = session.query(Ping).order_by(-Ping.PingID).limit(60).all()

    for row in rows:
        print(row)

    #session.query(Ping).order_by(-Ping.PingID).first()))


def display_tables(configfile, args):
    """
    Test the defined tables and database
    """
    db_config = get_dbconfig(configfile, section=DBTYPE)
    session = create_sqlalchemy_session(db_config, echo=args.verbose)

    for table in args.tables:
        if table == 'Companies':
            print_companies(session, verbose=args.details)
        elif table == 'Targets':
            print_targets(session, verbose=args.details)
        elif table == 'Users':
            print_users(session, verbose=args.details)
        elif table == 'PreviousScans':
            print_previous_scans(session, verbose=args.details)
        elif table == 'LastScans':
            print_lastscan(session, verbose=args.details)
        elif table == 'Pings':
            print_pings(session, verbose=args.details)
        elif table == 'Program':
            print_program(session, verbose=args.details)
        elif table == 'Notifications':
            print_notifications(session, verbose=args.details)

        elif table == "all":
            print_companies(session, verbose=args.details)
            print_targets(session, verbose=args.details)
            print_previous_scans(session, verbose=args.details)
            print_lastscan(session, verbose=args.details)
            print_pings(session, verbose=args.details)
            print_users(session, verbose=args.details)

        elif table == 'userpw':
            print_targets_user_pw(session, verbose=args.details)

        else:
            print('Table %s Not found' % table)
            raise ValueError('Table %s Not found' % table)


def display_table_names(configfile, args):

    db_config = get_dbconfig(configfile, section=DBTYPE)
    engine = create_sqlalchemy_engine(db_config, echo=args.details)
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
    parser.add_argument('-d', '--details', action='store_true',
                        help='If false, show only overview info on tables in '
                        '-t and database. If True, list entries in tables')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='If True show sql, etc.')
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
