#!/bin/sh

eww="$HOME/.config/eww/widgets/hud"

if [ -n "$1" ]; then
  brightnessctl s ${1}%
fi

