import os
import asyncio
import subprocess


class EwwUpdater:
    @staticmethod
    def update(var: str, value: str):
        subprocess.run(['eww', 'update', f'{var}={value}'], stdout=subprocess.DEVNULL)


class CmdRunner:
    @staticmethod
    async def get_output(cmd: str) -> str:
        try:
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                text=False
            )
            stdout, _ = await proc.communicate()
            return stdout.strip()
        except:
            return "N/A"


async def base_sys_loop():
    while True:
        vol, br, bat = await asyncio.gather(
            CmdRunner.get_output("wpctl get-volume @DEFAULT_AUDIO_SINK@"),
            CmdRunner.get_output("brightnessctl -m"),
            CmdRunner.get_output("acpi -b"),
        )
        print(f"Громкость: {vol}")
        print(f"Br: {br}")
        print(f"Bat: {bat}")
        await asyncio.sleep(2)


async def hyprland_events():
    his = os.environ.get('HYPRLAND_INSTANCE_SIGNATURE')
    if not his:
        print("Hyprland не запущен")
        return

    socket_path = f"{os.environ['XDG_RUNTIME_DIR']}/hypr/{his}/.socket2.sock"

    reader, writer = await asyncio.open_unix_connection(socket_path)

    print("Подписка на события Hyprland...")

    try:
        while True:
            data = await reader.readline()
            event = data.decode().strip()
            print(event)
    except asyncio.CancelledError:
        pass
    finally:
        writer.close()
        await writer.wait_closed()


async def main():
        tasks = [asyncio.create_task(hyprland_events()),
                 asyncio.create_task(base_sys_loop())]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
        asyncio.run(main())

