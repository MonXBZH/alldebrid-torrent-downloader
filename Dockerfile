FROM python:latest
LABEL Author=MonX Author_link=<https://github.com/MonXBZH>

RUN mkdir /downloads
RUN mkdir /watching

ENV TOKEN = ""

VOLUME [ "/watching", "/downloads" ]

COPY alldebrid.py /
COPY requirements.txt /

RUN pip install -r /requirements.txt

WORKDIR /

ENTRYPOINT [ "python3", "/alldebrid.py" ]
CMD [ "-w", "./watching", "-d", "./downloads", "-t", "$TOKEN" ]
