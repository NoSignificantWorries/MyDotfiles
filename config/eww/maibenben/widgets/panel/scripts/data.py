import os
import sys
import json
import signal
import asyncio
import subprocess
from pathlib import Path


pid_file = Path("~/.config/eww/widgets/panel/scripts/data.pid").expanduser()

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


KB_LAYOUTS = {
    "Russian": "RU",
    "English (US)": "EN"
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


def parse_worspaces(ws, workspaces, active_workspaces):
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
        json_workspaces.append({
                "active": active,
                "occupied": occupied,
                "cmd": cmd,
                "text": w
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

        base_workspaces = {"1", "2", "3", "4", "5"}
        workspaces = base_workspaces.copy()
        current_workspace = "1"
        workspaces_json = parse_worspaces(current_workspace, sorted(workspaces), [])
        EwwUpdater.update("workspaces-json", json.dumps(workspaces_json))
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
                case "submap":
                    if len(value) > 0:
                        EwwUpdater.update("submap", value)
                        EwwUpdater.update("is_submap", "true")
                        subprocess.run(['eww', 'open', '-c', CONFIG, 'submap-window'], stdout=subprocess.DEVNULL)
                    else:
                        EwwUpdater.update("submap", "")
                        EwwUpdater.update("is_submap", "false")
                        subprocess.run(['eww', 'close', '-c', CONFIG, 'submap-window'], stdout=subprocess.DEVNULL)
                case "workspace":
                    current_workspace = value

                    workspaces_data = await CmdRunner.get_output("hyprctl workspaces -j")
                    workspaces_js = json.loads(workspaces_data)
                    current_workspaces = [str(ws["id"]) for ws in workspaces_js if str(ws["id"]) != current_workspace]
                    workspaces = sorted(base_workspaces | set(current_workspaces + [current_workspace]))

                    workspaces_json = parse_worspaces(current_workspace, workspaces, current_workspaces)
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

