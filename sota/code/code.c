\begin{lstlisting}[style=CStyle]
// Some raw data
const int A[250];

// Imported function
int ftoi(float a);

int main() {
    for(int i = 0; i < 250; i++) {
        if (A[i] > 100)
            return A[i] + ftoi(12.54); 
    }

    return A[0];
}
\end{lstlisting}
