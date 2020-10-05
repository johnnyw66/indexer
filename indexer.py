#!/usr/bin/env python3
import subprocess
from datetime import datetime
import getopt as go
import sys, os, fcntl, struct, stat
#import os.path
import time
import hashlib
import uuid
import sqlite3
import platform
from sqlite3 import Error
import constants


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
SELECT *  FROM `harddrives`
WHERE name LIKE '%{drivename}%'
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

query_file_on_drive_from_name = """
SELECT f.id, hash, size, hdrive_id, fname, path, h.name as harddrivename FROM `fileindex` f
JOIN `harddrives` h ON h.id = hdrive_id
WHERE fname LIKE '%{name}%' AND h.name LIKE '%{drivename}%'
"""

#query_filepath_on_drive_from_name = """
#SELECT f.id, hash, size, hdrive_id, fname, path, h.name as harddrivename FROM `fileindex` f
#JOIN `harddrives` h ON h.id = hdrive_id
#WHERE (fname LIKE '%{name}%' OR path LIKE '%{name}%') AND h.name LIKE '%{drivename}%'
#"""

query_filepath_on_drive_from_name = """
SELECT f.id, hash, size, hdrive_id, fname, path, h.name as harddrivename FROM `fileindex` f
JOIN `harddrives` h ON h.id = hdrive_id
WHERE  path LIKE '%{name}%' AND h.name LIKE '%{drivename}%'
"""

query_file_on_drive_org = """
SELECT id, hash  FROM `fileindex` f
WHERE f.hdrive_id = {hdid} AND f.path = '{path}' AND f.fname = '{name}'
"""


def log(*args):
    #if (constants.DEBUG):
    if (executeDebug):
        print(args)

def error(*args):
    print('*** ERROR ***', args)


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
        print("Connection to SQLite DB successful.")
    except Error as e:
        error(f"The error '{e}' occurred")

    return connection


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        log(f"Query '{query}'executed successfully")
    except Error as e:
        error(f"The error '{e}' occurred")


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
        error(f"The error '{e}' occurred")

def initTables(connection):
    execute_query(connection, create_fileindex_table)
    execute_query(connection, create_harddrive_table)

def getTime():
    return datetime.now().strftime("%H:%M:%S")

def md5(fname, bsize = 4096):

    print("%s calculating md5 of %s with buffer size %d" % (getTime(),fname,bsize))

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
        error(f"addFileIndex  {e}")
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
        error(f"The error '{e}' occurred")
        return -1


def debugAllHardDrives():
    results=execute_read_query(connection, query_all_harddrives)

    for result in results:
        r = dict(result)
        print(r)



def extractQuote(str):
    return '"' if str.find("'") > -1 else "'"


def reportHardDrives(connection, hdid="%"):
    query = query_drivenames.format(**{'drivename': hdid })
    results=execute_read_query(connection, query)
    for result in results:
        r = dict(result)
        #print(r)
        print(f"name: {r['name']}, uid: {r['uid']} volume:  {r['rootdir']}")

    print("Total number of drives: ", len(results))
    return(len(results), results)


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

def findEntriesFromHash(connection, hash):
    query = query_file_on_drive_from_hash.format(**{'hash': hash})
    print("findEntriesFromHash", query)
    results=execute_read_query(connection, query)
    return results


def findEntryFromName(connection, searchPath, name, drivename='%'):
#    queryTemplate = query_file_on_drive_from_name
#    queryTemplate = query_filepath_on_drive_from_name
    queryTemplate = query_filepath_on_drive_from_name if (searchPath) else query_file_on_drive_from_name
    query = queryTemplate.format(**{'name': name, 'drivename' : drivename})

    print("findEntryFromName", query)
    results=execute_read_query(connection, query)
    return results

def issocket(filename):
    return stat.S_ISSOCK(os.stat(filename).st_mode)

def validFile(filename):
    return not os.path.islink(filename) and (stat.S_ISREG(os.stat(filename).st_mode) or stat.S_ISDIR(os.stat(filename).st_mode))



def scanFiles(connection,rootDir, hdid, bufsize = 4096, dryRun = False):
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
#                    if (not os.path.islink(ffname) and notissocket(ffname)):
                    if(validFile(ffname)):

                        sz = os.path.getsize(ffname)
                        mtime = os.path.getmtime(ffname)
                        ctime = creation_date(ffname)
                        md5h = md5(ffname,bufsize)

                        #entryExistsTest(connection,hdid,fname,dirName)

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
                            #return added,skipped,errors

                except FileNotFoundError as fnf:
                    error(f"File NOT FOUND! {ffname} ... Skipping")
                    errors = errors + 1

                except PermissionError as perr:
                    error(f"PermissionError! {ffname} ... Skipping")
                    errors = errors + 1

            else:
                skipped = skipped + 1

    return added,skipped,errors

# Starts Here

