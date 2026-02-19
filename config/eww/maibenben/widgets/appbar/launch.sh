#!/usr/bin/sh

config="$HOME/.config/eww/widgets/appbar"

# eww daemon 2>/dev/null
eww --force-wayland open -c "$config" --toggle apps-window 2>/dev/null

