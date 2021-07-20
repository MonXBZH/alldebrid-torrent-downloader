# alldebrid-torrent-downloader
A Docker image which allows you to automatically download torrent on a specific FS using notify-tools via Alldebrid API. This need you to be premium for API key !


# HOW TO USE

Just build the docker image or go to my Dockerhub to download a prebuild image: 

Launch the container:
```docker run -d --name=alldebrid-torrent-downloader -e "API_KEY=<YOUR_ALLDEBRID_API_KEY>" -v <YOUR/TORRENT/PATH>:/download alldebrid-torrent-downloader:latest```

# HOW IT WORKS
The debain-slim based container launches a bash script which gonna check if the alldebrid magnets service is UP, if the service is not available (happens sometimes), you will see in the container's log a message that will indicates you:
```
Alldebrid Magnets service seems to be down for now (HTTP returns 302)
Confirm by visiting this link: https://alldebrid.fr/magnets/
Next retry in 5min...
```

If the service is well up, the torrent file will disappears and the file will be be downloaded at the exact same place than your torrents place.

This has been made for me and has been made quickly and dirty.
Feel free to collaborate !

# Files

## Dockerfile:
```
FROM debian:stable-slim
MAINTAINER MonX <https://github.com/MonXBZH>

RUN apt update && apt install -y inotify-tools curl wget

RUN mkdir /download

ENV EBOOKS_PATH="/download"
ENV ALLDEBRID_API_KEY=${API_KEY}
ENV UPLOAD_CURL_COMMAND="https://api.alldebrid.com/v4/magnet/upload/file?agent=nas&apikey="
ENV STATUS_CURL_COMMAND="https://api.alldebrid.com/v4/magnet/status?agent=nas&apikey="
ENV LINK_CURL_COMMAND="https://api.alldebrid.com/v4/link/unlock?agent=nas&apikey="


COPY alldebrid.sh /

ENTRYPOINT ["/bin/bash", "/alldebrid.sh" ]
```
## Script
```
#!/bin/bash

#set -x

ALLDEBRID_API_KEY=${API_KEY}

code=$(curl -sw '%{http_code}' https://alldebrid.fr/magnets)

while [[ ${code} != "200" ]]
do
        code=$(curl -sw '%{http_code}' https://alldebrid.fr/magnets)
        echo "Alldebrid Magnets service seems to be down for now (HTTP returns ${code})"
        echo "Confirm by visiting this link: https://alldebrid.fr/magnets/"
        echo "Next retry in 5min..."
        sleep 5m
done

while read -r file
do
        if [[ "${file}" =~ .*torrent$ ]]
        then
                file_basename="$(echo ${file} |xargs basename)"
                echo "Uploading ${file_basename} to alldebrid..."
                TORRENT_ID=$(curl -s -X POST -F "files[]=@${file}" "${UPLOAD_CURL_COMMAND}${ALLDEBRID_API_KEY}"|grep '"id":'| cut -d ':' -f 2)
                echo "Deleting torrent file ${file_basename}..."
                rm -f ${file}
                echo "Get hosting provider link..."
                TORRENT_LINK=$(curl -s -G --data-urlencode "id=${TORRENT_ID}" "${STATUS_CURL_COMMAND}${ALLDEBRID_API_KEY}"| sed 's/\\//g')
                echo "Get alldebrid link..."
                DIRECT_LINK=$(curl -s -G --data-urlencode "link=${TORRENT_LINK}" "${LINK_CURL_COMMAND}${ALLDEBRID_API_KEY}" |grep '"link":' |cut -d '"' -f 4 |sed 's/\\//g')
                echo "Downloading file..."
                wget ${DIRECT_LINK} -P ${EBOOKS_PATH}/
                if [[ ${?} != "0" ]]; then
                        echo "Download KO !!! wget get return code different of 0."
                        exit 1
                else
                        echo "Download OK."
                fi
        fi

done < <(inotifywait -m -r --format '%w%f' -e create "${EBOOKS_PATH}")
```
