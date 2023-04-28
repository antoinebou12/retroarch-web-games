#!/bin/bash

download_7z_files() {
  url="$1"
  wget -qO- "$url" | \
    grep -Eo '<td><a href="[^"]+\.7z' | \
    head -1 | \
    sed 's/^<td><a href="//' | \
    while read -r file; do
      wget -nc --show-progress --quiet "$url/$file"
    done
}

export -f download_7z_files

urls=(
  "https://archive.org/download/nointro.gb"
  "https://archive.org/download/nointro.gbc"
  "https://archive.org/download/nointro.gba"
  "https://archive.org/download/nointro.snes"
  "https://archive.org/download/nointro.md"
  "https://archive.org/download/nointro.nes-headered"
)

parallel -j 6 download_7z_files ::: "${urls[@]}"
