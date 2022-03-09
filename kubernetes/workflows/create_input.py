import json


if __name__ == '__main__':
    R = []

    l =open('t.txt', 'r').read().split("\n")

    for line in l:
        R.append(dict(
            folder=line[2:],
            filter="*.wasm"
        ))    
    open("input.json", 'w').write(json.dumps(R))