#!/bin/sh

BASE_DIR="$HOME/Hyprdots_main/config/waybar/"
CONFIG_DIR="$HOME/.config/waybar/"

if [ ! -d "$BASE_DIR" ]; then
  echo "[ERROR]: Dir $BASE_DIR is not exists"
  exit 1
fi

mkdir -p "$CONFIG_DIR"

for file in "$BASE_DIR"*; do
  if [ -f "$file" ] && [ ! -d "$file" ]; then
    filename=$(basename "$file")
    ln -sf "$file" "$CONFIG_DIR/$filename"
    echo "[INFO]: Created symlink: $CONFIG_DIR/$filename"
  fi
done

# Перезапускаем waybar
killall waybar 2>/dev/null
sleep 1
waybar -c "${CONFIG_DIR}/config.jsonc" & 2>/dev/null

