#!/bin/bash

ROOT_WWW_PATH="$1"

# Navigate to the target directory
cd "${ROOT_WWW_PATH}"

# Download RetroArch archive for yesterday's date
wget "https://buildbot.libretro.com/nightly/emscripten/$(date -d "yesterday" '+%Y-%m-%d')_RetroArch.7z"

# Extract the RetroArch archive
7z x -y "$(date -d "yesterday" '+%Y-%m-%d')_RetroArch.7z"

# Move the extracted content to the current directory and remove the temporary directory
mv retroarch/* ./
find retroarch/ -mindepth 1 -maxdepth 1 -name ".*" -exec mv {} . \;
rmdir retroarch

# Remove a specific script tag from index.html if present
sed -i '/<script src="analytics.js"><\/script>/d' ./index.html

# Ensure indexer is executable
chmod +x indexer

# Prepare the directory structure
mkdir -p "${ROOT_WWW_PATH}/assets/cores" "${ROOT_WWW_PATH}/assets/frontend/bundle"

# Navigate to the frontend bundle directory
cd "${ROOT_WWW_PATH}/assets/frontend/bundle"

# Combine bundle parts if they exist and extract the combined bundle
if ls bundle.zip.* 1> /dev/null 2>&1; then
    cat bundle.zip.* > bundle.zip
    7z x -y bundle.zip
    # Optionally, clean up the split parts after extraction
    rm -f bundle.zip.*
fi

# Generate index files
cd "${ROOT_WWW_PATH}/assets/frontend/bundle" && ../../../indexer > .index-xhr
cd "${ROOT_WWW_PATH}/assets/cores" && ../../indexer > .index-xhr

# Cleanup downloaded and temporary files
rm -rf "${ROOT_WWW_PATH}/$(date -d "yesterday" '+%Y-%m-%d')_RetroArch.7z" "${ROOT_WWW_PATH}/assets/frontend/bundle.zip"
