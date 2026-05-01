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

