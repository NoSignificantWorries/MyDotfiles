#!/usr/bin/sh

config="$HOME/.config/eww/widgets/panel"
pid_file="$HOME/.config/eww/widgets/panel/data.pid"

if [ -f "$pid_file" ]; then
  pid=$(cat "$pid_file")
  if kill -0 "$pid" 2>/dev/null; then
    echo "Убиваем data.py (PID: $pid)"
    kill "$pid"
  fi
  rm -f "$pid_file"
fi

eww close-all -c $config
pkill -f "eww daemon"

