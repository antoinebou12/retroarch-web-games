#!/usr/bin/env bash

for letter in {0..9} {a..z}; do
    files_array=()
    upper_letter=$(echo "$letter" | awk '{ print toupper($0) }')
    if find "$1" -maxdepth 1 -type f -iname "$letter*" -print0 | grep -q .; then
        mkdir -p "${1}${upper_letter}"
        while IFS= read -r -d $'\0' file; do
            files_array+=("$file")
        done < <(find "$1" -maxdepth 1 -type f -iname "$letter*" -print0)
        for file in "${files_array[@]}"; do
            mv "$file" "${1}${upper_letter}"
        done
    fi
done
