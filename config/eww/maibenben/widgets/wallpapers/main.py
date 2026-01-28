#!/bin/python
import json
import subprocess
from pathlib import Path

QUALITY=90
SIZE=256

ROW_LEN = 2
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif', '.svg'}


def make_cmd(a, b):
    return ["magick", str(a), "-thumbnail", f"x{SIZE}^", "-gravity", "center", "-extent", f"{SIZE}x{SIZE}", "-quality", str(QUALITY), str(b)]


def get_files(root):
    items = []
    for obj in root.iterdir():
        if obj.is_file() and obj.suffix.lower() in IMAGE_EXTS:
            items.append(obj)
        elif obj.is_dir():
            items += get_files(obj)
    return items


def main():
    tmp_dir = Path("/tmp/wallpapers").expanduser()
    tmp_file = Path("/tmp/wallpapers/data.json").expanduser()
    tmp_dir.mkdir(parents=True, exist_ok=True)
    wallpaper_folder = Path("~/Pictures/Wallpapers").expanduser()

    if tmp_file.exists():
        with open(tmp_file, "r") as file:
            grid = json.load(file)
            return json.dumps(grid)

    walls = get_files(wallpaper_folder)

    grid = {"rows": []}

    row = []
    for wall in walls:
        if len(row) == ROW_LEN:
            grid["rows"].append(row)
            row = []
        target = tmp_dir / wall.name
        data = {
            "from": str(wall),
            "tumb": str(target),
            "name": wall.name.split(".")[0],
        }
        result = subprocess.run(make_cmd(wall, target), stdout=subprocess.DEVNULL)
        if result.returncode != 0:
            print(f"[ERROR]: Can not make thumbnail for {str(wall)}")
        else:
            row.append(data)
    if len(row) > 0:
        grid["rows"].append(row)

    with open(tmp_file, "w") as file:
        json.dump(grid, file)

    return json.dumps(grid)



if __name__ == "__main__":
    print(main())

