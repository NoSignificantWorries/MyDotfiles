#!/bin/bash

eww="$HOME/.config/eww/widgets/panel"

state=$(swaync-client -D)

eww update -c "$eww" noti-dnd-state=$state

echo $state

