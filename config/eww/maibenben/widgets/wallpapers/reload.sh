#!/bin/bash

eww="$HOME/.config/eww/widgets/wallpapers"

rm -rf "~/.cache/wallpapers"

python "$eww/main.py"

eww update -c "$eww" img_grid='$(cat "~/.cache/wallpapers/data.json")'

