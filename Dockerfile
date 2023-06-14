FROM debian:stable-slim
LABEL Author=MonX Author_link=<https://github.com/MonXBZH>

RUN apt update && apt install -y inotify-tools curl wget python3 python3-pip
RUN pip install -r requirements.txt

RUN mkdir /download

ENV EBOOKS_PATH="/download"
ENV UPLOAD_CURL_COMMAND="https://api.alldebrid.com/v4/magnet/upload/file?agent=nas&apikey="
ENV STATUS_CURL_COMMAND="https://api.alldebrid.com/v4/magnet/status?agent=nas&apikey="
ENV LINK_CURL_COMMAND="https://api.alldebrid.com/v4/link/unlock?agent=nas&apikey="


COPY alldebrid.sh /

ENTRYPOINT ["", "" ]

