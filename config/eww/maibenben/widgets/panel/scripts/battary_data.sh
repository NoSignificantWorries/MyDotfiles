#!/bin/bash

eww="$HOME/.config/eww/widgets/panel"

BAT_ICONS_CHARGING=( "󰢟" "󰢜" "󰂆" "󰂇" "󰂈" "󰢝" "󰂉" "󰢞" "󰂋" "󰂅" )
BAT_ICONS_NORMAL=( "󱃍" "󰁺" "󰁻" "󰁼" "󰁽" "󰁾" "󰁿" "󰂀" "󰂁" "󰁹" )

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
  time_str=$(echo "$DATA" | grep -oP '\d{2}:\d{2}:\d{2}')
  H=$(echo "$time_str" | cut -d: -f1)
  M=$(echo "$time_str" | cut -d: -f2)
  if [ "$STATE" = "Charging" ]; then
    TIME="${H}h ${M}m to full"
    ICON="${BAT_ICONS_CHARGING[${idx}]}"
  else
    TIME="${H}h ${M}m to empty"
  fi
fi

eww update -c "$eww" bat-time="$TIME"
eww update -c "$eww" bat-icon="$ICON"
eww update -c "$eww" bat="$PERCENT"
echo "$PERCENT"

