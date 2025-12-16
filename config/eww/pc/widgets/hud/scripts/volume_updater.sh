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

MUTED=$(wpctl get-volume @DEFAULT_AUDIO_SINK@ | grep -c 'MUTED')
VALUE=$(wpctl get-volume @DEFAULT_AUDIO_SINK@ | awk '{print $2*100}' | tr -d '%')

if [ "$MUTED" -eq 1 ]; then
  icon=" "
elif [ "$VALUE" -le 33 ]; then
  icon=" "
elif [ "$VALUE" -le 66 ]; then
  icon=" "
else
  icon=" "
fi

if [ "$MUTED" -eq 1 ]; then
  color="#6c7086"
elif [ "$VALUE" -le 10 ]; then
  color="#005f56"
elif [ "$VALUE" -le 20 ]; then
  color="#007f66"
elif [ "$VALUE" -le 30 ]; then
  color="#009f76"
elif [ "$VALUE" -le 40 ]; then
  color="#00bf86"
elif [ "$VALUE" -le 50 ]; then
  color="#00df96"
elif [ "$VALUE" -le 60 ]; then
  color="#00ffa6"
elif [ "$VALUE" -le 70 ]; then
  color="#40ffb6"
elif [ "$VALUE" -le 80 ]; then
  color="#80ffc6"
elif [ "$VALUE" -le 90 ]; then
  color="#b0ffd6"
else
  color="#e0ffe6"
fi

eww update -c $eww vol-icon=$icon
eww update -c $eww vol-color=$color
if [ "$MUTED" -eq 1 ]; then
  eww update -c $eww vol-mute=true
else
  eww update -c $eww vol-mute=false
fi

echo "$VALUE"

