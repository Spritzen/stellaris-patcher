"""What a mod that hasn't updated since a game release may undo, or still use.

    copies = older_copies(layers, now, updated, diffs, known)
    uses = note_uses(layers, now, updated, kept_notes, known)

`known` holds the idents reviewed at the last accepted check. A finding
whose copies haven't changed since is marked as not new, and gets no diff:
it was read then, and reading it again finds nothing more.

A mod's copy of a game object, or of a whole game file, replaces the game's.
When the game's file changed after the mod's last update, the copy may lack
what the release changed, with nothing in the error log to show it. 4.5.2's
Mega Bombard range and trait categories were found this way. Each finding is
a lead: a mod's own change and a missing game change look the same in a diff.
"""

import difflib
import re
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, replace

from stellaris_patcher.core.definitions import read_definitions, worth_reading
from stellaris_patcher.core.merge_rules import Rule, Rules, load_rules
from stellaris_patcher.patchmod.layers import GAME, LayerError, Layers
from stellaris_patcher.update import snapshot
from stellaris_patcher.update.notes import Note, modding_names
from stellaris_patcher.update.snapshot import Manifest

LANGUAGE = "l_english"
# Folders whose objects are read. Text is left out: its changes are wording.
FOLDERS = ("common", "events", "interface", "gfx", "prescripted_countries", "map")
_COMMENT = re.compile(rb"#[^\n]*")


@dataclass(frozen=True)
class OlderCopy:
    key: str  # the mod
    name: str
    updated: float  # the mod's last update
    kind: str  # the object's kind, like "common/traits", or "file" for a whole file
    object: str  # the object's name; the path for a whole file
    path: str  # the mod's file
    game_path: str  # the game's file
    game_changed: float  # when the game's file last changed
    diff: str = ""  # the diff's name in diffs/, if it was written
    against: str = GAME  # the layer whose copy it replaces, which the diff compares with
    fingerprint: str = ""  # the digests of its copy, the replaced copy and the game's
    new: bool = True  # not reviewed at the last accept, or changed since

    @property
    def ident(self) -> str:
        return f"older {self.key} {self.kind} {self.object} {self.fingerprint}"


@dataclass(frozen=True)
class NoteUse:
    name: str  # a name a release's Modding notes removed, renamed or moved
    key: str
    path: str
    note: str  # the note's title
    new: bool = True  # not reviewed at the last accept

    @property
    def ident(self) -> str:
        return f"note {self.name} {self.key} {self.path}"


@dataclass(frozen=True)
class _Def:
    order: int  # the layer's place in the load order
    key: str
    path: str
    start: int
    end: int
    digest: int
    rule: Rule  # its file's rule: who wins
    live: bool  # its file is the one the game reads at that path


def older_copies(
    layers: Layers,
    now: dict[str, Manifest],
    updated: dict[str, float],
    diffs: dict[str, str],
    known: Iterable[str] = (),
) -> list[OlderCopy]:
    """Every object or whole file a mod's copy wins with, where the game's
    file changed after the mod's last update and the two differ. Writes a
    diff of each new one into `diffs`."""
    reviewed = set(known)
    rules = load_rules()
    game = now[GAME].files
    found: list[OlderCopy] = []
    for (kind, name), defs in _definitions(layers, rules).items():
        theirs = [d for d in defs if d.key == GAME]
        live = [d for d in defs if d.live]
        mine = _winner(live)
        if not theirs or mine is None or mine.key == GAME:
            continue
        game_def = theirs[-1]
        changed = game[game_def.path.casefold()].mtime
        if changed <= _updated(mine.key, now, updated) or mine.digest == game_def.digest:
            continue
        # Compared with the copy the game would use without this mod: another
        # mod's, when that one updated for the release, as UI Overhaul Dynamic does.
        other = _winner([d for d in live if d.key != mine.key]) or game_def
        copy = _copy(mine.key, kind, name, mine.path, game_def.path, changed, now, updated)
        prints = f"{mine.digest:x}/{other.digest:x}/{game_def.digest:x}"
        copy = _review(replace(copy, against=other.key, fingerprint=prints), reviewed)
        found.append(copy)
        if copy.new:
            a = layers.read(other.key, other.path)[other.start : other.end]
            b = layers.read(mine.key, mine.path)[mine.start : mine.end]
            diffs[copy.diff] = diff_text(
                a, b, f"{other.key}:{other.path}", f"{mine.key}:{mine.path}"
            )
    for key in now:
        if key == GAME:
            continue
        for folded, entry in now[key].files.items():
            if folded not in game or _read_inside(entry.path, rules):
                continue
            changed = game[folded].mtime
            if changed <= _updated(key, now, updated) or game[folded].digest == entry.digest:
                continue
            if not _wins(layers, key, entry.path):
                continue
            game_path = game[folded].path
            copy = _copy(key, "file", entry.path, entry.path, game_path, changed, now, updated)
            copy = _review(
                replace(copy, fingerprint=f"{entry.digest}/{game[folded].digest}"), reviewed
            )
            if copy.new and snapshot.is_text(folded):
                a = layers.read(GAME, game_path)
                diffs[copy.diff] = diff_text(a, layers.read(key, entry.path), "game", key)
            else:
                copy = replace(copy, diff="")
            found.append(copy)
    return sorted(found, key=lambda c: (list(now).index(c.key), c.kind, c.object))


