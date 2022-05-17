import os
import json
import sys

THRESHOLD = int(os.environ.get("THRESHOLD", "1000000000"))

def get_line_and_col(position, content):
    L = 0
    COL = 0

    for c, ch in enumerate(content):
        if c == position:
            return L, COL

        COL += 1

        if ch == '\n':
            L += 1
            COL = 0

    return 0, 0
def get_similar_position(substr, content):
    score = 0.0

    SCORES = []
    #print(content, substr)
    for i in range(len(content)):
        read = ''
        for j in range(len(substr)):
            c2 = substr[j]
            
            if i + j >= len(content):
                break
            c = content[i + j]
            read += c
            if c == c2:
                score += 1.0
        SCORES.append((score, i))
        score = 0.0
    
    return max(SCORES, key = lambda x: x[0])

def process(jsonmap, ignore, revision, origin):
    report = json.loads(open(jsonmap, 'r').read())
    ignore = open(ignore, 'r').readlines()
    RANGE = 5
    TOTAL_COUNT = 0
    for match in report[::-1]:
        id, matches = match['id'], match['matches'] 
        p, _, f = id
        content = open(f, 'r').read()
        print(f"## {f}")
        notes = []
        for m in matches:
            offset = m['offset']
            length = m['errorLength']
            chunk = p[max(offset - RANGE,0): offset + length + RANGE]
            exact = p[offset: offset + length]

            if exact in ignore:
                continue
            #print(chunk, exact)
            
            score, position_in_tex = get_similar_position(chunk, content)
            #print(position_in_tex)
            #exit(1)
            # \pdfmarkupcomment[markup=StrikeOut,color=red]{stupid}{replace stupid with funny
            if len(m['replacements']) > 0:

                rep = "Replacements: " + ",".join(m['replacements'])
            else:
                rep = ""
            # PATCH
            rep = ""
            
            message = f"{m['message']}: '{exact}' {rep} {m['category']}"
            note = "\\pdfmarkupcomment[markup=Highlight,color=yellow]{" + content[ position_in_tex: position_in_tex + length:]+ f"}}{{{message}}}"

            # Avoid to insert one inside other
            notes = sorted(notes, key=lambda x: x[0])
            for ni, length in notes:
                if position_in_tex >= ni and position_in_tex <= ni + length:
                    # overlap ?
                    position_in_tex = ni + length

            #content = content[:position_in_tex] + note + content[ position_in_tex + length:]
            notes.append((position_in_tex, len(note)))
            L, C = get_line_and_col(position_in_tex, content)
            print(f"-  [{f}]({origin}/blob/{revision}/{f[2:]}#L{L}):{L}:{C}", message)
            print(f"{origin}/blob/{revision}/{f[2:]}#L{L}")
            TOTAL_COUNT += 1

            # Modify the tex file with a TODO, add a comment in the code
        #open(f, 'w').write(content)
    print(f"# {TOTAL_COUNT} Warnings")
    return TOTAL_COUNT
if __name__ == '__main__':
    TOTAL_COUNT = process(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

    #if TOTAL_COUNT >= THRESHOLD:
    sys.stderr.write(f"{TOTAL_COUNT}")

#https://github.com/Jacarte/KTH-Licentiate-Thesis/blob/b1eb874bfada7fe430a70173f492722e0fec87e8/Chapter1.tex#L37