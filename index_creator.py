import os
import re

TERMS = [
    'CROW ', 'MEWE ', 'program variant ', 'multivariant ' , 'program variant '
]
DIR = os.path.dirname(__file__)
DISTANCE = 20
BLACKLIST = ["termidx", 'cite', '{diagrams', 'fromjson']



if __name__ == '__main__':

    for dirpath, dirs, files in os.walk(DIR):
        for f in files:
            if f.endswith(".tex"):
                doc = open(f"{dirpath}/{f}", 'r')
                content = doc.read()
                doc.close()
                print(f)
                for term in TERMS:  
                    print(term)             
                    newc = ''
                    last = 0
                    matches = list(re.finditer(term, content))
                    for match in matches:
                        idx = match.start()
                        print(last, idx)
                        newc += content[last:idx]

                        chunk = content[max(idx - DISTANCE, 0): idx + DISTANCE]
                        if all([t not in chunk for t in BLACKLIST]):
                            print(chunk)
                            answer = input()

                            if answer.lower() == 'y':
                                newc += f"\\termidx{{{term}}}"
                            else:
                                newc += term
                        else:
                            newc += term
                        last = match.end()

                    if len(matches) > 0:
                        lasti = matches[-1]
                        idx = lasti.end()
                        newc += content[idx:]
                    else:
                        newc = content
                    content = newc
                
                doc = open(f"{dirpath}/{f}", 'w')
                doc.write(content)
                doc.close()


