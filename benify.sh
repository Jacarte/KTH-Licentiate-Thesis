if [ -z "$(git status --porcelain)" ]
then 
  
    texs=$(find . -name "*.tex")

    for t in $texs; do
        if grep -q "We then" $t 
        then
            cat $t | grep --color "We then"
            sed -i 's/We then/We/g' $t
        fi
    done
else 
  git status --porcelain
  echo "Commit changes before doing this"
fi

