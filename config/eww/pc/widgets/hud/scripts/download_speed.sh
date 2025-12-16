#!/bin/sh

IF="eth0"
R1=$(cat /sys/class/net/$IF/statistics/rx_bytes)
sleep 1
R2=$(cat /sys/class/net/$IF/statistics/rx_bytes)
RXBPS=$((R2 - R1))
echo $((RXBPS / 1024))
