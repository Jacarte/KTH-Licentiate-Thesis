import os
import sys
from pylatexenc.latex2text import LatexNodes2Text
import language_tool_python
tool = language_tool_python.LanguageTool('en-US')

exclude = eval(os.environ.get("EXCLUDE", "[]"))
def get_all_tex_files(folder):
    # Get tex files
    
    print(folder)
    r = []

    for d, _, files in os.walk(folder):
        for f in files:
            if f.endswith('.tex') and f"{d}/{f}" not in exclude:
                r.append((d, f))
    return r


def process(folder):

    tex_files = get_all_tex_files(folder)

    #print(tex_files)
    REPORT = []
    for d , f in tex_files:
        content = open(f"{d}/{f}", 'r').read()
        print(d, f)
        text = LatexNodes2Text().latex_to_text(content)

        # sanitize text by removing, ref, cites
        # separate by paragraphs
        paragraphs = text.split("\n\n")
        maps = []
        for p in paragraphs:
            if p:
                maps.append((p, text.index(p), f"{d}/{f}"))
        
        for p, i, f in maps:
            matches = tool.check(p)

            if len(matches) > 1:
                obj = dict(
                        id=(p, i, f),
                        matches = []
                        )

                for m in matches:
                    obj['matches'].append(dict(
                        message=m.message,
                        replacements=m.replacements,
                        ruleId=m.ruleId,
                        offsetInContext=m.offsetInContext,
                        category=m.category,
                        offset=m.offset,
                        errorLength=m.errorLength
                    ))

                REPORT.append(obj)
    return REPORT

        #print(maps)


if __name__ == '__main__':
    report = process(sys.argv[1])

    import json
    open("report.json", "w").write(json.dumps(report, indent=4))