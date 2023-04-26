#!/bin/bash

url="https://archive.org/download/nointro.nes-headered"

# Get the list of .7z files from the URL
file_list=$(wget -q -O- "${url}" | grep -oE 'href="([^"#]+\.7z)"' | cut -d'"' -f2)

# Download each .7z file
for file in $file_list; do
    echo "Downloading ${file}..."
    wget -q --show-progress "${url}/${file}"
done

echo "All .7z files have been downloaded."
