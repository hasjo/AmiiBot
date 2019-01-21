FROM ubuntu:18.04

RUN apt-get update && apt-get install -y python3 python3-pip locales && locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
RUN pip3 install -U pip
RUN pip3 install discord requests

ADD *.py /src/

ENTRYPOINT python3 /src/Amiibot.py
