"""What a game or mod update changed, and what it may break in a playset.
The steps around it are in docs/update-check.md.

    report = check(layers, game, base, fixes)
    folder = write(report, out)                # check.md, and diffs/ to read

Every finding is a lead to read, not a verdict. It never writes a fix.
"""

import difflib
import os
import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from stellaris_patcher.core.version import is_outdated
from stellaris_patcher.paradox.game import Game
from stellaris_patcher.paradox.script import scan
from stellaris_patcher.patchmod.cold_steel_mix import Outcome
from stellaris_patcher.patchmod.layers import GAME, Layers
from stellaris_patcher.update import snapshot
from stellaris_patcher.update.snapshot import Baseline, Manifest

_COMMENT = re.compile(rb"#[^\n]*")
# A variable use: not part of a word or a $parameter$, and not a name built from one.
_VARIABLE_USE = re.compile(rb"(?<![\w$])@([A-Za-z_]\w*)(?![\w$])")
_VARIABLE_DEF = re.compile(rb"^\s*(@\w+)\s*=", re.MULTILINE)
UPDATE_WINDOW = 3600.0  # seconds: game files this close to the program's time came with it


@dataclass(frozen=True)
class LayerChange:
    key: str
    name: str
    then: str  # its version at the baseline, "new", or "" with no baseline
    now: str
    changed: int  # files added, removed or changed since the baseline
    supported: str
    outdated: bool
    newest: float  # its newest file's time


@dataclass(frozen=True)
class OldCopy:
    path: str
    key: str
    name: str
    wins: bool
    verdict: str
    changed_since: bool  # the mod's copy changed since the baseline


@dataclass(frozen=True)
class Use:
    name: str  # a name the update no longer defines, or a variable nothing defines
    key: str
    path: str
    new: bool = True  # not in the baseline's reviewed findings

    @property
    def ident(self) -> str:
        return f"{self.name} {self.key} {self.path}"


@dataclass(frozen=True)
class Report:
    game_now: str
    base: Baseline | None
    layers: list[LayerChange]
    game_changed: list[str]
    by_file_time: bool  # no baseline: game_changed comes from file times
    fixes: list[Outcome]
    old_copies: list[OldCopy]
    removed: list[Use]
    undefined: list[Use]
    build: str
    diffs: dict[str, str] = field(default_factory=dict)  # file name -> unified diff


def check(
    layers: Layers,
    game: Game,
    base: Baseline | None,
    fixes: list[Outcome],
    build_record: Path | None = None,
) -> Report:
    now = {layer.key: snapshot.manifest(layer, game) for layer in layers.layers}
    then = _old_manifests(base)
    if base is not None and GAME in then:
        game_changed = _changed(then[GAME], now[GAME])
    else:
        game_changed = _changed_by_time(now[GAME], game)
    diffs: dict[str, str] = {}
    copies = old_copies(layers, base, now, then, game_changed, diffs)
    known = set(base.known) if base else set()
    removed = removed_names(layers, base, now, then) if base is not None else []
    undefined = [
        Use(u.name, u.key, u.path, u.ident not in known) for u in undefined_variables(layers)
    ]
    return Report(
        game_now=game.version,
        base=base,
        layers=_layer_changes(now, then, base, game.version),
        game_changed=game_changed,
        by_file_time=base is None or GAME not in then,
        fixes=fixes,
        old_copies=copies,
        removed=removed,
        undefined=undefined,
        build=_build_status(build_record, now),
        diffs=diffs,
    )


def _old_manifests(base: Baseline | None) -> dict[str, Manifest]:
    found: dict[str, Manifest] = {}
    for key, stamp in (base.layers if base else {}).items():
        if (m := snapshot.load_manifest(key, stamp)) is not None:
            found[key] = m
    return found


