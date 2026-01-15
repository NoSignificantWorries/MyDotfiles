from pathlib import Path


def parse(text):
    for s in text:
        if s in [" ", "\n", "\t"]:
            continue


def main() -> None:
    with open(Path("~/Hyprdots_main/basic.dconf").expanduser(), "r") as config_file:
        content = config_file.read()

    print(content)


if __name__ == "__main__":
    main()

