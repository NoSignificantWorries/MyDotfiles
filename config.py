import shutil
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple


def p(path: Path | str) -> List[str]:
    if isinstance(path, Path):
        path = str(path)
    return path.split("/")


def pth(path: Path | str | List[str]) -> Path:
    if isinstance(path, str):
        path = Path(path)
    elif isinstance(path, List):
        path = Path("/".join(path))
    return path.expanduser()


def replace_path_elements(path: List[str], patterns: Optional[Dict[str, str]]) -> List[str]:
    if not patterns:
        return path
    res = []
    for elem in path:
        matched = patterns.get(elem)
        if matched:
            res.append(matched)
        else:
            res.append(elem)
    return res


class Node:
    dry_run = True
    params = {}

    def __init__(self, *args, **kwargs) -> None:
        self.parent = None
        self.nodes = []
        for arg in args:
            if isinstance(arg, Node):
                arg.parent = self
                self.nodes.append(arg)
        self.kwargs = kwargs

    def __call__(self) -> None:
        raise NotImplementedError("Error")

    def compile(self) -> None:
        raise NotImplementedError("Error")


class Stage(Node):
    def __init__(self, label: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.label = label

    def __call__(self) -> None:
        print(self.label)
        for node in self.nodes:
            node()

    def compile(self) -> None:
        for node in self.nodes:
            node.compile()


class Provider(Node):
    def __init__(self, installer: Callable, updater: str, get_installed: str, batch_size: int = 6, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.installer = installer
        self.updater = updater
        self.batch_size = batch_size
        self.list_of_pkgs = []

    def __call__(self) -> None:
        for i in range(0, len(self.list_of_pkgs), self.batch_size):
            cmd = self.installer(" ".join(self.list_of_pkgs[i:i + self.batch_size]))
            if self.dry_run:
                print("Installing batch:", cmd)
            else:
                print(cmd)
        for node in self.nodes:
            node()

    def pkgs(self, pkgs_list: List[str]):
        new = Provider(self.installer, self.updater, self.batch_size)
        new.list_of_pkgs = pkgs_list
        return new

    def compile(self) -> None:
        for node in self.nodes:
            node.compile()


class Cmd(Node):
    def __init__(self, commands: List[str], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.commands = commands

    def __call__(self) -> None:
        for cmd in self.commands:
            if self.dry_run:
                print("Running:", cmd)
            else:
                print(cmd)
        for node in self.nodes:
            node()

    def compile(self) -> None:
        for node in self.nodes:
            node.compile()


class Fork(Node):
    def __init__(self, rule: bool, optionA: Tuple[Node] | Node, optionB: Tuple[Node] | Node) -> None:
        self.nodes = optionA if rule else optionB
        if not isinstance(self.nodes, Tuple):
            self.nodes = (self.nodes,)

    def __call__(self) -> None:
        for node in self.nodes:
            node()

    def compile(self) -> None:
        for node in self.nodes:
            node.parent = self.parent
            node.compile()


class Tree(Node):
    def __init__(self, root: Path | str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.root = p(root)

    def __call__(self) -> None:
        for node in self.nodes:
            node()

    def compile(self) -> None:
        if isinstance(self.parent, Tree):
            self.root = self.parent.root + self.root
        for node in self.nodes:
            node.compile()


class Link(Node):
    def __init__(self, source: Path | str, target: Optional[Path | str] = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.source = p(source)
        self.target = p(target) if target else self.source

        self.action = (lambda source, target: target.symlink_to(source))

    def __call__(self) -> None:
        source = pth(self.source)
        target = pth(self.target)
        if self.dry_run:
            tmp_path = self.params.get("tmp-links")
            if tmp_path:
                tmp_target = pth(tmp_path + self.target[1:])
                print(f"Creation: {str(source)} -> {str(tmp_target)} -> {str(target)}")
            else:
                print(f"Creation: {str(source)} -> {str(target)}")
        else:
            if source.exists():
                tmp_path = self.params.get("tmp-links")
                if tmp_path:
                    tmp_target = pth(tmp_path + self.target[1:])
                    if tmp_target.exists() and tmp_target.is_file():
                        tmp_target.unlink()
                    if tmp_target.exists() and tmp_target.is_dir():
                        shutil.rmtree(tmp_target)
                    if target.exists():
                        target.unlink()
                    if target.exists() and target.is_dir():
                        shutil.rmtree(target)
                    tmp_target.parent.mkdir(parents=True, exist_ok=True)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    self.action(source, tmp_target)
                    self.action(tmp_target, target)
                else:
                    if target.exists() and target.is_file():
                        target.unlink()
                    if target.exists() and target.is_dir():
                        shutil.rmtree(target)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    self.action(source, target)

        for node in self.nodes:
            node()

    def compile(self) -> None:
        if self.parent and isinstance(self.parent, Tree):
            self.source = self.parent.root + self.source
            pwd = self.params.get("source-pwd")
            if pwd and self.source[0] != "~":
                self.source = pwd + self.source

            if self.target[0] != "~":
                self.target = self.parent.root + self.target
            pwd = self.params.get("target-pwd")
            if pwd and self.target[0] != "~":
                self.target = pwd + self.target
            self.target = replace_path_elements(self.target, self.params.get("matches"))


class Copy(Link):
    def __init__(self, source: Path | str, target: Optional[Path | str] = None, *args, **kwargs) -> None:
        super().__init__(source, target, *args, **kwargs)
        self.action = (lambda source, target: source.copy(target))


def main() -> None:
    base = Provider((lambda pkg: f"sudo pacman -S {pkg}"), "sudo pacman -Suuy", "sudo pacman -Qqe")
    aur = Provider((lambda pkg: f"paru -S {pkg}"), "paru -Suuy", "paru -Qqe")

    version = "maibenben"
    Node.dry_run = True
    Node.params = {
        "source-pwd": p("~/Hyprdots_main"),
        "target-pwd": p("~"),
        "tmp-links": p("~/.tmp_links"),
        "matches": {
            "config": ".config",
            "scripts": ".scripts",
            "icons": ".icons"
        }
    }

    config = Stage("Config",
                   Stage("Packages",
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
                                    "cliphist"
                                    ])
                         ),
                   Cmd(["sudo usermod -aG input,fprint $USER"]),
                   base.pkgs(["pipewire",
                              "pipewire-alsa",
                              "pipewire-pulse",
                              "pipewire-jack",
                              "wireplumber"
                              ]),
                   base.pkgs(["qt5-wayland",
                              "qt6-wayland",
                              "qt6-svg",
                              "qt6-declarative",
                              "qt5-quickcontrols2",
                              "gtk3",
                              "gtk4",
                              "xdg-desktop-portal",
                              "xdg-desktop-portal-gtk",
                              ]),
                   base.pkgs(["sddm"]),
                   Cmd([
                   "sudo systemctl enable sddm.service",
                   "sudo systemctl start sddm.service",
                   ]),
                   aur.pkgs([
                   "fontconfig",
                   "ttf-jetbrains-mono-nerd",
                   "woff2-font-awesome",
                   "woff2-fira-code",
                   "noto-fonts-emoji",
                   "ttf-iosevka"
                   ]),
                   Cmd(["fc-cache -f -v"]),
                   aur.pkgs([
                   "qt5ct",
                   "qt6ct",
                   "nwg-look",
                   "kvantum",
                   "lxappearance",
                   ]),
                   aur.pkgs([
                   "bluez",
                   "bluez-utils",
                   "brightnessctl",
                   "openssh",
                   ]),
                   aur.pkgs([
                   "wlogout",
                   "kanata",
                   ]),
                   aur.pkgs(["opentabletdriver-git"]),
                   aur.pkgs([
                   "nushell",
                   "zsh",
                   "oh-my-zsh-git",
                   "zsh-theme-powerlevel10k-git",
                   "zsh-autosuggestions",
                   "zsh-syntax-highlighting",
                   ]),
                   Cmd(["chsh -s $(which nu)"]),
                   aur.pkgs([
                   "upower",
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
                   "zoxide",
                   ]),
                   aur.pkgs([
                   "papirus-icon-theme",
                   "papirus-folders",
                   ]),
                   Cmd(["papirus-folders -C yaru --theme Papirus-Dark"]),
                   aur.pkgs([
                   "imagemagick",
                   "pavucontrol",
                   "mission-center",
                   "network-manager-applet",
                   "blueman",
                   "gnome-disk-utility",
                   "bleachbit",
                   ]),
                   aur.pkgs([
                   "xed",
                   "mpv",
                   "zathura",
                   "geeqie",
                   "nemo",
                   "zathura-pdf-mupdf",
                   ]),
                   aur.pkgs([
                   "zen-browser-bin",
                   "min-browser-bin",
                   "telegram-desktop",
                   "visual-studio-code",
                   "obsidian",
                   "hiddify",
                   "gitkraken",
                   "xournalpp",
                   ]),
                   Stage("Links",
                         Tree("config",
                              # config
                              Link("starship.toml"),
                              Link("mimeapps.list"),
                              Link("vimrc", "~/.vimrc"),
                              Link("tmux.conf", "~/.tmux.conf"),
                              # bottom
                              Link("bottom/bottom.toml"),
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
                              # hypr
                              Tree("hypr",
                                   Fork(version == "maibenben",
                                        (Link("hyprland.maibenben.conf", "hyprland.conf"),
                                         Link("monitors.maibenben.conf", "monitors.conf")),
                                        (Link("hyprland.main.conf", "hyprland.conf"),
                                         Link("nvidia.conf"))
                                        ),
                                   Link("animation.conf"),
                                   Link("windowrules.conf"),
                                   Link("hypridle.conf"),
                                   Link("hyprlock.conf"),
                                   Link("keybindings.conf"),
                                   Link("mocha.conf"),
                                   Link("wallpaper_select.sh")
                                   )
                              ),
                         Tree("scripts"),
                         Tree("icons",
                              Copy("desktop"),
                              Copy("notify")
                              )
                         ),
                   )

    config.compile()
    config()


if __name__ == "__main__":
    main()

