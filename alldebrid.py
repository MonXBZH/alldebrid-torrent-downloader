#!/usr/bin/python
## Script in Python
import inotify.adapters
import pyinotify
import sys
import subprocess
from urllib.request import urlopen

ALL_DEBRIDE_URL = "https://alldebrid.fr/magnets"
API_KEY = "USE YOUR API_KEY !"
ALLDEBRID_API_KEY = str(API_KEY)
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
    return check
    
## Algo:
for event in check.event_gen(yield_nones=False):
  (_, filename) = event
  print("Found a new file ! ==> "+filename)
