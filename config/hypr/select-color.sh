#!/bin/bash

color_file="/tmp/color.png"
size=64

color=$(hyprpicker -n -a)

magick -size ${size}x${size} xc:$color "$color_file"

notify-send "Colorpicker" "Color <span color='$color'>$color</span> copiet to the clipboard" -i "$color_file"

