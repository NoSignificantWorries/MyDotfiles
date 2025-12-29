import os
import sys
import json
import signal
import asyncio
import subprocess
from pathlib import Path


pid_file = os.path.expanduser("~/.config/eww/widgets/hud/data.pid")

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


CONFIG = Path("~/.config/eww/widgets/hud").expanduser()

VOL_ICONS = ["", "", "", ""]
VOL_COLORS = [
    "#6c7086",
    "#005f56",
    "#007f66",
    "#009f76",
    "#00bf86",
    "#00df96",
    "#00ffa6",
    "#40ffb6",
    "#80ffc6",
    "#b0ffd6",
    "#e0ffe6"
]
BR_ICONS = ["󰃜", "󰃝", "󰃞", "󰃠"]
BR_COLORS = [
    "#1a4a8c",
    "#2060a3",
    "#2676ba",
    "#2c8cd1",
    "#32a2e8",
    "#38b8ff",
    "#5ec6ff",
    "#84d4ff",
    "#aae2ff",
    "#d0f0ff"
]
BAT_ICONS_CHARGING = ["󰢟", "󰢜", "󰂆", "󰂇", "󰂈", "󰢝", "󰂉", "󰢞", "󰂋", "󰂅"]
BAT_ICONS_NORMAL = ["󱃍", "󰁺", "󰁻", "󰁼", "󰁽", "󰁾", "󰁿", "󰂀", "󰂁", "󰁹"]
BAT_COLORS = [
    "#ed8796",
    "#ea909e",
    "#e799a6",
    "#e3a3af",
    "#e0acb8",
    "#d0b7a2",
    "#c0c28c",
    "#b1cd76",
    "#a1d860",
    "#91e34a"
]

KB_LAYOUTS = {
    "Russian": "RU 🇷🇺",
    "English (US)": "EN 🇺🇸"
}

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


async def bat_loop():
    while True:
        bat = await CmdRunner.get_output("acpi -b")

        bat = bat.split(", ")
        status = "Charging" in bat[0]
        percent = int(bat[1][:-1])
        if len(bat) > 2:
            time = bat[-1].split(" ")[0].split(":")
            print(bat)
            H, M = time[0], time[1]
            if status:
                time = f"{H}h {M}m to full"
            else:
                time = f"{H}h {M}m to empty"
        else:
            time = "Full"
        idx = round(percent / 100 * 9)
        bat_color = BAT_COLORS[idx]
        bat_icon = BAT_ICONS_CHARGING[idx] if status else BAT_ICONS_NORMAL[idx]
        EwwUpdater.update("bat-status", f"{bat_icon} {percent}%")
        EwwUpdater.update("bat-color", bat_color)
        EwwUpdater.update("bat-time", time)

        await asyncio.sleep(30)


async def vol_br_loop():
    last_muted = None
    last_vol = None
    last_br = None
    while True:
        vol, br = await asyncio.gather(
            CmdRunner.get_output("wpctl get-volume @DEFAULT_AUDIO_SINK@"),
            CmdRunner.get_output("brightnessctl -m"),
        )
        muted = "[MUTED]" in vol
        vol = vol.split(" ")
        vol = round(float(vol[1]) * 100)
        if last_vol != vol or last_muted is last_muted:
            if muted:
                vol_color = VOL_COLORS[0]
                vol_icon = VOL_ICONS[0]
            else:
                vol_color = VOL_COLORS[round(vol / 100 * 9 + 1)]
                vol_icon = VOL_ICONS[round(vol / 100 * 2 + 1)]
            EwwUpdater.update("vol-mute", "true" if muted else "false")
            EwwUpdater.update("vol-icon", vol_icon)
            EwwUpdater.update("vol-color", vol_color)
            EwwUpdater.update("vol", str(vol))

            last_muted = muted
            last_vol = vol

        br = br.split(",")
        br = int(br[3][:-1])
        if last_br != br:
            br_color = BR_COLORS[round(br / 100 * 9)]
            br_icon = BR_ICONS[round(br / 100 * 3)]
            EwwUpdater.update("br", str(br))
            EwwUpdater.update("br-color", br_color)
            EwwUpdater.update("br-icon", br_icon)

            last_br = br

        await asyncio.sleep(1)


def parse_worspaces(ws, workspaces, active_workspaces):
    workspaces_line = ""
    items = []
    for w in workspaces:
        cmd = f"hyprctl dispatch workspace {w}"
        if w == ws:
            items.append(f"(button :class \"activebtn\" :onclick `{cmd}` (label :class \"activews\" :text \"{w}\"))")
        elif w in active_workspaces:
            items.append(f"(button :class \"fullbtn\" :onclick `{cmd}` (label :class \"fullws\" :text \"{w}\"))")
        else:
            items.append(f"(button :class \"normalbtn\" :onclick `{cmd}` (label :class \"normalws\" :text \"{w}\"))")
    workspaces_line = f"(box :orientation 'h' :space-evenly false :class \"workspaces\" {' '.join(items)})"

    return workspaces_line


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

        base_workspaces = {"1", "2", "3", "4", "5"}
        workspaces = base_workspaces.copy()
        current_workspace = "1"
        workspaces_line = parse_worspaces(current_workspace, workspaces, [])
        EwwUpdater.update("workspaces", workspaces_line)
        while True:
            data = await reader.readline()
            event = data.decode().strip()
            print(event)
            event, value = event.split(">>", 1)
            match event:
                case "activelayout":
                    new_layout = value.split(",")[-1]
                    if new_layout in KB_LAYOUTS.keys():
                        new_layout = KB_LAYOUTS[new_layout]
                    EwwUpdater.update("kb_layout", new_layout)
                case "workspace":
                    current_workspace = value

                    workspaces_data = await CmdRunner.get_output("hyprctl workspaces -j")
                    workspaces_js = json.loads(workspaces_data)
                    current_workspaces = [str(ws["id"]) for ws in workspaces_js if str(ws["id"]) != current_workspace]
                    workspaces = sorted(base_workspaces | set(current_workspaces + [current_workspace]))

                    workspaces_line = parse_worspaces(current_workspace, workspaces, current_workspaces)
                    print(workspaces_line)
                    EwwUpdater.update("workspaces", workspaces_line)
    except asyncio.CancelledError:
        pass
    finally:
        writer.close()
        await writer.wait_closed()


async def main():
    tasks = [asyncio.create_task(hyprland_events()),
             asyncio.create_task(vol_br_loop()),
             asyncio.create_task(bat_loop())]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        if os.path.exists(pid_file):
            os.unlink(pid_file)

