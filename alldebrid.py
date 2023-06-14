import inotify.adapters
import argparse
import urllib.request
import os

def parse_args():
    parser = argparse.ArgumentParser(description="Wait a minute !",
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-d", "--directory", type=str, help="Specify directory to watch", default="/tmp")
    args = parser.parse_args()
    return args

def check_url():
    url_status = urllib.request.urlopen("https://alldebrid.fr/magnets").getcode()
    return url_status


args = parse_args()
i = inotify.adapters.InotifyTree(args.directory)


for event in i.event_gen(yield_nones=False):
    (_, type_names, path, filename) = event
    file_name, file_extension = os.path.splitext(filename)
    # print(file_name, file_extension)
    if "IN_CREATE" in type_names:
        if ".torrent" in file_extension:
            print("FILENAME=[{}] EVENT_TYPES={}".format(filename, type_names))
            url_status = check_url()
            while url_status != 200:
                print("Status of alldebrid website is KO:", "HTTP",url_status)
                url_status = check_url()
            print("alldebrid status is OK:", "HTTP",url_status)
        else:
            print(filename, "is not a torrent file. Skipping...")