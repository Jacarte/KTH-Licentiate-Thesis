import json
import sys
import os

BLACKLIST = ['artificial_diversity', 'natural_diversity', 'static', 'dynamic', 'security', 'reliability', 'fault_tolerance', 'nversion', 'number_of_variants', 'architecture', 'intermixing']
SIZES = {
    'architecture': 'p{3cm}',
    'mean': 'p{5cm}',
    'security': 'l',
    'fault_tolerance': 'l'
}

def print_table_end(fd):
    fd.write("\n\\end{tabular}")

def write_paper(fd, paper, slugs, positions):
    if paper['cite']:
        fd.write(f"{paper['authors']} \\cite{{{paper['cite']}}} &")
    else:
        fd.write(f"{paper['authors']} &")
    
    # Replace the features from this paper to the positions template
    t1 = positions
    CP = {}
    for k in slugs.keys():
        if k not in BLACKLIST:
            CP[k] = True
    for f in paper['features']:
        slug = f['slug']
        if slug in BLACKLIST:
            continue
        if f.get("special", None):
            desc = f['special']
            #print(slug)
            t1 = t1.replace(f"{slug}", f"{desc}")
        else:
            #print(slug)
            t1 = t1.replace(f"{slug}", "\\checkmark")
        try:
            del CP[f['slug']]
        except Exception as e:
            print(e)
            pass

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
    fd.write("\\begin{tabular}[t]{ l |")

    for group in features:
        for k in group:
            if k not in BLACKLIST:
                if k in SIZES:
                    fd.write(f"{SIZES[k]}")
                else:   
                    fd.write("l")
        fd.write("|")

    fd.write("}\n")

    # Write Column Names

    fd.write("\\textbf{Authors} &")
    
    index = 2
    positions = ""
    R = ""
    for group in features:
        for f in group:
            if f not in BLACKLIST:
                R += f" \\textbf{{{map[f]['id']}}} &"
                positions += f"{f} &"
                index += 1
    fd.write(f"{R[:-1]}\\\\\n\\hline\\hline\n") # Erase last character '&'
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
            if f['slug'] not in BLACKLIST:
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
        # Remove features based on BlackList
        for i, f in enumerate(paper['features']):
            if f['slug'] in BLACKLIST:
                del paper['features'][i]
    # Group by features
    #groups = {}

    #for paper in papers:
    #    features = [f['slug'] for f in paper['features']]
    #    features = tuple(features)
    #    if features not in groups:
    #        groups[features] = []
    #    groups[features].append(paper)

    #grouped_papers = []

    #for f, papers in groups.items():
    #    cites = [ p['cite'] for p in papers ]
    #    authors = [p['authors'] for p in papers]

    #    all_ = zip(authors, cites)

    #    all_ = [f"{a} \\cite{{{c}}}" for a, c in all_]
    #    if len(all_) > 1:
    #        print(all_)
    #        head = ",".join(all_[:-1])
    #        head = f"{head} and {all_[-1]}"
    #    else:
    #        head  = all_[-1]

    #    grouped_papers.append(
    #        dict(
    #            cite=f"",
    #            features = [{ "slug": s} for s in f],
    #            seed=False,
    #            authors=head
    #        )
    #    )

    print(papers)

    for paper in papers:
        if not paper.get("seed"): # It is a regular paper
            write_paper(fd, paper, slugs, positions)
    #print(positions)
    # Print footer
    print_table_end(fd)

    fd.close()