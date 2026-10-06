"""Stellaris Patcher's command line.

python3 -m stellaris_patcher cold-steel-mix                  # show what it would write
python3 -m stellaris_patcher cold-steel-mix --write          # write the mod and link it
python3 -m stellaris_patcher cold-steel-mix --write --add-to-playset [--cold-steel-closed]
python3 -m stellaris_patcher check-update [--notes]           # after an update: what changed
python3 -m stellaris_patcher check-update --accept            # once reviewed: the new baseline
"""

import argparse
import sys
from datetime import date, datetime
from pathlib import Path

from stellaris_patcher.coldsteel import files as cold_steel
from stellaris_patcher.coldsteel.records import Playset, PlaysetFile
from stellaris_patcher.paradox import processes
from stellaris_patcher.paradox.descriptor import Descriptor
from stellaris_patcher.paradox.game import DEFAULT_STEAM_DIRS, Game, find_game
from stellaris_patcher.patchmod import cold_steel_mix
from stellaris_patcher.patchmod.layers import Layers
from stellaris_patcher.patchmod.write import (
    THUMBNAIL,
    check_files,
    supported_version,
    thumbnail,
    with_mod_last,
    write_mod,
)
from stellaris_patcher.store.paths import cache_dir, shown
from stellaris_patcher.update import check, notes, snapshot


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="stellaris_patcher")
    commands = parser.add_subparsers(dest="command", required=True)
    mix = commands.add_parser("cold-steel-mix", help=f"build the {cold_steel_mix.NAME}")
    mix.add_argument("--write", action="store_true", help="write the mod and link it into mod/")
    mix.add_argument(
        "--add-to-playset",
        action="store_true",
        help=f"also put it last in Cold Steel's {cold_steel_mix.PLAYSET} playset",
    )
    mix.add_argument(
        "--cold-steel-closed",
        action="store_true",
        help="the user says Cold Steel is closed (needed in the container)",
    )
    update = commands.add_parser(
        "check-update", help="after a game or mod update: what changed, and what it may break"
    )
    update.add_argument("--notes", action="store_true", help="also fetch Steam's patch notes")
    update.add_argument(
        "--accept",
        action="store_true",
        help="save the game and mods as they are now, as the baseline for the next check",
    )
    update.add_argument("--out", type=Path, help="the folder for the check (default: in ~/.cache)")
    args = parser.parse_args(argv)
    if args.command == "check-update":
        return _check_update(args.notes, args.accept, args.out)
    return _cold_steel_mix(args.write, args.add_to_playset, args.cold_steel_closed)


def _playset() -> tuple[Game, PlaysetFile, Playset] | None:
    game = find_game(DEFAULT_STEAM_DIRS)
    book = cold_steel.load_playsets()
    found = [p for p in book.playsets if p.name == cold_steel_mix.PLAYSET] if book else []
    if book is None or len(found) != 1:
        print(f"Cold Steel has {len(found)} playsets called {cold_steel_mix.PLAYSET}, not 1.")
        return None
    return game, book, found[0]


def _check_update(fetch_notes: bool, accept: bool, out: Path | None) -> int:
    """Reads only, except our own snapshots (--accept) and the check folder."""
    found = _playset()
    if found is None:
        return 1
    game, _, playset = found
    layers = Layers.for_playset(playset, game, skip=cold_steel_mix.own_keys(game))
    if accept:
        reviewed = [u.ident for u in check.undefined_variables(layers)]
        saved = snapshot.accept(layers, game, playset.name, reviewed)
        print(f"Baseline saved: {len(saved.layers)} layers, game {saved.game_version}.")
        print(f"In {shown(snapshot.snapshots_dir())}. The next check compares with it.")
        return 0
    base = snapshot.load_baseline()
    if base is not None and base.playset != playset.name:
        print(f"The baseline is for {base.playset}, not {playset.name}. Ignoring it.")
        base = None
    record = cold_steel.build_record(playset.id)
    report = check.check(layers, game, base, cold_steel_mix.plan(layers), record)
    folder = out or cache_dir() / "checks" / datetime.now().strftime("%Y-%m-%d_%H%M")
    written = check.write(report, folder)
    if fetch_notes:
        _save_notes(folder, base)
    print(check.render(report).split("\n## ", 1)[0].rstrip())
    print(f"\nThe whole check: {shown(written)}")
    if base is None:
        print("No baseline yet. After reviewing, run check-update --accept.")
    return 0


