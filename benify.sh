#if [ -z "$(git status --porcelain)" ]
#then 
  
texs=$(find . -name "*.tex")

for t in $texs; do
    if grep -q "We then" $t 
    then
        # echo $t
        grep -nH --color "We then" $t
        # sed -i 's/We then/We/g' $t || exit 1
    fi
done


for t in $texs; do
    if grep -q "we then" $t 
    then
        # echo $t
        grep -nH --color "we then" $t
        # sed -i 's/We then/We/g' $t || exit 1
    fi
done

texs=$(find . -name "*.tex")

for t in $texs; do
    if grep -q "in the answering" $t 
    then
        # echo $t
        grep -nH --color "in the answerin" $t
        # sed -i 's/We then/We/g' $t || exit 1
    fi
done

#else 
#  git status --porcelain
#  echo "Commit changes before doing this"
#fi

