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
    ignore = [i.lower() for i in ignore]

    RANGE = 3
    TOTAL_COUNT = 0
    OVERALL = {}
    for match in report:
        id, matches = match['id'], match['matches'] 
        p, _, f = id
        
        if not os.path.exists(f):
            continue

        content = open(f, 'r').read()
        #print(f"## {f}")
        notes = []
        for m in matches:
            offset = m['offset']
            length = m['errorLength']
            cat = m['category']
            rule = m['ruleId']

            chunk = p[max(offset - RANGE,0): offset + length + RANGE]
            exact = p[offset: offset + length]

            if any([i in chunk.lower() for i  in ignore]):
                print(chunk, exact)
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
            if cat not in OVERALL:
                OVERALL[cat] = {}

            for ni, length in notes:
                if position_in_tex >= ni and position_in_tex <= ni + length:
                    # overlap ?
                    position_in_tex = ni + length

            #content = content[:position_in_tex] + note + content[ position_in_tex + length:]
            notes.append((position_in_tex, len(note)))
            L, C = get_line_and_col(position_in_tex, content)
            #print(f"-  [{f}]({origin}/blob/{revision}/{f[2:]}#L{L}):{L}:{C}", message)
            #print(f"{origin}/blob/{revision}/{f[2:]}#L{L}")
            TOTAL_COUNT += 1
            sys.stdout.write(f"\r{TOTAL_COUNT}      ")

            if f not in OVERALL[cat]:
                OVERALL[cat][f] = []

            OVERALL[cat][f].append(dict(
                    file=f,
                    message=message,
                    line=L,
                    column=C,
                    rule=rule
                )
            )

            # Modify the tex file with a TODO, add a comment in the code
        #open(f, 'w').write(content)
    print(f"\n# {TOTAL_COUNT} Warnings")

    # Generating files
    for c in OVERALL.keys():
        # Create file
        TOTAL_WARNINGS = [ len(matches) for _, matches in OVERALL[c].items() ]
        TOTAL_WARNINGS = sum(TOTAL_WARNINGS)

        md = open(f"({TOTAL_WARNINGS}){c}.md", 'w')
        md.write(f"# {TOTAL_WARNINGS} Warnings\n")

        print(c, TOTAL_WARNINGS)

        for file, matches in OVERALL[c].items():
            md.write(f"## {file}\n")
            for m in matches:
                message = m['message']
                L = m['line']
                C = m['column']
                f = file

                md.write(f"-  [{f}]({origin}/blob/{revision}/{f[2:]}#L{L}):{L}:{C} {message}\n")
                md.write(f"{origin}/blob/{revision}/{f[2:]}#L{L}\n")
        md.close()
    return TOTAL_COUNT
if __name__ == '__main__':
    TOTAL_COUNT = process(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

    #if TOTAL_COUNT >= THRESHOLD:
    sys.stderr.write(f"{TOTAL_COUNT}")

#https://github.com/Jacarte/KTH-Licentiate-Thesis/blob/b1eb874bfada7fe430a70173f492722e0fec87e8/Chapter1.tex#L37