#print(validFile('/Volumes/Backup Nov 2012/Library/Server/Mail/Data/spool/public/pickup'))
#print(validFile( '/Volumes/Backup Nov 2012/Applications/Unity/MonoDevelop.app/Contents/Frameworks/Mono.framework/Versions/2.10.2/2.6'))
#exit()

#print(f"Name of the script      : {sys.argv[0]}")
#print(f"Arguments of the script : {sys.argv[1:]}")

argv = sys.argv[1:]
bufsize = 4096

executeScanning = False
executeQuery = False
executeListDrives = False
executeDebug = False

hashQuery = False
executeReporting = False
dryRun = False
searchPath = False
verbose = False

dbase = 'indexdb.sqlite'


try:
    #opts, args = go.getopt(argv, 'h:r:d:n:b:f:', ['report','query','disk','root', 'database', 'name', 'bufsize', 'find', 'scanning'])
    opts, args = go.getopt(argv, 'h:r:d:n:b:f:', ['find','report','scanning','query','dryrun','searchpath','hash','verbose','listdrives','debug'])

    print("opts",opts)
    print("args",args)
    for opt, arg in opts:
        #print("for>>>>>",opt,arg)

        if opt in ('-h'):
            disk = arg
        elif opt in ('-f'):
            findname = arg
        elif opt in ('-m'):
            findhash = arg
        elif opt in ('-r'):
            root = arg
        elif opt in ('-b'):
            bufsize = int(arg)
        elif opt in ('-n'):
            name = arg
        elif opt in ('-d'):
            dbase = arg
        elif opt in ('--dryrun'):
            dryRun = True
        elif opt in ('--scanning'):
            executeScanning = True
        elif opt in ('--query','--find'):
            executeQuery = True
        elif opt in ('--listdrives'):
            executeListDrives = True
        elif opt in ('--debug'):
            executeDebug = True
        elif opt in ('--hash'):
            hashQuery = True
            executeQuery = True
        elif opt in ('--report'):
            executeReporting = True
        elif opt in ('--searchpath'):
            searchPath = True
        elif opt in ('--verbose'):
            verbose = True

except go.GetoptError as e1:
    # Print something useful
    error(f"**** error e1 '{e1}' occurred")
    sys.exit(2)
except Error as e2:
    error(f"**** error e3 '{e3}' occurred")
    sys.exit(2)





#if os.geteuid() >  0:
#    print("ERROR: Must be root to use")
#    sys.exit(1)





#id = uuid.uuid1()
#print ("uuid",id.hex)
#print (id)
#z = uuid.UUID(id.hex)
#if (z == id):
#    print("*****SAME*******!!!")


#connection = create_connection("/Users/johnny/.indexer.sqlite")
connection = create_connection(dbase)

initTables(connection)

# Reporting
if (executeListDrives):
    reportHardDrives(connection, name if 'name' in globals() or 'name' in vars() else "%")

if (executeReporting):
    print("Reporting")
    results=execute_read_query(connection, query_count_fileindex)
    print("Number of Records",results[0][0])
    debugAllHardDrives()

if (executeQuery):
    print("Execute Query",findname)
    #find selected files with filename and Optional HardDrive name
    if (hashQuery):
        foundEntries = findEntriesFromHash(connection,findname)
    else:
        foundEntries = findEntryFromName(connection, searchPath , findname, name)

#    foundEntries = findEntryFromName(connection, query_file_on_drive_from_name, findname, name)
    #print(findTest4)
    for res in foundEntries:
        r2 = dict(res)
        if(verbose):
            print(r2)
        else:
            print(r2['harddrivename'] + ":" + r2['path'] + "/" + r2['fname'])
    print("Found",len(foundEntries),"records")

#user_records = ", ".join(["%s"] * len(users[0]))
#print(user_records)
#insert_query = f"INSERT INTO fileindex (hdrive_uid, path, size, hash) VALUES {user_records}"

#debugAllHardDrives()

# Scanning
if (executeScanning):

    try:

        hduid = uuid.UUID(os.popen(f"diskutil info '{disk}' | grep 'Volume UUID'").read().split()[2])

    except IndexError as e2:
        error(f"**** error e2 '{e2}' occurred")
        sys.exit(2)

    harddriveid = hduid.hex
    rootDir = root
    #def addHardDriveEntry(connection, harddriveid, name, rootDir):
    addHardDriveEntry(connection, harddriveid, name, rootDir)
    #results=execute_read_query(connection, query_driveid)

    # get HardDrive Index ID from harddriveid
    hdid = getHardDriveIdFromUID(connection,harddriveid)
    #print(hdid)

    print("Scanning files ", harddriveid, "name", name, "directory",rootDir)
    added,skipped,errors = scanFiles(connection,root, hdid, bufsize, dryRun)
    print("Added", added, "Skipped", skipped, "Errors", errors)
