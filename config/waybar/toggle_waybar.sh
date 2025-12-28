#!/bin/sh

WAYBAR_PID=$(pidof waybar)
CONFIG_PATH="$HOME/.config/waybar/config.jsonc"

if [ -n "${WAYBAR_PID}" ]; then
    kill "${WAYBAR_PID}"
else
    waybar -c "${CONFIG_PATH}" &
fi

