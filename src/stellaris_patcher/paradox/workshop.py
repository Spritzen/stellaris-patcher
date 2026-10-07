"""When Steam last updated each Workshop mod, from `appworkshop_281990.acf`.

    updated = update_times(game)               # {"workshop:1623423360": 1791..., ...}

A mod's file times aren't the same thing: Steam sometimes rewrites a mod's
files without a new version, so its newest file can be weeks younger than
its last update.
"""

from pathlib import Path

from stellaris_patcher.paradox.game import STELLARIS_APP_ID, Game
from stellaris_patcher.paradox.vdf import VdfError, parse_vdf


def manifest_path(game: Game) -> Path:
    return game.library_dir / "steamapps/workshop" / f"appworkshop_{STELLARIS_APP_ID}.acf"


def update_times(game: Game) -> dict[str, float]:
    """Each installed Workshop mod's last update, in seconds, by Cold Steel
    key. Empty if Steam's file is missing or can't be read."""
    try:
        root = parse_vdf(manifest_path(game).read_text("utf-8", errors="replace"))
    except OSError, VdfError:
        return {}
    app = root.get("AppWorkshop")
    items = app.get("WorkshopItemsInstalled") if isinstance(app, dict) else None
    if not isinstance(items, dict):
        return {}
    found: dict[str, float] = {}
    for item_id, item in items.items():
        when = item.get("timeupdated") if isinstance(item, dict) else None
        if isinstance(when, str) and when.isdigit():
            found[f"workshop:{item_id}"] = float(when)
    return found
