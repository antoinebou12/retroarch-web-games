#!/usr/bin/env bash
# download all the gba game
cd ~/retroarch
mkdir gba
cd gba
wget -m -np -c -U "eye01" -R "index.html*" "https://the-eye.eu/public/rom/Nintendo%20Gameboy%20Advance/"
unzip the-eye.eu/*.zip
rm -rf the-eye.eu/*.zip
mv the-eye.eu/* .

