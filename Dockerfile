FROM python:latest
LABEL Author=MonX Author_link=<https://github.com/MonXBZH>

RUN mkdir /downloads
RUN mkdir /watching

ENV TOKEN ""
ENV USERRUN "root"
ENV UID "0"
ENV GID "0"

VOLUME [ "/watching", "/downloads" ]

COPY alldebrid.py /
COPY requirements.txt /

RUN pip install -r /requirements.txt

WORKDIR /
RUN groupadd $GID || true
RUN useradd -ms /bin/bash -u $UID -g $GID $USERRUN || true
USER $USERRUN

ENTRYPOINT [ "python3", "/alldebrid.py" ]
CMD [ "-w", "./watching", "-d", "./downloads", "-t", "$TOKEN" ]
