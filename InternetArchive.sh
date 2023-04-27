#!/bin/bash

url="https://archive.org/download/nointro.nes-headered"

wget -qO- "$url" | \
  grep -Eo '<td><a href="[^"]+\.7z' | \
  head -1 | \
  sed 's/^<td><a href="//' | \
  while read -r file; do
    wget -nc --show-progress --quiet "$url/$file"
  done

echo "All .7z files have been downloaded."
