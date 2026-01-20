import shutil
from pathlib import Path
from typing import Callable, List, Optional, Tuple, Union


def pth(path: Union[Path, str]) -> Path:
    if not isinstance(path, (Path, str)):
        raise TypeError("Error")
    if isinstance(path, str):
        path = Path(path)
    return path


def run_cmd(command: str):
    pass


def check_file_and_delete(path: Path) -> None:
    if path.exists():
        if path.is_symlink():
            path.unlink()
        elif path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)
        else:
            path.unlink()
    else:
        raise FileNotFoundError("File not found")

def prepare_path(path: Path) -> Path:
    path = path.expanduser()
    return path


def run_link(src: Path, dst: Path):
    src = prepare_path(src)
    dst = prepare_path(dst)
    check_file_and_delete(dst)
    check_file_and_delete(dst.parent)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.symlink_to(src)


def run_copy(src: Path, dst: Path):
    src = prepare_path(src)
    dst = prepare_path(dst)
    check_file_and_delete(dst)
    check_file_and_delete(dst.parent)
    dst.parent.mkdir(parents=True, exist_ok=True)
    src.copy(dst)


class Node:
    dry_run = True
    tmp_only = True
    with_tmp_dir = True

    actions = {
        "cmd": run_cmd,
        "link": run_link,
        "copy": run_copy
    }
    compilation = []

    def __init__(self, params=Tuple, nodes: Optional[List] = None) -> None:
        self.parent = None
        self.params = params
        self.nodes = []
        if nodes:
            self.nodes = nodes
        for node in self.nodes:
            node.parent = self

    def _compiler(self, hook: Optional[Callable] = None) -> None:
        for node in self.nodes:
            if isinstance(hook, Callable):
                hook(node)
            node.compile()

    def go(self):
        for label, params in Node.compilation:
            func = Node.actions.get(label)
            if Node.dry_run:
                print(label, params)
            else:
                if func:
                    if isinstance(params, (List, Tuple)):
                        func(*params)
                    else:
                        func(params)
                else:
                    pass

    def compile(self):
        raise NotImplementedError("Method compile must be implemented")


class Stage(Node):
    def __init__(self, params=Tuple, nodes: Optional[List] = None) -> None:
        super().__init__(params, nodes)

        match len(self.params):
            case 0:
                self.label = None
            case 1:
                self.label = self.params[0]
            case _:
                raise TypeError("Error")

    def compile(self) -> None:
        print("Stage:", self.label)
        def hook(node: Node):
            node.parent = self.parent
        self._compiler(hook)


class Cmd(Node):
    def __init__(self, commands=List[str], nodes: Optional[List] = None) -> None:
        super().__init__((), nodes)
        self.commands = commands

    def compile(self):
        for cmd in self.commands:
            self.compilation.append(("cmd", cmd))
        self._compiler()


class Provider(Node):
    def __init__(self, params=Tuple, nodes: Optional[List] = None) -> None:
        super().__init__(params, nodes)
        self.batch_size = 6
        match len(self.params):
            case 2:
                self.install, self.update = self.params
            case 3:
                self.install, self.update, self.batch_size = self.params
            case _:
                raise TypeError("Error")
        self.pkgs_list = []

    def pkgs(self, pkgs_list: List[str]) -> Provider:
        new = Provider(self.params)
        new.pkgs_list = pkgs_list
        return new

    def compile(self):
        for i_start in range(0, len(self.pkgs_list), self.batch_size):
            cmd = self.install(" ".join(self.pkgs_list[i_start:i_start + self.batch_size]))
            self.compilation.append(("cmd", cmd))
        self._compiler()


class Fork(Node):
    def __init__(self, rule: bool, nodesA: List[Node], nodesB: List[Node]) -> None:
        if rule:
            nodes = nodesA
        else:
            nodes = nodesB

        super().__init__((), nodes)

    def compile(self):
        def hook(node: Node):
            node.parent = self.parent
        self._compiler(hook)


class Tree(Node):
    def __init__(self, params=Tuple, nodes: Optional[List] = None) -> None:
        super().__init__(params, nodes)
        match len(self.params):
            case 1:
                self.src = self.params[0]
                self.dst = self.src
            case 2:
                self.src, self.dst = self.params
            case _:
                raise TypeError("Error")

        self.src = pth(self.src)
        self.dst = pth(self.dst)

    def compile(self) -> None:
        if isinstance(self.parent, Tree):
            if not str(self.src).startswith("~"):
                self.src = self.parent.src / self.src
            if not str(self.dst).startswith("~"):
                self.dst = self.parent.dst / self.dst
        self._compiler()


class Link(Node):
    def __init__(self, src: Union[Path, str], dst: Optional[Union[Path, str]] = None) -> None:
        def action():
            self.compilation.append(("link", (self.src, self.dst)))

        self.action = action

        self.src = pth(src)
        if dst:
            self.dst = pth(dst)
        else:
            self.dst = self.src

    def compile(self) -> None:
        if isinstance(self.parent, Tree):
            if not str(self.src).startswith("~"):
                self.src = self.parent.src / self.src
            if not str(self.dst).startswith("~"):
                self.dst = self.parent.dst / self.dst
        self.action()


class Copy(Link):
    def __init__(self, src: Union[Path, str], dst: Optional[Union[Path, str]] = None) -> None:
        super().__init__(src, dst)
        def action():
            self.compilation.append(("copy", (self.src, self.dst)))

        self.action = action


