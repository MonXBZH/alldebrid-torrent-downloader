import inotify.adapters
import argparse
import urllib.request
import requests
import json
import os
import sys
import time
import unicodedata
import re
from torrentool.api import Torrent

ALLDEBRID_API_PATH = "https://api.alldebrid.com/v4"
ALLDEBRID_AGENT = "AllDebridTorrentDownloader"

def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

def parse_args():
    parser = argparse.ArgumentParser(description="Wait a minute !",
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-w", "--watch", type=str, help="Specify directory to watch", default="/tmp")
    parser.add_argument("-t", "--token", type=str, help="Alldebrid token to use", default="NOTATOKEN!")
    parser.add_argument("-d", "--download", type=str, help="Specify directory to download files", default="/tmp")
    args = parser.parse_args()
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    return args
args = parse_args()

def check_url():
    url_status = urllib.request.urlopen("https://alldebrid.fr/magnets", None, 20).getcode()
    while url_status != 200:
        url_status = urllib.request.urlopen("https://alldebrid.fr/magnets", None, 20).getcode()
        print("Alldebrid website seems to be down ! Get status code:", url_status)
    return url_status

def upload_magnet(filename):
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
    jsonResponse = json.dumps(response.json())
    datas = json.loads(jsonResponse)
    statusreturn = datas['status']
    idreturn = datas['data']['magnets'][0]['id']
    print("UPLOADING MAGNET... : ", statusreturn)
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
    magnet_status = datas['data']['magnets']['status']
    print("Torrent file is in a ", magnet_status, " status !")
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
    nb_file = 0
    for i in datas['data']['magnets']['links']:
        nb_file = nb_file + 1
    print("FOUND", nb_file, "FILE(S) IN THE MAGNET")
    
    temp_dict = {}
    list_link_dict = {}
    file = 0
    while file < nb_file:
        list_link_dict[file] = {}
        temp_dict['filename'] = datas['data']['magnets']['links'][file]['filename']
        temp_dict['url'] = datas['data']['magnets']['links'][file]['link']
        list_link_dict[file] = dict(temp_dict)
        file = file + 1
        
    list_link_dict_json_temp = json.dumps(list_link_dict)
    list_link_dict_json = json.loads(list_link_dict_json_temp)
    return list_link_dict_json, nb_file

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
    unlocked_link = datas['data']['link']
    return unlocked_link
    

def download_file(file_url, filename):
    download_dir = str(args.download+"/"+filename)
    print("DOWNLOADING FILE: ", download_dir)
    file_dl = requests.get(file_url, allow_redirects=True)
    with open(download_dir, 'wb') as f:
        f.write(file_dl.content)

def delete_magnet(magnet_name):
    print("Deleting magnet file: ", magnet_name)
    magnet_file = str(args.download+"/"+magnet_name)
    os.remove(magnet_file)
    if magnet_file == False:
        print("CAN'T DELETE MAGNET FILE !")
    else:
        print("Magnet file has been deleted.")

created_files = set()
i = inotify.adapters.InotifyTree(args.watch)
for event in i.event_gen(yield_nones=False):
    (_, type_names, path, filename) = event
    print(filename)
    file_name, file_extension = os.path.splitext(filename)
    if "IN_CREATE" in type_names:
        created_files.add(filename)
    if "IN_CLOSE_WRITE" in type_names:
        if filename in created_files:
            if ".torrent" in file_extension:
                os.rename(filename, filename+".inprogress")
                filename = filename+".inprogress"
                print("FILENAME=[{}] EVENT_TYPES={}".format(filename, type_names))
                print("TEST ALLDEBRID WEBSITE STATUS...")
                url_status = check_url()
                while url_status != 200:
                    print("Status of alldebrid website is KO:", "HTTP",url_status)
                    url_status = check_url()
                print("alldebrid status is OK.", "Get status code:",url_status)
                print("UPLOAD MAGNET ON ALLDEBRID WEBSITE...")
                idreturn = upload_magnet(filename)
                magnet_status = check_status()
                print("CHECK MAGNET STATUS...")
                while magnet_status != "Ready":
                    magnet_status = check_status()
                    print("Retrying...")
                    time.sleep(5)
                print("GET LINK FOR MAGNET...")
                list_link, nb_file = get_ddl_link()
                print("CHECK LINK STATUS...")
                list_link_json_temp = json.dumps(list_link)
                list_link_json = json.loads(list_link_json_temp)
                file = 0
                while file < nb_file:
                    url_file = list_link_json[str(file)]['url']
                    name_file = list_link_json[str(file)]['filename']
                    link_status = check_link(url_file)
                    if link_status == "success":
                        print("UNLOCK URL FILE: ", name_file, "WITH URL: ", url_file)
                        unlocked_link = unlock_link(url_file)
                        download_file(unlocked_link, name_file)
                    else:
                        print("One of the link in the magnet is not available !")
                    file = file + 1
                print("LAUNCHING DELETE FUNCTION...")
                delete_magnet(filename)
                print("WAITING FOR NEW FILE...")
            else:
                print(filename, "is not a torrent file. Skipping...")
