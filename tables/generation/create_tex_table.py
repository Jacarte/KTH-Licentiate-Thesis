import json
import sys

# Script to generate the tex table
if __name__ == '__main__':

    result = ""
    content = open(sys.argv[1], 'r').read()
    data = json.loads(content)

    for repoid, repo in data.items():
        corpusname = repo['name']
        #
        corpus_row_count = 0
        corpusprojects = repo['projects']
        corpus_count = 0
        for project in corpusprojects:
            project_name = project['name']
            #result += " &\multirow{{PROJECROWCOUNT}}{*}{%s } &  &  &   \\\\\n"%( project_name,  )
            corpus_row_count += 1
            project_row_count = 0

            project_modules = project['modules']
            for module in project_modules:
                module_name = module['name']
                module_row_count = 0

                module_function = module['functions']
                # result += " & &\multirow{{MODULECOUNT}}{*}{%s} &  &  \\\\\n"%(  module_name,)
                corpus_row_count += 1
                project_row_count += 1
                
                for function in module_function:
                    function_name = function['name']
                    variants_count = function['variants_count']
                    # result += " & & & %s & %s  \\\\\n\n"%(  function_name, variants_count)
                    corpus_row_count += 1
                    project_row_count += 1
                    module_row_count += 1
                    corpus_count += int(variants_count)
                
                result = result.replace("{MODULECOUNT}", f"{module_row_count}")
                if 'function_count'in module:
                    function_count = module['function_count']
                else:
                    function_count = module_row_count
                # result += "\n&  & & %s &  \\\\\n\n"%(  function_count,)

            result = result.replace("{PROJECROWCOUNT}", f"{project_row_count}")
        result = result.replace("{CORPUSCOUNT}", f"{corpus_row_count}")
        result += "%s & & & & %s    \\\\\n\\hline\n"%(corpusname, corpus_count)
        #result += "\n\midrule\n"
    result_file = open("table_template.tex", 'r').read()
    # sanitize
    result = result.replace("_", "\\_")
    result_file = result_file.replace("{{content}}", result)
    open("result_static_diversity.tex", 'w').write(result_file)
