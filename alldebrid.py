import inotify.adapters
import argparse
import urllib.request
import requests
import json
import os
import sys
import time
from torrentool.api import Torrent

ALLDEBRID_API_PATH = "https://api.alldebrid.com/v4"
ALLDEBRID_AGENT = "AllDebridTorrentDownloader"
ALLDEBRID_MAGNET_URL = "https://alldebrid.fr/magnets"

def parse_args():
    parser = argparse.ArgumentParser(description="Wait a minute !",
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-w", "--watch", type=str, help="Specify directory to watch", default="/tmp")
    parser.add_argument("-t", "--token", type=str, help="Alldebrid token to use", default="NOTATOKEN!")
    parser.add_argument("-d", "--download", type=str, help="Specify directory to download files", default="/tmp")
    parser.add_argument("-D", "--delete", type=str, help="Delete or not the magnet file after download. If not, the magnet file change from '.inprogress' to '.done'", default="yes")
    
    args = parser.parse_args()
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    return args
args = parse_args()

# Directories for docker volumes
watching_dir = "/watching"
download_dir = "/downloads"

# For standalone usage, comment docker volumes and uncomment lines below:
# watching_dir = args.watch
# download_dir = args.download

def check_url():
    url_status = urllib.request.urlopen(ALLDEBRID_MAGNET_URL, None, 20).getcode()
    while url_status != 200:
        url_status = urllib.request.urlopen(ALLDEBRID_MAGNET_URL, None, 20).getcode()
        print("Alldebrid website seems to be down ! Get status code:", url_status)
    return url_status

def upload_magnet(filename):
    print("DEBUG TOKEN: ", args.token)
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
    print("DEBUG DATAS: ", datas)
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
    print("DOWNLOADING FILE:", download_dir+"/"+filename)
    file_path = download_dir+"/"+filename
    response = requests.get(file_url, stream=True)
    with open(file_path, mode="wb") as file:
        for chunk in response.iter_content(chunk_size=10 * 1024):
            file.write(chunk)

def done_magnet(magnet_name):
    magnet_filename, magnet_extension = os.path.splitext(magnet_name)
    os.rename(magnet_name, magnet_filename+".done")
    print("MAGNET IS NOW IN '.done' STATUS: ", magnet_filename+".done")

def delete_magnet(magnet_name):
    print("Deleting magnet file: ", magnet_name)
    magnet_file = str(magnet_name)
    os.remove(magnet_file)
    if magnet_file == False:
        print("CAN'T DELETE MAGNET FILE !")
    else:
        print("Magnet file has been deleted.")

created_files = set()
i = inotify.adapters.InotifyTree(watching_dir)
for event in i.event_gen(yield_nones=False):
    (_, type_names, path, filename) = event
    file_name, file_extension = os.path.splitext(filename)
    if "IN_OPEN" in type_names:
        created_files.add(filename)
    if "IN_CLOSE_WRITE" in type_names:
        if filename in created_files:
            if ".torrent" in file_extension:
                filename = path+"/"+filename
                os.rename(filename, filename+".inprogress")
                filename = filename+".inprogress"
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
                if args.delete == "yes":
                    print("LAUNCHING DELETE FUNCTION...")
                    delete_magnet(filename)
                else:
                    done_magnet(filename)

                print("WAITING FOR NEW FILE...")
            else:
                print(filename, "is not a torrent file. Skipping...")
