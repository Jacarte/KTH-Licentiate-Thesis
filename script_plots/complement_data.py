import json
import sys
import numpy as np

if __name__ == '__main__':

    f = open(sys.argv[1], 'r').read()
    data = json.loads(f)

    CUMUL = []
    TOTALS = []
    for function,v in data.items():
        try:
            CUMUL.append(len(v['wasm_groups']))
            for vi in v['wasm_groups'].keys():
                TOTALS.append(len(v['wasm_groups'][vi]))
        except:
            print(function)

    data['UNIQUE_WASM_TOTAL'] = sum(CUMUL)
    data['WASM_TOTAL'] = sum(TOTALS)
    data['UNIQUE_WASM_MEDIAN'] = np.median(CUMUL)
    data['UNIQUE_WASM_AVG'] = np.mean(CUMUL)
    
    data['TOTAL_WASM_AVG'] = np.mean(TOTALS)
    data['TOTAL_WASM_MEDIAN'] = np.median(TOTALS)

    d = json.dumps(data, indent = 4)
    open(sys.argv[2], 'w').write(d)

