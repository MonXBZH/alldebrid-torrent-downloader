#!/bin/bash

ALLDEBRID_API_KEY=${API_KEY}

file="${1}"
echo "new file: $file"
if [[ "${file}" =~ .*torrent$ ]]
        then
                file_basename="$(echo ${file} |sed 's/ /_/g'|xargs basename)"
                echo "Uploading ${file_basename} to alldebrid..."
                TORRENT_ID=$(curl -s -X POST -F "files[]=@${file}" "${UPLOAD_CURL_COMMAND}${ALLDEBRID_API_KEY}"|grep '"id":'| cut -d ':' -f 2)
                echo "Deleting torrent file ${file_basename}..."
		file_basename=$(echo ${file_basename} | sed 's/_/\\\ /g')
                rm -f ${file_basename}
                echo "Get hosting provider link..."
                TORRENT_LINK=$(curl -s -G --data-urlencode "id=${TORRENT_ID}" "${STATUS_CURL_COMMAND}${ALLDEBRID_API_KEY}"|grep '"link":' |cut -d '"' -f 4 | sed 's/\\//g')
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