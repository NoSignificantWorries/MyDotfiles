#!/bin/sh

ACTIVE=$(niri msg -j workspaces | jq '.[] | select(.is_active == true)')

name=$(echo "$ACTIVE" | jq -r ".name")
idx=$(echo "$ACTIVE" | jq -r ".idx")

case $name in
  code)
    res=" ${name}"
    ;;
  QoL)
    res="󰐵 ${name}"
    ;;
  *)
    res=" ${idx}"
    ;;
esac

echo $res

