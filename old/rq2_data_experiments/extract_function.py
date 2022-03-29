import sys
import os
import shutil
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
import json
import hashlib

function_name = re.compile(r"@(.+)\(")
variantre = re.compile(r"((_\d+_$)|_original$|\.\d+$)")
variantre = re.compile(r"((_\d+_$)|_original$|\.\d+$)")

functionbodyre = re.compile(r"BeginFunctionBody\((\d+), size:(\d+)\)")

hex_function = re.compile(r"_wasm_function_\d+")
hex_trampoline = re.compile(r"_trampoline_\d+")
OUT = sys.argv[2]

def sort_and_fix_hex_code(hex):
    content = hex.decode()
    result = []
    lines = content.split("\n")
    functions = {

    }
    last = None
    BLACKLIST = ['wasmtime.info']
    for l in lines[2:]:
        if l.strip() == "Disassembly of section .text:":
            continue
        if l.strip() == "Disassembly of section .shstrtab:":
            continue

        if l.strip() == "Disassembly of section .strtab:":
            continue

        if hex_function.findall(l):
            functions[hex_function.findall(l)[0]] = []
            last = hex_function.findall(l)[0]
            continue
        if hex_trampoline.findall(l):
            functions[hex_trampoline.findall(l)[0]] = []
            last = hex_trampoline.findall(l)[0]
            continue
            
        if "eh_frame" in l:
            functions["eh_frame"] = []
            last = "eh_frame"
            continue
        if "wasmtime.addrmap" in l:
            functions["wasmtime.addrmap"] = []
            last = "wasmtime.addrmap"
            continue

        if "wasmtime.traps" in l:
            functions["wasmtime.traps"] = []
            last = "wasmtime.traps"
            continue
        if "wasmtime.info" in l:
            functions["wasmtime.info"] = []
            last = "wasmtime.info"
            continue
        if "strtab" in l:
            functions["strtab"] = []
            last = "strtab"
            continue
        if last:
            sanitized = l
            sanitized = re.sub(r"[\da-f]+:(( )+[\da-f]+)+", "\t", sanitized)
            sanitized = sanitized.strip()
            functions[last].append(sanitized)     

            # Start a new function scope
        # print(l)
        result.append(l)
    
    for f in BLACKLIST:
        del functions[f]

    def merge(lines):
        return "\t\n".join(lines)
    items = functions.items()
    items = sorted(items, key=lambda x: x[0])
    result = [ f"{f}:\n{merge(v)}\n" for f,v in items]

    return "\n".join(result).encode()

def convert_to_machine_code_wasmtime(wasmfile):
    #print("Generating machine code with wasmtime", wasmfile)
    #print(" ".join([
    #    os.environ.get("WASMTIME", None),
    #    "compile",
    #    "-o",
    #    f"{wasmfile}.wasmtime.x86",
    #    wasmfile
    #]))

    subprocess.check_output([
        os.environ.get("WASMTIME", None),
        "compile",
        "--target",
        "x86_64",
        "--opt-level",
        "2",
        "-o",
        f"{wasmfile}.wasmtime.x86",
        wasmfile
    ])

    x86md5 = hashlib.md5(open( f"{wasmfile}.wasmtime.x86", 'rb').read())
    x86md5 = x86md5.hexdigest()
    with open(f"{wasmfile}.wasmtime.hex",'wb') as hexfile:
        out = subprocess.check_output([
            "objdump",
            "-D",
            f"{wasmfile}.wasmtime.x86",
        ])
        out = sort_and_fix_hex_code(out)
        hexfile.write(out)
        hexmd5 = hashlib.md5(out)
        hexmd5 = hexmd5.hexdigest()

    return dict(x86=f"{wasmfile}.wasmtime.x86", hex=f"{wasmfile}.wasmtime.hex", hexmd5=hexmd5, x86md5=x86md5)

def process_wasm(wasmfile):

    md5wasm = hashlib.md5(open(wasmfile, 'rb').read())
    md5wasm = md5wasm.hexdigest()
    out = subprocess.check_output([
        os.environ['WASM2WAT'],
        wasmfile,
        '-o',
        f"{wasmfile}.wat",
        "--verbose"
    ], stderr=subprocess.STDOUT)

    functions = functionbodyre.findall(out.decode())
    functions = [ dict(id=int(id), size=int(size)) for id, size in functions ]
    # print(functions)
    wasmtime_code = convert_to_machine_code_wasmtime(wasmfile)
    # TODO add V8 here
    
    return md5wasm, f"{wasmfile}.wat",functions, dict(wasmtime=wasmtime_code)


