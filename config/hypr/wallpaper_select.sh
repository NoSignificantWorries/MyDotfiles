#!/bin/sh

wallpaper="$HOME/.wallpaper"

img=$(zenity --file-selection --file-filter="Images | *.jpg *.png *.jpeg" --title="Wallpaper select")

[ -z "$img" ] && exit 1

ln -sf "${img}" "${wallpaper}"
swww img "${wallpaper}" --transition-type wipe

