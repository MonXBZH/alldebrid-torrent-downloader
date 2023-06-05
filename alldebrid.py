## Script in Python
import inotify
import sys
import subprocess
from urllib.request import urlopen

ALL_DEBRIDE_URL = "https://alldebrid.fr/magnets"
API_KEY = "USE YOUR API_KEY !"
ALLDEBRID_API_KEY = str(API_KEY)
status_code = "0"

## Functions:
def test_connectivity(URL):
    print("Test alldebrid connection")
    status_code = int(urllib.request.urlopen(ALL_DEBRIDE_URL).getcode())
    return status_code


def read_fs_notify(FS_NAME):
    
    

while status_code != 200:
    test_connectivity(ALL_DEBRIDE_URL)