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
                echo "Ajout du fichier ${file_basename} sur alldebrid..."
                TORRENT_ID=$(curl -s -X POST -F "files[]=@${file}" "${UPLOAD_CURL_COMMAND}${ALLDEBRID_API_KEY}"|grep '"id":'| cut -d ':' -f 2)
                echo "Suppression du fichier torrent ${file_basename}..."
                rm -f ${file}
                echo "Obtention du lien hebergeur..."
                TORRENT_LINK=$(curl -s -G --data-urlencode "id=${TORRENT_ID}" "${STATUS_CURL_COMMAND}${ALLDEBRID_API_KEY}"| sed 's/\\//g')
                echo "Obtention du lien alldebrid..."
                DIRECT_LINK=$(curl -s -G --data-urlencode "link=${TORRENT_LINK}" "${LINK_CURL_COMMAND}${ALLDEBRID_API_KEY}" |grep '"link":' |cut -d '"' -f 4 |sed 's/\\//g')
                echo "Telechargement du fichier..."
                wget ${DIRECT_LINK} -P ${EBOOKS_PATH}/
                if [[ ${?} != "0" ]]; then
                        echo "Telechargement KO !!! wget get return code different of 0."
			exit 1
                else
                        echo "Telechargement OK."
                fi
        fi

done < <(inotifywait -m -r --format '%w%f' -e create "${EBOOKS_PATH}")

