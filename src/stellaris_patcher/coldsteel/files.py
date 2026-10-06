"""Reading and writing Cold Steel's own files (decision 11).

    book = load_playsets()                         # None: no file yet, or unreadable
    save_playsets(book)                            # raises the errors below, or OSError
    save_playsets(book, cold_steel_closed=True)    # in the container, after asking

Every write is guarded three ways (decision 12):

1. **Cold Steel must be closed.** It loads its files when it starts and saves
   over them, which would undo our change. From inside the container its
   process can't be seen, so the caller must say the user confirmed it.
2. **The file on disk must be one we fully understand.** msgspec drops fields
   it doesn't know, so writing a newer Cold Steel's file would lose data.
3. **The file is backed up first**, into `~/.local/share/stellaris-patcher/backups/cold-steel/`.
"""

import os
from pathlib import Path
from typing import Any

import msgspec

from stellaris_patcher.coldsteel.records import (
    PLAYSETS_VERSION,
    RESOLUTIONS_VERSION,
    PlaysetFile,
    ResolutionFile,
    Settings,
)
from stellaris_patcher.paradox.backup import backup_file
from stellaris_patcher.store import paths
from stellaris_patcher.store.files import load_json, save_json

APP_NAME = "cold-steel"
PATCH_PREFIX = "cold_steel_patch_"  # mod/cold_steel_patch_<playset id>: its patch mod's link


class ColdSteelOpenError(Exception):
    """Cold Steel is running, or we can't tell that it isn't."""


class UnknownFormatError(Exception):
    """The file holds something these records don't: writing it would lose data."""


def data_dir() -> Path:
    """`~/.local/share/cold-steel/`."""
    return paths._xdg("XDG_DATA_HOME", ".local/share", APP_NAME)


def config_dir() -> Path:
    """`~/.config/cold-steel/`."""
    return paths._xdg("XDG_CONFIG_HOME", ".config", APP_NAME)


def playsets_file() -> Path:
    return data_dir() / "playsets.json"


def resolutions_file(playset_id: str) -> Path:
    return data_dir() / "resolutions" / f"{playset_id}.json"


def patch_dir(playset_id: str) -> Path:
    """Where Cold Steel writes a playset's patch mod."""
    return data_dir() / "patches" / playset_id


def build_record(playset_id: str) -> Path:
    """Which mod each file in a playset's build came from."""
    return data_dir() / "builds" / f"{playset_id}.json"


def settings_file() -> Path:
    return config_dir() / "settings.json"


def backup_dir() -> Path:
    return paths.data_dir() / "backups" / APP_NAME


def load_playsets(path: Path | None = None) -> PlaysetFile | None:
    return load_json(path or playsets_file(), PlaysetFile)


def load_resolutions(playset_id: str, path: Path | None = None) -> ResolutionFile | None:
    return load_json(path or resolutions_file(playset_id), ResolutionFile)


def load_settings(path: Path | None = None) -> Settings:
    return load_json(path or settings_file(), Settings) or Settings()


def save_playsets(
    data: PlaysetFile, path: Path | None = None, *, cold_steel_closed: bool = False
) -> Path | None:
    """Returns the backup made, or None when there was no file yet."""
    return _save(path or playsets_file(), data, PlaysetFile, PLAYSETS_VERSION, cold_steel_closed)


def save_resolutions(
    playset_id: str,
    data: ResolutionFile,
    path: Path | None = None,
    *,
    cold_steel_closed: bool = False,
) -> Path | None:
    return _save(
        path or resolutions_file(playset_id),
        data,
        ResolutionFile,
        RESOLUTIONS_VERSION,
        cold_steel_closed,
    )


def in_container() -> bool:
    return Path("/.dockerenv").exists() or Path("/run/.containerenv").exists()


def cold_steel_running(proc: Path = Path("/proc"), *, container: bool | None = None) -> bool | None:
    """True or False, or None when we can't tell: inside a container, host
    processes aren't in /proc."""
    if in_container() if container is None else container:
        return None
    try:
        entries = list(proc.iterdir())
    except OSError:
        return None
    for entry in entries:
        if not entry.name.isdigit() or entry.name == str(os.getpid()):
            continue
        try:
            args = (entry / "cmdline").read_bytes().split(b"\0")
        except OSError:  # it ended while we looked, or isn't ours to read
            continue
        # `python3 -m cold_steel` from source, `python /usr/bin/cold-steel` installed.
        if any(arg == b"cold_steel" or Path(os.fsdecode(arg)).name == "cold-steel" for arg in args):
            return True
    return False


def _save(path: Path, data: Any, type_: type[Any], version: int, closed: bool) -> Path | None:
    running = cold_steel_running()
    if running:
        raise ColdSteelOpenError("Cold Steel is open. Close it, then try again.")
    if running is None and not closed:
        raise ColdSteelOpenError(
            "Can't see whether Cold Steel is open from here (in the container). "
            "Ask the user to close it, then pass cold_steel_closed=True."
        )
    if data.version != version:
        raise UnknownFormatError(f"Writing version {data.version}, but we know only {version}.")
    if path.exists():
        check_known(path, type_, version)
    backup = backup_file(path, backup_dir())  # OSError: then don't write
    save_json(path, data)
    return backup


def check_known(path: Path, type_: type[Any], version: int) -> None:
    """Raises UnknownFormatError unless `path` is a file these records fully
    understand: the same version, and no field they lack."""
    raw = path.read_bytes()
    try:
        found = msgspec.json.decode(raw)
        known = msgspec.to_builtins(msgspec.json.decode(raw, type=type_))
    except msgspec.DecodeError as error:
        raise UnknownFormatError(f"{path} doesn't read as Cold Steel's format: {error}") from error
    if found.get("version") != version:
        raise UnknownFormatError(f"{path} is version {found.get('version')}; we know {version}.")
    if not _covers(known, found):
        raise UnknownFormatError(
            f"{path} has fields these records don't. Cold Steel's format has changed: "
            "add the new fields to coldsteel/records.py first."
        )


def _covers(known: Any, found: Any) -> bool:
    """Every field in `found` is in `known` with the same value. `known` may have
    more: fields an older file left out come back as their defaults."""
    if isinstance(found, dict):
        return isinstance(known, dict) and all(
            k in known and _covers(known[k], v) for k, v in found.items()
        )
    if isinstance(found, list):
        return (
            isinstance(known, list | tuple)  # to_builtins keeps tuples
            and len(known) == len(found)
            and all(_covers(a, b) for a, b in zip(known, found, strict=True))
        )
    return bool(known == found)
