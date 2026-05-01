#!/bin/bash

idle_time_path="$HOME/.local/state/idle-time"

lock="$HOME/.config/niri/lock.sh"
if [ ! -f "$idle_time_path" ]; then
  echo "5 minutes" > idle_time_path
fi
idle_time=$(cat "$idle_time_path")
case $idle_time in
  "5 minutes")
    swayidle -w \
      timeout 300 $lock \
      timeout 420 'niri msg action power-off-monitors' \
      timeout 1800 'systemctl suspend' \
      before-sleep $lock
    ;;
  "10 minutes")
    swayidle -w \
      timeout 600 $lock \
      timeout 720 'niri msg action power-off-monitors' \
      timeout 1800 'systemctl suspend' \
      before-sleep $lock
    ;;
  "20 minutes")
    swayidle -w \
      timeout 1200 $lock \
      timeout 1500 'niri msg action power-off-monitors' \
      timeout 2400 'systemctl suspend' \
      before-sleep $lock
    ;;
  "30 minutes")
    swayidle -w \
      timeout 1800 $lock \
      timeout 2100 'niri msg action power-off-monitors' \
      timeout 3600 'systemctl suspend' \
      before-sleep $lock
    ;;
  "infinity") ;;
  *) ;;
esac

