import inotify.adapters
import argparse
import urllib.request
import requests
import json
import os

ALLDEBRID_URL = "https://api.alldebrid.com/v4/magnet/file?agent="
ALLDEBRID_AGENT = "AllDebridTorrentDownloader"

def parse_args():
    parser = argparse.ArgumentParser(description="Wait a minute !",
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-d", "--directory", type=str, help="Specify directory to watch", default="/tmp")
    parser.add_argument("-t", "--token", type=str, help="Alldebrid token to use", default="NOTATOKEN!")
    args = parser.parse_args()
    return args
args = parse_args()
i = inotify.adapters.InotifyTree(args.directory)

def check_url():
    url_status = urllib.request.urlopen("https://alldebrid.fr/magnets").getcode()
    while url_status != 200:
        url_status = urllib.request.urlopen("https://alldebrid.fr/magnets").getcode()
        print("Alldebrid website seems to be down ! Get status code:", url_status)
    return url_status

def upload_files():
    ALLDEBRID_URL_UPLOAD = ALLDEBRID_URL+ALLDEBRID_AGENT+"apikey="+args.token
    response = requests.post(ALLDEBRID_URL_UPLOAD, files=file)
    jsonResponse = json.loads(response.json())
    statusreturn = print(jsonResponse['status']['data.files.name'])
    filenamereturn = print(jsonResponse['data.files.name'])
    idreturn = print(jsonResponse['data.files.id'])
    print("status:", statusreturn)
    print("filename", filenamereturn)
    return idreturn

def check_status():
    ALLDEBRID_URL_UPLOAD = ALLDEBRID_URL+ALLDEBRID_AGENT+"apikey="+args.token
    magnet_status = urllib.request.urlopen(ALLDEBRID_URL_UPLOAD+"&id="+idreturn)
    while magnet_status.json(['status']) != "Ready":
        magnet_status = urllib.request.urlopen(ALLDEBRID_URL_UPLOAD+"&id="+idreturn)
        print(magnet_status.json(['status']))

def get_ddl_link():
    ALLDEBRID_URL_UPLOAD = ALLDEBRID_URL+ALLDEBRID_AGENT+"apikey="+args.token
    ddl_link = urllib.request.urlopen(ALLDEBRID_URL_UPLOAD+"&id="+idreturn).json(['data.magnets.links[0]'])
    return ddl_link



for event in i.event_gen(yield_nones=False):
    (_, type_names, path, filename) = event
    file_name, file_extension = os.path.splitext(filename)
    print(file_name, file_extension)
    if "IN_CLOSE_WRITE" in type_names:
        if "torrent" in file_extension:
            print("FILENAME=[{}] EVENT_TYPES={}".format(filename, type_names))
            url_status = check_url()
            while url_status != 200:
                print("Status of alldebrid website is KO:", "HTTP",url_status)
                url_status = check_url()
            print("alldebrid status is OK.", "Get status code:",url_status)
            file = {'upload_file': open(filename, 'r')}
            idreturn = upload_files()
            check_status()
            ddl_link = get_ddl_link()
            print(ddl_link)
        else:
            print(filename, "is not a torrent file. Skipping...")
