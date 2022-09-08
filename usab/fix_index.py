from pikepdf import Pdf, OutlineItem
import os
import sys

if __name__ == "__main__":
    file = sys.argv[1]
    usab = sys.argv[2]
    name = sys.argv[3]

    pdf = Pdf.open(file)
    usabpdf = Pdf.open(usab)
   
    # first delete the first 
    del pdf.pages[0:2]
    # patch blank page
    del pdf.pages[68]

    for n, page in enumerate(usabpdf.pages):

        if n == 3: break

        pdf.pages.insert(n, page)
    

    pdf.save(f'{name}')