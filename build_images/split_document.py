from PyPDF2 import PdfFileWriter, PdfFileReader
import os
import sys

inputpdf = PdfFileReader(open(sys.argv[1], "rb"))
OUT = sys.argv[2]

ranges = []
pages = []
num = "intro"

for i in range(inputpdf.numPages):
    output = PdfFileWriter()
    print(i)
    content = inputpdf.getPage(i).extractText() + "\n"
    
    if content.startswith("Chapter"):
        with open("%s/chapter%s.pdf" % (OUT, "wb")) as outputStream:
            for p in pages:
                output.addPage(p)
                output.write(outputStream)
                pages = []
        num = content.replace("Chapter", "")[:1]

    pages.append(inputpdf.getPage(i))

with open("%s/chapter%s.pdf" % (OUT, "wb")) as outputStream:
    for p in pages:
        output.addPage(p)
        output.write(outputStream)
        pages = []

