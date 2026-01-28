#!/bin/bash

eww="$HOME/.config/eww/widgets/panel"

target=$(echo "scale=2; $1 * ($2 / 100)" | bc)

echo "$target"

playerctl position $target

