#!/usr/bin/sh

config="$HOME/.config/eww/widgets/apps"

eww daemon 2>/dev/null

eww --force-wayland open-many -c "$config" apps-window 2>/dev/null
