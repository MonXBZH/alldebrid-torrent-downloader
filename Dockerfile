FROM python:slim-bullseye
LABEL Author=MonX Author_link=<https://github.com/MonXBZH>

RUN apt update && apt install -y python3 python3-pip
RUN pip3 install -r requirements.txt

RUN mkdir /download
RUN mkdir /watching

ENV TOKEN = "NOTATOKEN"

VOLUME [ "/watching", "/downloads" ]

COPY alldebrid.py /

ENTRYPOINT ["python3", "/alldebrid.py", "-w", "/watching", "-d", "/downloads", "-t", $TOKEN ]
CMD [ "/bin/sh" ]
