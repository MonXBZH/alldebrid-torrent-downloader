FROM alpine:latest
LABEL Author=MonX Author_link=<https://github.com/MonXBZH>

RUN mkdir /downloads
RUN mkdir /watching

RUN apk --update add python3 py3-pip openssl bash

# ENV TOKEN=NOTATOKEN!
# ENV USERRUN "root"
# ENV UID "0"
# ENV GID "0"
# ENV DELETE_MAGNET=yes

VOLUME [ "/watching", "/downloads" ]

COPY alldebrid.py /
COPY requirements.txt /

RUN pip install --upgrade pip
RUN pip install -r /requirements.txt

WORKDIR /
RUN groupadd $GID || true
RUN useradd -ms /bin/bash -u $UID -g $GID $USERRUN || true
USER $USERRUN

#RUN echo "python /alldebrid.py -w ./watching -d ./downloads -t $TOKEN -D $DELETE_MAGNET" > /run_script.sh
COPY run.sh /
RUN chmod +x /run.sh

ENTRYPOINT [ "bash", "-c", "/run.sh" ]
#CMD [ "/run_script.sh" ]
