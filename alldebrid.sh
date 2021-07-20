#!/bin/bash

#set -x

ALLDEBRID_API_KEY=${API_KEY}

curl -s -L https://alldebrid.fr/magnets |grep favicon
code=$?

while [[ ${code} != "0" ]]
do
	curl -s -L https://alldebrid.fr/magnets |grep favicon
	code=$?
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

