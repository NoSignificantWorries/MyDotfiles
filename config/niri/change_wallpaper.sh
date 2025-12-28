#!/bin/sh

WALLPAPER="$HOME/.wallpaper"

ln -sf "$1" "$WALLPAPER"

swww img "$WALLPAPER" --transition-type wipe