def process_bitcode(bc):
    try:
        #print("bitcode", bc)
        # create the ll content
        subprocess.check_output([
            'llvm-dis',
            bc,
            '-o',
            f"{bc}.ll"
            ])

        md5bc = hashlib.md5(open(bc, 'rb').read())
        md5bc = md5bc.hexdigest()

        content = open(f"{bc}.ll", 'r').read()

        try:
            index  = content.index("define ")
            
                
            function_body = ''
            OPEN = 0
            NEWLINE = False
            for c in content[index:]:
                if c == '{':
                    OPEN += 1
                if c == '}':
                    OPEN -= 1
                    if OPEN == 0 and NEWLINE:
                        function_body += c
                        break
                if c == '\n':
                    NEWLINE = True
                function_body += c

            if OPEN != 0:
                print("Incorrect function body")
                return None

            # Copy the function body to the input folder
            # print(function_body)
            # Get the function name
            functions = function_name.findall(function_body)
            
            if len(functions) == 0:
                print("Could not extract function name")
                return None
            
            # Get defined name
            names = subprocess.check_output([
                'llvm-nm',
                bc            ])
            names = names.decode()
            names = names.split("\n")
            

            for l in names:
                if "-- T" in l:
                    names = l
                    break

            #print(names)
            if "-- T" in names:
                names = names[names.index("-- T") + 4:]
            elif "-- U" in names:
                names = names[names.index("-- U") + 4:]
            names = names.strip()
           
            # Compile to wasm 
            subprocess.check_output([
                # This is our changed backend
                os.environ.get("WASMLD", None),
                bc,
                "-O0",
                "--no-entry",
                "--export-all",
                "--allow-undefined",
                "-o",
                f"{bc}.wasm"
            ])

            wasm_data = process_wasm(f"{bc}.wasm")
            llvmlines = len(function_body.split("\n"))

            return names, function_body, f"{bc}.ll", bc, md5bc, f"{bc}.wasm", llvmlines, *wasm_data
        except Exception as e:
            print(e, bc)
            return None
    except Exception as e:
        print(e, bc)
        return None


def fix_names(file, realnames, wasmfile, remove_x=0):
    content = open(file, 'r').read()

    lines = content.split("\n")
    lines = lines[remove_x:]
    content = "\n".join(lines)

    for f,r in realnames.items():
        content = content.replace(f, r)


    open(file, 'w').write(content)

    md5bc = hashlib.md5(open(file, 'rb').read())
    md5bc = md5bc.hexdigest()

    return wasmfile, md5bc

