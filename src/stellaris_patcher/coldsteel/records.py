"""The records in Cold Steel's data files, as of Cold Steel 0.6.0.

Field names, order and defaults must match what Cold Steel writes, or the
files we write won't read back in Cold Steel. When its files gain a field or a
new `version`, writing them is refused (files.py), and
`test_records_read_cold_steels_real_files` fails. Add the change here then.
"""

import msgspec

PLAYSETS_VERSION = 1
RESOLUTIONS_VERSION = 1


# ~/.local/share/cold-steel/playsets.json


class PlaysetEntry(msgspec.Struct, frozen=True):
    key: str  # a Mod.key: "workshop:<id>" or "local:<name of the .mod file>"
    enabled: bool = True
    name: str = ""  # kept so a mod that's gone from disk still shows its name


class Pin(msgspec.Struct, frozen=True):
    """A Workshop mod the playset plays from a saved copy, not Steam's folder."""

    key: str  # the Workshop mod's Mod.key
    snapshot: str  # the copy's id, in the snapshot store


class Playset(msgspec.Struct, frozen=True):
    id: str
    name: str
    entries: tuple[PlaysetEntry, ...] = ()  # in load order
    disabled_dlcs: tuple[str, ...] = ()  # DLC folder names, e.g. "dlc033_cosmic_storms"
    launcher_id: str = ""  # the launcher playset this was imported from or exported to
    pins: tuple[Pin, ...] = ()  # empty: every mod plays from Steam's folder


class PlaysetFile(msgspec.Struct):
    version: int = PLAYSETS_VERSION
    active: str = ""  # the id of the playset Play uses
    playsets: list[Playset] = msgspec.field(default_factory=list)


# ~/.local/share/cold-steel/resolutions/<playset id>.json


class Seen(msgspec.Struct, frozen=True):
    """One version of an object, as it was when the choice was made."""

    layer: str  # "game" or a Mod.key
    path: str
    digest: int  # the object's digest (core/definitions.py), or the file's hash


class Resolution(msgspec.Struct, frozen=True):
    kind: str  # "file", or a kind of object such as "common/technology"
    key: str
    # The chosen version. Both are empty for the user's own version.
    layer: str = ""
    path: str = ""
    text: str = ""  # the user's own version
    seen: tuple[Seen, ...] = ()  # every version when the choice was made

    @property
    def own(self) -> bool:
        return not self.layer


class Ignore(msgspec.Struct, frozen=True):
    """One ignore rule. Set `kind` and `key` for one conflict, `kind` alone for
    every conflict of a type, or `mod` alone for every conflict of a mod."""

    kind: str = ""
    key: str = ""
    mod: str = ""


class ResolutionFile(msgspec.Struct):
    version: int = RESOLUTIONS_VERSION
    resolutions: list[Resolution] = msgspec.field(default_factory=list)
    ignored: list[Ignore] = msgspec.field(default_factory=list)
    # Which choices the patch mod was last made from (Cold Steel's
    # core.resolve.choices_digest). Cold Steel rebuilds the patch when it differs.
    built: int = 0


# ~/.config/cold-steel/settings.json. Read only.


class Settings(msgspec.Struct):
    steam_dir: str = ""  # set by hand when Steam isn't in the usual place
    game_data_dir: str = ""  # Stellaris's data folder, when not where the game says
    theme: str = "system"
    welcomed: bool = False
