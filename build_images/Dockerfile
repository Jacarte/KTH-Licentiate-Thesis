FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y texlive-full git wget jq
# This will allow to get the html textidot report
RUN apt-get install -y chromium-browser
# We will need python and java as well
RUN apt-get install -y python3 default-jre python3-pip

# Spell checking tooling
RUN mkdir /tools
WORKDIR /tools

RUN wget https://github.com/sylvainhalle/textidote/releases/download/v0.8.3/textidote.jar
RUN pip install PyPDF4 reportlab PyPDF2
# Download parsing script
COPY parse_json2md.py parse_json2md.py 
COPY annotate_at_side.py annotate_at_side.py 
COPY split_document.py split_document.py 
COPY get_latex_pieces.py get_latex_pieces.py 
COPY annotate_tex.py annotate_tex.py 