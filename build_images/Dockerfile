FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y texlive-full git wget jq
# This will allow to get the html textidot report
RUN apt-get install -y chromium-browser
# We will need python and java as well
RUN apt-get install -y python3 default-jre python3-pip
# Ruby
RUN apt-get install -y bundler ruby-full 
# Encoding fixes
RUN apt-get install -y locales poppler-utils tesseract-ocr >/dev/null

# Spell checking tooling
RUN mkdir /tools
WORKDIR /tools

RUN wget https://github.com/sylvainhalle/textidote/releases/download/v0.8.3/textidote.jar
RUN pip install PyPDF4 reportlab PyPDF2 pylatexenc language_tool_python jinja2 pytesseract opencv-python pdf2image intervaltree dtw-python
# Download parsing script
COPY parse_json2md.py parse_json2md.py 
COPY annotate_at_side.py annotate_at_side.py 
COPY split_document.py split_document.py 
COPY get_latex_pieces.py get_latex_pieces.py 
COPY annotate_tex.py annotate_tex.py 
COPY create_html_report.py create_html_report.py 
COPY ocr_spell_check.py ocr_spell_check.py 
COPY templates templates
RUN mkdir rois
RUN mkdir OUT 