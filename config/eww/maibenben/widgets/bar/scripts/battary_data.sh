#!/bin/bash

eww="$HOME/.config/eww/widgets/bar"

BAT_ICONS_CHARGING=( "󰢟" "󰢜" "󰂆" "󰂇" "󰂈" "󰢝" "󰂉" "󰢞" "󰂋" "󰂅" )
BAT_ICONS_NORMAL=( "󱃍" "󰁺" "󰁻" "󰁼" "󰁽" "󰁾" "󰁿" "󰂀" "󰂁" "󰁹" )
BAT_COLORS=( "#ed8796" "#ea909e" "#e799a6" "#e3a3af" "#e0acb8" "#d0b7a2" "#c0c28c" "#b1cd76" "#a1d860" "#91e34a" )

DATA=$(acpi -b)

STATE=$(echo "$DATA" | grep -oP "(Charging|Discharging|Full)")
PERCENT=$(echo "$DATA" | grep -oP '\d+(?=%)')

if [ "$PERCENT" -le 10 ]; then
  idx=0
elif [ "$PERCENT" -le 20 ]; then
  idx=1
elif [ "$PERCENT" -le 30 ]; then
  idx=2
elif [ "$PERCENT" -le 40 ]; then
  idx=3
elif [ "$PERCENT" -le 50 ]; then
  idx=4
elif [ "$PERCENT" -le 60 ]; then
  idx=5
elif [ "$PERCENT" -le 70 ]; then
  idx=6
elif [ "$PERCENT" -le 80 ]; then
  idx=7
elif [ "$PERCENT" -le 90 ]; then
  idx=8
else
  idx=9
fi

ICON="${BAT_ICONS_NORMAL[${idx}]}"
if [ "$STATE" = "Full" ]; then
  TIME="Full"
else
  HOURS=$(echo "$DATA" | grep -oP '\K\d{2}(?=:)' | head -1)
  MINUTES=$(echo "$DATA" | grep -oP '\K\d{2}(?=:\d{2} remaining)' | head -1)
  if [ "$STATE" = "Charging" ]; then
    TIME="${HOURS}h ${MINUTES}m to full"
    ICON="${BAT_ICONS_CHARGING[${idx}]}"
  else
    TIME="${HOURS}h ${MINUTES}m to empty"
  fi
fi

eww update -c "$eww" bat-time="$TIME"
eww update -c "$eww" bat-icon="$ICON"
eww update -c "$eww" bat-color="${BAT_COLORS[${idx}]}"
if [ -n "$1" ]; then
  eww update -c "$eww" bat="$PERCENT"
else
  echo "$PERCENT"
fi

