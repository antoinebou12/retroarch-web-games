#!/bin/bash

ROOT_WWW_PATH="$1"

# Ensure ROOT_WWW_PATH is not empty
if [ -z "$ROOT_WWW_PATH" ]; then
    echo "Usage: $0 <path>"
    exit 1
fi

# Navigate to the target directory
cd "${ROOT_WWW_PATH}" || { echo "Failed to navigate to ${ROOT_WWW_PATH}"; exit 1; }

# Download RetroArch archive for yesterday's date
ARCHIVE_NAME="$(date -d "yesterday" '+%Y-%m-%d')_RetroArch.7z"
wget "https://buildbot.libretro.com/nightly/emscripten/${ARCHIVE_NAME}" || { echo "Failed to download archive"; exit 1; }

# Extract the RetroArch archive
if 7z x -y "${ARCHIVE_NAME}"; then
    if [ -d "retroarch" ]; then
        cp -r retroarch/. .
        rm -rf retroarch
    else
        echo "Extraction did not create the expected 'retroarch' directory."
    fi
else
    echo "Failed to extract ${ARCHIVE_NAME}"
    exit 1
fi
# Remove a specific script tag from index.html if present
if [ -f "./index.html" ]; then
    sed -i '/<script src="analytics.js"><\/script>/d' ./index.html
else
    echo "index.html not found, skipping script tag removal."
fi

# Ensure indexer is executable, if it exists
if [ -f "./indexer" ]; then
    chmod +x indexer
else
    echo "indexer not found, skipping chmod +x."
fi

# No need to prepare these directories if they already exist
mkdir -p "assets/cores"
mkdir -p "assets/frontend/bundle"

# Combine bundle parts if they exist and extract the combined bundle
BUNDLE_PATH="./assets/frontend/bundle"
if ls "./assets/frontend/" 1> /dev/null 2>&1; then
	if [ -f "./assets/frontend/bundle.zip.aa" ]; then

		cat "./assets/frontend/bundle.zip."* > "${BUNDLE_PATH}/bundle.zip" && \
		7z x -y "${BUNDLE_PATH}/bundle.zip" -o"./assets/frontend/"
	else
		echo "No bundle parts to combine."
	fi
else
    echo "No bundle parts to combine."
fi

# Generate index files
current_dir=$(pwd)
if [ -f "indexer" ]; then
    cd "./assets/frontend/bundle" && echo $(pwd) && ../../../indexer > .index-xhr && echo "indexer found, generating index."
    cd "${current_dir}/assets/cores" && echo $(pwd) && ../../indexer > .index-xhr && echo "indexer found, generating index."
else
	echo "indexer not found, skipping index generation."
fi

echo "Setup completed."
