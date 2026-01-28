#!/bin/bash

eww="$HOME/.config/eww/widgets/panel"

status=$(playerctl status 2>/dev/null)
if [ "$status" != "Playing" ] && [ "$status" != "Paused" ]; then
  eww update -c "$eww" player-status=false
else
  eww update -c "$eww" player-status=true
fi

echo "${status}"

