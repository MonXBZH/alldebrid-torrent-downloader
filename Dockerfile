FROM python:slim-bullseye
LABEL Author=MonX Author_link=<https://github.com/MonXBZH>

WORKDIR /

RUN mkdir ./download
RUN mkdir ./watching

ENV TOKEN = "NOTATOKEN"

VOLUME [ "/watching", "/downloads" ]

COPY alldebrid.py ./
COPY requirements.txt ./

RUN pip install -r ./requirements.txt

ENTRYPOINT [ "python", "./alldebrid.py" ]
CMD [ "-w", "./watching", "-d", "./downloads", "-t", "${TOKEN}" ]
