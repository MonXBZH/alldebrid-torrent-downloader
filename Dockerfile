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

