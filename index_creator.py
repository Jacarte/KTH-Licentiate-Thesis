import os
import re

TERMS = [
    'CROW'
]
DIR = os.path.dirname(__file__)
DISTANCES = {

}

if __name__ == '__main__':

    for dirpath, dirs, files in os.walk(DIR):
        for f in files:
            if f.endswith(".tex"):
                content = open(f"{dirpath}/{f}", 'r').read()
                newc = content
                print(f)
                last = 0
                for term in TERMS:
                    matches = list(re.finditer(term, content))
                    for match in matches:
                        idx = match.start()
                        newc += content[last:idx]

                        chunk = content[max(idx - 10, 0): idx + 10]
                        if "termidx" not in chunk:
                            #print(idx, chunk)
                            newc += f"\\termidx{{{term}}}"
                        else:
                            newc += term
                        last = match.end()

                    if len(matches) > 0:
                        last = matches[-1]
                        idx = last.end()
                        newc += content[idx:]
                    content = newc
                open(f"{dirpath}/{f}",'w').write(content)


