#!/bin/bash

eww="$HOME/.config/eww/widgets/popups"
PIDFILE="/tmp/popup.pid"

if [ -f "$PIDFILE" ]; then
    OLD_PID=$(cat "$PIDFILE")
      kill -9 $OLD_PID 2>/dev/null
        rm -f "$PIDFILE"
fi

echo $$ > "$PIDFILE"

window_state="$(eww get -c $eww brightness-state)"

if [[ $window_state = "false" ]]; then
    eww update -c "$eww" brightness-state=true
fi

eww update -c "$eww" volume-state=false

"$eww/scripts/brightness_updater.sh" 2>/dev/null

sleep 1.2
eww update -c "$eww" brightness-state=false

rm -f "$PIDFILE"


