import json
import sys
import os

def print_table_end(fd):
    fd.write("\n\\end{tabular}")

def write_paper(fd, paper, slugs, positions):
    fd.write(f"{paper['authors']} \\cite{{{paper['cite']}}} & {paper['title']} & {paper['year']} &")
    
    # Replace the features from this paper to the positions template
    t1 = positions
    CP = {}
    for k in slugs.keys():
        CP[k] = True
    for f in paper['features']:
        slug = f['slug']
        if f.get("description", None):
            desc = f['description']
            #print(slug)
            t1 = t1.replace(f"{slug}", f"{desc}")
        else:
            #print(slug)
            t1 = t1.replace(f"{slug}", "X")
        del CP[f['slug']]

    for f in CP.keys():
        
        t1 = t1.replace(f"{f}", "")
    
    fd.write(t1[:-1])
    fd.write("\\\\")
    
    fd.write("\n")

def print_table_header(fd, map, pre="", features = []):
    fd.write(pre)
    #fd.write("\\begin{table}[h]\n")
    #fd.write("\\centering\n")

    # Table layout, Authors, Title, Features
    fd.write("\\begin{tabular}[t]{ l  p{3cm} l |")

    for group in features:
        for _ in group:
            fd.write("p{2cm}")
        fd.write("|")

    fd.write("}\n")

    # Write Column Names

    fd.write("Authors & Title & Year &")
    
    index = 2
    positions = ""
    R = ""
    for group in features:
        for f in group:
            R += f" \\textbf{{{map[f]['id']}}} &"
            positions += f"{f} &"
            index += 1
    fd.write(f"{R[:-1]}\\\\\n\\hline\n") # Erase last character '&'
    fd.flush()

    return positions

if __name__ == "__main__":

    data = sys.argv[1]
    data = open(data, 'r').read()
    data = json.loads(data)

    o = sys.argv[2]
    fd = open(o, 'w')

    #print(data)


    # Get features from seed papers,
    # Also write seed names
    seeds = []
    for paper in data:
        if paper.get("seed"):
            seeds.append(paper)

    features = {}
    slugs = {}
    for seed in seeds:
        for f in seed['features']:
            if f['level'] not in features:
                features[f['level']] = []
            features[f['level']].append(f)
            slugs[f['slug']] = f

    # Print table header
    positions = print_table_header(fd,slugs, features = [
        [ i['slug'] for i in items ] for k, items in features.items()
    ])

    # Sort by year
    papers = [d for d in data if not d['seed']]
    papers = sorted(papers, key=lambda x: x['year'])

    print(len(papers))
    for paper in papers:
        if not paper.get("seed"): # It is a regular paper
            write_paper(fd, paper, slugs, positions)
    #print(positions)
    # Print footer
    print_table_end(fd)

    fd.close()