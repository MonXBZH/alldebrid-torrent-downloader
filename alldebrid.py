import inotify.adapters
import argparse
import urllib.request
import requests
import json
import os
import urllib.parse
from torrentool.api import Torrent
from collections import Counter
from pprint import pprint as pp

ALLDEBRID_API_PATH = "https://api.alldebrid.com/v4"
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

def upload_magnet():
    Torrentfile = Torrent.from_file(filename)
    params = {
        'agent': ALLDEBRID_AGENT,
        'apikey': args.token,
    }
    files = {
        'magnets[]': (None, Torrentfile.magnet_link),
    }
    headers = {
        'Accept': 'application/json'
    }
    response = requests.post(ALLDEBRID_API_PATH+"/magnet/upload", params=params, files=files, headers=headers)
    #print(response)
    jsonResponse = json.dumps(response.json())
    #print(jsonResponse)
    datas = json.loads(jsonResponse)
    #print("DATA: ", datas)
    statusreturn = datas['status']
    idreturn = datas['data']['magnets'][0]['id']
    print(statusreturn)
    return idreturn

def check_status():
    params = {
        'agent': ALLDEBRID_AGENT,
        'apikey': args.token,
        'id': idreturn
    }
    headers = {
        'Accept': 'application/json'
    }
    magnet_response = requests.post(ALLDEBRID_API_PATH+"/magnet/status", params=params, headers=headers)
    jsonResponse = json.dumps(magnet_response.json())
    datas = json.loads(jsonResponse)
    #print(datas)
    magnet_status = datas['data']['magnets']['status']
    return magnet_status

def get_ddl_link():
    params = {
        'agent': ALLDEBRID_AGENT,
        'apikey': args.token,
        'id': idreturn
    }
    headers = {
        'Accept': 'application/json'
    }
    magnet_response = requests.post(ALLDEBRID_API_PATH+"/magnet/status", params=params, headers=headers)
    jsonResponse = json.dumps(magnet_response.json())
    datas = json.loads(jsonResponse)
    print("DISPLAY JSON:", datas)
    #data = dict(datas)
    nb_file = 0
    for i in datas['data']['magnets']['links']:
        print(i['filename'])
        nb_file = nb_file + 1
    print("FOUND", nb_file, "FILE(S) IN THE MAGNET")
    
    temp_dict = {}
    list_link_dict = {}
    file = 0
    while file < nb_file:
        temp_dict['filename'] = datas['data']['magnets']['links'][file]['filename']
        temp_dict['url'] = datas['data']['magnets']['links'][file]['link']
        print("temp_dict:", temp_dict)
        list_link_dict = list_link_dict.update(temp_dict)
        #print("list_link_dict:", list_link_dict)
        file = file + 1
    print("FINAL DICT: ", list_link_dict)
    return list_link_dict, nb_file

def check_link(links):
    params = {
        'agent': ALLDEBRID_AGENT,
        'apikey': args.token,
        'link[]': links
    }
    headers = {
        'Accept': 'application/json'
    }
    link_status_url = requests.post(ALLDEBRID_API_PATH+"/link/infos", params=params, headers=headers)
    jsonResponse = json.dumps(link_status_url.json())
    datas = json.loads(jsonResponse)
    print(datas)
    link_status = datas['status']
    print("LINK STATUS: ", link_status)
    return link_status

def unlock_link(links):
    params = {
        'agent': ALLDEBRID_AGENT,
        'apikey': args.token,
        'link': links
    }
    headers = {
        'Accept': 'application/json'
    }
    link_to_unlock = requests.post(ALLDEBRID_API_PATH+"/link/unlock", params=params, headers=headers)
    jsonResponse = json.dumps(link_to_unlock.json())
    datas = json.loads(jsonResponse)
    print(datas)
    unlocked_link = datas['data']['link']
    return unlocked_link
    

def download_file(file_url, filename):
    params = {
        'agent': ALLDEBRID_AGENT,
        'apikey': args.token,
        'id': idreturn
    }
    headers = {
        'Accept': 'application/json'
    }
    file_dl = requests.get(file_url, allow_redirects=True)
    open(filename, 'wb').write(file_dl.content)
    #filenamereturn.close()


for event in i.event_gen(yield_nones=False):
    (_, type_names, path, filename) = event
    file_name, file_extension = os.path.splitext(filename)
    print(file_name, file_extension)
    # if "IN_CREATE" in type_names:
    if ".torrent" in file_extension:
        print("FILENAME=[{}] EVENT_TYPES={}".format(filename, type_names))
        print("TEST ALLDEBRID WEBSITE STATUS...")
        url_status = check_url()
        while url_status != 200:
            print("Status of alldebrid website is KO:", "HTTP",url_status)
            url_status = check_url()
        print("alldebrid status is OK.", "Get status code:",url_status)
        print("UPLOAD MAGNET ON ALLDEBRID WEBSITE...")
        idreturn = upload_magnet()
        magnet_status = check_status()
        print("CHECK MAGNET STATUS...")
        while magnet_status != "Ready":
            magnet_status = check_status()
        print("GET LINK FOR MAGNET...")
        list_link = get_ddl_link()
        print("CHECK LINK STATUS...")
        print(list_link)
        for url in list_link:
            print(url['url'])
            print(url['filename'])
            link_status = check_link(url['url'])
            if link_status == "success":
                unlocked_link = unlock_link(url['url'])
                download_file(url['url'], url['filename'])
            else:
                print("One of the link in the magnet is not available !")
    else:
        print(filename, "is not a torrent file. Skipping...")
