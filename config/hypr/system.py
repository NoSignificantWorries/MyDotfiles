import os
import re
import sys
import json
import signal
import asyncio
import subprocess
from pathlib import Path


pid_file = Path("~/.config/hypr/system.pid").expanduser()


def cleanup(signum, frame):
    print("Получен SIGTERM, завершаем...")
    if os.path.exists(pid_file):
        os.unlink(pid_file)
    sys.exit(0)


signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGHUP, signal.SIG_IGN)

with open(pid_file, 'w') as f:
    f.write(str(os.getpid()))


CONFIG = Path("~/.config/eww/widgets/panel").expanduser()


NUMBER_ICONS = {
    "1": "󰎤",
    "2": "󰎧",
    "3": "󰎪",
    "4": "󰎭",
    "5": "󰎱",
    "6": "󰎳",
    "7": "󰎶",
    "8": "󰎹",
    "9": "󰎼",
    "10": "󰽽",
    "-98": "󰗣",
}


KB_LAYOUTS = {
    "Russian": "RU",
    "English (US)": "EN"
}

SIZE=64
CACHE = Path("~/.cache/icons.json").expanduser()
DEFAULT_ICON = Path("").expanduser()
DIRS = [
    "/usr/share/icons",
    "~/.local/share/icons",
    "/usr/share/pixmaps",
    "~/.icons"
]

def desktop_file(app_name, apps_dir="/usr/share/applications"):
    root = Path(apps_dir)
    all_paths = list(root.rglob("*.desktop"))

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


def find_app_icon(app_name, cache_file=CACHE, dirs=DIRS):
    if cache_file.exists():
        with open(cache_file, "r") as file:
            cache = json.load(file)
    else:
        cache = {
            "apps-list": [],
            "apps": {}
        }

    if app_name in cache["apps-list"]:
        return cache["apps"][app_name]["icon"]

    cache["apps-list"].append(app_name)

    dfile = desktop_file(app_name)
    if dfile is None:
        icon = find_icons(app_name, dirs)
        cache["apps"].update({
            app_name: { "icon": str(icon) }
        })
        with open(cache_file, "w") as file:
            json.dump(cache, file)
        return str(icon)

    dicon = get_icon(dfile)
    if dicon is None:
        icon = find_icons(app_name, dirs)
        cache["apps"].update({
            app_name: { "icon": str(icon) }
        })
        with open(cache_file, "w") as file:
            json.dump(cache, file)
        return str(icon)

    icon = find_icons(dicon, dirs)
    cache["apps"].update({
        app_name: { "icon": str(icon) }
    })
    with open(cache_file, "w") as file:
        json.dump(cache, file)
    return str(icon)


class EwwUpdater:
    @staticmethod
    def update(var: str, value: str):
        subprocess.run(['eww', '-c', CONFIG, 'update', f'{var}={value}'], stdout=subprocess.DEVNULL)


class CmdRunner:
    @staticmethod
    async def get_output(cmd: str) -> str:
        try:
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            try:
                text = stdout.decode('utf-8').strip()
            except UnicodeDecodeError:
                text =  stdout.decode('latin1').strip()
            return text
        except:
            return "N/A"


def parse_worspaces(ws, workspaces, active_workspaces, ws_clients):
    json_workspaces = []
    for w in workspaces:
        cmd = f"hyprctl dispatch workspace {w}"
        if w == ws:
            active = True
            occupied = False
        elif w in active_workspaces:
            active = False
            occupied = True
        else:
            active = False
            occupied = False
        wapps = ws_clients.get(w)
        if wapps is None:
            wapps = []
        json_workspaces.append({
                "active": active,
                "occupied": occupied,
                "empty": bool(wapps),
                "cmd": cmd,
                "text": NUMBER_ICONS[w],
                "apps": wapps
            })
    json_workspaces = {
        "count": len(json_workspaces),
        "data": json_workspaces
    }

    return json_workspaces


async def hyprland_events():
    his = os.environ.get('HYPRLAND_INSTANCE_SIGNATURE')
    if not his:
        print("Hyprland didn't start")
        return

    socket_path = f"{os.environ['XDG_RUNTIME_DIR']}/hypr/{his}/.socket2.sock"

    reader, writer = await asyncio.open_unix_connection(socket_path)

    try:
        devices_res = subprocess.run(["hyprctl", "devices", "-j"], capture_output=True, text=True)
        devices_text = devices_res.stdout
        devices = json.loads(devices_text)
        keyboards = devices["keyboards"]
        for kb in keyboards:
            if kb["main"]:
                print(kb)
                kb_layout = kb["active_keymap"]
                if kb_layout in KB_LAYOUTS.keys():
                    kb_layout = KB_LAYOUTS[kb_layout]
                EwwUpdater.update("kb_layout", kb_layout)
                break

        base_workspaces = {"1"}
        workspaces = base_workspaces.copy()
        current_workspace = "1"
        client_apps = dict()
        workspaces_json = parse_worspaces(current_workspace, sorted(workspaces), [], client_apps)
        EwwUpdater.update("workspaces-json", json.dumps(workspaces_json))
        while True:
            clients = await reader.readline()
            event = clients.decode().strip()
            print(event)
            event, value = event.split(">>", 1)
            if event == "activelayout":
                new_layout = value.split(",")[-1]
                if new_layout in KB_LAYOUTS.keys():
                    new_layout = KB_LAYOUTS[new_layout]
                EwwUpdater.update("kb_layout", new_layout)
            elif event == "submap":
                if len(value) > 0:
                    EwwUpdater.update("submap", value)
                    EwwUpdater.update("is_submap", "true")
                    subprocess.run(['eww', 'open', '-c', CONFIG, 'submap-window'], stdout=subprocess.DEVNULL)
                else:
                    EwwUpdater.update("submap", "")
                    EwwUpdater.update("is_submap", "false")
                    subprocess.run(['eww', 'close', '-c', CONFIG, 'submap-window'], stdout=subprocess.DEVNULL)
            elif event in ["workspace", "openwindow", "closewindow", "movewindow", "activespecial"]:
                if event in ["workspace", "activespecial"]:
                    if event == "workspace":
                        current_workspace = value
                    else:
                        current_workspace = "-98"

                    workspaces_data = await CmdRunner.get_output("hyprctl workspaces -j")
                    workspaces_js = json.loads(workspaces_data)
                    current_workspaces = [str(ws["id"]) for ws in workspaces_js if str(ws["id"]) != current_workspace]
                    workspaces = sorted(base_workspaces | set(current_workspaces + [current_workspace]))
                else:
                    current_workspaces = []

                    clients_data = await CmdRunner.get_output("hyprctl clients -j")
                    clients_js = json.loads(clients_data)
                    client_apps = {}
                    for client_app in clients_js:
                        icon = find_app_icon(client_app["class"])
                        cid = str(client_app["workspace"]["id"])
                        if cid in client_apps.keys():
                            client_apps[cid].append({"class": client_app["class"], "icon": icon})
                        else:
                            client_apps[cid] = [{"class": client_app["class"], "icon": icon}]

                workspaces_json = parse_worspaces(current_workspace, workspaces, current_workspaces, client_apps)
                print(workspaces_json)
                EwwUpdater.update("workspaces-json", json.dumps(workspaces_json))
    except asyncio.CancelledError:
        pass
    finally:
        writer.close()
        await writer.wait_closed()


async def main():
    tasks = [asyncio.create_task(hyprland_events())]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        if os.path.exists(pid_file):
            os.unlink(pid_file)

