#!/bin/sh

if ! pgrep -x "wlogout" > /dev/null; then
    wlogout --layout ~/.config/wlogout/layout --css ~/.config/wlogout/style.css -b 6
fi

