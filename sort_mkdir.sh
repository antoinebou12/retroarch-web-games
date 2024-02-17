#!/usr/bin/env bash

# Check if a directory argument is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

# Save the current working directory
original_dir=$(pwd)

# Change to the target directory
cd "$1" || exit

# Loop through numbers and letters as file name prefixes
for letter in {0..9} {a..z}; do
    # Convert the letter to uppercase for the directory name
    upper_letter=$(echo "$letter" | tr '[:lower:]' '[:upper:]')

    # Initialize an empty array to store the file paths
    files_array=()

    # Find files starting with the current prefix (case-insensitive) and populate the array
    if find . -maxdepth 1 -type f -iname "${letter}*" -print0 | grep -qz .; then
        mkdir -p "${upper_letter}"
        while IFS= read -r -d $'\0' file; do
            files_array+=("$file")
        done < <(find . -maxdepth 1 -type f -iname "${letter}*" -print0)

        # Move each file to the corresponding uppercase directory
        for file in "${files_array[@]}"; do
            mv "$file" "${upper_letter}/"
        done
    fi
done

# Return to the original directory
cd "$original_dir"
