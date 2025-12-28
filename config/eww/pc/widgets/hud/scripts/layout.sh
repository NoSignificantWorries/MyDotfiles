#!/bin/sh

LAYOUT=$(niri msg -j keyboard-layouts | jq -r ".names[.current_idx]")

case $LAYOUT in
  "Russian")
    LAYOUT="RU 🇷🇺"
    ;;
  "English (US)")
    LAYOUT="EN 🇺🇸"
    ;;
esac

echo $LAYOUT

