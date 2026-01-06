#!/bin/sh

BR_ICONS=( "󰃜" "󰃝" "󰃞" "󰃠" )

eww="$HOME/.config/eww/widgets/hud"

if [ -n "$1" ]; then
  brightnessctl s ${1}%
fi

val=$(brightnessctl -m | cut -d ',' -f4 | tr -d '%')

if [ $val -le 25 ]; then
  index=0
elif [ $val -le 50 ]; then
  index=1
elif [ $val -le 75 ]; then
  index=2
else
  index=3
fi

eww update -c "$eww" br-icon=${BR_ICONS[$index]}
if [ -n "$1" ]; then
  eww update -c "$eww" br=$val
else
  eww update -c "$eww" br=$val
  echo $val
fi
