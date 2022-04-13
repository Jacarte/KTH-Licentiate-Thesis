\begin{lstlisting}[numbers=left]
(module
  (type (;0;) (func (param f32) (result i32))) (*@\label{tpe1}@*)
  (type (;1;) (func))(*@\label{tpe2}@*)
  (type (;2;) (func (result i32)))(*@\label{tpe3}@*)
  (import "env" "ftoi" (func $ftoi (type 0)))(*@\label{import1}@*) (*@\tikzmarkMap{3}{}{-68.5}{1}{2.0cm}@*)
  (func $main (type 2) (result i32)(*@\label{func1}@*)
    (local i32 i32)
    i32.const -1000
    local.set 0 ;loop iteration counter;
    block  ;label = @1; (*@\label{block1}@*)
      loop  ;label = @2; (*@\label{block2}@*)
        i32.const 0
        local.get 0
        i32.add
        i32.load (*@\label{load}@*)
        local.tee 1
        i32.const 101
        i32.ge_s ;loop iteration condition;
        br_if 1 ;@1; (*@\label{break1}@*)
        local.get 0
        i32.const 4
        i32.add
        local.tee 0
        br_if 0 ;@2; (*@\label{break2}@*)
      end (*@\label{end1}@*)
      i32.const 0
      return
    end (*@\label{end2}@*)
    f32.const 0x1.9147aep+3 ;=12.54;
    call $ftoi (*@\label{call}@*) (*@\tikzmarkMap{2}{}{-21.5}{1}{2.0cm}@*)
    local.get 1
    i32.add) (*@\label{result}@*)
  (memory (;0;) 1) (*@\label{mem1}@*)
  (global (;4;) i32 (i32.const 1000))(*@\label{global1}@*)
  (export "memory" (memory 0)) (*@\label{export1}@*)
  (export "A" (global 2))(*@\label{export2}@*)
  (data $data (0) "\00\00\00\00...")(*@\label{data}@*)
)
\end{lstlisting}