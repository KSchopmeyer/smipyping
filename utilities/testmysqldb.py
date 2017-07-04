#!/usr/bin/python
"""
Simple test to acquire the mysql database and get some table info
using MySQLdb
"""

import MySQLdb

# Open database connection
db = MySQLdb.connect("localhost","kschopmeyer","test8play","SMIStatus" )

# prepare a cursor object using cursor() method
cursor = db.cursor()

# execute SQL query using execute() method.
cursor.execute("SELECT VERSION()")
# Fetch a single row using fetchone() method.
data = cursor.fetchone()
print "Database version : %s " % data

cursor = db.cursor()
# Prepare SQL query to INSERT a record into the database.
sql = "SELECT * FROM Companies"

try:
    cursor = db.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    for row in results:
        name = row[1]
        print("companies table %s %s" % (row[0], row[1]))
except:
    print "Error"

# disconnect from server
db.close()
