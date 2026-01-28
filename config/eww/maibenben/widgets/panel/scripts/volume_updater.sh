#!/bin/sh

VOL_ICONS=( "" "" "" "" )

eww="$HOME/.config/eww/widgets/panel"

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

out=$(wpctl get-volume @DEFAULT_AUDIO_SINK@)
muted=$(echo "$out" | grep -c 'MUTED')
vol=$(echo "$out" | awk '{print $2*100}')
if [ $muted -gt 0 ]; then
  eww update -c "$eww" vol-mute=true
  index=0
else
  eww update -c "$eww" vol-mute=false
  if [ $vol -eq 0 ]; then
    index=0
  elif [ $vol -le 33 ]; then
    index=1
  elif [ $vol -le 66 ]; then
    index=2
  else
    index=3
  fi
fi

eww update -c "$eww" vol-icon=${VOL_ICONS[$index]}
if [ -n "$1" ]; then
  eww update -c "$eww" vol=$vol
else
  eww update -c "$eww" vol=$vol
  echo $vol
fi

