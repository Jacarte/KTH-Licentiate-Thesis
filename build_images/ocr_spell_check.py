import cv2
import numpy as np
from pdf2image import convert_from_path
import sys
import os
import pytesseract
import json

import language_tool_python
tool = language_tool_python.LanguageTool('en-US')

OUT = os.path.dirname(__file__)


def get_paragraphs_from_image(imagefile, sizemin=32000):
    print("Getting paragraphs from image")
    # Load image, grayscale, Gaussian blur, Otsu's threshold
    image = cv2.imread(imagefile)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7,7), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Create rectangular structuring element and dilate
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4,4))
    dilate = cv2.dilate(thresh, kernel, iterations=10)

    # Find contours and draw rectangle
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    result = []
    for c in cnts:
        # Get the largest and not overlaping
        # Use a segment tree, kd tree ?
        x,y,w,h = cv2.boundingRect(c)
        # cv2.rectangle(image, (x, y), (x + w, y + h), (36,255,12), 2)

        # Filter by size
        # print(w*h)
        if w*h >= 30000: 
            result.append((
                image[y:y + h, x: x + w], w*h, (x, y, w, h))
            )
        # return each rectangle in an image

    # For debugging
    #cv2.imshow('thresh', thresh)
    #cv2.imshow('dilate', dilate)
    # cv2.imshow('image', image)
    # cv2.waitKey()

    return result

def process_pdf(pdffile, ignore):
    words2ignore = open(ignore, 'r').readlines()
    words2ignore = [l.lower().strip().replace("\n", "").replace("\\\\", "\\") for l in words2ignore]

    images = convert_from_path(pdffile, dpi=350, first_page=0)

    pagen = 0
    REPORT = {}
    ID = 0
    for image in images:
        # Save temp
        REPORTPAGE = []
        relative = f"rois/page_{pagen}.jpg"
        name = f"{OUT}/{relative}"
        image.save(name, "JPEG")
        squares = get_paragraphs_from_image(name)
        i = 0
        imagedata = cv2.imread(name)

        for roi, s, rect in squares:
            # Comment this, it is debugging
            data = pytesseract.image_to_data(roi,output_type='dict')#, config=custom_config)
            #print(data)
            boxes = len(data['level'])
            text = ""
            for i in range(boxes):
                text += " " +  data['text'][i]
                
            # cv2.imwrite(f"{OUT}/rois/roi_{i}_{pagen}_{s}.png", roi)
            # Some sanitization
            text = text.replace("\n", " ")
            text = text.replace(". ", ".\n")
            text = text.strip()
            text = text.replace("  ", " ")

            # Call language tool or any other

            matches = tool.check(text)
            
            if len(matches) > 0:
                
                obj = dict(
                            # Unique id
                            id=ID,
                            matches = []
                            )

                for m in matches:
                    chunk = text[m.offset:m.offset + m.errorLength]
                    if chunk.lower() not in words2ignore:
                        obj['matches'].append(dict(
                            message=m.message,
                            replacements=m.replacements,
                            ruleId=m.ruleId,
                            offsetInContext=m.offsetInContext,
                            category=m.category,
                            offset=m.offset,
                            errorLength=m.errorLength,
                            text=text
                        ))
                        obj['places'] = []

                        offset = 0
                        
                        #print(m.offsetInContext, m.offset)
                        print(m)
                        print()
                        MAXLEVEL = 4
                        found = False
                        for i in range(boxes):
                            #if data['level'][i] >= MAXLEVEL: 
                            offset += len(data['text'][i]) + 1
                            if offset > m.offset:
                                # print(offset, i)
                                # This is the box
                                #i = i - 1
                                found = True
                                break
                        if found:
                            (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                            # Annotate the entire page not roi
                            globalx, globaly, _, _ = rect
                            margin = 20
                            cv2.rectangle(imagedata, (x + globalx - margin, y + globaly - margin), (x + w  + globalx + margin, y + h + globaly + margin), (255,36,12), 2)
                            obj['places'].append(dict(
                                x=x + globalx ,
                                y =  y + globaly,
                                w = w,
                                h = h
                            ))
                        obj['pagefile'] = relative
                        obj['pageannotatedfile'] = f"rois/annotated_{pagen}.png"
                        # Add a different color per rule and annotate the image

                        ID += 1
                        REPORTPAGE.append(obj)

        if len(REPORTPAGE) > 0:
            cv2.imwrite(f"{OUT}/rois/annotated_{pagen}.png", imagedata)

            if name not in REPORT:
                REPORT[f"rois/annotated_{pagen}.png"] = []

            REPORT[f"rois/annotated_{pagen}.png"] += REPORTPAGE
        else:
            os.remove(name)

        i += 1
        pagen += 1

        if pagen == 15:
            break
    open(f"{OUT}/report.json", "w").write(json.dumps(REPORT, indent=4))

if __name__ == '__main__':
    process_pdf(sys.argv[1], sys.argv[2])