#!/usr/bin/env python3
import getopt as go
import sys
import os
import time
import hashlib
import uuid
import sqlite3
import platform
from sqlite3 import Error

#Python 3


create_fileindex_table = """
CREATE TABLE IF NOT EXISTS fileindex (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  hdrive_uid TEXT NOT NULL,
  fname TEXT NOT NULL,
  path TEXT NOT NULL,
  hash TEXT NOT NULL,
  size INTEGER NOT NULL,
  UNIQUE(hdrive_uid,path,fname)

);
"""
create_fileindex = """
INSERT INTO
  `fileindex` (`hdrive_uid`, `fname`, `path`, `hash`,`size`)
VALUES
  ('James', 25, 'male', 'USA'),
  ('Leila', 32, 'female', 'France'),
  ('Brigitte', 35, 'female', 'England'),
  ('Mike', 40, 'male', 'Denmark'),
  ('Elizabeth', 21, 'female', 'Canada');
"""


def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")



def initTables(connection):
    execute_query(connection, create_fileindex_table)



def md5(fname):
    print("md5 of ",fname)
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


print(f"Name of the script      : {sys.argv[0]}")
print(f"Arguments of the script : {sys.argv[1:]}")

argv = sys.argv[1:]
sum = 0
try:
    opts, args = go.getopt(argv, 'r:d:', ['root', 'database'])
#if len(opts) == 0 or len(opts) > 2:
#    print ('usage: w.py -r <root director> -d <sqlite database file>')
#print(foperand)
except go.GetoptError as e:
    # Print something useful
    print(f"**** error '{e}' occurred")
    sys.exit(2)

for opt, arg in opts:
    sum += int(arg)


print(sum)
exit()

id = uuid.uuid1()
print ("uuid",id.hex)
print (id)
z = uuid.UUID(id.hex)

if (z == id):
    print("*****SAME*******!!!")


connection = create_connection("/Users/johnny/.indexer.sqlite")
initTables(connection)


users = [
    ("James", 25, "male", "USA"),
    ("Leila", 32, "female", "France"),
    ("Brigitte", 35, "female", "England"),
    ("Mike", 40, "male", "Denmark"),
    ("Elizabeth", 21, "female", "Canada"),
]

user_records = ", ".join(["%s"] * len(users))
print(user_records)
insert_query = f"INSERT INTO fileindex (hdrive_uid, path, size, hash) VALUES {user_records}"
#buildQuery(insert_query,users)

rootDir = '.'
for dirName, subdirList, fileList in os.walk(rootDir, topdown=False):
    print('Found directory: %s' % dirName)
    for fname in fileList:
        ffname = dirName + "/" + fname
        sz = os.path.getsize(ffname)
        mtime = os.path.getmtime(ffname)
        ctime = creation_date(ffname)
        md5h = md5(ffname)
#        print('\t%s\t%s\t%s\t%d\t%s\t%s' % (fname, dirName, md5h, sz, time.ctime(ctime), time.ctime(mtime) ))
        print('\t%s\t%s\t%s\t%d\t%s\t%s' % (fname, dirName, md5h, sz, ctime, mtime ))

        # add to database
        # uuid + ffname is unique key
