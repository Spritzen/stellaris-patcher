"""A playset as the game sees it: the game, then each mod in load order.

    layers = Layers.for_playset(playset, game)
    layers.winner("common/defines/00_defines.txt")    # the layer whose file is used
    layers.read("game", "common/defines/00_defines.txt")
    layers.defined("common/scripted_triggers")         # every top-level key there

A file at the same path, ignoring case, replaces the earlier one, as it does in
the game. Only mods in folders are read: zipped mods raise LayerError.
"""

import os
from collections.abc import Iterable
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path

from stellaris_patcher.coldsteel.records import Playset
from stellaris_patcher.paradox.descriptor import decode_descriptor
from stellaris_patcher.paradox.game import Game
from stellaris_patcher.paradox.localisation import keys, language
from stellaris_patcher.paradox.script import Node, parse, scan

GAME = "game"


class LayerError(Exception):
    """A mod in the playset can't be read from its folder."""


@dataclass(frozen=True)
class Layer:
    key: str  # "game", or a Cold Steel mod key: "workshop:<id>" or "local:<.mod stem>"
    root: Path


@dataclass(frozen=True)
class Layers:
    layers: tuple[Layer, ...]  # the game first, then the mods in load order
    _listings: dict[tuple[str, str], dict[str, str]] = field(default_factory=dict, repr=False)

    @classmethod
    def for_playset(cls, playset: Playset, game: Game, skip: Iterable[str] = ()) -> Layers:
        """The game and the playset's enabled mods, leaving out the keys in `skip`."""
        left_out = set(skip)
        mods = [e.key for e in playset.entries if e.enabled and e.key not in left_out]
        return cls((Layer(GAME, game.install_dir), *(_mod_layer(k, game) for k in mods)))

    def layer(self, key: str) -> Layer:
        for layer in self.layers:
            if layer.key == key:
                return layer
        raise LayerError(f"{key} isn't in the playset.")

    def name(self, key: str) -> str:
        """A mod's name, as its descriptor.mod gives it: what `dependencies` lists."""
        try:
            name = decode_descriptor((self.layer(key).root / "descriptor.mod").read_bytes()).name
        except OSError as error:
            raise LayerError(f"{key} has no descriptor.mod.") from error
        if not name:
            raise LayerError(f"{key}'s descriptor.mod has no name.")
        return name

    def read(self, key: str, path: str) -> bytes:
        layer = self.layer(key)
        written = self._listing(layer, path.rpartition("/")[0]).get(path.casefold(), path)
        return (layer.root / written).read_bytes()

    def has(self, key: str, path: str) -> bool:
        folder, _, _ = path.rpartition("/")
        return path.casefold() in self._listing(self.layer(key), folder)

    def paths(self, key: str, folder: str, suffix: str = ".txt") -> list[str]:
        """Every file under `folder` in one layer, whether or not a later layer replaces it."""
        listing = self._listing(self.layer(key), folder)
        return sorted(path for folded, path in listing.items() if folded.endswith(suffix))

    def winner(self, path: str) -> str:
        """The layer whose copy of `path` the game uses. LayerError if none has it."""
        for layer in reversed(self.layers):
            if self.has(layer.key, path):
                return layer.key
        raise LayerError(f"No mod in the playset, nor the game, has {path}.")

    def files(self, folder: str, suffix: str = "") -> dict[str, tuple[str, str]]:
        """Every file the game reads under `folder`: its path, folded to lower
        case, to (layer, path as written). A later layer's file replaces an
        earlier one at the same path."""
        found: dict[str, tuple[str, str]] = {}
        for layer in self.layers:
            for folded, path in self._listing(layer, folder).items():
                if folded.endswith(suffix):
                    found[folded] = (layer.key, path)
        return found

    def ordered(self, folder: str, suffix: str = ".txt") -> list[tuple[str, str]]:
        """`files()`, sorted by file name as the game sorts them, then by path."""
        files = self.files(folder, suffix)
        return [files[k] for k in sorted(files, key=lambda p: (p.rpartition("/")[2], p))]

    def defined(self, folder: str) -> dict[str, tuple[str, str]]:
        """Each top-level key in `folder`'s script files, to the (layer, path)
        of the file that defines it first by file name."""
        found: dict[str, tuple[str, str]] = {}
        for layer, path in self.ordered(folder):
            for entry in scan(self.read(layer, path)):
                found.setdefault(entry.key.decode("utf-8", "replace"), (layer, path))
        return found

    def localisation(self, lang: str = "l_english") -> set[str]:
        """Every localisation key in `lang`, from every file the game reads."""
        found: set[str] = set()
        for layer, path in self.files("localisation", ".yml").values():
            data = self.read(layer, path)
            if language(data) == lang:
                found.update(e.key.decode("utf-8", "replace") for e in keys(data))
        return found

    def define(self, category: str, name: str) -> tuple[str, Node] | None:
        """A define's value as the game uses it, with the layer it comes from.
        The file whose name sorts last wins."""
        result: tuple[str, Node] | None = None
        for layer, path in self.ordered("common/defines"):
            node = find_define(parse_file(self.read(layer, path)), category, name)
            if node is not None:
                result = (layer, node)
        return result

    def _listing(self, layer: Layer, folder: str) -> dict[str, str]:
        """Every file under `folder` in one layer: lower-case path to path as written."""
        cached = self._listings.get((layer.key, folder))
        if cached is None:
            cached = _walk(layer.root, folder)
            self._listings[(layer.key, folder)] = cached
        return cached


