#!/usr/bin/env python3 -m smtpd -c DebuggingServer -n localhost:1025

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

smtp_server = 'localhost'
port = 1025

dryRun = False
argv = sys.argv[1:]
bufsize = 4096



try:
    #opts, args = go.getopt(argv, 'h:r:d:n:b:f:', ['report','query','disk','root', 'database', 'name', 'bufsize', 'find', 'scanning'])
    opts, args = go.getopt(argv, 'm:t:s:', ['dryrun'])

    print("opts",opts)
    print("args",args)
    for opt, arg in opts:
        #print("for>>>>>",opt,arg)

        if opt in ('-m'):
            message = arg
        elif opt in ('-s'):
            subject = arg
        elif opt in ('-t'):
            to = arg
        elif opt in ('--dryrun'):
            dryRun = True

except go.GetoptError as e1:
    # Print something useful
    print(f"**** error e1 '{e1}' occurred")
    sys.exit(2)
except Error as e2:
    print(f"**** error e3 '{e3}' occurred")
    sys.exit(2)

try:
    print("To", to)
    print("Message", message)

    print("DryRun", dryRun)
    print("Subject", subject)

#print("Message", message)
except NameError as e:
    print(f"!!Error {e}")
