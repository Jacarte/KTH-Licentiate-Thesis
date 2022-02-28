from PyPDF2 import PdfFileWriter, PdfFileReader

inputpdf = PdfFileReader(open("Lic.pdf", "rb"))

ranges = []
pages = []
num = "intro"

for i in range(inputpdf.numPages):
    output = PdfFileWriter()
    content = inputpdf.getPage(i).extractText() + "\n"
    
    if content.startswith("Chapter"):
        with open("chapter%s.pdf" % num, "wb") as outputStream:
            for p in pages:
                output.addPage(p)
                output.write(outputStream)
                pages = []
        num = content.replace("Chapter", "")[:2]

    pages.append(inputpdf.getPage(i))

