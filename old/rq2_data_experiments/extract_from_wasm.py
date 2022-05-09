from statistics import median, mean
import sys
import json


BLACKLIST = ['total_functions', 'diversified_bc', 'diversified', 'population']
ONLY_ORIGINAL = True

if __name__ == '__main__':

    with open(sys.argv[1], 'r') as jsonf:
        data = json.load(jsonf)

        distribution = []
        wasm_distribs = []
        for k, v in data.items():
            if k not in BLACKLIST:
                # It is a function key
                variants = v['variants']
                distribs = []
                orig = 0
                for variant in variants:
                    if "_original" in variant['name'] or not ONLY_ORIGINAL:
                        if "_original" in variant['name']:
                            orig = variant['llvmlines']
                        distribs.append(variant['llvmlines'])
                        wasm_distribs += [ i['size'] for i in variant['function_wasm_stats'] ]
                if any( x < orig for x in distribs):
                    print("Better variant")

                distribution += distribs
        data['max_llvm_loc'] = max(distribution)
        data['min_llvm_loc'] = min(distribution)
        data['meam_llvm_loc'] = mean(distribution)
        data['sum_llvm_loc'] = sum(distribution)
        data['max_wasm_loc'] = max(wasm_distribs)
        data['min_wasm_loc'] = min(wasm_distribs)
        data['mean_wasm_loc'] = mean(wasm_distribs)
        data['sum_wasm_loc'] = sum(wasm_distribs)


        with open(f"{sys.argv[1]}.extended.json", 'w') as jsonfw:
            json.dump(data, jsonfw, indent=4)