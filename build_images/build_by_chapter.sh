mkdir -p chapters

TIME=30
NUMBERS="1 2 3 4 5 6"

cp Lic.bib chapter.bib

for ch in $NUMBERS
do
    echo "Chapter $ch"
    sed  "s/<< CHAPTER >>/\\\\input{Chapter$ch}/g" LicChapterOnly.template > chapter_$ch.tex
    pdflatex -interaction=nonstopmode -shell-escape chapter_$ch.tex > /dev/null
    sleep $TIME
    bibtex chapter_$ch
    sleep $TIME
    pdflatex -shell-escape -interaction=nonstopmode chapter_$ch.tex  > /dev/null
    sleep $TIME
done

cp chapter*.pdf chapters/

