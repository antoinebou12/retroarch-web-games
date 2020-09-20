#!/usr/bin/env bash
for letter in {0..9} {a..z};
do
        files_array=()
        if [ $(find "$1" -maxdepth 1 -type f -iname "$letter*" -print0| wc -c)  -ne 0 ]; then
                mkdir "$1""$(printf '%s\n' "$letter" | awk '{ print toupper($0) }')" > /dev/null
                set +m
                shopt -s lastpipe
                find "$1" -maxdepth 1 -type f -iname "$letter*" -print0 | while IFS=  read -r -d $'\0'; do files_array+=("$REPLY"); done; declare -p files_array > /dev/null
                for file in "${files_array[@]}"
                do
                        cp "$file" "$1""$(printf '%s\n' "$letter" | awk '{ print toupper($0) }')" > /dev/null
                        rm "$file" > /dev/null
                done
        fi
done
