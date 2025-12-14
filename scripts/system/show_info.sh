#!/bin/bash

current_datetime=$(date "+%Y.%m.%d %H:%M:%S")

battery_info=$(upower -i $(upower -e | grep battery) 2>/dev/null)

if [ -n "$battery_info" ]; then
    battery_percentage=$(echo "$battery_info" | grep "percentage" | awk '{print $2}')
    
    battery_time=$(echo "$battery_info" | grep "time to empty" | awk -F: '{print $2}' | xargs)
    
    if [ -z "$battery_time" ]; then
        battery_time="не доступно"
    fi
else
    battery_percentage="не доступно"
    battery_time="не доступно"
fi

message="  Datetime: $current_datetime
󱊢 Battery charge: $battery_percentage ($battery_time)"

notify-send "Системная информация" "$message"

