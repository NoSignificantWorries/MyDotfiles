#!/bin/bash

eww="$HOME/.config/eww/widgets/panel"

cover_path="/tmp/player_cover.jpg"
default_icon="/usr/share/icons/hicolor/64x64/apps/multimedia-player.png"

status=$(playerctl status 2>/dev/null)
if [ "$status" != "Playing" ] && [ "$status" != "Paused" ]; then
  eww update -c "$eww" playing=false
  eww update -c "$eww" player-status=false
  echo "$default_icon"
  exit 0
elif [ "$status" = "Playing" ]; then
  eww update -c "$eww" playing=true
  eww update -c "$eww" player-status=true
elif [ "$status" = "Paused" ]; then
  eww update -c "$eww" playing=false
  eww update -c "$eww" player-status=true
fi

title=$(playerctl metadata title 2>/dev/null)
eww update -c "$eww" player-title="$title"

shuffle=$(playerctl shuffle 2>/dev/null)
if [ "$shuffle" = "On" ]; then
  eww update -c "$eww" player-shuffle=true
else
  eww update -c "$eww" player-shuffle=false
fi

loop=$(playerctl loop 2>/dev/null)
eww update -c "$eww" player-loop="$loop"

all_time=$(playerctl metadata mpris:length)
eww update -c "$eww" player-all-time="$all_time"


cover=$(playerctl metadata mpris:artUrl 2>/dev/null)

rm -f "$cover_path"

if [[ "$cover" == http* ]]; then
  curl -s --max-time 5 "$cover" -o "$cover_path" 2>/dev/null
elif [[ "$cover" == data:image*base64,* ]]; then
  base64data="${cover##*,}"
  echo "$base64data" | base64 -d > "$cover_path" 2>/dev/null
fi

if [ -f "$cover_path" ] && [ -s "$cover_path" ]; then
  if command -v convert >/dev/null 2>&1; then
    convert "$cover_path" -resize 200x200^ -gravity center -extent 200x200 -quality 95 "$cover_path" 2>/dev/null
  fi
  echo "$cover_path"
else
  echo "$default_icon"
fi

