from pikepdf import Pdf, OutlineItem
import os
import sys

if __name__ == "__main__":
    file = sys.argv[1]
    usab = sys.argv[2]
    name = sys.argv[3]

    pdf = Pdf.open(file)
    usabpdf = Pdf.open(usab)
   
    for n, page in enumerate(usabpdf.pages):

        if n == 3: break

        print(page)

        pdf.pages.insert(n, page)
        # remove next page
        del pdf.pages[n+1]
    
    del pdf.pages[68]

    pdf.save(f'{name}')