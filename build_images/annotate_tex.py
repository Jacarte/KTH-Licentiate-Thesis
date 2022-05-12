import os
import json
import sys

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

def process(jsonmap, ignore):
    report = json.loads(open(jsonmap, 'r').read())
    ignore = open(ignore, 'r').readlines()
    RANGE = 5

    for match in report[::-1]:
        id, matches = match['id'], match['matches'] 
        p, _, f = id
        content = open(f, 'r').read()
        print(f)
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
            print(f"{f}:{L}:{C}", message)
            # Modify the tex file with a TODO, add a comment in the code
        #open(f, 'w').write(content)

if __name__ == '__main__':
    process(sys.argv[1], sys.argv[2])