#!/usr/bin/sh

pid_file="$HOME/.config/hypr/system.pid"

if [ -f "$pid_file" ]; then
  old_pid=$(cat "$pid_file")
  if kill -0 "$old_pid" 2>/dev/null; then
    echo "Останавливаем старый system.py (PID: $old_pid)"
    kill "$old_pid"
    sleep 0.5
  fi
  rm -f "$pid_file"
fi

python3 -u "$HOME/.config/hypr/system.py" > /dev/null 2>&1 &
python_pid=$!
echo $python_pid > "$pid_file"
disown $python_pid
echo "system.py запущен (PID: $!)"

