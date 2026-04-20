#!/usr/bin/python

import os
import json
import asyncio
import sys


async def get_keyboard_layouts():
    proc = await asyncio.create_subprocess_exec(
        "niri", "msg", "-j", "keyboard-layouts",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, _ = await proc.communicate()
    if proc.returncode == 0:
        return json.loads(stdout.decode())
    return {"names": [], "current_idx": 0}


async def get_workspaces():
    proc = await asyncio.create_subprocess_exec(
        "niri", "msg", "-j", "workspaces",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, _ = await proc.communicate()
    if proc.returncode == 0:
        data = json.loads(stdout.decode())
        res = [
            {
                "name": str(w["idx"]) if w["name"] is None else w["name"],
                "id": w["id"],
                "idx": w["idx"],
                "is_active": w["is_active"],
                "is_urgent": w["is_urgent"],
                "is_empty": w["active_window_id"] is None
            }
            for w in data
        ]
        return list(sorted(res, key=(lambda x: x["idx"])))
    return []


async def read_niri_stream_async():
    sock_path = os.environ.get("NIRI_SOCKET")
    if not sock_path:
        raise EnvironmentError("NIRI_SOCKET is not set")

    # Асинхронная инициализация
    kbs_task = get_keyboard_layouts()
    wsps_task = get_workspaces()
    
    kbs, wsps = await asyncio.gather(kbs_task, wsps_task)
    
    KB_NAMES_MAP = {"English (US)": "EN", "Russian": "RU"}
    kb_variants = {i: KB_NAMES_MAP.get(name, name) for i, name in enumerate(kbs["names"])}
    
    state = {
        "kb": kb_variants.get(kbs["current_idx"], "??"),
        "wsp": wsps,
        "is_overview": False
    }
    current_kb_idx = kbs["current_idx"]
    
    print(json.dumps(state))
    sys.stdout.flush()

    # Асинхронное чтение сокета
    reader, writer = await asyncio.open_unix_connection(sock_path)
    writer.write(b'"EventStream"\n')
    await writer.drain()
    
    buffer = ""
    
    try:
        while True:
            data = await reader.read(8192)
            if not data:
                break
            
            buffer += data.decode()
            
            while True:
                try:
                    decoder = json.JSONDecoder()
                    obj, idx = decoder.raw_decode(buffer)
                    buffer = buffer[idx:].lstrip()
                    
                    changed = False
                    
                    if "WorkspaceActivated" in obj:
                        state["wsp"] = await get_workspaces()
                        changed = True
                    elif "WorkspacesChanged" in obj:
                        state["wsp"] = [
                            {
                                "name": str(w["idx"]) if w.get("name") is None else w["name"],
                                "id": w["id"],
                                "idx": w["idx"],
                                "is_active": w["is_active"],
                                "is_urgent": w["is_urgent"],
                                "is_empty": w.get("active_window_id") is None
                            }
                            for w in obj["WorkspacesChanged"]["workspaces"]
                        ]
                        changed = True
                        
                    elif "KeyboardLayoutSwitched" in obj:
                        new_idx = obj["KeyboardLayoutSwitched"].get("idx")
                        if new_idx is not None and new_idx != current_kb_idx:
                            current_kb_idx = new_idx
                            state["kb"] = kb_variants.get(new_idx, "??")
                            changed = True
                            
                    elif "OverviewOpenedOrClosed" in obj:
                        is_open = obj["OverviewOpenedOrClosed"].get("is_open")
                        if is_open is not None:
                            state["is_overview"] = is_open
                            changed = True
                    
                    if changed:
                        print(json.dumps(state))
                        sys.stdout.flush()
                        
                except json.JSONDecodeError:
                    break
                    
    except Exception:
        pass
    finally:
        writer.close()
        await writer.wait_closed()


if __name__ == "__main__":
    asyncio.run(read_niri_stream_async())


'''
import os
import json
import socket
import subprocess


def get_keyboard_layouts():
    try:
        result = subprocess.run(
            ["niri", "msg", "-j", "keyboard-layouts"],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except Exception as e:
        return {"names": [], "current_idx": 0}


def get_workspaces():
    try:
        result = subprocess.run(
            ["niri", "msg", "-j", "workspaces"],
            capture_output=True,
            text=True,
            check=True
        )
        data =  json.loads(result.stdout)
        workspaces = []
        for elem in data:
            workspaces.append({
                    "name": str(elem["idx"]) if elem["name"] is None else elem["name"],
                    "id": elem["id"],
                    "idx": elem["idx"],
                    "is_active": elem["is_active"],
                    "is_urgent": elem["is_urgent"],
                    "is_empty": elem["active_window_id"] is None
                    })
        return workspaces
    except Exception as e:
        return []


def match_kb_name(name):
    NAMES = {
            "English (US)": "EN",
            "Russian": "RU"
            }
    matched_name = NAMES.get(name)
    if matched_name:
        return matched_name
    return name


def read_niri_stream():
    sock_path = os.environ.get("NIRI_SOCKET")
    if not sock_path:
        raise EnvironmentError("NIRI_SOCKET is not set")

    kbs = get_keyboard_layouts()
    kb_variants = {}
    for i, name in enumerate(kbs["names"]):
        kb_variants[i] = match_kb_name(name)
    wsps = get_workspaces()

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(sock_path)
        s.sendall(b'"EventStream"\n')

        buffer = ""

        result = {"kb": kb_variants[kbs["current_idx"]], "wsp": wsps, "is_overview": False}

        while True:
            try:
                data = s.recv(4096)
                if not data:
                    break

                buffer += data.decode()

                while True:
                    try:
                        decoder = json.JSONDecoder()
                        obj, idx = decoder.raw_decode(buffer)

                        if "KeyboardLayoutSwitched" in obj:
                            kb = obj["KeyboardLayoutSwitched"].get("idx")
                            if kb is not None:
                                result["kb"] = kb_variants[kb]
                            print(kb)
                            print(json.dumps(result))
                        elif "WorkspaceActivated" in obj:
                            # obj["WorkspaceActivated"]
                            wsp = get_workspaces()
                            result["wsp"] = wsp
                            print(wsp)
                            print(json.dumps(result))
                        elif "OverviewOpenedOrClosed" in obj:
                            is_open = obj["OverviewOpenedOrClosed"].get("is_open")
                            if is_open is not None:
                                result["is_overview"] = is_open
                            print(is_open)
                            print(json.dumps(result))

                        buffer = buffer[idx:].lstrip()

                    except json.JSONDecodeError:
                        break

            except Exception as e:
                # print(f"Ошибка: {e}", file=sys.stderr)
                break

if __name__ == "__main__":
    read_niri_stream()
'''

