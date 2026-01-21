from manager import Node, Stage, Tree, Link, Copy, Provider, Cmd, Fork


base = Provider(((lambda pkg: f"sudo pacman -S {pkg} --noconfirm"), "sudo pacman -Suuy"))
aur = Provider(((lambda pkg: f"paru -S {pkg} --noconfirm"), "paru -Suuy"))

version = "maibenben"
Node.dry_run = False
Node.tmp_only = False
Node.with_tmp_dir = True

Node.actions_enabled["cmd"] = False
Node.actions_enabled["popen"] = False

config = Stage(("Config",), [
    Stage(("Packages",), [
        base.pkgs(["git",
                   "wget",
                   "curl",
                   "base-devel",
                   "unzip",
                   "tar",
                   "7zip",
                   "mesa" if version == "maibenben" else "nvidia",
                   "hyprland",
                   "hyprlock",
                   "hypridle",
                   "kitty",
                   "rofi",
                   "swww",
                   "wl-clipboard",
                   "cliphist"]),
        Cmd(["sudo usermod -aG input,fprint $USER"]),
        base.pkgs(["pipewire",
                   "pipewire-alsa",
                   "pipewire-pulse",
                   "pipewire-jack",
                   "wireplumber"]),
        base.pkgs(["qt5-wayland",
                   "qt6-wayland",
                   "qt6-svg",
                   "qt6-declarative",
                   "qt5-quickcontrols2",
                   "gtk3",
                   "gtk4",
                   "xdg-desktop-portal",
                   "xdg-desktop-portal-gtk", ]),
        base.pkgs(["sddm"]),
        Cmd(["sudo systemctl enable sddm.service",
             "sudo systemctl start sddm.service"]),
        aur.pkgs(["fontconfig",
                  "ttf-jetbrains-mono-nerd",
                  "woff2-font-awesome",
                  "woff2-fira-code",
                  "noto-fonts-emoji",
                  "ttf-iosevka",
                  "ttf-all-the-icons"]),
        Cmd(["fc-cache -f -v"]),
        aur.pkgs(["qt5ct",
                  "qt6ct",
                  "nwg-look",
                  "kvantum",
                  "lxappearance"]),
        aur.pkgs(["bluez",
                  "bluez-utils",
                  "brightnessctl",
                  "openssh"]),
        aur.pkgs(["wlogout", "kanata"]),
        aur.pkgs(["opentabletdriver-git"]),
        aur.pkgs(["nushell"]),
        Cmd(["chsh -s $(which nu)"]),
        aur.pkgs(["upower",
                  "nvtop",
                  "bottom",
                  "powertop",
                  "ncdu",
                  "ps_mem",
                  "neofetch",
                  "nitch",
                  "atuin",
                  "yazi",
                  "lsd",
                  "tmux",
                  "timg",
                  "tree",
                  "lazygit",
                  "slidev-cli",
                  "bc",
                  "fzf",
                  "fd",
                  "ripgrep",
                  "tumbler",
                  "libnotify",
                  "ripdrag-git",
                  "zoxide"]),
        aur.pkgs(["papirus-icon-theme", "papirus-folders"]),
        Cmd(["papirus-folders -C yaru --theme Papirus-Dark"]),
        aur.pkgs(["imagemagick",
                  "pavucontrol",
                  "mission-center",
                  "network-manager-applet",
                  "blueman",
                  "gnome-disk-utility",
                  "bleachbit"]),
        aur.pkgs(["xed",
                  "mpv",
                  "zathura",
                  "geeqie",
                  "nemo",
                  "zathura-pdf-mupdf"]),
        aur.pkgs(["zen-browser-bin",
                  "min-browser-bin",
                  "telegram-desktop",
                  "visual-studio-code",
                  "obsidian",
                  "hiddify",
                  "gitkraken",
                  "xournalpp"])
    ]),
    Stage(("Links",), [
        Tree(("~/Hyprdots_main", "~"), [
            Tree(("config", ".config",), [
                # home
                Link("home/vimrc", "~/.vimrc"),
                Link("home/tmux.conf", "~/.tmux.conf"),
                # config
                Link("starship.toml"),
                Link("mimeapps.list"),
                # bottom
                Link("bottom/bottom.toml"),
                # btop
                Link("btop/themes/catppuccin_mocha.theme"),
                Link("btop/btop.conf"),
                # kitty
                Link("kitty/kitty.conf"),
                Link("kitty/theme.conf"),
                # lsd
                Link("lsd/colors.yaml"),
                Link("lsd/config.yaml"),
                # mpv
                Link("mpv/mpv.conf"),
                # neofetch
                Link("neofetch/config.conf"),
                # kvantum
                Tree(("Kvantum",), [
                    Copy("catppuccin-mocha-mauve"),
                    Link("kvantum.kvconfig")
                ]),
                # atuin
                Tree(("atuin",), [
                    Link("themes/catppuccin-mocha-lavender.toml"),
                    Link("atuin-receipt.json"),
                    Link("config.toml"),
                ]),
                # rofi
                Tree(("rofi",), [
                    Link("menu/launch.sh"),
                    Link("menu/menu.rasi"),
                    Link("themes/catppuccin-mocha.rasi")
                ]),
                # nushell
                Tree(("nushell",), [
                    Link("catppuccin.nu"),
                    Link("config.nu"),
                    Link("env.nu")
                ]),
                # swaync
                Tree(("swaync",), [
                    Link("config.json"),
                    Link("notification.ogg"),
                    Link("style.css")
                ]),
                # wlogout
                Tree(("wlogout",), [
                    Copy("icons"),
                    Link("layout"),
                    Link("logout_menu.sh"),
                    Link("style.css"),
                    Link("theme.css"),
                ]),
                # yazi
                Tree(("yazi",), [
                    Link("init.lua"),
                    Link("keymap.toml"),
                    Link("theme.toml"),
                    Link("yazi.toml"),
                ]),
                # hypr
                Tree(("hypr",), [
                    Fork(version == "maibenben",
                         [Link("hyprland.maibenben.conf", "hyprland.conf"),
                          Link("monitors.maibenben.conf", "monitors.conf")],
                         [Link("hyprland.main.conf", "hyprland.conf"),
                          Link("nvidia.conf")]),
                    Link("animation.conf"),
                    Link("windowrules.conf"),
                    Link("hypridle.conf"),
                    Link("hyprlock.conf"),
                    Link("keybindings.conf"),
                    Link("mocha.conf"),
                    Link("wallpaper_select.sh")
                ]),
                # eww
                Tree((f"eww/{version}", "eww"), [
                    Link("colors/catppuccin-mocha.scss"),
                    Tree(("widgets",), [
                        Tree(("bar",), [
                            Tree(("scripts",), [
                                Link("brightness_updater.sh"),
                                Link("micro_updater.sh"),
                                Link("volume_updater.sh"),
                                Link("battary_data.sh"),
                                Link("system.py"),
                                Link("data.py"),
                                Link("weather.py"),
                                Link("api.key"),
                            ]),
                            Link("eww.scss"),
                            Link("eww.yuck"),
                            Link("kill.sh"),
                            Link("launch.sh")
                        ])
                    ])
                ])
            ]),
            Tree(("scripts", ".scripts"), [
                Link("bluetooth/toggle_bluetooth.sh"),
                Link("network/toggle_wifi.sh"),
                Link("battery_allert.sh"),
                Link("fzf_preview.sh"),
                Link("screen_rec.sh"),
            ]),
            Tree(("icons", ".icons"), [
                Copy("desktop"),
                Copy("notify")
            ])
        ])
    ]),
    Stage(("Post-install",), [
        Cmd(["atuin init nu | save -f ~/.config/nushell/.atuin.nu",
             "zoxide init nushell | save -f ~/.config/nushell/.zoxide.nu"])
    ])
])


config.compile()

config.go()

