"""Copies of the game's and the playset mods' text files, kept so the next
update can be compared with what came before (decision 26).

    base = load_baseline()                     # None before the first accept
    old = load_manifest(GAME, base.layers[GAME])
    texts = read_old(GAME, base.layers[GAME], {"common/defines/00_defines.txt"})
    base = accept(layers, game, playset_name, known)

Kept in `~/.local/share/stellaris-patcher/snapshots/`. Each layer has a
folder (`game`, `workshop_<id>`, `local_<name>`) holding `<stamp>.json`, a
manifest of every file, and `<stamp>.tar.zst`, the text files themselves.
The stamp is a hash of the manifest, so an unchanged layer is stored once.
`baseline.json` names each layer's stamp at the last accepted check.

A zipped mod's files are read from inside the zip, at the paths the game
sees.
"""

import io
import os
import shutil
import tarfile
import zipfile
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import msgspec
import xxhash

from stellaris_patcher.paradox.descriptor import decode_descriptor
from stellaris_patcher.paradox.game import Game
from stellaris_patcher.patchmod.layers import GAME, Layer, Layers
from stellaris_patcher.store import paths
from stellaris_patcher.store.files import load_json, save_json

TEXT_SUFFIXES = (".txt", ".yml", ".gui", ".gfx", ".asset", ".csv", ".mod")
LANGUAGE = "l_english"  # the only text kept (decision 19); others are tracked by time
KEEP_BASELINES = 3  # older baselines, and archives only they use, are removed


class File(msgspec.Struct, frozen=True, array_like=True):
    path: str  # as written
    size: int
    digest: str  # xxh64 of a text file's bytes; "t<mtime_ns>" or "c<crc>" for others
    mtime: float  # seconds


class Manifest(msgspec.Struct, frozen=True):
    key: str  # "game", or a Cold Steel mod key
    name: str
    version: str  # the game's version, or the mod descriptor's
    supported_version: str = ""
    files: dict[str, File] = {}  # path folded to lower case -> its entry

    @property
    def newest(self) -> float:
        return max((f.mtime for f in self.files.values()), default=0.0)


class Baseline(msgspec.Struct, frozen=True):
    taken: str  # ISO time
    playset: str
    game_version: str
    layers: dict[str, str]  # layer key -> stamp, in load order
    known: tuple[str, ...] = ()  # findings already reviewed, by id


def is_text(folded: str) -> bool:
    """A file whose text is kept: script, and English localisation."""
    if folded.endswith(".yml"):
        return LANGUAGE in folded.rpartition("/")[2]
    return folded.endswith(TEXT_SUFFIXES)


def snapshots_dir() -> Path:
    return paths.data_dir() / "snapshots"


def load_baseline() -> Baseline | None:
    return load_json(snapshots_dir() / "baseline.json", Baseline)


def load_manifest(key: str, stamp: str) -> Manifest | None:
    return load_json(_folder(key) / f"{stamp}.json", Manifest)


def read_old(key: str, stamp: str, wanted: Iterable[str]) -> dict[str, bytes]:
    """Old copies of some files, by folded path. A path not in the archive is left out."""
    want = {p.casefold() for p in wanted}
    found: dict[str, bytes] = {}
    archive = _folder(key) / f"{stamp}.tar.zst"
    if not want or not archive.is_file():
        return found
    with tarfile.open(archive, "r:zst") as tar:
        for member in tar:
            folded = member.name.casefold()
            if folded in want and (f := tar.extractfile(member)) is not None:
                found[folded] = f.read()
    return found


def read_now(layer: Layer, wanted: Iterable[str]) -> dict[str, bytes]:
    """Files as they are now, by folded path, from a mod folder or the zips in it."""
    want = {p.casefold() for p in wanted}
    return {e.folded: e.read() for e in _entries(layer.root) if e.folded in want}


def manifest(layer: Layer, game: Game) -> Manifest:
    name, version, supported = _describe(layer, game)
    files = {e.folded: File(e.path, e.size, e.digest(), e.mtime) for e in _entries(layer.root)}
    return Manifest(layer.key, name, version, supported, files)


def stamp(found: Manifest) -> str:
    listing = sorted((k, f.size, f.digest) for k, f in found.files.items())
    return xxhash.xxh64_hexdigest(msgspec.msgpack.encode(listing))


