#!/usr/bin/sh

config="$HOME/.config/eww/widgets/hud"
pid_file="$HOME/.config/eww/widgets/hud/data.pid"

if [ -f "$pid_file" ]; then
  old_pid=$(cat "$pid_file")
  echo "Перезапуск data.py (старый PID: $old_pid)"
  kill "$old_pid" 2>/dev/null
  rm -f "$pid_file"
fi

eww --force-wayland close-many -c "$config" hud-window volume-window brightness-window 2>/dev/null
eww --force-wayland open-many -c "$config" hud-window volume-window brightness-window 2>/dev/null

python3 -u "$HOME/.config/eww/widgets/hud/data.py" > /dev/null 2>&1 &
python_pid=$!
echo $python_pid > "$pid_file"
disown $python_pid
echo "data.py перезапущен (PID: $python_pid)"

