#!/usr/bin/sh

config="$HOME/.config/eww/widgets/wallpapers"

eww daemon 2>/dev/null
eww --force-wayland open-many -c "$config" wallpapers-window 2>/dev/null

