from PyPDF2 import PdfFileWriter, PdfFileReader
import os

inputpdf = PdfFileReader(open("Lic.pdf", "rb"))

ranges = []
pages = []
num = "intro"

for i in range(inputpdf.numPages):
    output = PdfFileWriter()
    content = inputpdf.getPage(i).extractText() + "\n"
    
    if content.startswith("Chapter"):
        with open("%s/chapter%s.pdf" % (os.path.dirname(__file__),num), "wb") as outputStream:
            for p in pages:
                output.addPage(p)
                output.write(outputStream)
                pages = []
        num = content.replace("Chapter", "")[:1]

    pages.append(inputpdf.getPage(i))

with open("%s/chapter%s.pdf" % (os.path.dirname(__file__),num), "wb") as outputStream:
    for p in pages:
        output.addPage(p)
        output.write(outputStream)
        pages = []

