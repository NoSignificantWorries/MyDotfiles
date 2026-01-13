#!/usr/bin/python
import json
import psutil

COLORS = [
    "#89dceb",
    "#94e2d5",
    "#a6e3a1",
    "#f9e2af",
    "#fab387",
    "#eba0ac",
    "#f38ba8"
]


def match_color(value):
    return COLORS[int(value / 100 * 6)]


def main():
    cpu = psutil.cpu_percent(interval=0.5)

    ram = psutil.virtual_memory().percent
    total_gb = psutil.virtual_memory().total / 1024 ** 3
    used_gb = psutil.virtual_memory().used / 1024 ** 3

    temps = psutil.sensors_temperatures()
    temp = temps.get('coretemp', [None])[0].current if temps.get('coretemp') else None

    disk = psutil.disk_usage('/')
    disk_total_db = disk.total / 1024 ** 3
    disk_used_db = disk.used / 1024 ** 3
    disk = disk.used / disk.total * 100

    res = {
        "cpu": {
            "val": str(cpu),
            "color": match_color(cpu)
        },
        "ram": {
            "val": str(ram),
            "color": match_color(ram),
            "totalGB": total_gb,
            "usedGB": used_gb
        },
        "temp": {
            "val": str(temp) if temp else "N/A",
            "color": match_color(temp) if temp else "#ff0000"
        },
        "disk": {
            "val": str(disk),
            "color": match_color(disk),
            "totalGB": disk_total_db,
            "usedGB": disk_used_db
        }
    }
    print(json.dumps(res))


if __name__ == "__main__":
    main()

