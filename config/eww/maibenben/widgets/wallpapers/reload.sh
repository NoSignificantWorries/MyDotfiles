#!/bin/bash

eww="$HOME/.config/eww/widgets/wallpapers"

rm -rf "/tmp/wallpapers"

python "$eww/main.py"

eww update -c "$eww" img_grid='$(cat "/tmp/wallpapers/data.json")'

