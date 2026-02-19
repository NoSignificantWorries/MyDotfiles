import re
import json
from pathlib import Path


SIZE=64
CACHE = Path("~/.cache/all-apps-icons.json").expanduser()
APPS_CONF = Path("~/.config/eww/widgets/apps_list.json").expanduser()
APPS = Path("~/.config/eww/widgets/apps.json").expanduser()
DEFAULT_ICON = Path("~/.icons/desktop/unknown_app.png").expanduser()
DIRS = [
    "/usr/share/icons",
    "~/.local/share/icons",
    "/usr/share/pixmaps",
    "~/.icons"
]
APPS_DIRS = [
    "/usr/share/applications",
    "~/.local/share/applications"
]

def desktop_file(app_name, apps_dirs=APPS_DIRS):
    all_paths = []
    for apps_dir in apps_dirs:
        root = Path(apps_dir).expanduser()
        all_paths.extend(list(root.rglob("*.desktop")))

    paths = []
    for path in all_paths:
        if app_name.lower() in path.name.lower().split(".")[0]:
            paths.append(path)

            print(paths)

    def score(path):
        name = path.name.lower()
        name_score = 1 if app_name == name.split(".")[0] else 0
        return name_score

    if not paths:
        return None

    return max(paths, key=score)


def all_desktop_files(apps_dirs=APPS_DIRS):
    all_paths = []
    for apps_dir in apps_dirs:
        root = Path(apps_dir).expanduser()
        all_paths.extend(list(root.rglob("*.desktop")))

    return all_paths


def get_app_icon(path):
    with open(path, "r") as file:
        content = file.read()

    icon_match = re.search(r'Icon[=:]\s*([^\s\n]+)', content)
    if icon_match:
        icon_name = icon_match.group(1)
        return icon_name

    return None


def find_icons(app_name, dirs):
    app_name = app_name.split(" ")[0]
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
        if "Papirus" in path_str:
            size_score += 20
        if f"{SIZE}x{SIZE}" in path_str:
            size_score = 100
        elif "48x48" in path_str:
            size_score = 90
        elif "32x32" in path_str:
            size_score = 80
        else:
            size_score = 50
        return size_score + name_score, icon.stat().st_size

    if not paths:
        return DEFAULT_ICON

    return max(paths, key=score_icon)


def find_apps_icons(app_names, cache_file=CACHE, dirs=DIRS):
    if cache_file.exists():
        with open(cache_file, "r") as file:
            cache = json.load(file)
    else:
        cache = {
            "apps-list": [],
            "apps": {}
        }

    icons = []
    for app_name in app_names:
        if app_name in cache["apps-list"]:
            icons.append(cache["apps"][app_name]["icon"])

        cache["apps-list"].append(app_name)

        dfile = desktop_file(app_name)
        if dfile is None:
            icon = find_icons(app_name, dirs)
            icons.append(icon)
            cache["apps"].update({
                app_name: { "icon": str(icon) }
            })
            continue

        dicon = get_app_icon(dfile)
        if dicon is None:
            icon = find_icons(app_name, dirs)
            icons.append(icon)
            cache["apps"].update({
                app_name: { "icon": str(icon) }
            })
            continue

        icon = find_icons(dicon, dirs)
        icons.append(icon)
        cache["apps"].update({
            app_name: { "icon": str(icon) }
        })

    with open(cache_file, "w") as file:
        json.dump(cache, file, indent=2)

    return icons


def main():
    with open(APPS, "r") as file:
        apps = json.load(file)

    res = []
    for app in apps:
        icon = find_apps_icons([app["class"]])[0]
        res.append({
            "id": app["id"],
            "class": app["class"],
            "icon": icon,
            "cmd": app["cmd"]
        })
    res = list(sorted(res, key=lambda x: x["id"]))
    res = {
        "count": len(res),
        "apps": res
    }

    with open(APPS_CONF, "w") as file:
        json.dump(res, file, indent=2)


if __name__ == "__main__":
    main()


