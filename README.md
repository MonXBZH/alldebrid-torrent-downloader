# alldebrid-torrent-downloader
A Docker image which allows you to automatically download torrent on a specific FS using notify-tools via Alldebrid API. This need you to be premium for API key !
The image should work on multiple OS.

# HOW TO USE

Just build the docker image or go to my Dockerhub to download a prebuild image: https://hub.docker.com/r/monx/alldebrid-torrent-downloader

Launch the container:

```docker run -d --name=alldebrid-torrent-downloader -e "API_KEY=<YOUR_ALLDEBRID_API_KEY>" -v <YOUR/TORRENT/PATH>:/download monx/alldebrid-torrent-downloader```

# HOW IT WORKS
The debian-slim based container launches a bash script which gonna check if the alldebrid magnets service is UP, if the service is not available (happens sometimes), you will see in the container's log a message that will indicates you:
```
Alldebrid Magnets service seems to be down for now (HTTP returns 302)
Confirm by visiting this link: https://alldebrid.fr/magnets/
Next retry in 5min...
```

If the service is well up, the torrent file will disappears and the file will be be downloaded at the exact same place than your torrents place.

This has been made for me and has been made quickly and dirty.
Feel free to collaborate !

