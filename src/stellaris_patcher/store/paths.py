"""Where Stellaris Patcher keeps its own files, following the XDG base directory spec."""

import os
from pathlib import Path

APP_NAME = "stellaris-patcher"


def _xdg(var: str, default: str, app: str = APP_NAME) -> Path:
    # The spec says to ignore the variable when it is empty or not absolute.
    value = os.environ.get(var, "")
    base = Path(value) if value and Path(value).is_absolute() else Path.home() / default
    return base / app


def shown(path: Path) -> str:
    """A path as the user reads it: the home folder as `~`."""
    try:
        return f"~/{path.relative_to(Path.home())}"
    except ValueError:
        return str(path)


def config_dir() -> Path:
    """Settings. `~/.config/stellaris-patcher/`."""
    return _xdg("XDG_CONFIG_HOME", ".config")


def data_dir() -> Path:
    """Backups of the files we write, and our patch work.
    `~/.local/share/stellaris-patcher/`."""
    return _xdg("XDG_DATA_HOME", ".local/share")


def cache_dir() -> Path:
    """Caches, such as update checks. Safe to delete.
    `~/.cache/stellaris-patcher/`."""
    return _xdg("XDG_CACHE_HOME", ".cache")
