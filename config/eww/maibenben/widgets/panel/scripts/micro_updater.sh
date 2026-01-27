#!/bin/sh

MIC_ICONS=( "" "" )
VOL_COLORS=( "#6c7086" "#00df96" )

eww="$HOME/.config/eww/widgets/bar"

if [ -n "$1" ]; then
  case "$1" in
    toggle)
      wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle
      ;;
    *)
      wpctl set-volume @DEFAULT_AUDIO_SOURCE@ ${1}%
      ;;
  esac
fi

out=$(wpctl get-volume @DEFAULT_AUDIO_SOURCE@)
muted=$(echo "$out" | grep -c 'MUTED')
mic=$(echo "$out" | awk '{print $2*100}')
if [ $muted -gt 0 ]; then
  eww update -c "$eww" mic-mute=true
  eww update -c "$eww" mic-color=${VOL_COLORS[0]}
  index=0
else
  eww update -c "$eww" mic-mute=false
  eww update -c "$eww" mic-color=${VOL_COLORS[1]}
  index=1
fi

eww update -c "$eww" mic-icon=${MIC_ICONS[$index]}
if [ -n "$1" ]; then
  eww update -c "$eww" mic=$mic
else
  eww update -c "$eww" mic=$mic
  echo $mic
fi

