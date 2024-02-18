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


download_zip_files() {
  url="$1"
  wget -qO- "$url" | \
    grep -Eo '<td><a href="[^"]+\.zip' | \
    head -1 | \
    sed 's/^<td><a href="//' | \
    while read -r file; do
      wget -nc --show-progress --quiet "$url/$file"
    done
}

export -f download_zip_files

urls=(
  "https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Game%20Boy/"
  "https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Game%20Boy%20%28Private%29/"
  "https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Game%20Boy%20Advance/"
  "https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Game%20Boy%20Color/"
)

parallel -j 4 download_zip_files ::: "${urls[@]}"
