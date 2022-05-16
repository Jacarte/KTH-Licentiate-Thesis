from PyPDF4 import PdfFileWriter, PdfFileReader
import os
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.graphics.shapes import _baseGFontName, _baseGFontNameBI
from reportlab.lib.units import inch

import io

inputpdf = PdfFileReader(open(sys.argv[1], "rb"))

ranges = []
pages = []
num = "intro"

def wrap(t, max=50):
    count = 1
    T = []
    buff = ''
    for c in t:
        buff += c
        if len(buff) % max == max - 1:
            buff = buff.replace("b'", "")
            buff = buff.replace("\\n", "\n")
            T.append(buff)
            count += 1
            buff = ''
    buff = buff.replace("b'", "")
    buff = buff.replace("\\n", "\n")
    T.append(buff)
    return T, count

with open("%s/annotated.pdf" % (os.path.dirname(__file__),), "wb") as outputStream:
    output = PdfFileWriter()

    for i in range(inputpdf.numPages):
    
        p = inputpdf.getPage(i)
    
        # reading annotations and draw them in the 
        # side margin
        # Create a watermark page and add the comments to it
        packet = io.BytesIO()
        size = letter
        SCALE = 400
        can = canvas.Canvas(packet, pagesize=(2*size[0] - SCALE, size[1]))
        can.setFont(_baseGFontName, 11)
        a = False

        #print(p.cropBox.upperLeft)
        origcrop = p.cropBox.upperRight
        y = float(origcrop[1]) - 300                    
        M = 50
        YOFFSET = 10


        if '/Annots' in p:
            for annot in p['/Annots']:
                # Modify the page size to add the annotations at the right
                p.cropBox.upperRight = (2*float(origcrop[0]),float(origcrop[1]))
                obj = annot.getObject()
                if '/Contents' in obj:
                    #print(obj)
                    if "Marked set by" in str(obj["/Contents"]):
                        continue

                    l, t = float(obj['/Rect'][0]), float(obj['/Rect'][1])
                    # left margin
                    l = size[0] - M

                    #print(obj['/Contents'])
                    text, lines = wrap(str(obj['/Contents']))
                    print(text)
                    can.line(float(obj['/Rect'][0]), t, l, y + YOFFSET)
                    can.line(l, y + YOFFSET, size[1], y + YOFFSET)

                    for t in text:
                        can.drawString(l,y, t)
                        y -=  YOFFSET
                    
                    y -= YOFFSET
                    
                    #print(str(obj['/Contents']))
                    a = True
        if a:        
            can.save()
            packet.seek(0)
            new_pdf = PdfFileReader(packet)
            new_pdf.getPage(0).mergePage(p)
            output.addPage(new_pdf.getPage(0))
        else:
            output.addPage(p)
    output.write(outputStream)

