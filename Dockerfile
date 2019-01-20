FROM ubuntu:18.04

RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip3 install -U pip
RUN pip3 install discord requests

ADD *.py /src/

ENTRYPOINT python3 /src/Amiibot.py
