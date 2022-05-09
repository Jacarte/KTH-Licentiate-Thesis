import os

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
                for term in TERMS:
                    if term in content:
                        idx = content.index(term)
                        chunk = content[max(idx - 10, 0): idx + 10]
                        print(chunk)

