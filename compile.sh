echo "Compiling"

pdflatex -draftmode -interaction=nonstopmode -shell-escape Lic.tex
bibtex Lic
pdflatex -interaction=nonstopmode -shell-escape Lic.tex