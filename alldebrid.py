#!/usr/bin/python
## Script in Python
import inotify.adapters
import sys
import subprocess
from urllib.request import urlopen
from daemonize import Daemonize

ALL_DEBRIDE_URL = "https://alldebrid.fr/magnets"
API_KEY = "USE YOUR API_KEY !"
ALLDEBRID_API_KEY = str(API_KEY)
event_type_to_watch = 'IN_CREATE'
status_code = "0"
check = "C:"

## Functions:
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def test_connectivity(URL):
    print("Test alldebrid connection")
    status_code = int(urllib.request.urlopen(URL).getcode())
    return status_code

def read_fs_notify(CHECK_FS):
    check = inotify.adapters.InotifyTree(CHECK_FS)
    return check_return
    
## Algo:
read_fs_notify(check)
for event in check_return.event_gen(yield_nones=False):
    test_connectivity(ALL_DEBRIDE_URL)
    (_, filename) = event
    print("Found a new file ! ==> "+filename)