def split_bitcode(bitcode, skipsplit=True):
    print("Splitting bitcode")
    
    def extract_llvm(bitcode, funcname, out):
        subprocess.check_output([
            "llvm-extract",
            f"--func={funcname}",
            f"-o={out}",
            bitcode
        ])
        return out

    # Calls llvm-extract on each function 
    if not skipsplit:
        MEWE_STATS = os.environ.get("MEWE_STATS", None)

        if MEWE_STATS is None:
            print("MEWE_STATS bin not found")
            exit(1)
        if os.path.exists(OUT):
            shutil.rmtree(OUT)
        
        os.mkdir(OUT)
        #do_splittiing(bitcode, limit=2)
        meta = subprocess.check_output([
            MEWE_STATS,
            bitcode
        ])

        meta = json.loads(meta.decode())
        print("Declared", meta['declared'])
        print("Defined", meta['defined'])

        # Calling llvm-extract for each function name

        FUNCTIONS_MAP = {}
        COUNT = 1

        with ThreadPoolExecutor(12) as pool:
            futures = []
            for funcname in meta['functions']:
                futures.append(pool.submit(extract_llvm, bitcode, funcname, f"{OUT}/a{COUNT}.bc" ))
                FUNCTIONS_MAP[COUNT] = funcname
                COUNT += 1
            
            for i, job in enumerate(futures):
                r = job.result()
                sys.stdout.write(f"\r{i}/{meta['defined']} {r}                    ")
            print()

        
        with open(f"function.maps.json", 'w') as jsonf:
            json.dump(FUNCTIONS_MAP, jsonf, indent=4)
        #exit(2)

    OVERALL = {

    }
    REALNAMES = {}
    with ThreadPoolExecutor(12) as pool:
        futures = []
        files = os.listdir(OUT)
        files = [f for f in files if  f.endswith(".bc")]
        for functionbc in files:
            futures.append(pool.submit(process_bitcode, f"{OUT}/{functionbc}"))
        for i, future in enumerate(futures):
            r = future.result()
            if r:
                name, body, llfile, bcfile, md5bc, wasmfile, llvmlines, wasmmd5, watfile, wasmmeta, machine_code  = r
                # Do name sanitization
                sanitized = name
                #print(variantre.findall(sanitized))
                sys.stdout.write(f"\r{i}/{len(futures)}                                                                ")
                if variantre.findall(sanitized):
                    sys.stdout.write(f"\nVariant {sanitized}                                              ")
                    sanitized = re.sub(variantre, "", sanitized)
                
                if "call i32 @discriminate" in body:
                    print("\nSkipping dispatcher")
                    continue

                if sanitized not in OVERALL:
                    OVERALL[sanitized] = dict(variants = [])
                
                REALNAMES[name] = sanitized
                wasmfile, md5fix = fix_names(watfile,  REALNAMES, wasmfile )
                bcfile, md5bc = fix_names(llfile,  REALNAMES, bcfile, remove_x=3)

                OVERALL[sanitized]['variants'].append(dict(
                        name=name,
                        #body=body,
                        llfile=llfile,
                        bcfile=bcfile,
                        function_wasm_stats=wasmmeta,
                        llvmlines=llvmlines,
                        md5bc=md5bc,
                        wasmfile=wasmfile,
                        wasmmd5=md5fix,
                        watfile=watfile,
                        parent=sanitized,
                        machine_code=machine_code
                    ))

    # meta stats
    getter = lambda x,y,z: x['machine_code'][y][z]
    for k, v in OVERALL.items():
        OVERALL[k]['COUNT'] = len(v['variants'])
        # Getting unique wasm files
        unique_wasm = [v['wasmmd5'] for v in v['variants']]
        wasm_group = {  }
        hex_group_wasmtime = {  }
        for wasm in v['variants']:
            if wasm['wasmmd5'] not in wasm_group:
                wasm_group[wasm['wasmmd5']] = []

            if getter(wasm, 'wasmtime', 'hexmd5') not in hex_group_wasmtime:
                hex_group_wasmtime[getter(wasm, 'wasmtime', 'hexmd5')] = []

            hex_group_wasmtime[getter(wasm, 'wasmtime', 'hexmd5')].append(getter(wasm, 'wasmtime', 'hex'))
            wasm_group[wasm['wasmmd5']].append(wasm['watfile'])


        unique_wasm = set(unique_wasm)
        unique_wasm = len(unique_wasm)
        # Getting unique bc files

        unique_bc = [v['md5bc'] for v in v['variants']]
        unique_bc = set(unique_bc)
        unique_bc = len(unique_bc)
        # Getting unique machine code files per engine

        unique_wasmtime_hex = [getter(v, 'wasmtime', 'hexmd5') for v in v['variants']]
        unique_wasmtime_hex = set(unique_wasmtime_hex)
        unique_wasmtime_hex = len(unique_wasmtime_hex)

        OVERALL[k]['unique_wasm'] = unique_wasm
        OVERALL[k]['unique_bc'] = unique_bc
        OVERALL[k]['unique_wasmtime_hex'] = unique_wasmtime_hex
        OVERALL[k]['unique_wasm_ratio'] = 1.0*unique_wasm/len(v['variants'])
        OVERALL[k]['unique_wasmtime_hex_ratio'] = 1.0*unique_wasmtime_hex/(unique_wasm)
        OVERALL[k]['unique_bc_ratio'] = 1.0*unique_bc/len(v['variants'])
        OVERALL[k]['wasm_groups'] = wasm_group
        OVERALL[k][f"hex_groups_wasmtime"] = hex_group_wasmtime
    return OVERALL

if __name__ == '__main__':


    for file in os.listdir(sys.argv[1]):
        if file.endswith(".bc"):
            print(file)
            massive = split_bitcode(f"{sys.argv[1]}/{file}")
            
            total = len(massive)
            diversified_bc = len([v for k, v in massive.items() if v['COUNT'] > 1])
            diversified = len([v for k, v in massive.items() if v['unique_wasm'] > 1])
            population = sum([v['COUNT'] for k, v in massive.items()])


            print("TOTAL functions", total)
            print("Diversified_bc", diversified_bc)
            print("Diversified", diversified)
            print("Population", population)

            ks = [k for k, v in massive.items()]
            ks = sorted(ks)
            for k in ks:
                print("\t", k)

            massive['total_functions'] = total
            massive['diversified_bc'] = diversified_bc 
            massive['diversified'] = diversified 
            massive['population'] = population
            with open(f"{file}.massive.json", 'w') as massivejson:
                json.dump(massive, massivejson, indent=4)
            # Compile it to Wasm and copy as well

            # Call V8 and wasmtime to get the machine code and save them as well

