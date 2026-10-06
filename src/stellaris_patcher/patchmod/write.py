"""Writing a patch mod we made, linking it into the game, and adding it to a playset.

    problems = check_files(files)                  # empty when every file reads
    folder = write_mod(files, "cold_steel_mix_patch", "stellaris_patcher_cold_steel_mix",
                       descriptor, game)
    book = with_mod_last(book, playset_id, key, name)

The mod lives in `~/.local/share/stellaris-patcher/mods/<folder>/` and is
always rebuilt whole. The game's mod folder gets a link to it and a .mod file,
so a rebuild is live at once (decision 15).
"""

import shutil
from collections.abc import Iterable
from importlib import resources
from pathlib import Path

import msgspec

from stellaris_patcher.coldsteel.files import PATCH_PREFIX
from stellaris_patcher.coldsteel.records import PlaysetEntry, PlaysetFile
from stellaris_patcher.paradox.descriptor import Descriptor, decode_descriptor, format_descriptor
from stellaris_patcher.paradox.game import Game
from stellaris_patcher.paradox.localisation import keys, language
from stellaris_patcher.paradox.script import ParseError, parse
from stellaris_patcher.store import paths

BOM = b"\xef\xbb\xbf"
SCRIPT_SUFFIXES = (".txt", ".asset", ".gfx", ".gui")
THUMBNAIL = "thumbnail.png"


class WriteError(Exception):
    """Something that isn't ours is in the way. Nothing was written."""


def mods_dir() -> Path:
    return paths.data_dir() / "mods"


def check_files(files: dict[str, bytes]) -> list[str]:
    """What's wrong with the files, in plain words. Empty if nothing.

    One typo breaks a file in game, so every script
    file must parse, and every localisation file must name its language.
    """
    problems: list[str] = []
    for path, data in files.items():
        lowered = path.casefold()
        if lowered.endswith(SCRIPT_SUFFIXES):
            try:
                parse(data.decode("utf-8-sig"))
            except (ParseError, UnicodeDecodeError) as error:
                problems.append(f"{path}: {error}")
        elif lowered.endswith(".yml"):
            if not data.startswith(BOM):
                problems.append(f"{path}: no byte-order mark, so the game skips it")
            if not language(data) or not keys(data):
                problems.append(f"{path}: no language line, or no keys")
    return problems


def thumbnail() -> bytes:
    """Our patch mods' icon: Cold Steel's, with the sword in emerald.
    Rendered from data/patch-icon.svg with `rsvg-convert -w 512 -h 512`."""
    return resources.files("stellaris_patcher").joinpath(f"data/{THUMBNAIL}").read_bytes()


def supported_version(version: str) -> str:
    """The game's major.minor, as a .mod file's supported_version: "v4.5.*"."""
    major, minor = version.lstrip("v").split(".")[:2]
    return f"v{major}.{minor}.*"


def winning_name(rivals: Iterable[str], tail: str, *, first: bool) -> str | None:
    """A file name that sorts before (`first`) or after every rival, with and
    without case, or None if none can. "z"s are tried first, then "~"s, which
    sort after "z": a real mod names a file `~ariphaos_…` to sort last.
    """
    rivals = list(rivals)
    for char in ("!",) if first else ("z", "~"):
        run = max((len(r) - len(r.lstrip(char + char.upper())) for r in rivals), default=0)
        name = char * max(2, run + 1) + "_" + tail
        if all(_sorts(name, rival, first=first) for rival in rivals):
            return name
    return None


def _sorts(name: str, rival: str, *, first: bool) -> bool:
    pairs = ((name, rival), (name.casefold(), rival.casefold()))
    return all((a < b) if first else (a > b) for a, b in pairs)


def write_mod(
    files: dict[str, bytes], folder: str, link: str, descriptor: Descriptor, game: Game
) -> Path:
    """Rebuild the mod in `mods_dir()/folder`, then link it into the game's mod
    folder as `link`, with `link`.mod beside it. Returns the mod's folder.

    The Workshop id the launcher saved after an upload is kept, so the next
    upload updates the same Workshop item instead of making a new one.

    Raises WriteError, having written nothing, if a real folder or someone
    else's link is where ours goes.
    """
    root = mods_dir()
    target = root / folder
    linked = game.mod_dir / link
    if linked.exists() and not (linked.is_symlink() and linked.readlink() == target):
        raise WriteError(f"{linked} is in the way. It isn't ours, so move it, then try again.")
    if not descriptor.remote_file_id:
        uploaded = workshop_id(target / "descriptor.mod", linked.with_name(link + ".mod"))
        descriptor = msgspec.structs.replace(descriptor, remote_file_id=uploaded)

    new, old = root / f".{folder}.new", root / f".{folder}.old"
    shutil.rmtree(new, ignore_errors=True)
    for path, data in files.items():
        (new / path).parent.mkdir(parents=True, exist_ok=True)
        (new / path).write_bytes(data)
    new.mkdir(parents=True, exist_ok=True)
    (new / "descriptor.mod").write_text(format_descriptor(descriptor), "utf-8")
    shutil.rmtree(old, ignore_errors=True)
    if target.exists():
        target.rename(old)
    new.rename(target)
    shutil.rmtree(old, ignore_errors=True)

    game.mod_dir.mkdir(parents=True, exist_ok=True)
    if not linked.is_symlink():
        linked.symlink_to(target, target_is_directory=True)
    outer = linked.with_name(link + ".mod")
    text = format_descriptor(msgspec.structs.replace(descriptor, path=str(linked)))
    if not outer.exists() or outer.read_text("utf-8") != text:
        outer.write_text(text, "utf-8")
    return target


def workshop_id(*descriptors: Path) -> str:
    """The first remote_file_id in these .mod files, or "" if none has one."""
    for path in descriptors:
        try:
            found = decode_descriptor(path.read_bytes()).remote_file_id
        except OSError:
            continue
        if found:
            return found
    return ""


def with_mod_last(book: PlaysetFile, playset_id: str, key: str, name: str) -> PlaysetFile:
    """The playsets, with mod `key` turned on and last in one playset, but
    before Cold Steel's own patch mod, which must stay last."""
    playsets = []
    for playset in book.playsets:
        if playset.id == playset_id:
            rest = [e for e in playset.entries if e.key != key]
            at = next(
                (i for i, e in enumerate(rest) if e.key.startswith(f"local:{PATCH_PREFIX}")),
                len(rest),
            )
            rest.insert(at, PlaysetEntry(key, True, name))
            playset = msgspec.structs.replace(playset, entries=tuple(rest))
        playsets.append(playset)
    return msgspec.structs.replace(book, playsets=playsets)
