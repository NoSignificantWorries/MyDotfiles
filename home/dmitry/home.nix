{ config, pkgs, ... }:

{
  home.username = "dmitry";
  home.homeDirectory = "/home/dmitry";
  home.stateVersion = "25.11";

  wayland.windowManager.hyprland = {
    enable = true;
    systemdIntegration = true;
  };

  home.packages = [
    xdg-desktop-portal-hyprland
    hyprpaper
    hypridle
    wl-clipboard
  ];
}

