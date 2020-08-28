#!/usr/bin/env python3
import subprocess

import getopt as go
import sys, os, fcntl, struct
import time
import hashlib
import uuid
import sqlite3
import platform
from sqlite3 import Error

create_harddrive_table = """
CREATE TABLE IF NOT EXISTS harddrives (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uid TEXT NOT NULL,
  rootdir TEXT NOT NULL,
  name TEXT NOT NULL UNIQUE,
  UNIQUE(uid,rootdir)

);
"""

insert_harddrive = """
INSERT INTO
  `harddrives` (`uid`, `name`, `rootDir`)
VALUES (?, ?, ?) ;
"""

query_all_harddrives = """
SELECT id, uid as uid, name as name, rootdir  FROM `harddrives`
"""


query_driveid = """
SELECT id  FROM `harddrives` WHERE uid =
"""

query_drivenames = """
SELECT *  FROM `harddrives` WHERE name =
"""

query_count_harddrives = """
SELECT count(*) FROM `harddrives`
"""


create_fileindex_table = """
CREATE TABLE IF NOT EXISTS fileindex (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  hdrive_id INTEGER NOT NULL,
  fname TEXT NOT NULL,
  path TEXT NOT NULL,
  hash TEXT NOT NULL,
  size INTEGER NOT NULL,
  FOREIGN KEY(hdrive_id) REFERENCES harddrives(id),
  UNIQUE(hdrive_id,path,fname)

);
"""



insert_fileindex = """
INSERT INTO
  `fileindex` (`hdrive_id`, `fname`, `path`, `hash`,`size`)
VALUES (?, ?, ?, ?, ?) ;
"""

query_count_fileindex = """
SELECT count(*) FROM `fileindex`
"""


query_all_fileindex = """
SELECT f.id, hdrive_id as hdid, fname as file, path, hash, size, h.name as harddrivename, h.uid  FROM `fileindex` f
JOIN `harddrives` h ON h.id = hdid
"""

query_file_on_drive = """
SELECT id, hash  FROM `fileindex` f
WHERE f.hdrive_id = {hdid} AND f.path = {quotepath}{path}{quotepath}
AND f.fname = {quotename}{name}{quotename}
"""

query_file_on_drive_from_hash = """
SELECT id, hash, size, hdrive_id, fname, path FROM `fileindex` f
WHERE f.hash='{hash}'
"""