def _changed(old: Manifest, new: Manifest) -> list[str]:
    """Files added, removed or changed between two manifests, as written."""
    out: list[str] = []
    for k in old.files.keys() | new.files.keys():
        a, b = old.files.get(k), new.files.get(k)
        if a is None or b is None or (a.size, a.digest) != (b.size, b.digest):
            out.append(b.path if b is not None else old.files[k].path)
    return sorted(out)


def _changed_by_time(found: Manifest, game: Game) -> list[str]:
    """With nothing to compare: the game files written with the game program."""
    try:
        when = game.exe.stat().st_mtime
    except OSError:
        return []
    exe = game.exe.name.casefold()
    return sorted(
        f.path
        for k, f in found.files.items()
        if k != exe and snapshot.is_text(k) and f.mtime >= when - UPDATE_WINDOW
    )


def _layer_changes(
    now: dict[str, Manifest], then: dict[str, Manifest], base: Baseline | None, game: str
) -> list[LayerChange]:
    out: list[LayerChange] = []
    for key, m in now.items():
        old = then.get(key)
        if base is None:
            was, changed = "", 0
        elif old is None:
            was, changed = "new", len(m.files)
        else:
            was, changed = old.version or "?", len(_changed(old, m))
        outdated = key != GAME and is_outdated(m.supported_version, game)
        out.append(
            LayerChange(
                key, m.name, was, m.version, changed, m.supported_version, outdated, m.newest
            )
        )
    gone = [k for k in then if k not in now]
    out += [LayerChange(k, then[k].name, then[k].version, "removed", 0, "", False, 0) for k in gone]
    return out


def old_copies(
    layers: Layers,
    base: Baseline | None,
    now: dict[str, Manifest],
    then: dict[str, Manifest],
    game_changed: list[str],
    diffs: dict[str, str],
) -> list[OldCopy]:
    """Every mod file at the path of a game file the update changed. Compared
    with the game's old copy when there is one: a mod copy missing lines the
    update added has most likely undone part of the update."""
    wanted = {p.casefold(): p for p in game_changed}
    game_new = snapshot.read_now(layers.layer(GAME), wanted)
    game_old = (
        snapshot.read_old(GAME, base.layers[GAME], wanted) if base and GAME in base.layers else {}
    )
    found: list[OldCopy] = []
    order = [layer.key for layer in layers.layers]
    for folded, path in wanted.items():
        shipping = [k for k in order[1:] if folded in now[k].files]
        if not shipping or folded not in game_new:
            continue
        for key in shipping:
            copy = snapshot.read_now(layers.layer(key), {folded})[folded]
            verdict = _verdict(game_old.get(folded), game_new[folded], copy)
            old = then.get(key)
            since = old is not None and (
                folded not in old.files or old.files[folded].digest != now[key].files[folded].digest
            )
            found.append(OldCopy(path, key, now[key].name, key == shipping[-1], verdict, since))
            stem = path.replace("/", "__")
            if folded in game_old:
                diffs[f"{stem}__game.diff"] = _diff(
                    game_old[folded], game_new[folded], "old", "new"
                )
            diffs[f"{stem}__{key.replace(':', '_')}.diff"] = _diff(
                game_new[folded], copy, "game", key
            )
    return found


def _lines(data: bytes) -> set[str]:
    text = _COMMENT.sub(b"", data).decode("utf-8-sig", "replace")
    return {" ".join(line.split()) for line in text.splitlines() if line.strip()}


def _verdict(old: bytes | None, new: bytes, copy: bytes) -> str:
    if copy == new:
        return "the same as the game's new file"
    if old is None:
        differ = len(_lines(new) ^ _lines(copy))
        return f"no old game copy to compare: {differ} lines differ from the new file"
    if copy == old:
        return "the game's old file, unchanged: every change in the update is lost"
    added = _lines(new) - _lines(old)
    missing = added - _lines(copy)
    if not added:
        return "the update only removed lines; check the diff"
    if not missing:
        return f"has all {len(added)} lines the update added"
    return f"misses {len(missing)} of the {len(added)} lines the update added"


