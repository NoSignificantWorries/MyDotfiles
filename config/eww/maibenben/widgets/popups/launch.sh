#!/usr/bin/sh

config="$HOME/.config/eww/widgets/popups"

# eww daemon 2>/dev/null
eww --force-wayland open-many -c "$config" volume-window brightness-window 2>/dev/null

