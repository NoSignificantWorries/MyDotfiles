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
    temps = psutil.sensors_temperatures()
    temp = temps.get('coretemp', [None])[0].current if temps.get('coretemp') else None
    disk = psutil.disk_usage('/')
    disk = disk.used / disk.total * 100
    res = {
        "cpu": {
            "val": str(cpu),
            "color": match_color(cpu)
        },
        "ram": {
            "val": str(ram),
            "color": match_color(ram)
        },
        "temp": {
            "val": str(temp) if temp else "N/A",
            "color": match_color(temp) if temp else "#ff0000"
        },
        "disk": {
            "val": str(disk),
            "color": match_color(disk)
        }
    }
    print(json.dumps(res))


if __name__ == "__main__":
    main()