def parse_file(data: bytes) -> tuple[Node, ...]:
    return parse(data.decode("utf-8-sig", errors="replace"))


def find_define(nodes: tuple[Node, ...], category: str, name: str) -> Node | None:
    """The last `name = ...` inside `category = { ... }`, or None."""
    found: Node | None = None
    for group in nodes:
        if group.key == category and isinstance(group.value, tuple):
            for node in group.value:
                if node.key == name:
                    found = node
    return found


def numbers(node: Node) -> list[float]:
    """A define's `{ 1 2 3 }` as numbers."""
    if not isinstance(node.value, tuple):
        raise ValueError(f"{node.key} isn't a list.")
    return [float(n.value) for n in node.value if n.key is None and isinstance(n.value, str)]


def _mod_layer(key: str, game: Game) -> Layer:
    kind, _, name = key.partition(":")
    if kind == "workshop":
        root = game.workshop_dir / name
    elif kind == "local":
        outer = game.mod_dir / f"{name}.mod"
        try:
            descriptor = decode_descriptor(outer.read_bytes())
        except OSError as error:
            raise LayerError(f"Can't read {outer}: {error}") from error
        if descriptor.archive or not descriptor.path:
            raise LayerError(f"{outer} doesn't point at a mod folder.")
        root = Path(descriptor.path)
        if not root.is_absolute():
            root = game.data_dir / root
    else:
        raise LayerError(f"Unknown mod key {key}.")
    if not root.is_dir():
        raise LayerError(f"{key} has no folder at {root}. Is it zipped, or not downloaded?")
    return Layer(key, root)


@cache
def _folder_case(root: Path, folder: str) -> Path | None:
    """`root/folder`, matching each part of `folder` ignoring case."""
    path = root
    for part in folder.split("/") if folder else ():
        try:
            names = {p.name.casefold(): p.name for p in path.iterdir() if p.is_dir()}
        except OSError:
            return None
        if part.casefold() not in names:
            return None
        path = path / names[part.casefold()]
    return path


def _walk(root: Path, folder: str) -> dict[str, str]:
    start = _folder_case(root, folder)
    if start is None:
        return {}
    found: dict[str, str] = {}
    prefix = folder + "/" if folder else ""
    for dirpath, _, filenames in os.walk(start):
        inner = Path(dirpath).relative_to(start).as_posix()
        inner = "" if inner == "." else inner + "/"
        for name in filenames:
            path = prefix + inner + name
            found[path.casefold()] = path
    return found
