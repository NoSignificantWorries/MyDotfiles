#!/bin/bash

loop=$(playerctl loop 2>/dev/null)

if [ "$loop" = "None" ]; then
  playerctl loop track
elif [ "$loop" = "Track" ]; then
  playerctl loop playlist
else
  playerctl loop none
fi

