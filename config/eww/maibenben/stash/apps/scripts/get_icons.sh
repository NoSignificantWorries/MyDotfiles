#!/bin/sh

theme_path="/usr/share/icons/Papirus/48x48/apps/"

find $theme_path /usr/share/pixmaps ~/.icons/desktop /usr/local/share/icons -name "*xournal*" -type f 2>/dev/null
find $theme_path /usr/share/pixmaps ~/.icons/desktop /usr/local/share/icons -name "*hiddify*" -type f 2>/dev/null
find $theme_path /usr/share/pixmaps ~/.icons/desktop /usr/local/share/icons -name "*text-editor*" -type f 2>/dev/null
find $theme_path /usr/share/pixmaps ~/.icons/desktop /usr/local/share/icons -name "*min-browser*" -type f 2>/dev/null
find $theme_path /usr/share/pixmaps ~/.icons/desktop /usr/local/share/icons -name "*emacs*" -type f 2>/dev/null
find $theme_path /usr/share/pixmaps ~/.icons/desktop /usr/local/share/icons -name "*code*" -type f 2>/dev/null
find $theme_path /usr/share/pixmaps ~/.icons/desktop /usr/local/share/icons -name "*obsidian*" -type f 2>/dev/null

