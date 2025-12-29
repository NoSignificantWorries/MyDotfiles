#!/bin/sh

eww="$HOME/.config/eww/widgets/hud"

if [ -n "$1" ]; then
  case "$1" in
    toggle)
      wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle
      ;;
    *)
      wpctl set-volume @DEFAULT_AUDIO_SINK@ ${1}%
      ;;
  esac
fi