def _diff(a: bytes, b: bytes, name_a: str, name_b: str) -> str:
    left = a.decode("utf-8-sig", "replace").splitlines()
    right = b.decode("utf-8-sig", "replace").splitlines()
    return "\n".join(difflib.unified_diff(left, right, name_a, name_b, lineterm="", n=2)) + "\n"


def _defined(layers: Layers, keys: Iterable[str]) -> set[str]:
    """Top-level names the given layers define in `common/`, counting files
    a later layer replaces."""
    names: set[str] = set()
    for key in keys:
        for path in layers.paths(key, "common"):
            names.update(e.key.decode("utf-8", "replace") for e in scan(layers.read(key, path)))
    return names


def removed_names(
    layers: Layers, base: Baseline, now: dict[str, Manifest], then: dict[str, Manifest]
) -> list[Use]:
    """Names the game defined at the baseline and no longer does, that a mod
    still uses. Renamed triggers, effects and variables show up here."""
    old_files = [f.path for f in then.get(GAME, now[GAME]).files.values()]
    common = [p for p in old_files if p.casefold().startswith("common/") and p.endswith(".txt")]
    before: set[str] = set()
    for data in snapshot.read_old(GAME, base.layers[GAME], common).values():
        before.update(e.key.decode("utf-8", "replace") for e in scan(data))
    mods = [layer.key for layer in layers.layers[1:]]
    gone = before - _defined(layers, [GAME]) - _defined(layers, mods)
    gone = {n for n in gone if "_" in n or n.startswith("@")}
    if not gone:
        return []
    pattern = re.compile(
        rb"(?<![\w@.])("
        + b"|".join(re.escape(n.encode()) for n in sorted(gone, key=len, reverse=True))
        + rb")(?![\w])"
    )
    found: list[Use] = []
    for key in mods:
        texts = snapshot.read_now(layers.layer(key), _text_paths(now[key]))
        for folded, data in sorted(texts.items()):
            names = {m.decode() for m in pattern.findall(_COMMENT.sub(b"", data))}
            path = now[key].files[folded].path
            found += [Use(n, key, path) for n in sorted(names)]
    return found


def _text_paths(found: Manifest) -> list[str]:
    return [k for k in found.files if k.endswith((".txt", ".gui", ".gfx", ".asset"))]


def undefined_variables(layers: Layers) -> list[Use]:
    """`@variables` a mod's `common/` files use that neither the file nor any
    scripted_variables file defines."""
    known = set(layers.defined("common/scripted_variables"))
    found: list[Use] = []
    for layer, path in sorted(layers.files("common", ".txt").values()):
        if layer == GAME:
            continue
        data = _COMMENT.sub(b"", layers.read(layer, path))
        local = {m.decode() for m in _VARIABLE_DEF.findall(data)}
        used = {"@" + m.decode() for m in _VARIABLE_USE.findall(data)}
        found += [Use(name, layer, path) for name in sorted(used - local - known)]
    return found


def _build_status(record: Path | None, now: dict[str, Manifest]) -> str:
    """Whether Cold Steel's build of the playset is older than its game or mods."""
    if record is None or not record.is_file():
        return "Cold Steel has no build of this playset."
    built = record.stat().st_mtime
    after = [m.name for m in now.values() if m.newest > built]
    when = _time(built)
    if not after:
        return f"Built {when}. Nothing changed after it."
    return f"Built {when}. Changed after it: {', '.join(after)}. Rebuild it in Cold Steel."


def _time(seconds: float) -> str:
    return datetime.fromtimestamp(seconds).astimezone().strftime("%Y-%m-%d %H:%M")