def _save_notes(folder: Path, base: snapshot.Baseline | None) -> None:
    try:
        found = notes.fetch()
    except notes.NotesError as why:
        print(why)
        return
    since = datetime.fromisoformat(base.taken) if base else None
    recent = [n for n in found if n.date > since] if since else found[:3]
    (folder / "notes").mkdir(parents=True, exist_ok=True)
    for note in recent:
        (folder / "notes" / note.file_name).write_text(
            f"{note.title}\n{note.url}\n\n{note.text}", "utf-8"
        )
    print(f"Patch notes: {len(recent)} announcements in {shown(folder / 'notes')}")
    for note in recent:
        print(f"  {note.date:%Y-%m-%d} {note.title}")


def _cold_steel_mix(write: bool, add: bool, closed: bool) -> int:
    found = _playset()
    if found is None:
        return 1
    game, book, playset = found

    layers = Layers.for_playset(playset, game, skip=cold_steel_mix.own_keys(game))
    files: dict[str, bytes] = {}
    outcomes = cold_steel_mix.plan(layers)
    for outcome in outcomes:
        mark = "left out" if outcome.left_out else "ok"
        print(f"{outcome.number}. {outcome.title}: {mark}")
        for line in (outcome.left_out, *outcome.notes):
            if line:
                print(f"     {line}")
        files.update(outcome.files)
    if problems := check_files(files):
        print("\nNot written. These files wouldn't load:", *problems, sep="\n  ")
        return 1
    if not write:
        print(f"\n{len(files)} files. Nothing written: pass --write.")
        return 0

    if processes.running(processes.GAME | processes.LAUNCHER):
        print("\nClose the game and the Paradox launcher, then try again.")
        return 1
    order = [layer.key for layer in layers.layers]
    names = {k: layers.name(k) for k in cold_steel_mix.patched_mods(outcomes, order)}
    descriptor = Descriptor(
        name=cold_steel_mix.NAME,
        version=date.today().strftime("%Y.%m.%d"),
        supported_version=supported_version(game.version),
        tags=("Fixes", "Graphics"),
        picture=THUMBNAIL,
        dependencies=tuple(names.values()),
    )
    files[THUMBNAIL] = thumbnail()
    folder = write_mod(files, cold_steel_mix.FOLDER, cold_steel_mix.LINK, descriptor, game)
    print(f"\nWrote {len(files)} files to {shown(folder)}, linked as mod/{cold_steel_mix.LINK}.")
    text = cold_steel_mix.workshop_description(outcomes, names, game.version)
    about = folder.with_name(f"{cold_steel_mix.FOLDER}.workshop.txt")
    about.write_text(text, "utf-8")
    print(f"Workshop description: {shown(about)}")

    uploaded = cold_steel_mix.workshop_key(game)
    if add and uploaded in {e.key for e in playset.entries}:
        print(f"{playset.name} has the Workshop copy, {uploaded}. Left it as it is.")
    elif add:
        new = with_mod_last(book, playset.id, cold_steel_mix.KEY, cold_steel_mix.NAME)
        if new == book:
            print(f"It's already last in {playset.name}.")
        else:
            try:
                backup = cold_steel.save_playsets(new, cold_steel_closed=closed)
            except (cold_steel.ColdSteelOpenError, cold_steel.UnknownFormatError) as why:
                print(f"Not added to {playset.name}: {why}")
                return 1
            print(f"Added to {playset.name}. Backup: {shown(backup) if backup else 'none'}.")
        print(f"In Cold Steel, rebuild {playset.name} so the build includes it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
