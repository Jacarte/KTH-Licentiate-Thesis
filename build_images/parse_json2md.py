
import json
import sys
import os

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

def find_in_source(matching_text, files):
    r = []
    # traverse the tex files 
    for f in files:
        content = open(f, 'r').read()

        if matching_text in content:
            r.append((f, content.index(matching_text)))
    return r

def process(f, files, revision, repo):
    issues = json.loads(open(f, 'r').read())
    
    # language issues

    # Exit with error if threshold of warnings is reached
    print("## %s Warnings"%(len(issues["matches"])))

    for m in issues["matches"]:
        sentence = m["sentence"]
        rule = m["rule"]["description"]
        message = m["message"]
        position = m["offset"]
        length = m["length"]

        matches_in_source = find_in_source(sentence, files)
        
        for file, p in matches_in_source:
        
            error = sentence[position:position + length]

            # estimating line
            prev = file[:p]
            n = len(prev.split("\n"))


            print(f"- [ ] [*{error}*]({repo}/blob/{revision}/{file}#L{n}) {message}\n  {rule}")
            print(f"  > ...{sentence} ...")

if __name__ == "__main__":
    #print(sys.argv)
    files = get_all_tex_files(sys.argv[2])
    #print(files)
    process(sys.argv[1], [f"{d}/{f}" for d, f in files], sys.argv[3], sys.argv[4])