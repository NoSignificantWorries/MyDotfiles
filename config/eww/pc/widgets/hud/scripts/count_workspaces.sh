#!/bin/sh

count=$(niri msg -j workspaces | jq "length")

echo $count

