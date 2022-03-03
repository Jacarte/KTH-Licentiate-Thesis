import sys
import os


def log(msg):
    f = open("pythonlogs.txt", 'a')
    f.write(msg)
    f.close()

if __name__ == '__main__':
    args = "".join(sys.argv[1:])
    
    # Patch 
    args = args.replace("{", "(")
    args = args.replace("}", ")")

    log(f"Arguments {args}\n")

    result = eval(args)
    # Two decimal places by default
    if type(result) == float:
        print(f"{result:.2f}")
    else:
        print(f"{result}")
    log(f"Result {eval(args)}\n")