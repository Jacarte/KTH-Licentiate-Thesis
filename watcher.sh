#!/bin/bash

#./watch.sh $PATH $COMMAND

daemon() {
    chsum1=""

    while [[ true ]]
    do
        chsum2=`find $1 -name "*.tex" -type f -exec md5 {} \;`
        if [[ $chsum1 != $chsum2 ]] ; then
            echo $chsum2           
            if [ -n "$chsum1" ]; then
                echo "Compiling"
                bash compile.sh
            fi
            chsum1=$chsum2
        fi
        sleep 2
    done
}

daemon $1 $2