#!/usr/bin/sh

config="$HOME/.config/eww/widgets/bar"
pid_file="$HOME/.config/eww/widgets/bar/data.pid"

if [ -f "$pid_file" ]; then
  old_pid=$(cat "$pid_file")
  if kill -0 "$old_pid" 2>/dev/null; then
    echo "Останавливаем старый data.py (PID: $old_pid)"
    kill "$old_pid"
    sleep 0.5
  fi
  rm -f "$pid_file"
fi

eww daemon 2>/dev/null
eww --force-wayland open-many -c "$config" bar-window 2>/dev/null

python3 -u "$HOME/.config/eww/widgets/bar/scripts/data.py" > /dev/null 2>&1 &
python_pid=$!
echo $python_pid > "$pid_file"
disown $python_pid
echo "data.py запущен (PID: $!)"

