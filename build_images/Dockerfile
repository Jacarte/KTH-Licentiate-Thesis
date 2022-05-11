FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y texlive-full git wget jq
# This will allow to get the html textidot report
RUN apt-get install -y chromium-browser
# We will need python and java as well
RUN apt-get install -y python3 default-jre

# Spell checking tooling
RUN mkdir /tools
WORKDIR /tools

RUN wget https://github.com/sylvainhalle/textidote/releases/download/v0.8.3/textidote.jar
# Download parsing script
COPY parse_json2md.py parse_json2md.py 