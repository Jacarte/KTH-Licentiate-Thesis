clang -c -fPIC code.c -O1  --target=wasm32-unknown-emscripten -o code.o
wasm-ld --pie -o code.wasm   code.o --export-all --allow-undefined --no-entry
$WASM2WAT code.wasm -o code.wat
cp code.wat code.comp.wat

# Unneeded imports
sed 's/  (import "env" "__indirect_function_table" (table (;0;) 0 funcref))//g' code.wat > code.fix.wat && mv code.fix.wat code.wat
sed 's/(import "env" "__memory_base" (global $__memory_base i32))//g' code.wat > code.fix.wat && mv code.fix.wat code.wat
sed 's/ (import "env" "__table_base" (global $__table_base i32))//g' code.wat > code.fix.wat && mv code.fix.wat code.wat

sed  "s/(func \$__wasm_call_ctors (type 0)//g" code.wat > code.fix.wat && mv code.fix.wat code.wat
sed  "s/call \$__wasm_apply_data_relocs)//g" code.wat > code.fix.wat && mv code.fix.wat code.wat
sed  "s/(func \$__wasm_apply_data_relocs (type 0))//g" code.wat > code.fix.wat && mv code.fix.wat code.wat
sed  "s/__original_main/main/g" code.wat > code.fix.wat && mv code.fix.wat code.wat


# Uneeded functions
sed  's/  (func $main (type 2) (param i32 i32) (result i32)//g' code.wat > code.fix.wat && mv code.fix.wat code.wat

sed  's/    call $main)//g' code.wat > code.fix.wat && mv code.fix.wat code.wat

# unneeded globals

sed  's/(global (;2;) i32 (i32.const 0))//g' code.wat > code.fix.wat && mv code.fix.wat code.wat

sed  's/(global (;3;) i32 (i32.const 0))//g' code.wat > code.fix.wat && mv code.fix.wat code.wat

# unneeded exports

sed  "s/(export \"__wasm_call_ctors\" (func \$__wasm_call_ctors))//g" code.wat > code.fix.wat && mv code.fix.wat code.wat

sed  "s/(export \"main\" (func \$main))//" code.wat > code.fix.wat && mv code.fix.wat code.wat


sed  's/(export "__main_void" (func $main))//' code.wat > code.fix.wat && mv code.fix.wat code.wat

sed  's/(export "__dso_handle" (global 2))//' code.wat > code.fix.wat && mv code.fix.wat code.wat

sed  's/(export "__data_end" (global 3))//' code.wat > code.fix.wat && mv code.fix.wat code.wat

sed  's/(export "__wasm_apply_data_relocs" (func $__wasm_apply_data_relocs)))//' code.wat > code.fix.wat && mv code.fix.wat code.wat

