from PyPDF4 import PdfFileWriter, PdfFileReader
import os
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.graphics.shapes import _baseGFontName, _baseGFontNameBI
from reportlab.lib.units import inch
import pytesseract

from pdf2image import convert_from_path

import io
from wand.image import Image

inputpdf = PdfFileReader(open(sys.argv[1], "rb"))

ranges = []
pages = []
num = "intro"

def pdf_page_to_png(src_pdf, pagenum = 0, resolution = 72,):
    """
    Returns specified PDF page as wand.image.Image png.
    :param PyPDF2.PdfFileReader src_pdf: PDF from which to take pages.
    :param int pagenum: Page number to take.
    :param int resolution: Resolution for resulting png in DPI.
    """
    dst_pdf = PdfFileWriter()
    dst_pdf.addPage(src_pdf.getPage(pagenum))

    pdf_bytes = io.BytesIO()
    dst_pdf.write(pdf_bytes)
    pdf_bytes.seek(0)

    img = Image(file = pdf_bytes, resolution = resolution)
    img.convert("png")

    return img


images = convert_from_path(sys.argv[1])
for i,image in enumerate(images,start=1):
    image.save(f"./images/page_{i}.jpg","JPEG")

    print(pytesseract.image_to_string(f"./images/page_{i}.jpg"))