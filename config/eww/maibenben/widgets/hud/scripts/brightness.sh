#!/bin/sh

BRIGHTNESS=$(brightnessctl -m | cut -d ',' -f4 | tr -d '%')

case "$1" in
  color)
    if [ "$BRIGHTNESS" -le 10 ]; then
      color="#1a4a8c"
    elif [ "$BRIGHTNESS" -le 20 ]; then
      color="#2060a3"
    elif [ "$BRIGHTNESS" -le 30 ]; then
      color="#2676ba"
    elif [ "$BRIGHTNESS" -le 40 ]; then
      color="#2c8cd1"
    elif [ "$BRIGHTNESS" -le 50 ]; then
      color="#32a2e8"
    elif [ "$BRIGHTNESS" -le 60 ]; then
      color="#38b8ff"
    elif [ "$BRIGHTNESS" -le 70 ]; then
      color="#5ec6ff"
    elif [ "$BRIGHTNESS" -le 80 ]; then
      color="#84d4ff"
    elif [ "$BRIGHTNESS" -le 90 ]; then
      color="#aae2ff"
    else
      color="#d0f0ff"
    fi
    echo $color
    ;;
  icon)
    if [ "$BRIGHTNESS" -le 25 ]; then
      icon="󰃜"
    elif [ "$BRIGHTNESS" -le 50 ]; then
      icon="󰃝"
    elif [ "$BRIGHTNESS" -le 75 ]; then
      icon="󰃞"
    else
      icon="󰃠"
    fi
    echo "$icon"
    ;;
  *)
    echo "$BRIGHTNESS"
    ;;
esac