def accept(layers: Layers, game: Game, playset: str, known: Iterable[str]) -> Baseline:
    """Saves every layer as it is now, and makes that the baseline. The old
    baseline is kept beside it, and the oldest pruned."""
    stamps: dict[str, str] = {}
    for layer in layers.layers:
        found = manifest(layer, game)
        stamps[layer.key] = stamp(found)
        _save(layer, found, stamps[layer.key])
    taken = datetime.now().astimezone().isoformat(timespec="seconds")
    base = Baseline(taken, playset, game.version, stamps, tuple(sorted(set(known))))
    old = snapshots_dir() / "baseline.json"
    if old.is_file():
        (snapshots_dir() / "baselines").mkdir(parents=True, exist_ok=True)
        previous = load_baseline()
        name = (previous.taken if previous else "unknown").replace(":", "-")
        shutil.copy2(old, snapshots_dir() / "baselines" / f"{name}.json")
    save_json(old, base)
    _prune()
    return base


def _folder(key: str) -> Path:
    return snapshots_dir() / key.replace(":", "_")


def _save(layer: Layer, found: Manifest, name: str) -> None:
    folder = _folder(layer.key)
    if (folder / f"{name}.json").is_file():
        return
    folder.mkdir(parents=True, exist_ok=True)
    archive = folder / f"{name}.tar.zst"
    part = archive.with_name(f".{archive.name}.part")
    with tarfile.open(part, "w:zst") as tar:
        for entry in _entries(layer.root):
            if entry.text:
                data = entry.read()
                info = tarfile.TarInfo(entry.path)
                info.size, info.mtime = len(data), int(entry.mtime)
                tar.addfile(info, io.BytesIO(data))
    part.replace(archive)
    save_json(folder / f"{name}.json", found)


def _prune() -> None:
    """Keeps the newest baselines, and only the archives they name."""
    kept = sorted((snapshots_dir() / "baselines").glob("*.json"))
    for old in kept[:-KEEP_BASELINES]:
        old.unlink()
    used: set[tuple[str, str]] = set()
    for path in [snapshots_dir() / "baseline.json", *kept[-KEEP_BASELINES:]]:
        if (base := load_json(path, Baseline)) is not None:
            used.update((k.replace(":", "_"), s) for k, s in base.layers.items())
    for folder in snapshots_dir().iterdir():
        if not folder.is_dir() or folder.name == "baselines":
            continue
        for file in folder.iterdir():
            name = file.name.split(".")[0]
            if (folder.name, name) not in used and not file.name.startswith("."):
                file.unlink()


@dataclass(frozen=True)
class _Entry:
    folded: str
    path: str
    size: int
    mtime: float
    read: Callable[[], bytes]
    other: str  # the digest for a file that isn't hashed

    @property
    def text(self) -> bool:
        return is_text(self.folded)

    def digest(self) -> str:
        return xxhash.xxh64_hexdigest(self.read()) if self.text else self.other


def _entries(root: Path) -> Iterator[_Entry]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for name in filenames:
            full = Path(dirpath, name)
            rel = full.relative_to(root).as_posix()
            stat = full.stat()
            if name.casefold().endswith(".zip") and Path(dirpath) == root:
                yield from _zip_entries(full, stat.st_mtime)
                continue
            other = f"t{stat.st_mtime_ns}"
            yield _Entry(rel.casefold(), rel, stat.st_size, stat.st_mtime, full.read_bytes, other)


def _zip_entries(path: Path, mtime: float) -> Iterator[_Entry]:
    with zipfile.ZipFile(path) as archive:
        infos = [i for i in archive.infolist() if not i.is_dir()]
    for info in infos:

        def read(name: str = info.filename) -> bytes:
            with zipfile.ZipFile(path) as again:
                return again.read(name)

        name = info.filename
        yield _Entry(name.casefold(), name, info.file_size, mtime, read, f"c{info.CRC}")


def _describe(layer: Layer, game: Game) -> tuple[str, str, str]:
    """(name, version, supported_version) of the game or a mod. A zipped mod's
    descriptor is the game's `mod/ugc_<id>.mod`."""
    if layer.key == GAME:
        return "Stellaris", game.version, ""
    kind, _, ident = layer.key.partition(":")
    places = [layer.root / "descriptor.mod"]
    if kind == "workshop":
        places.append(game.mod_dir / f"ugc_{ident}.mod")
    for place in places:
        try:
            found = decode_descriptor(place.read_bytes())
        except OSError:
            continue
        return found.name or layer.key, found.version, found.supported_version
    return layer.key, "", ""
