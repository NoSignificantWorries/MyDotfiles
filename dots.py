import shutil
from pathlib import Path
from typing import Any, Callable, List, Optional, Tuple, Union, Dict, Type


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
        self.params = []
        for arg in args:
            if isinstance(arg, Node):
                arg.parent = self
                self.nodes.append(arg)
            else:
                self.params.append(arg)
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


def match_params(obj: Node, params: List[Any], schedule: Dict[int, List[Tuple[Any, ...]]]) -> None:
    if obj is None:
        raise TypeError("Object mustn't be a None")
    if not isinstance(obj, Node):
        raise TypeError(f"Wrong type of object ({type(obj).__name__}. It must be Node)")
    n = len(params)
    for m, param_list in schedule.items():
        if m <= 0:
            pass
        if m != len(param_list):
            pass
        if n == m:
            for param, param_matching in zip(params, param_list):
                if isinstance(param_matching, Tuple):
                    name, val_type = param_matching
                    if isinstance(val_type, Type):
                        if isinstance(param, val_type):
                            setattr(obj, name, param)
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
            break


class Stage(Node):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.label = None
        self.schedule = { 0: [], 1: [("label", str)] }
        match_params(self, self.params, self.schedule)

    def compile(self) -> None:
        def hook(n):
            n.parent = self.parent
        self.compile_subnodes(hook)


class Provider(Node):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.installer = None
        self.get_installed = None
        self.updater = None
        self.batch_size = 6
        self.schedule = {
            3: [("installer", Callable), ("updater", str), ("get_installed", str)],
            4: [("installer", Callable), ("updater", str), ("get_installed", str), ("batch_size", int)]
        }
        match_params(self, self.params, self.schedule)

        if not (self.installer or self.get_installed or self.updater):
            raise TypeError("Error")

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
        self.commands = []
        self.schedule = { 1: [("commands", list)] }
        match_params(self, self.params, self.schedule)

    def compile(self) -> None:
        for cmd in self.commands:
            Node.compilation.append(("cmd", cmd))
        self.compile_subnodes()


class Fork(Node):
    def __init__(self, rule: bool, optionA: Union[Tuple[Node, ...], Node], optionB: Union[Tuple[Node, ...], Node]) -> None:
        args = optionA if rule else optionB
        if not isinstance(args, Tuple):
            args = (args,)
        super().__init__(*args, **{})

    def compile(self) -> None:
        def hook(n):
            n.parent = self.parent
        self.compile_subnodes(hook)


class Tree(Node):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.root = None
        self.target_root = None

        self.schedule = {
            1: [("root", str)],
            2: [("root", str), ("target_root", str)]
        }

        match_params(self, self.params, self.schedule)

        if self.target_root is None:
            self.target_root = self.root
        if not (self.root or self.target_root):
            raise TypeError("Error")
        self.root = p(self.root)
        self.target_root = p(self.target_root)

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
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.source = None
        self.target = None

        self.schedule = {
            1: [("source", str)],
            2: [("source", str), ("target", str)]
        }

        match_params(self, self.params, self.schedule)

        if self.target is None:
            self.target = self.source
        if not (self.source or self.target):
            raise TypeError("Error")

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
                            print("Is a loop")
                    else:
                        print(source, tmp_target)
                        Node.compilation.append((self.action_label, [source, tmp_target]))
                else:
                    print("Is a loop")
            else:
                if source != target:
                    print(source, target)
                    Node.compilation.append((self.action_label, [source, target]))
                else:
                    print("Is a loop")
        else:
            print(source, source.exists(), source.is_symlink())

        self.compile_subnodes()


class Copy(Link):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.action_label = "copy"

        def action(source, target):
            check_file_and_delete(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            source.copy(target)

        Node.actions.update({self.action_label: action})