def render(report: Report) -> str:
    """The report as Markdown: what to read first, then each finding."""
    base = report.base
    since = f"the baseline of {base.taken} (game {base.game_version})" if base else "no baseline"
    left_out = [o for o in report.fixes if o.left_out]
    lost = [c for c in report.old_copies if c.wins and not c.verdict.startswith("has all")]
    new_undefined = [u for u in report.undefined if u.new]
    lines = [
        f"# Update check, {datetime.now().astimezone():%Y-%m-%d %H:%M}",
        "",
        f"Game {report.game_now}, compared with {since}.",
        "",
        f"- **Game files changed:** {len(report.game_changed)}"
        + (" (by file time: no baseline to compare)" if report.by_file_time else ""),
        f"- **Mods changed:** {sum(1 for c in report.layers if c.key != GAME and c.changed)}",
        f"- **Fixes left out:** {len(left_out)} of {len(report.fixes)}",
        f"- **Winning mod copies of changed game files that may undo the update:** {len(lost)}",
        f"- **Removed names still used by mods:** {len(report.removed)}"
        + ("" if base else " (needs a baseline)"),
        f"- **Undefined variables:** {len(report.undefined)}, {len(new_undefined)} not reviewed",
        f"- **Cold Steel build:** {report.build}",
        "",
        "## Game and mods",
        "",
        "| Layer | Then | Now | Files changed | Supports | Newest file |",
        "|---|---|---|---:|---|---|",
    ]
    for c in report.layers:
        flag = " **outdated**" if c.outdated else ""
        lines.append(
            f"| {c.name} (`{c.key}`) | {c.then} | {c.now} | {c.changed} | "
            f"{c.supported}{flag} | {_time(c.newest) if c.newest else ''} |"
        )
    lines += ["", "## The patch's fixes", ""]
    lines += [
        f"- {o.number}. {o.title}: " + (f"**left out**: {o.left_out}" if o.left_out else "ok")
        for o in report.fixes
    ]
    lines += ["", "## Mod copies of changed game files", ""]
    if report.old_copies:
        lines += [
            "| File | Mod | Wins | Its copy | Changed since baseline |",
            "|---|---|---|---|---|",
        ]
        lines += [
            f"| `{c.path}` | {c.name} | {'yes' if c.wins else 'no'} | {c.verdict} | "
            f"{('yes' if c.changed_since else 'no') if base else ''} |"
            for c in report.old_copies
        ]
        lines += [
            "",
            "Diffs are in `diffs/`: `__game.diff` is the update, the others each mod's copy.",
        ]
    else:
        lines.append("None.")
    lines += ["", "## Names the update removed that mods still use", ""]
    lines += _uses(report.removed) if base else ["Needs a baseline: run with `--accept` first."]
    lines += ["", "## Variables nothing defines", ""]
    lines += _uses(report.undefined, mark=True)
    lines += ["", "## Game files changed", ""]
    lines += _folders(report.game_changed)
    return "\n".join(lines) + "\n"


def _uses(uses: list[Use], mark: bool = False) -> list[str]:
    if not uses:
        return ["None."]
    return [
        f"- `{u.name}` in {u.key} `{u.path}`" + (" **(new)**" if mark and u.new else "")
        for u in uses
    ]


def _folders(paths: list[str]) -> list[str]:
    counts: dict[str, int] = {}
    for p in paths:
        folder = p.rpartition("/")[0] or "."
        counts[folder] = counts.get(folder, 0) + 1
    return [f"- `{f}/`: {n}" for f, n in sorted(counts.items())] or ["None."]


def write(report: Report, out: Path) -> Path:
    """Writes check.md and the diffs into `out`, and returns check.md's path."""
    (out / "diffs").mkdir(parents=True, exist_ok=True)
    for name, text in report.diffs.items():
        (out / "diffs" / name).write_text(text, "utf-8")
    (out / "game-files-changed.txt").write_text(
        "".join(p + os.linesep for p in report.game_changed), "utf-8"
    )
    target = out / "check.md"
    target.write_text(render(report), "utf-8")
    return target
