import re
import json
from pathlib import Path


SIZE=64
CACHE = Path("~/.cache/icons.json").expanduser()
DEFAULT_ICON = Path("").expanduser()
DIRS = [
    "/usr/share/icons/Papirus",
    "~/.local/share/icons",
    "/usr/share/pixmaps",
    "~/.icons"
]

def desktop_file(app_name, apps_dir="/usr/share/applications"):
    root = Path(apps_dir)
    paths = list(root.rglob(f"*{app_name}*.desktop"))

    def score(path):
        name = path.name.lower()
        name_score = 1 if app_name == name.split(".")[0] else 0
        return name_score

    if not paths:
        return None

    return max(paths, key=score)


def get_icon(path):
    with open(path, "r") as file:
        content = file.read()

    icon_match = re.search(r'Icon[=:]\s*([^\s\n]+)', content)
    if icon_match:
        icon_name = icon_match.group(1)
        return icon_name
    return None


def find_icons(app_name, dirs):
    paths = []
    for root_dir in dirs:
        root = Path(root_dir).expanduser()
        for ext in [".svg", ".png"]:
            paths += list(root.rglob(f"*{app_name}*{ext}"))

    def score_icon(icon):
        name = icon.name.lower()
        path_str = str(icon)
        name_score = 10 if app_name.lower() == name.split('.')[0] else 5
        size_score = 0
        if f"{SIZE}x{SIZE}" in path_str:
            size_score = 100
        else:
            size_score = 50
        return size_score + name_score, icon.stat().st_size

    if not paths:
        return DEFAULT_ICON

    return max(paths, key=score_icon)


def main(app_names, cache_file=CACHE, dirs=DIRS):
    if cache_file.exists():
        with open(cache_file, "r") as file:
            cache = json.load(file)
    else:
        cache = {
            "apps-list": [],
            "apps": []
        }

    for app_name in app_names:
        if app_name in cache["apps-list"]:
            continue

        cache["apps-list"].append(app_name)

        dfile = desktop_file(app_name)
        if dfile is None:
            icon = find_icons(app_name, dirs)
            cache["apps"].append({
                "app": app_name,
                "icon": str(icon)
            })
            continue

        dicon = get_icon(dfile)
        if dicon is None:
            icon = find_icons(app_name, dirs)
            cache["apps"].append({
                "app": app_name,
                "icon": str(icon)
            })
            continue

        icon = find_icons(dicon, dirs)
        cache["apps"].append({
            "app": app_name,
            "icon": str(icon)
        })

    with open(cache_file, "w") as file:
        json.dump(cache, file)


if __name__ == "__main__":
    main(["zen", "firefox", "kitty", "hiddify", "org.telegram.desktop"], CACHE, DIRS)


