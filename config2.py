import re
from pathlib import Path
from typing import List, Tuple

PWD = Path("Hyprdots_main")


LINKS_WHITE_LIST = [
    r".*\.conf$",
    r".*\.toml$",
    r".*\.yaml$",
    r".*\.json$",
    r".*\.list$",
    r".*\.rasi$",
    r".*\.sh$",
    r".*\.py$",
    r".*\.nu$",
    r".*\.theme$",
    r".*\.kvconfig$",
    r".*\.yuck$",
    r".*\.scss$",
    r".*\.css$",
    r".*\.jpg$",
    r".*\.svg$",
    r".*\.png$"
]

MIRRORS = [
    (r"home", ""),
    (r"config", ".config"),
    (rf"{str(Path.home() / PWD)}", str(Path.home()))
]

print(MIRRORS)

def match_re_patterns(name: str, patterns: List[str]) -> bool:
    for pattern in patterns:
        if re.match(pattern, name):
            return True
    return False


def sub_re_patterns(text: str, patterns: List[Tuple[str, str]]) -> str:
    new = text
    for pattern in patterns:
        new = re.sub(*pattern, new)
    return new


def pth(path: Path | str) -> Path:
    if isinstance(path, str):
        path = Path(path)
    return path.expanduser()


def parse_dir(path: Path | str) -> List[Path]:
    items = []
    path = pth(path)
    for elem in path.iterdir():
        if elem.is_dir():
            items += parse_dir(elem)
        else:
            if match_re_patterns(elem.name, LINKS_WHITE_LIST):
                target = sub_re_patterns(str(elem), MIRRORS)
                target = pth(target)
                items.append((elem, target))
    return items


def main() -> None:
    config = parse_dir("~/Hyprdots_main/config")
    print(config)
    scripts = parse_dir("~/Hyprdots_main/scripts")
    print(scripts)


if __name__ == "__main__":
    main()

