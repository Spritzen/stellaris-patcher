"""Backups made before every write to a file that isn't ours (decision 6).

    backup_file(path, backup_dir)   # raises OSError: then don't write

Each backup is a dated copy in `backup_dir`, and the newest `KEEP` copies of
each file are kept.
"""

import shutil
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

KEEP = 20


def backup_file(path: Path, backup_dir: Path, keep: int = KEEP) -> Path | None:
    """Copy `path` into `backup_dir` with the date and time in its name.

    Returns the copy, or None when `path` doesn't exist (nothing to lose).
    Raises OSError if the copy can't be made, so the caller never writes
    without a backup.
    """
    if not path.exists():
        return None
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
    target = backup_dir / f"{path.stem}.{stamp}{path.suffix}"
    _copy(path, target)
    _prune(backup_dir, path, keep)
    return target


def backups_of(path: Path, backup_dir: Path) -> list[Path]:
    """The dated backups of `path`, oldest first."""
    if not backup_dir.is_dir():
        return []
    prefix = f"{path.stem}."
    return sorted(
        p
        for p in backup_dir.iterdir()
        if p.name.startswith(prefix)
        and p.suffix == path.suffix
        and p.name[len(prefix) : len(prefix) + 1].isdigit()
    )


def _copy(source: Path, target: Path) -> None:
    tmp = target.with_name(f".{target.name}.tmp")
    try:
        if source.suffix == ".sqlite":
            _copy_sqlite(source, tmp)
        else:
            shutil.copy2(source, tmp)
        tmp.replace(target)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def _copy_sqlite(source: Path, target: Path) -> None:
    # SQLite's own backup gives a consistent copy, even mid-write by another program.
    try:
        with (
            closing(sqlite3.connect(f"{source.as_uri()}?mode=ro", uri=True)) as src,
            closing(sqlite3.connect(target)) as dst,
        ):
            src.backup(dst)
    except sqlite3.Error as error:
        raise OSError(f"Couldn't back up {source}: {error}") from error


def _prune(backup_dir: Path, path: Path, keep: int) -> None:
    for old in backups_of(path, backup_dir)[:-keep]:
        old.unlink(missing_ok=True)
