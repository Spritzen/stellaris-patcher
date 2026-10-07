import os
import zipfile
from datetime import UTC, datetime
from pathlib import Path

import pytest

from stellaris_patcher.coldsteel.records import Playset, PlaysetEntry
from stellaris_patcher.paradox.game import Game
from stellaris_patcher.paradox.workshop import manifest_path, update_times
from stellaris_patcher.patchmod.layers import GAME, Layers
from stellaris_patcher.update import check, notes, older, snapshot
from stellaris_patcher.update.notes import Note, plain


@pytest.fixture
def game(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Game:
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
    return Game(
        install_dir=tmp_path / "steam/steamapps/common/Stellaris",
        library_dir=tmp_path / "steam",
        version="v4.5.1",
        version_name="Cygnus v4.5.1",
        data_dir=tmp_path / "paradox",
        exe=tmp_path / "steam/steamapps/common/Stellaris/stellaris",
    )


def _put(root: Path, files: dict[str, str]) -> None:
    for path, text in files.items():
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(text, "utf-8")


def _layers(game: Game, mods: dict[str, dict[str, str]]) -> Layers:
    _put(game.install_dir, mods.pop(GAME, {}))
    for key, files in mods.items():
        _put(game.workshop_dir / key.removeprefix("workshop:"), files)
    entries = tuple(PlaysetEntry(k) for k in mods)
    return Layers.for_playset(Playset("p1", "Mix", entries), game)


OLD_GAME = {
    "common/buildings/00_buildings.txt": "building_a = {\n\tcost = 1\n}\n",
    "common/scripted_triggers/00_triggers.txt": "is_old_trigger = { always = yes }\n",
    "common/scripted_variables/00_vars.txt": "@kept = 1\n",
}
MOD = {
    "common/buildings/00_buildings.txt": OLD_GAME["common/buildings/00_buildings.txt"],
    "events/mod_events.txt": "event = { trigger = { is_old_trigger = yes } }\n",
}


def _update(game: Game) -> Layers:
    """The game after an update: a building gained a line, a trigger was renamed."""
    _put(
        game.install_dir,
        {
            "common/buildings/00_buildings.txt": "building_a = {\n\tcost = 1\n\tupkeep = 2\n}\n",
            "common/scripted_triggers/00_triggers.txt": "is_new_trigger = { always = yes }\n",
        },
    )
    return _layers(game, {"workshop:1": {}})


def test_a_check_after_an_update_finds_the_old_copy_and_the_removed_name(game: Game) -> None:
    layers = _layers(game, {GAME: dict(OLD_GAME), "workshop:1": dict(MOD)})
    snapshot.accept(layers, game, "Mix", [])
    layers = _update(game)
    base = snapshot.load_baseline()
    assert base is not None

    report = check.check(layers, game, base, [])

    assert report.game_changed == [
        "common/buildings/00_buildings.txt",
        "common/scripted_triggers/00_triggers.txt",
    ]
    assert not report.by_file_time
    (copy,) = report.old_copies
    assert copy.key == "workshop:1" and copy.wins
    assert copy.verdict.startswith("the game's old file, unchanged")
    assert [(u.name, u.path) for u in report.removed] == [
        ("is_old_trigger", "events/mod_events.txt")
    ]
    assert "+\tupkeep = 2" in report.diffs["common__buildings__00_buildings.txt__game.diff"]
    assert "| Building" not in check.render(report)


def test_a_mod_copy_with_the_updates_lines_is_told_apart(game: Game) -> None:
    mod = dict(MOD)
    mod["common/buildings/00_buildings.txt"] = "building_a = {\n\tcost = 5 # mod\n}\n"
    layers = _layers(game, {GAME: dict(OLD_GAME), "workshop:1": mod})
    snapshot.accept(layers, game, "Mix", [])
    layers = _update(game)
    report = check.check(layers, game, snapshot.load_baseline(), [])
    assert report.old_copies[0].verdict == "misses 1 of the 1 lines the update added"

    _put(game.workshop_dir / "1", {"common/buildings/00_buildings.txt": "a = {\nupkeep = 2\n}"})
    report = check.check(layers, game, snapshot.load_baseline(), [])
    assert report.old_copies[0].verdict == "has all 1 lines the update added"
    assert report.old_copies[0].changed_since


def test_without_a_baseline_changed_files_come_from_file_times(game: Game) -> None:
    layers = _layers(game, {GAME: dict(OLD_GAME)})
    game.exe.write_bytes(b"")
    old = game.install_dir / "common/buildings/00_buildings.txt"
    os.utime(old, (game.exe.stat().st_mtime - 2 * check.UPDATE_WINDOW,) * 2)
    report = check.check(layers, game, None, [])
    assert report.by_file_time
    assert report.game_changed == [
        "common/scripted_triggers/00_triggers.txt",
        "common/scripted_variables/00_vars.txt",
    ]
    assert report.removed == []


def test_an_unchanged_layer_is_stored_once_and_old_baselines_are_kept(game: Game) -> None:
    layers = _layers(game, {GAME: dict(OLD_GAME), "workshop:1": dict(MOD)})
    first = snapshot.accept(layers, game, "Mix", [])
    second = snapshot.accept(layers, game, "Mix", ["@x workshop:1 a.txt"])
    assert first.layers == second.layers
    assert second.known == ("@x workshop:1 a.txt",)
    assert len(list((snapshot.snapshots_dir() / "game").glob("*.tar.zst"))) == 1
    assert len(list((snapshot.snapshots_dir() / "baselines").glob("*.json"))) == 1
    texts = snapshot.read_old(GAME, second.layers[GAME], ["common/buildings/00_BUILDINGS.txt"])
    assert texts == {"common/buildings/00_buildings.txt": b"building_a = {\n\tcost = 1\n}\n"}


def test_a_zipped_mods_files_are_read_from_the_zip(game: Game) -> None:
    folder = game.workshop_dir / "7"
    folder.mkdir(parents=True)
    with zipfile.ZipFile(folder / "mod.zip", "w") as archive:
        archive.writestr("common/defines/a.txt", "NGraphics = { A = 1 }\n")
    layers = _layers(game, {})
    layers = Layers.for_playset(Playset("p1", "Mix", (PlaysetEntry("workshop:7"),)), game)
    found = snapshot.manifest(layers.layer("workshop:7"), game)
    assert list(found.files) == ["common/defines/a.txt"]
    texts = snapshot.read_now(layers.layer("workshop:7"), ["common/defines/a.txt"])
    assert texts == {"common/defines/a.txt": b"NGraphics = { A = 1 }\n"}


def test_undefined_variables_skip_parameters_and_local_names(game: Game) -> None:
    text = (
        "@local = 1\n"
        "a = { cost = @local value = @global flag = $PATH$@ROOT x = flag@ROOT }\n"
        "b = { mult = @prefix_$PLANET$_high sum = @[ x * 2 ] lost = @missing } # @commented\n"
    )
    layers = _layers(
        game,
        {
            GAME: {"common/scripted_variables/00.txt": "@global = 2\n"},
            "workshop:1": {"common/buildings/mod.txt": text},
        },
    )
    assert [u.name for u in check.undefined_variables(layers)] == ["@missing"]


def test_the_build_status_names_what_changed_after_the_build(game: Game, tmp_path: Path) -> None:
    layers = _layers(game, {GAME: dict(OLD_GAME), "workshop:1": dict(MOD)})
    record = tmp_path / "build.json"
    record.write_text("{}", "utf-8")
    later = record.stat().st_mtime + 60
    os.utime(game.workshop_dir / "1/events/mod_events.txt", (later, later))
    report = check.check(layers, game, None, [], record)
    assert "Changed after it: workshop:1. Rebuild it in Cold Steel." in report.build


def test_plain_turns_steams_bbcode_into_text() -> None:
    bbcode = "[h3]4.5.2 Notes[/h3][p][b]Modding[/b][/p][list][*][p]Added `x`[/p][/*][/list]"
    assert plain(bbcode) == "## 4.5.2 Notes\n\nModding\n\n- Added `x`\n"


MOD_UPDATED = 1_000_000.0  # the mods' last update; the game's files change after it


def _older_playset(game: Game, mods: dict[str, dict[str, str]]) -> Layers:
    """A game whose files all changed after MOD_UPDATED."""
    layers = _layers(game, mods)
    for path in game.install_dir.rglob("*"):
        if path.is_file():
            os.utime(path, (MOD_UPDATED + 10,) * 2)
    return layers


def _now(layers: Layers, game: Game) -> dict[str, snapshot.Manifest]:
    return {layer.key: snapshot.manifest(layer, game) for layer in layers.layers}


def test_an_older_mod_copy_of_a_changed_game_object_is_found(game: Game) -> None:
    layers = _older_playset(
        game,
        {
            GAME: {
                "common/buildings/00_buildings.txt": "building_a = {\n\tcost = 1\n\tupkeep = 2\n}\n"
                "building_b = { cost = 3 }\n",
                "common/component_templates/weapons.csv": "key;range\nGUN;100\n",
            },
            "workshop:1": {
                # Sorts after the game's file, so its building_a wins. building_b is the same.
                "common/buildings/zz_mod.txt": "building_a = {\n\tcost = 1\n}\n"
                "building_b = { cost = 3 }\n",
                "common/component_templates/weapons.csv": "key;range\nGUN;2\n",
            },
        },
    )
    diffs: dict[str, str] = {}
    found = older.older_copies(layers, _now(layers, game), {"workshop:1": MOD_UPDATED}, diffs)
    assert [(c.kind, c.object) for c in found] == [
        ("common/buildings", "building_a"),
        ("file", "common/component_templates/weapons.csv"),
    ]
    assert "-\tupkeep = 2" in diffs[found[0].diff]
    assert "+GUN;2" in diffs[found[1].diff]

    # Updated after the game's files: nothing to report.
    later = {"workshop:1": MOD_UPDATED + 20}
    assert older.older_copies(layers, _now(layers, game), later, {}) == []


def test_an_older_copy_is_compared_with_the_copy_it_replaces(game: Game) -> None:
    layers = _older_playset(
        game,
        {
            GAME: {"interface/view.gui": "containerWindowType = { name = view a = 1 }\n"},
            # workshop:1 updated for the release and added b; workshop:2 sorts last and wins.
            "workshop:1": {"interface/view.gui": "containerWindowType = { name = view b = 1 }\n"},
            "workshop:2": {"interface/zz_view.gui": "containerWindowType = { name = view }\n"},
        },
    )
    updated = {"workshop:1": MOD_UPDATED + 20, "workshop:2": MOD_UPDATED}
    diffs: dict[str, str] = {}
    (copy,) = older.older_copies(layers, _now(layers, game), updated, diffs)
    assert (copy.key, copy.against) == ("workshop:2", "workshop:1")
    assert "b = 1" in diffs[copy.diff]


def test_a_name_the_notes_removed_is_found_in_a_mod_older_than_the_notes(game: Game) -> None:
    layers = _layers(
        game,
        {
            GAME: {"common/scripted_triggers/00.txt": "new_trigger = { always = yes }\n"},
            "workshop:1": {"events/a.txt": "e = { trigger = { old_trigger = yes } }\n"},
        },
    )
    text = (
        "Bugfix\n\n- Fixed old_trigger in an event\n\nModding\n\n"
        "- Scripted trigger `old_trigger` is now `new_trigger`\n\nThanks for playing!\n"
    )
    note = Note(datetime.fromtimestamp(MOD_UPDATED + 10, UTC), "4.5.2 released", text, "")
    assert notes.modding_names(text) == {"old_trigger", "new_trigger"}
    now = _now(layers, game)
    (use,) = older.note_uses(layers, now, {"workshop:1": MOD_UPDATED}, [note])
    assert (use.name, use.path, use.note) == ("old_trigger", "events/a.txt", "4.5.2 released")
    # A mod updated after the note is left alone.
    assert older.note_uses(layers, now, {"workshop:1": MOD_UPDATED + 20}, [note]) == []


def test_kept_notes_are_read_back_newest_first(game: Game) -> None:
    first = Note(datetime(2026, 9, 22, tzinfo=UTC), "4.5 released", "Text\n\nmore\n", "u1")
    second = Note(datetime(2026, 10, 6, tzinfo=UTC), "4.5.2 released", "Fixes\n", "u2")
    assert notes.archive([first, second]) == 2
    assert notes.archive([second]) == 0
    assert notes.load_archive() == [second, first]


def test_workshop_update_times_come_from_steams_manifest(game: Game) -> None:
    manifest_path(game).parent.mkdir(parents=True)
    manifest_path(game).write_text(
        '"AppWorkshop" { "WorkshopItemsInstalled" { "123" { "timeupdated" "1758000000" } } }',
        "utf-8",
    )
    assert update_times(game) == {"workshop:123": 1758000000.0}


def test_a_reviewed_older_copy_is_not_analysed_again_until_a_copy_changes(game: Game) -> None:
    mods = {
        GAME: {"common/buildings/00_buildings.txt": "building_a = { cost = 1 upkeep = 2 }\n"},
        "workshop:1": {"common/buildings/zz_mod.txt": "building_a = { cost = 1 }\n"},
    }
    layers = _older_playset(game, mods)
    updated = {"workshop:1": MOD_UPDATED}
    (first,) = older.older_copies(layers, _now(layers, game), updated, {})
    assert first.new

    diffs: dict[str, str] = {}
    (again,) = older.older_copies(layers, _now(layers, game), updated, diffs, [first.ident])
    assert not again.new and again.diff == "" and diffs == {}

    # The mod changes its copy (without a Steam update): it's read again.
    _put(game.workshop_dir / "1", {"common/buildings/zz_mod.txt": "building_a = { cost = 5 }\n"})
    (changed,) = older.older_copies(layers, _now(layers, game), updated, diffs, [first.ident])
    assert changed.new and changed.diff in diffs


def test_accepting_a_check_marks_its_findings_as_reviewed(game: Game) -> None:
    layers = _older_playset(
        game,
        {
            GAME: {"common/buildings/00_buildings.txt": "building_a = { cost = 1 upkeep = 2 }\n"},
            "workshop:1": {
                "common/buildings/zz_mod.txt": "building_a = { cost = 1 }\n",
                "events/a.txt": "e = { trigger = { old_trigger = yes } }\n",
            },
        },
    )
    text = "Modding\n\n- Removed `old_trigger`\n"
    note = Note(datetime.fromtimestamp(MOD_UPDATED + 10, UTC), "4.5.2 released", text, "")
    updated = {"workshop:1": MOD_UPDATED}

    report = check.check(layers, game, None, [], None, updated, [note])
    assert [c.new for c in report.older] == [True]
    assert [u.new for u in report.note_uses] == [True]
    assert report.notes == [note]

    snapshot.accept(layers, game, "Mix", check.reviewed(report))
    report = check.check(layers, game, snapshot.load_baseline(), [], None, updated, [note])
    assert [c.new for c in report.older] == [False]
    assert [u.new for u in report.note_uses] == [False]
    assert not any(name.startswith("older__") for name in report.diffs)
    assert report.notes == []  # read already, with the copies they were matched to
    assert "0 new, 1 reviewed" in check.render(report)
