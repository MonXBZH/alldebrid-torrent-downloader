FROM alpine:latest
LABEL Author=MonX Author_link=<https://github.com/MonXBZH>

RUN mkdir /downloads /watching

RUN apk --update add python3 py3-pip openssl bash

ENV USERRUN "root"
ENV DELETE_MAGNET=yes
ENV TVSHOWS=no

VOLUME [ "/watching", "/downloads" ]

COPY alldebrid.py /
COPY requirements.txt /

RUN pip install --upgrade pip --break-system-packages \
    && pip install -r /requirements.txt --break-system-packages

WORKDIR /
RUN groupadd $GID || true \
    && useradd -ms /bin/bash -u $UID -g $GID $USERRUN || true
USER $USERRUN

COPY run.sh /
RUN chmod +x /run.sh

ENTRYPOINT [ "bash", "-c", "/run.sh" ]