def note_uses(
    layers: Layers,
    now: dict[str, Manifest],
    updated: dict[str, float],
    notes: list[Note],
    known: Iterable[str] = (),
) -> list[NoteUse]:
    """Names a release's Modding notes removed, renamed or moved, that a mod
    last updated before that release still uses. Names the game's own files
    still contain are left out: those are the new names, or still in use."""
    by_note = {n.title: modding_names(n.text) for n in notes}
    wanted = set().union(*by_note.values()) if by_note else set()
    if not wanted:
        return []
    game_text = _text(layers, GAME, now)
    game_files = {k.rpartition("/")[2] for k in now[GAME].files}
    gone = {n for n in wanted if n.encode() not in game_text and n.casefold() not in game_files}
    reviewed = set(known)
    found: list[NoteUse] = []
    for key in now:
        if key == GAME:
            continue
        since = _updated(key, now, updated)
        names = {
            name: note.title
            for note in sorted(notes, key=lambda n: n.date)
            if note.date.timestamp() > since
            for name in by_note[note.title] & gone
        }
        if not names:
            continue
        pattern = re.compile(
            rb"(?<![\w@.])(" + b"|".join(re.escape(n.encode()) for n in names) + rb")(?![\w])"
        )
        for folded, data in sorted(_texts(layers, key, now).items()):
            for hit in sorted({m.decode() for m in pattern.findall(_COMMENT.sub(b"", data))}):
                use = NoteUse(hit, key, now[key].files[folded].path, names[hit])
                found.append(replace(use, new=use.ident not in reviewed))
    return found


def _review(copy: OlderCopy, reviewed: set[str]) -> OlderCopy:
    """Not new, with no diff to read, if reviewed and unchanged since."""
    return copy if copy.ident not in reviewed else replace(copy, new=False, diff="")


def _definitions(layers: Layers, rules: Rules) -> dict[tuple[str, str], list[_Def]]:
    """Every object in every layer. A file a later layer replaces is kept
    but not live: the game's own copy is still what a mod's is compared with."""
    found: dict[tuple[str, str], list[_Def]] = defaultdict(list)
    for order, layer in enumerate(layers.layers):
        for folder in FOLDERS:
            for path in layers.paths(layer.key, folder, ""):
                rule = rules.for_file(path)
                if not worth_reading(path, rule, LANGUAGE):
                    continue
                live = _wins(layers, layer.key, path)
                data = layers.read(layer.key, path)
                for d in read_definitions(path, data, rule, LANGUAGE):
                    found[(d.kind, d.key)].append(
                        _Def(order, layer.key, path, d.start, d.end, d.digest, rule, live)
                    )
    return found


def _winner(defs: list[_Def]) -> _Def | None:
    """The copy the game uses: by file name, then load order. None for
    objects the game merges."""
    if not defs:
        return None
    ordered = sorted(defs, key=lambda d: (d.path.rpartition("/")[2].casefold(), d.path, d.order))
    rule = ordered[-1].rule
    if rule.winner == "merged":
        return None
    return ordered[0] if rule.first_wins else ordered[-1]


def _wins(layers: Layers, key: str, path: str) -> bool:
    """False too for a file inside a zipped mod, which Layers can't see."""
    try:
        return layers.winner(path) == key
    except LayerError:
        return False


def _read_inside(path: str, rules: Rules) -> bool:
    """Whether the game reads the file for objects, so `_definitions` covers it."""
    rule = rules.for_file(path)
    return path.casefold().startswith(FOLDERS) and worth_reading(path, rule, LANGUAGE)


def _updated(key: str, now: dict[str, Manifest], updated: dict[str, float]) -> float:
    """Steam's update time, or the mod's newest file for a local mod."""
    return updated.get(key, now[key].newest)


def _copy(
    key: str,
    kind: str,
    name: str,
    path: str,
    game_path: str,
    changed: float,
    now: dict[str, Manifest],
    updated: dict[str, float],
) -> OlderCopy:
    stem = re.sub(r"[^\w.-]+", "_", f"{kind}__{name}")[:120]
    diff = f"older__{key.replace(':', '_')}__{stem}.diff"
    return OlderCopy(
        key, now[key].name, _updated(key, now, updated), kind, name, path, game_path, changed, diff
    )


def diff_text(a: bytes, b: bytes, name_a: str, name_b: str) -> str:
    left = a.decode("utf-8-sig", "replace").splitlines()
    right = b.decode("utf-8-sig", "replace").splitlines()
    return "\n".join(difflib.unified_diff(left, right, name_a, name_b, lineterm="", n=2)) + "\n"


def _texts(layers: Layers, key: str, now: dict[str, Manifest]) -> dict[str, bytes]:
    wanted = [k for k in now[key].files if k.endswith((".txt", ".gui", ".gfx", ".asset", ".csv"))]
    return snapshot.read_now(layers.layer(key), wanted)


def _text(layers: Layers, key: str, now: dict[str, Manifest]) -> bytes:
    return b"\n".join(_COMMENT.sub(b"", d) for d in _texts(layers, key, now).values())
