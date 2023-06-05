#!/usr/bin/python

# CONFIG
from daemonize import Daemonize
import inotify.adapters
import subprocess
import sys

directory_to_watch = str(sys.argv[1])
script_to_call = './alldebrid_upload.sh'
event_type_to_watch = 'IN_CREATE'
# END CONFIG

pid = "/run/watchfs.pid"

def main():

  i = inotify.adapters.InotifyTree(directory_to_watch)

  for event in i.event_gen(yield_nones=False):
    (_, type_names, path, filename) = event
    for event_type in type_names:
      if event_type == event_type_to_watch: 
        subprocess.call([script_to_call,filename])

  daemon = Daemonize(app="watchfs",pid=pid, action=main)
  daemon.start()