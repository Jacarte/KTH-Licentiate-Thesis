from statistics import mean, median
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


def get_paragraphs_from_image(imagefile, sizemin=10000):
    print("Getting paragraphs from image")
    # Load image, grayscale, Gaussian blur, Otsu's threshold
    image = cv2.imread(imagefile)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7,7), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Create rectangular structuring element and dilate
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10,3))
    dilate = cv2.dilate(thresh, kernel, iterations=13)

    # Find contours and draw rectangle
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    result = []

    filtered = []
    for c in cnts:

        x,y,w,h = cv2.boundingRect(c)

        if w*h >= sizemin: 
            filtered.append(c)
    
    non_overlap = []
    for c1 in range(len(filtered)):
        for c2 in range(len(filtered)):
            if c1 != c2:
                contour1 = filtered[c1]
                contour2 = filtered[c2]
                x,y,w,h = cv2.boundingRect(contour2)
                
                non_overlap.append(contour2)

                r1 = cv2.pointPolygonTest(contour1, (x, y), False) in [1, 0]
                r2 = cv2.pointPolygonTest(contour1, (x + w, y), False) in [1, 0]
                r3 = cv2.pointPolygonTest(contour1, (x, y + h), False) in [1, 0]
                r4 = cv2.pointPolygonTest(contour1, (x + w, y + h), False) in [1, 0]
                
                if all([r1, r2, r3, r4]):
                    # Remove contour2
                    non_overlap.pop()

    
    for c in non_overlap:
        # Remove those contours that are inside other

        # Get the largest and not overlaping
        # Use a segment tree, kd tree ?
        x,y,w,h = cv2.boundingRect(c)
        cv2.rectangle(image, (x, y), (x + w, y + h), (36,255,12), 2)

        # Filter by size
        # print(w*h)
        if w*h >= sizemin: 
            result.append((
                image[y:y + h, x: x + w], w*h, (x, y, w, h))
            )
        # return each rectangle in an image

    # For debugging
    #cv2.imshow('thresh', thresh)
    #cv2.imshow('dilate', dilate)
    # cv2.imshow('image', image)
    # cv2.waitKey()

    #cv2.imwrite(f"{imagefile}.contours.jpg", image)
    #cv2.imwrite(f"{imagefile}.dilate.jpg", dilate)
    return result

def get_score(text1, text2):


    ec1 = text1.encode('utf-8')
    ec2 = text2.encode('utf-8')

    if len(ec1) < len(ec2):
        ec1, ec2 = ec2, ec1

    DTW = [[10000000000 for _ in range(len(ec1) + 1) ] for _ in range(len(ec2) + 1)]

    def d(c1, c2):
        if c1 == c2:
            return 0
        else:
            return 300

    DTW[0][0] = 0
    for i in range(len(ec2) + 1):
        for j in range(len(ec1) + 1):
            if i == 0:
                DTW[i][j] = 100*j
                continue
            if j == 0:
                DTW[i][j] = 100*i
                continue
            
            c1 = ec2[i - 1]
            c2 = ec1[j - 1]

            DTW[i][j] = min(
                DTW[i - 1][j - 1] + d(c1, c2),
                min(DTW[i - 1][j] + 100, DTW[i][j - 1] + 100)
            )
    #print(text1, text2, DTW[i][j])
    return DTW[i][j]

def process_pdf(pdffile, ignore):
    words2ignore = open(ignore, 'r').readlines()
    words2ignore = [l.lower().strip().replace("\n", "").replace("\\\\", "\\") for l in words2ignore]

    images = convert_from_path(pdffile, dpi=350, first_page=0)

    pagen = 0
    REPORT = {}
    ID = 0

    for image in images:
        try:
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

                        if not chunk:
                            continue
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
                            #print(m.offsetInContext, m.offset)
                            print(m)
                            print()
                            globalx, globaly, _, _ = rect
                            margin = 3
                            # check each box and collect the text again, if it is equal to the error chunk, then, that is the place
                            scores = []
                            for i in range(boxes):
                                text = data['text'][i]
                                score = get_score(text, chunk)
                                scores.append((score, i, data['width'][i], data['height'][i]))


                            # the smaller the rectangle the better
                            scores = sorted(scores, key=lambda x: x[2]*x[3])
                            scores = sorted(scores, key=lambda x: x[0])


                            # Draw all rectangles with the same score
                            for sc, i, w, h in scores:
                                if w < 80:
                                    continue
                                if h < 10:
                                    continue
                                if sc != scores[0][0]:
                                    break
                                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                                cv2.rectangle(imagedata, (x + globalx - margin, y + globaly - margin), (x + w  + globalx + margin, y + h + globaly + margin), (255,36,12), 2)

                                if len(obj['places']) == 0:
                                    # But only keep one ?
                                    obj['places'].append(dict(
                                        x=x + globalx ,
                                        y =  y + globaly,
                                        w = w,
                                        h = h
                                    ))
                            obj['pagefile'] = relative
                            obj['chunk'] = chunk
                            obj['pageannotatedfile'] = f"rois/annotated_{pagen}.png"
                            # Add a different color per rule and annotate the image

                            ID += 1
                            REPORTPAGE.append(obj)

            if len(REPORTPAGE) > 0:
                cv2.imwrite(f"{OUT}/rois/annotated_{pagen}.png", imagedata)

                if name not in REPORT:
                    REPORT[relative] = []

                REPORT[relative] += REPORTPAGE
            else:
                os.remove(name)

            i += 1
            pagen += 1
        except KeyboardInterrupt:
            break

    open(f"{OUT}/report.json", "w").write(json.dumps(REPORT, indent=4))

if __name__ == '__main__':
    process_pdf(sys.argv[1], sys.argv[2])