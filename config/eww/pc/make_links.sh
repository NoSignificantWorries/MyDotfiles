#!/bin/sh

CONF_DIR="$HOME/.config/eww"
SOURCE_DIR="$HOME/Dotfiles/config/eww/pc"

mkdir -p $CONF_DIR

ln -sf "$SOURCE_DIR/colors" "$CONF_DIR/colors"
ln -sf "$SOURCE_DIR/widgets" "$CONF_DIR/widgets"

