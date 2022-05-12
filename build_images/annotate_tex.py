import os
import json
import sys

def get_similar_position(substr, content):
    score = 0.0

    SCORES = []
    #print(content, substr)
    for i in range(len(content)):
        for j in range(len(substr)):
            c2 = substr[j]
            
            if i + j >= len(content):
                break
            c = content[i + j]
            if c == c2:
                score += 1.0
        SCORES.append((score, i))
        score = 0.0
    
    return max(SCORES, key = lambda x: x[0])

def process(jsonmap, ignore):
    report = json.loads(open(jsonmap, 'r').read())
    ignore = open(ignore, 'r').readlines()
    RANGE = 5

    for match in report:
        id, matches = match['id'], match['matches'] 
        p, _, f = id
        content = open(f, 'r').read()
        print(f)
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
            rep = ",".join(m['replacements'])
            message = f"{m['message']}: '{exact}'...{chunk}.... Replacements: {rep}"

            # Avoid to insert 
            content = content[:position_in_tex] + "\\pdfmarkupcomment[markup=Highlight,color=yellow]{" + content[ position_in_tex: position_in_tex + length:]+ f"}}{{{message}}}" + content[ position_in_tex + length:]
            # Modify the tex file with a TODO, add a comment in the code
        open(f, 'w').write(content)

if __name__ == '__main__':
    process(sys.argv[1], sys.argv[2])