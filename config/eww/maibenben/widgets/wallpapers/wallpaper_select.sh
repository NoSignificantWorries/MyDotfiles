#!/bin/sh

wallpaper="$HOME/.wallpaper"

[ -z "$1" ] && exit 1

ln -sf "$1" "${wallpaper}"

notify-send "Wallpapers" "Selected wallpaper '$3'" -i "$2"

swww img "${wallpaper}" --transition-type wipe

