#!/usr/bin/sh

config="$HOME/.config/eww/widgets/hud"

eww daemon 2>/dev/null

eww --force-wayland open-many -c "$config" hud-window volume-window 2>/dev/null