query_file_on_drive_org = """
SELECT id, hash  FROM `fileindex` f
WHERE f.hdrive_id = {hdid} AND f.path = '{path}' AND f.fname = '{name}'
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
        connection.row_factory = sqlite3.Row  #this for getting the column names!
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


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def insert(connection, query, params):
    cursor = connection.cursor()
    cursor.execute(query,params)
    connection.commit()
    return cursor.lastrowid




def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    except Error as e:
        print(f"The error '{e}' occurred")

def initTables(connection):
    execute_query(connection, create_fileindex_table)
    execute_query(connection, create_harddrive_table)


def md5(fname, bsize = 4096):
    print("calculating md5 of ",fname, "with buffer size",bsize)
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(bsize), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


#def getRecordCount(connection):
    #query_driveid
#    cursor = connection.cursor()
#    cursor.execute_query(query,params)

#    return 0


def addFileIndexRecord(connection, harddriveid, filename, pathname, hash, sz):
    try:
    #  `fileindex` (`hdrive_uid`, `fname`, `path`, `hash`,`size`)
        print("addFileIndexRecord", harddriveid, filename, pathname, hash, sz)

        lr = insert(connection, insert_fileindex, (harddriveid, filename, pathname, hash, sz))
        return lr
    except Error as e:
        print(f"addFileIndex  {e}")
        return -1



def addHardDriveEntry(connection, harddriveid, name, rootDir):
    try:
        lr = insert(connection, insert_harddrive, (harddriveid, name, rootDir))
        return lr
    except Error as e:
        return -1

def getHardDriveIdFromUID(connection, uid):
    cursor = connection.cursor()
    results = None
    try:
        cursor.execute(f"{query_driveid}'{uid}'")
        results = cursor.fetchall()
        return dict(results[0])['id']
    except Error as e:
        print(f"The error '{e}' occurred")
        return -1


def debugAllHardDrives():
    results=execute_read_query(connection, query_all_harddrives)

    for result in results:
        r = dict(result)
        print(r)



def extractQuote(str):
    return '"' if str.find("'") > -1 else "'"



def entryExists(connection, hdid, fname, dirName):
    query = query_file_on_drive.format(**{'hdid': hdid, 'path': dirName, 'quotepath': extractQuote(dirName), 'name' : fname, 'quotename': extractQuote(fname)})
    #print(query)
    results=execute_read_query(connection, query)
    #print("entryExists returns ", len(results))
    if (results is None):
        print(f"******NONE TYPE***** \"{fname}\"")
        print("query", query)

    return (len(results) == 1)
#    if (len(results) != 1):
#        print("FOUND ONE THAT DID NOT EXIST", dirName, fname)
#    return True
def entryExistsTest(connection, hdid, fname, dirName):
    query = query_file_on_drive.format(**{'hdid': hdid, 'path': dirName, 'quotepath': extractQuote(dirName), 'name' : fname, 'quotename': extractQuote(fname)})
    print("query",query)
    results=execute_read_query(connection, query)
    #print("entryExists returns ", len(results))
    if (results is None):
        print(f"******NONE TYPE***** \"{fname}\"")
        print("query", query)

    return (len(results) == 1)

def escape_quotes(str):
    return str.replace("'","\\'").replace('"','\\"')


def findEntry(connection, hdid, fname, dirName):
#    query = query_file_on_drive.format(**{'hdid': hdid, 'path': escape_quotes(dirName), 'name' : escape_quotes(fname)})
    query = query_file_on_drive.format(**{'hdid': hdid, 'path': dirName, 'quotepath': extractQuote(dirName), 'name' : fname, 'quotename': extractQuote(fname)})

    results=execute_read_query(connection, query)
    return results

def findEntryFromHash(connection, hash):
    query = query_file_on_drive_from_hash.format(**{'hash': hash})
    print("findEntryFromHash", query)
    results=execute_read_query(connection, query)
    return results

def scanFiles(connection,rootDir, hdid, bufsize = 4096):
    added = 0
    skipped = 0
    errors = 0
    recalculateEntry = False

    for dirName, subdirList, fileList in os.walk(rootDir, topdown=False):
        #print('Found directory: %s' % dirName)
        for fname in fileList:
#            if (True):
            if (recalculateEntry or not entryExists(connection,hdid,escape_quotes(fname),escape_quotes(dirName))):
                ffname = dirName + "/" + fname
                try:
                    sz = os.path.getsize(ffname)
                    mtime = os.path.getmtime(ffname)
                    ctime = creation_date(ffname)
                    md5h = md5(ffname,bufsize)
                    entryExistsTest(connection,hdid,fname,dirName)

                    #e = findEntry(connection,hdid,fname,dirName)
                    #if (e['hash'] != md5h):
                    #    print("compare failed",ffname,md5h,e['hash'])
                    #print('\t%s\t%s\t%s\t%d\t%s\t%s' % (fname, dirName, md5h, sz, time.ctime(ctime), time.ctime(mtime) ))
                    #print('\t%s\t%s\t%s\t%d\t%s\t%s' % (fname, dirName, md5h, sz, ctime, mtime ))

                    if (not dryRun):
                        lr = addFileIndexRecord(connection, hdid, fname, dirName, md5h, sz)
                    else:
                        lr = 1
                        print("DryRun ",hdid, dirName, fname, md5h)

                    if (lr > 0):
                        added = added + 1
                    else:
                        print("***Add File Record failed****",fname)
                        errors = errors + 1
                        return added,skipped,errors

                except FileNotFoundError as fnf:
                    print(f"File NOT FOUND! {ffname} ... Skipping")
                    errors = errors + 1

                except PermissionError as perr:
                    print(f"PermissionError! {ffname} ... Skipping")
                    errors = errors + 1

            else:
                skipped = skipped + 1

    return added,skipped,errors

# Starts Here

print(f"Name of the script      : {sys.argv[0]}")
print(f"Arguments of the script : {sys.argv[1:]}")

#print(escape_quotes("'Hello World'"))
#print(escape_quotes('"Hello World"'))

argv = sys.argv[1:]
bufsize = 4096

try:
    opts, args = go.getopt(argv, 'h:r:d:n:b:', ['disk','root', 'database', 'name', 'bufsize'])
    print(opts)
    print(args)
    for opt, arg in opts:
        if opt in ('-h', '--disk'):
            print("DISK!!!!",arg)
            disk = arg
        elif opt in ('-r', '--root'):
            root = arg
        elif opt in ('-b', '--bufsize'):
            bufsize = int(arg)
        elif opt in ('-n', '--name'):
            name = arg
        elif opt in ('-d', '--database'):
            dbase = arg

    hduid = uuid.UUID(os.popen(f"diskutil info '{disk}' | grep 'Volume UUID'").read().split()[2])

except go.GetoptError as e1:
    # Print something useful
    print(f"**** error e1 '{e1}' occurred")
    sys.exit(2)
except IndexError as e2:
    print(f"**** error e2 '{e2}' occurred")
    sys.exit(2)
except Error as e2:
    print(f"**** error e3 '{e3}' occurred")
    sys.exit(2)





#if os.geteuid() >  0:
#    print("ERROR: Must be root to use")
#    sys.exit(1)




dryRun = False

harddriveid = hduid.hex

#id = uuid.uuid1()
#print ("uuid",id.hex)
#print (id)
#z = uuid.UUID(id.hex)
#if (z == id):
#    print("*****SAME*******!!!")


connection = create_connection("/Users/johnny/.indexer.sqlite")
initTables(connection)



#user_records = ", ".join(["%s"] * len(users[0]))
#print(user_records)
#insert_query = f"INSERT INTO fileindex (hdrive_uid, path, size, hash) VALUES {user_records}"

#debugAllHardDrives()

rootDir = root
#def addHardDriveEntry(connection, harddriveid, name, rootDir):
addHardDriveEntry(connection, harddriveid, name, rootDir)
#results=execute_read_query(connection, query_driveid)

# get HardDrive Index ID from harddriveid
hdid = getHardDriveIdFromUID(connection,harddriveid)
#print(hdid)
executeScanning = True
executeQuery = True
executeReporting = True

if (executeScanning):
    print("Scanning files ", harddriveid, name, rootDir)
    added,skipped,errors = scanFiles(connection,root, hdid, bufsize)
    print("Added", added, "Skipped", skipped, "Errors", errors)

if (executeQuery):
    print("Execute Query")
    fname = 'APKExternalNames.csv'
    dirName = '/Volumes/Seagate Backup Plus Drive/myDesktopJan162015'

    findTest = findEntry(connection,hdid, escape_quotes(fname), escape_quotes(dirName))
    print("Result of Find Test",len(findTest))
    print(findTest)
    for result in findTest:
        r = dict(result)
        print(r)
        hash = r['hash']
        findTest2 = findEntryFromHash(connection, hash)
        print("Result of Find Test2",len(findTest2))
        print(findTest2)
        for res in findTest2:
            r2 = dict(res)
            print(r2)
        findTest3 = findEntryFromHash(connection, '98b7be282899ad1ebfcec4a206a07e3d')
        #findTest3 = findEntryFromHash(connection, '6350274352f317207bc5254dd2242cd9')
#
        print(findTest3)
        for res in findTest3:
            r2 = dict(res)
            print(r2)


# add to database
# uuid + ffname is unique key
if (executeReporting):
    results=execute_read_query(connection, query_count_fileindex)
    print("Number of Records",results[0][0])


#results=execute_read_query(connection, query_all_fileindex)
#for result in results:
#    r = dict(result)
#    print(r)
    #print(r['id'], r['hdid'], r['file'], r['path'], r['hash'], r['size'])

print("Name ",name)
print("Name ",harddriveid)

debugAllHardDrives()

#results=execute_read_query(connection, query_all_harddrives)

#for result in results:
#    r = dict(result)
#    print(r)
