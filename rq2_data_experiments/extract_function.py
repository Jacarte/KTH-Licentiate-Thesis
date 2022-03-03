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
    print("Generating machine code with wasmtime", wasmfile)
    print(" ".join([
        os.environ.get("WASMTIME", None),
        "compile",
        "-o",
        f"{wasmfile}.wasmtime.x86",
        wasmfile
    ]))

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
    subprocess.check_output([
        os.environ['WASM2WAT'],
        wasmfile,
        '-o',
        f"{wasmfile}.wat"
    ])

    wasmtime_code = convert_to_machine_code_wasmtime(wasmfile)
    # TODO add V8 here
    
    return md5wasm, f"{wasmfile}.wat", dict(wasmtime=wasmtime_code)


def process_bitcode(bc):
    try:
        print("bitcode", bc)
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
            
            #sanitized = functions[0]
            #sanitized = sanitized.replace("_original", "")
            
            print(functions[0])
            # Compile to wasm 
            subprocess.check_output([
                "wasm-ld",
                bc,
                "--no-entry",
                "--export-all",
                "--allow-undefined",
                "-o",
                f"{bc}.wasm"
            ])

            wasm_data = process_wasm(f"{bc}.wasm")

            return functions[0], function_body, f"{bc}.ll", bc, md5bc, f"{bc}.wasm", *wasm_data
        except Exception as e:
            print(e, bc)
            return None
    except Exception as e:
        print(e, bc)
        return None

def do_splittiing(bitcode, limit=3):
    """
        The limit parameter specifies the number of times the llvm-split is called
    """

    queue = [bitcode]

    def split(file, it):
        print("splitting", file)
        name = os.path.basename(file)
        subprocess.check_output([
            "llvm-split",
            "-j=2",
            f"-o={OUT}/{name}_{it}",
            file
        ])
        return [ f"{OUT}/{f}" for f in os.listdir(OUT) if f.startswith(f"{name}_{it}")]
    last = []
    with ThreadPoolExecutor(8) as pool:
        for it in range(limit):
            print(it)

            futures = []
            last = []
            while queue:
                b = queue.pop()
                print(b)
                futures.append(pool.submit(split, b, it))
            for f in futures:
                splat = f.result()
                print(splat)
                queue += splat
                last += splat
    for f in os.listdir(OUT):
        if f"{OUT}/{f}" not in last:
            os.remove(f"{OUT}/{f}")

def fix_names(file, realnames, wasmfile):
    content = open(file, 'r').read()
    for f,r in realnames.items():
        content = content.replace(f, r)


    open(file, 'w').write(content)

    md5bc = hashlib.md5(open(file, 'rb').read())
    md5bc = md5bc.hexdigest()

    return wasmfile, md5bc

def split_bitcode(bitcode, skipsplit=True):
    print("Splitting bitcode")
    
    # Calls llvm-split with a large enough number to separate each function
    if not skipsplit:
        if os.path.exists(OUT):
            shutil.rmtree(OUT)
        
        os.mkdir(OUT)
        #do_splittiing(bitcode, limit=2)
        subprocess.check_output([
            "llvm-split",
            "-j=3000",
            f"-o={OUT}/a",
            bitcode
        ])

    OVERALL = {

    }
    REALNAMES = {}
    with ThreadPoolExecutor(8) as pool:
        futures = []
        files = os.listdir(OUT)
        files = [f for f in files if not f.endswith(".wasm") and not f.endswith(".wat") and not f.endswith(".ll") and not f.endswith(".wasmtime.x86") and not f.endswith(".wasmtime.hex")]
        for functionbc in files:
            futures.append(pool.submit(process_bitcode, f"{OUT}/{functionbc}"))
        for future in futures:
            r = future.result()
            if r:
                name, body, llfile, bcfile, md5bc, wasmfile, wasmmd5, watfile, machine_code  = r
                # Do name sanitization
                sanitized = name
                print(variantre.findall(sanitized))
                if variantre.findall(sanitized):
                    print("Variant", sanitized)
                    sanitized = re.sub(variantre, "", sanitized)
                
                if sanitized not in OVERALL:
                    OVERALL[sanitized] = dict(variants = [])
                REALNAMES[name] = sanitized
                wasmfile, md5fix = fix_names(watfile,  REALNAMES, wasmfile )
                OVERALL[sanitized]['variants'].append(dict(
                        name=name,
                        #body=body,
                        llfile=llfile,
                        bcfile=bcfile,
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
        OVERALL[k]['unique_wasmtime_hex_ratio'] = 1.0*unique_wasmtime_hex/unique_wasm
        OVERALL[k]['unique_bc_ratio'] = 1.0*unique_bc/len(v['variants'])

    return OVERALL

if __name__ == '__main__':


    for file in os.listdir(sys.argv[1]):
        if file.endswith(".bc"):
            print(file)
            massive = split_bitcode(f"{sys.argv[1]}/{file}")

            print("TOTAL functions", len(massive))

            print("Diversified", len([v for k, v in massive.items() if v['COUNT'] > 1]))
            print("Population", sum([v['COUNT'] for k, v in massive.items()]))

            ks = [k for k, v in massive.items()]
            ks = sorted(ks)
            for k in ks:
                print("\t", k)

            with open(f"{file}.massive.json", 'w') as massivejson:
                json.dump(massive, massivejson, indent=4)
            # Compile it to Wasm and copy as well

            # Call V8 and wasmtime to get the machine code and save them as well

