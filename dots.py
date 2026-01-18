import shutil
from pathlib import Path
from typing import Any, Callable, List, Optional, Tuple, Union


def p(path: Union[Path, str]) -> List[str]:
    if isinstance(path, Path):
        path = str(path)
    return path.split("/")


def pth(path: Union[Path, str, List[str]]) -> Path:
    if isinstance(path, str):
        path = Path(path)
    elif isinstance(path, List):
        path = Path("/".join(path))
    return path.expanduser()


def run_cmd(cmd: Union[str, List[str]]):
    pass


class Node:
    dry_run = True
    tmp_only = True
    with_tmp_dir = True
    params = {}

    actions = {
        "cmd": run_cmd
    }
    compilation = []

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.parent = None
        self.nodes = []
        for arg in args:
            if isinstance(arg, Node):
                arg.parent = self
                self.nodes.append(arg)
        self.kwargs = kwargs

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

    def compile(self) -> None:
        raise NotImplementedError("Error")

    def compile_subnodes(self, hook: Optional[Callable] = None) -> None:
        for node in self.nodes:
            if hook and isinstance(hook, Callable):
                hook(node)
            node.compile()


class Stage(Node):
    def __init__(self, label: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.label = label

    def compile(self) -> None:
        self.compile_subnodes()


class Provider(Node):
    def __init__(self, installer: Callable, updater: str, get_installed: str, batch_size: int = 6, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.installer = installer
        self.get_installed = get_installed
        self.updater = updater
        self.batch_size = batch_size
        self.list_of_pkgs = []

    def pkgs(self, pkgs_list: List[str]):
        new = Provider(self.installer, self.updater, self.get_installed, self.batch_size)
        new.list_of_pkgs = pkgs_list
        return new

    def compile(self) -> None:
        for i in range(0, len(self.list_of_pkgs), self.batch_size):
            cmd = self.installer(" ".join(self.list_of_pkgs[i:i + self.batch_size]))
            Node.compilation.append(("cmd", cmd))
        self.compile_subnodes()


class Cmd(Node):
    def __init__(self, commands: List[str], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.commands = commands

    def compile(self) -> None:
        for cmd in self.commands:
            Node.compilation.append(("cmd", cmd))
        self.compile_subnodes()


class Fork(Node):
    def __init__(self, rule: bool, optionA: Union[Tuple[Node, ...], Node], optionB: Union[Tuple[Node, ...], Node]) -> None:
        self.nodes = optionA if rule else optionB
        if not isinstance(self.nodes, Tuple):
            self.nodes = (self.nodes,)

    def compile(self) -> None:
        def hook(n):
            n.parent = self.parent
        self.compile_subnodes(hook)


class Tree(Node):
    def __init__(self, root: Union[Path, str], target_root: Union[Path, str] = "", *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if isinstance(target_root, Node):
            args = (target_root, *args)
            target_root = ""
        self.root = p(root)
        if target_root != "":
            self.target_root = p(target_root)
        else:
            self.target_root = self.root

    def compile(self) -> None:
        if isinstance(self.parent, Tree):
            self.root = self.parent.root + self.root
            self.target_root = self.parent.target_root + self.target_root
        self.compile_subnodes()


def check_file_and_delete(path: Path) -> None:
    if path.exists():
        if path.is_symlink():
            path.unlink()
        elif path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)
        else:
            path.unlink()


class Link(Node):
    def __init__(self, source: Union[Path, str], target: Union[Path, str] = "", *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.source = p(source)
        self.target = p(target) if target != "" else self.source

        self.action_label = "link"

        def action(source, target):
            check_file_and_delete(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(source)

        Node.actions.update({self.action_label: action})

    def compile(self) -> None:
        if self.parent and isinstance(self.parent, Tree):
            self.source = self.parent.root + self.source
            pwd = self.params.get("source-pwd")
            if pwd and self.source[0] != "~":
                self.source = pwd + self.source

            if self.target[0] != "~":
                self.target = self.parent.target_root + self.target
            pwd = self.params.get("target-pwd")
            if pwd and self.target[0] != "~":
                self.target = pwd + self.target

        source = pth(self.source)
        target = pth(self.target)

        if source.exists() and not source.is_symlink():
            tmp_path = self.params.get("tmp-links")
            if self.with_tmp_dir and tmp_path:
                tmp_target = pth(tmp_path + self.target[1:])

                if tmp_target != source:

                    if not self.tmp_only:
                        if tmp_target != target:
                            Node.compilation.append((self.action_label, [source, tmp_target]))
                            Node.compilation.append((self.action_label, [tmp_target, target]))
                        else:
                            pass
                    else:
                        print(source, tmp_target)
                        Node.compilation.append((self.action_label, [source, tmp_target]))
                else:
                    pass
            else:
                if source != target:
                    print(source, target)
                    Node.compilation.append((self.action_label, [source, target]))
                else:
                    pass

        self.compile_subnodes()


class Copy(Link):
    def __init__(self, source: Union[Path, str], target: Union[Path, str] = "", *args, **kwargs) -> None:
        super().__init__(source, target, *args, **kwargs)
        self.action_label = "copy"

        def action(source, target):
            check_file_and_delete(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            source.copy(target)

        Node.actions.update({self.action_label: action})

