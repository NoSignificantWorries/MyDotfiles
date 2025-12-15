#!/bin/sh

MUTED=$(wpctl get-volume @DEFAULT_AUDIO_SINK@ | grep -c 'MUTED')
VALUE=$(wpctl get-volume @DEFAULT_AUDIO_SINK@ | awk '{print $2*100}' | tr -d '%')

get_icon() {
  if [ "$MUTED" -eq 1 ]; then
    icon=" "
  elif [ "$VALUE" -le 33 ]; then
    icon=" "
  elif [ "$VALUE" -le 66 ]; then
    icon=" "
  else
    icon=" "
  fi

  echo "$icon"
}

case "$1" in
  value)
    echo "$VALUE"
    ;;
  icon)
    echo $(get_icon)
    ;;
  color)
    if [ "$MUTED" -eq 1 ]; then
      color="#6c7086"
    elif [ "$VALUE" -le 10 ]; then
      color="#005f56"
    elif [ "$VALUE" -le 20 ]; then
      color="#007f66"
    elif [ "$VALUE" -le 30 ]; then
      color="#009f76"
    elif [ "$VALUE" -le 40 ]; then
      color="#00bf86"
    elif [ "$VALUE" -le 50 ]; then
      color="#00df96"
    elif [ "$VALUE" -le 60 ]; then
      color="#00ffa6"
    elif [ "$VALUE" -le 70 ]; then
      color="#40ffb6"
    elif [ "$VALUE" -le 80 ]; then
      color="#80ffc6"
    elif [ "$VALUE" -le 90 ]; then
      color="#b0ffd6"
    else
      color="#e0ffe6"
    fi
    echo $color
    ;;
  *)
    echo "$MUTED"
    ;;
esac

