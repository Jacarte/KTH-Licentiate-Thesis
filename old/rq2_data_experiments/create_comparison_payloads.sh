BITCODE=$1
BITCODEFOLDER=$(dirname $1)

rm -rf out
mkdir out
# Split bitcode in functions and group them per function variants
llvm-split -j 10000 -o out/a $BITCODE
find out -name "*" -exec llvm-dis {} -o {}.ll \;

# Get the function body in LLVM
for l in out/*.ll
do
    echo $l
    python3 extract_function.py $l
    break
done