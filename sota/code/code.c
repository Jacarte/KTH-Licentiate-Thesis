\begin{lstlisting}[style=CStyle]
// Some raw data
const int A[250];

// Imported function
int ftoi(float a);(*@\tikzmarkMap{4}{code block 2}{12.5}{1}{2.5cm}@*)

int main() {
    for(int i = 0; i < 250; i++) {
        if (A[i] > 100)
            return A[i] + ftoi(12.54); (*@\tikzmarkMap{1}{code block 2}{8.5}{1}{2.5cm}@*)
    }

    return A[0];
}
\end{lstlisting}
