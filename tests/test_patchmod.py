from pathlib import Path

import pytest

from stellaris_patcher.coldsteel import files as cold_steel
from stellaris_patcher.coldsteel.records import Playset, PlaysetEntry, PlaysetFile
from stellaris_patcher.paradox.descriptor import Descriptor, decode_descriptor
from stellaris_patcher.paradox.game import DEFAULT_STEAM_DIRS, Game, GameNotFound, find_game
from stellaris_patcher.paradox.script import scan, value_of
from stellaris_patcher.patchmod import cold_steel_mix
from stellaris_patcher.patchmod.cold_steel_mix import (
    FixError,
    mirror_scale,
    repoint_slots,
    section_slots,
)
from stellaris_patcher.patchmod.layers import GAME, Layers, numbers
from stellaris_patcher.patchmod.write import (
    BOM,
    WriteError,
    check_files,
    supported_version,
    thumbnail,
    winning_name,
    with_mod_last,
    write_mod,
)


def _game(root: Path) -> Game:
    return Game(
        install_dir=root / "steam/steamapps/common/Stellaris",
        library_dir=root / "steam",
        version="v4.5.1",
        version_name="Cygnus v4.5.1",
        data_dir=root / "paradox",
    )


def _put(root: Path, files: dict[str, str]) -> None:
    for path, text in files.items():
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(text, "utf-8")


@pytest.fixture
def game(tmp_path: Path) -> Game:
    return _game(tmp_path)


def _layers(game: Game, mods: dict[str, dict[str, str]]) -> Layers:
    _put(game.install_dir, mods.pop(GAME, {}))
    for key, files in mods.items():
        _put(game.workshop_dir / key.removeprefix("workshop:"), files)
    entries = tuple(PlaysetEntry(k) for k in mods)
    return Layers.for_playset(Playset("p1", "Mix", entries), game)


# Layers


def test_a_later_mod_replaces_a_file_at_the_same_path_ignoring_case(game: Game) -> None:
    layers = _layers(
        game,
        {
            GAME: {"common/defines/00_defines.txt": "NCamera = { A = 1 }"},
            "workshop:1": {"common/defines/00_Defines.txt": "NCamera = { A = 2 }"},
        },
    )
    assert layers.winner("common/defines/00_defines.txt") == "workshop:1"
    assert list(layers.files("common/defines").values()) == [
        ("workshop:1", "common/defines/00_Defines.txt")
    ]


def test_the_define_in_the_file_sorting_last_wins(game: Game) -> None:
    layers = _layers(
        game,
        {
            GAME: {"common/defines/00_defines.txt": "NCamera = { A = { 1 2 } }"},
            "workshop:1": {"common/defines/zz_cc.txt": "NCamera = { A = { 3 4 5 } }"},
            "workshop:2": {"common/defines/aa.txt": "NCamera = { A = { 6 } }"},
        },
    )
    found = layers.define("NCamera", "A")
    assert found is not None
    assert found[0] == "workshop:1"
    assert numbers(found[1]) == [3, 4, 5]


def test_defined_gives_the_file_sorting_first(game: Game) -> None:
    layers = _layers(
        game,
        {
            GAME: {"common/scripted_triggers/b.txt": "t = { }"},
            "workshop:1": {"common/scripted_triggers/a.txt": "t = { }\nu = { }"},
        },
    )
    assert layers.defined("common/scripted_triggers") == {
        "t": ("workshop:1", "common/scripted_triggers/a.txt"),
        "u": ("workshop:1", "common/scripted_triggers/a.txt"),
    }


# Fix 1: mirror_scale


GAME_ASSET = b"""@size = 35
entity = { name = "storm_entity" scale = 20 }
entity = { name = "core_entity" }
entity = { name = "humanoid_01_stage_entity" pdxmesh = "m" }
entity = { name = "humanoid_01_phase_entity" scale = 1.0 }
entity = { name = "starlit_entity" scale = 4 attach = { "core" = "starlit_core_entity" } }
entity = { name = "starlit_core_entity" scale = 7 }
entity = { name = "toxoid_01_stage_entity" pdxmesh = "m" }
entity = { name = "toxoid_01_phase_entity" scale = 1.0 }
"""
MOD_ASSET = b"""@big = 120
entity = { name = "storm_entity" scale = @big }
entity = { name = "core_entity" }
entity = { name = "humanoid_01_stage_entity" scale = 6 }
entity = { name = "humanoid_01_phase_entity" scale = 1.0 }
"""


def _scales(data: bytes) -> dict[str, str | None]:
    found: dict[str, str | None] = {}
    for entry in scan(data):
        if entry.key == b"entity":
            name = value_of(data, entry, b"name")
            scale = value_of(data, entry, b"scale")
            assert name is not None
            found[name.decode()] = None if scale is None else scale.decode()
    return found


def test_mirror_scale_keeps_every_game_entity_at_the_mods_size() -> None:
    out, factor = mirror_scale(GAME_ASSET, MOD_ASSET)
    assert factor == 6
    assert out.startswith(b"@big = 120\n@size = 35\n")
    assert _scales(out) == {
        "storm_entity": "@big",  # the mod's own scale
        "core_entity": None,  # the mod left it alone
        "humanoid_01_stage_entity": "6",
        "humanoid_01_phase_entity": "1.0",
        "starlit_entity": "24",  # new: scaled by the same factor
        "starlit_core_entity": "7",  # new, but attached: left alone
        "toxoid_01_stage_entity": "6",  # follows humanoid_01's stage
        "toxoid_01_phase_entity": "1.0",  # follows humanoid_01's phase
    }


def test_mirror_scale_changes_a_variable_the_mod_changed() -> None:
    game = b'@s = 35\nentity = { name = "a" scale = @s }\nentity = { name = "b" scale = @s }\n'
    mod = b'@s = 140\nentity = { name = "a" scale = @s }\n'
    out, factor = mirror_scale(game, mod)
    assert factor == 4
    assert out == game.replace(b"@s = 35", b"@s = 140")


def test_mirror_scale_refuses_a_mod_that_scales_by_two_factors() -> None:
    game = b'entity = { name = "a" scale = 1 }\nentity = { name = "b" scale = 1 }\n'
    mod = b'entity = { name = "a" scale = 2 }\nentity = { name = "b" scale = 3 }\n'
    with pytest.raises(FixError, match="one factor"):
        mirror_scale(game, mod)


# Fix 2: repoint_slots


DESIGN = b"""ship_design = {
\tname = "NAME_Starlit"
\tsection = {
\t\ttemplate = "CITADEL"
\t\tcomponent = { slot = "MEDIUM_GUN_09" template = "G" }
\t\tcomponent = { slot = "MEDIUM_GUN_010" template = "G" }
\t\tcomponent = { slot = "MEDIUM_GUN_011" template = "G" }
\t\tcomponent = { slot = "LARGE_UTILITY_2" template = "A" }
\t}
}
"""


def test_slots_count_utility_slots_too(game: Game) -> None:
    section = (
        'ship_section_template = { key = "CITADEL"\n'
        '  component_slot = { name = "MEDIUM_GUN_10" }\n'
        "  large_utility_slots = 2 }"
    )
    layers = _layers(game, {"workshop:1": {"common/section_templates/!!!_x.txt": section}})
    assert section_slots(layers, "CITADEL") == {
        "MEDIUM_GUN_10",
        "LARGE_UTILITY_1",
        "LARGE_UTILITY_2",
    }


def test_repoint_slots_moves_leading_zero_slots_and_drops_the_rest() -> None:
    slots = {"MEDIUM_GUN_09", "MEDIUM_GUN_10", "LARGE_UTILITY_2"}
    out, _ = repoint_slots(DESIGN, "NAME_Starlit", "CITADEL", slots)
    assert b'slot = "MEDIUM_GUN_10"' in out
    assert b"MEDIUM_GUN_01" + b"0" not in out
    assert b"MEDIUM_GUN_011" not in out
    assert out.count(b"component") == 3


def test_repoint_slots_refuses_an_unknown_slot() -> None:
    with pytest.raises(FixError, match="LARGE_UTILITY_2"):
        repoint_slots(DESIGN, "NAME_Starlit", "CITADEL", {"MEDIUM_GUN_09", "MEDIUM_GUN_10"})


def test_repoint_slots_says_when_theres_nothing_to_fix() -> None:
    slots = {"MEDIUM_GUN_09", "MEDIUM_GUN_010", "MEDIUM_GUN_011", "LARGE_UTILITY_2"}
    with pytest.raises(FixError, match="Nothing to fix"):
        repoint_slots(DESIGN, "NAME_Starlit", "CITADEL", slots)


# Fix 4: zoom steps and planet scales


def _zoom_clash(game: Game, monkeypatch: pytest.MonkeyPatch, cc_extra: str = "") -> Layers:
    """System Scale's 3 zoom steps and planet scales, and Cinematic Camera's 5
    steps. Cinematic Camera enters systems at its last step, 4. Only fix 4
    runs: the others need files this doesn't have."""
    only_4 = tuple(f for f in cold_steel_mix.FIXES if f[0] == 4)
    monkeypatch.setattr(cold_steel_mix, "FIXES", only_4)
    return _layers(
        game,
        {
            cold_steel_mix.SYSTEM_SCALE: {
                "common/defines/systemscale_defines.txt": (
                    "NCamera = { ZOOM_STEPS_SYSTEM_PERCENTAGES = { 0.01 0.1 1.0 }\n"
                    "ENTER_SYSTEM_ZOOM_STEP = 2 }\n"
                    "NGraphics = { PLANET_SCALE_SYSTEM = { 1 2 4 } }\n"
                )
            },
            cold_steel_mix.CINEMATIC_CAMERA: {
                "common/defines/zzzzz_cc_defines.txt": (
                    "NCamera = { ZOOM_STEPS_SYSTEM_PERCENTAGES = { 0.01 0.03 0.1 0.3 1.0 }\n"
                    f"ENTER_SYSTEM_ZOOM_STEP = 4 {cc_extra} }}"
                )
            },
        },
    )


def test_fix_4_ships_system_scales_own_steps_and_scales(
    game: Game, monkeypatch: pytest.MonkeyPatch
) -> None:
    (outcome,) = cold_steel_mix.plan(_zoom_clash(game, monkeypatch))
    assert list(outcome.files) == ["common/defines/zzzzzz_stellaris_patcher_cold_steel_mix.txt"]
    (data,) = outcome.files.values()
    assert [e.key for e in scan(data)] == [b"NCamera", b"NGraphics"]
    assert b"ZOOM_STEPS_SYSTEM_PERCENTAGES = { 0.01 0.1 1 }" in data
    assert b"PLANET_SCALE_SYSTEM = { 1 2 4 }" in data


def test_fix_4_enters_systems_at_system_scales_step(
    game: Game, monkeypatch: pytest.MonkeyPatch
) -> None:
    (outcome,) = cold_steel_mix.plan(_zoom_clash(game, monkeypatch))
    (data,) = outcome.files.values()
    assert b"\tENTER_SYSTEM_ZOOM_STEP = 2\n" in data
    assert b"= 4" not in data


def test_fix_4_refuses_a_step_past_the_end(game: Game, monkeypatch: pytest.MonkeyPatch) -> None:
    layers = _zoom_clash(game, monkeypatch, cc_extra="ZOOM_STEPS_SHOW_FLEET_HEALTH_BARS = { 1 3 }")
    (outcome,) = cold_steel_mix.plan(layers)
    assert not outcome.files
    assert "ZOOM_STEPS_SHOW_FLEET_HEALTH_BARS names step { 1 3 }" in outcome.left_out


# Fix 6: More Events Mod's old name for Planetary Diversity's trigger

PD_TRIGGERS = "common/scripted_triggers/pd.txt"
PD_TRIGGER = "pd_is_planet_for_aqua_trait = { always = yes }\n"


def test_fix_6_calls_the_new_trigger_by_its_old_name(game: Game) -> None:
    layers = _layers(game, {cold_steel_mix.PLANETARY_DIVERSITY: {PD_TRIGGERS: PD_TRIGGER}})
    files, _ = cold_steel_mix.fix_pd_trigger(layers)
    (data,) = files.values()
    assert b"is_pd_planet_for_aqua_trait = {\n\tpd_is_planet_for_aqua_trait = yes\n}" in data
    assert check_files(files) == []


def test_fix_6_is_left_out_once_the_old_name_is_defined(game: Game) -> None:
    both = PD_TRIGGER + "is_pd_planet_for_aqua_trait = { always = yes }\n"
    layers = _layers(game, {cold_steel_mix.PLANETARY_DIVERSITY: {PD_TRIGGERS: both}})
    with pytest.raises(FixError, match="is defined now"):
        cold_steel_mix.fix_pd_trigger(layers)


# Writing


def test_winning_name_sorts_after_every_rival() -> None:
    assert winning_name(["zzzzz_cc_defines.txt", "00_defines.txt"], "x.txt", first=False) == (
        "zzzzzz_x.txt"
    )
    assert winning_name(["!!a.txt"], "x.txt", first=True) == "!!!_x.txt"


def test_the_thumbnail_is_a_512_pixel_png() -> None:
    data = thumbnail()
    assert data.startswith(b"\x89PNG\r\n\x1a\n")
    assert int.from_bytes(data[16:20]) == int.from_bytes(data[20:24]) == 512


def test_supported_version_is_major_and_minor() -> None:
    assert supported_version("v4.5.1") == "v4.5.*"


def test_check_files_finds_broken_files() -> None:
    problems = check_files(
        {
            "common/a.txt": b"a = { b = ",
            "common/ok.txt": b"a = { b = c }",
            "localisation/english/x_l_english.yml": b'l_english:\n k:0 "t"\n',
        }
    )
    assert len(problems) == 2
    assert problems[0].startswith("common/a.txt")
    assert "byte-order mark" in problems[1]


def test_write_mod_links_it_into_the_mod_folder(
    game: Game, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
    descriptor = Descriptor(name="Patch", version="1", supported_version="v4.5.*")
    folder = write_mod({"common/a.txt": b"a = b\n"}, "patch", "sp_patch", descriptor, game)
    assert folder == tmp_path / "data/stellaris-patcher/mods/patch"
    assert (folder / "common/a.txt").read_bytes() == b"a = b\n"
    link = game.mod_dir / "sp_patch"
    assert link.is_symlink() and link.readlink() == folder
    outer = decode_descriptor((game.mod_dir / "sp_patch.mod").read_bytes())
    assert outer.path == str(link)
    # A rebuild replaces the files whole.
    write_mod({"common/b.txt": b"b = c\n"}, "patch", "sp_patch", descriptor, game)
    assert not (folder / "common/a.txt").exists()
    assert (folder / "common/b.txt").exists()


def test_write_mod_keeps_the_workshop_id_after_an_upload(
    game: Game, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
    descriptor = Descriptor(name="Patch", version="1")
    folder = write_mod({}, "patch", "sp_patch", descriptor, game)
    outer = game.mod_dir / "sp_patch.mod"
    # The launcher writes the id into the .mod file after the first upload.
    outer.write_text(outer.read_text("utf-8") + 'remote_file_id="123"\n', "utf-8")
    write_mod({}, "patch", "sp_patch", descriptor, game)
    assert decode_descriptor(outer.read_bytes()).remote_file_id == "123"
    assert decode_descriptor((folder / "descriptor.mod").read_bytes()).remote_file_id == "123"


def test_write_mod_refuses_a_folder_that_isnt_ours(
    game: Game, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
    (game.mod_dir / "sp_patch").mkdir(parents=True)
    with pytest.raises(WriteError, match="in the way"):
        write_mod({}, "patch", "sp_patch", Descriptor(name="Patch"), game)
    assert not (tmp_path / "data").exists()


def test_with_mod_last_goes_before_cold_steels_patch() -> None:
    patch = PlaysetEntry(f"local:{cold_steel.PATCH_PREFIX}p1")
    book = PlaysetFile(
        playsets=[
            Playset("p1", "Mix", (PlaysetEntry("local:ours", False), PlaysetEntry("w:1"), patch)),
            Playset("p2", "Other", (PlaysetEntry("w:1"),)),
        ]
    )
    new = with_mod_last(book, "p1", "local:ours", "Ours")
    assert new.playsets[0].entries == (
        PlaysetEntry("w:1"),
        PlaysetEntry("local:ours", True, "Ours"),
        patch,
    )
    assert new.playsets[1] == book.playsets[1]
    assert with_mod_last(new, "p1", "local:ours", "Ours") == new


def test_the_workshop_description_lists_needed_mods_once_and_written_fixes() -> None:
    outcomes = [
        cold_steel_mix.Outcome(1, "Fix one", mods=("w:1", "w:2")),
        cold_steel_mix.Outcome(2, "Fix two", mods=("w:2",)),
        cold_steel_mix.Outcome(3, "Fix three", left_out="gone", mods=("w:3",)),
    ]
    # In load order, not the order the fixes name them.
    assert cold_steel_mix.patched_mods(outcomes, ["w:3", "w:2", "w:1"]) == ["w:2", "w:1"]
    text = cold_steel_mix.workshop_description(outcomes, {"w:2": "Two", "w:1": "One"}, "v4.5.1")
    assert "[*]Two\n[*]One\n" in text
    assert "[*]Fix one\n[*]Fix two\n" in text
    assert "Fix three" not in text
    waiting = text.partition("[h2]Known issues, waiting for the mod authors[/h2]")[2]
    assert all(f"[*]{problem}\n" in waiting for problem in cold_steel_mix.LEFT_TO_AUTHORS)
    off = waiting.partition("[h2]Mods taken out of the playset for now[/h2]")[2]
    assert all(f"[*]{mod}\n" in off for mod in cold_steel_mix.SWITCHED_OFF)


def test_the_workshop_description_has_no_taken_out_section_when_every_mod_is_on(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cold_steel_mix, "SWITCHED_OFF", ())
    text = cold_steel_mix.workshop_description([], {}, "v4.5.2")
    assert "taken out" not in text and text.endswith("[/list]\n")


def test_fix_10_ships_the_games_text_and_mends_the_tooltips(game: Game) -> None:
    pd = cold_steel_mix.PLANETARY_DIVERSITY
    game_text = 'l_english:\n mod_planet_bureaucrats_unity_produces_mult: "$a$ $b$"\n'
    game_text += ' bureaucrat_type_plural_with_icon: "[GetBureaucratSwapPluralWithIcon]"\n'
    old = "[GetAdministratorPluralWithIcon]"
    mod_text = f'l_english:\n mod_planet_bureaucrats_unity_produces_mult:1 "from {old}"\n'
    mod_text += f' pd_necro_planet_tooltip: "from {old}: +0.5" # a comment\n'
    layers = _layers(
        game,
        {
            GAME: {"localisation/english/economic_l_english.yml": game_text},
            pd: {"localisation/english/pd_l_english.yml": mod_text},
        },
    )
    files, _ = cold_steel_mix.fix_pd_bureaucrats(layers)
    assert files == {
        "localisation/replace/stellaris_patcher_cold_steel_mix_l_english.yml": BOM
        + b"l_english:\n"
        + b' mod_planet_bureaucrats_unity_produces_mult:0 "$a$ $b$"\n'
        + b' pd_necro_planet_tooltip:0 "from $bureaucrat_type_plural_with_icon$: +0.5"\n'
    }
    assert check_files(files) == []


def test_fix_10_is_left_out_when_nothing_calls_the_old_function(game: Game) -> None:
    text = 'l_english:\n bureaucrat_type_plural_with_icon: "x"\n pd_necro_planet_tooltip: "y"\n'
    layers = _layers(game, {GAME: {"localisation/english/a_l_english.yml": text}})
    with pytest.raises(FixError, match="No text calls"):
        cold_steel_mix.fix_pd_bureaucrats(layers)


# Fixes 11 and 12: More Events Mod's events

ZIASKEHORN = """namespace = mem_scfe_ziaskehorn\r
ship_event = {\r
\tid = mem_scfe_ziaskehorn.1\r
\timmediate = {\r
\t\trandom_list = {\r
\t\t\t10 = {\r
\t\t\t\tship_event = {\r
\t\t\t\t\tid = mem_scfe_ziaskehorn.2\r
\t\t\t\t}\r
\t\t\t\tset_global_flag = discovered_ziaskehorn\r
\t\t\t\tfrom = {\r
\t\t\t\t\tsave_event_target_as = mem_ziaskehorn_planet\r
\t\t\t\t}\r
\t\t\t}\r
\t\t}\r
\t}\r
}\r
ship_event = {\r
\tid = mem_scfe_ziaskehorn.2\r
\tlocation = event_target:mem_ziaskehorn_planet\r
}\r
"""


def test_fix_11_saves_the_planet_before_firing_the_discovery(game: Game) -> None:
    mem = cold_steel_mix.MORE_EVENTS
    layers = _layers(game, {mem: {"events/mem_asp_scfe_events.txt": ZIASKEHORN}})
    files, notes = cold_steel_mix.fix_ziaskehorn(layers)
    (path,) = files
    assert path == "events/!!_stellaris_patcher_cold_steel_mix_ziaskehorn.txt"
    data = files[path]
    assert data.startswith(b"namespace = mem_scfe_ziaskehorn\n\nship_event = {\n")
    assert b"\r" not in data
    saved = data.index(b"save_event_target_as")
    assert saved < data.index(b"id = mem_scfe_ziaskehorn.2") < data.index(b"set_global_flag")
    assert b"mem_scfe_ziaskehorn.2" in data and data.count(b"ship_event = {\n\tid") == 1
    assert notes == [
        "mem_scfe_ziaskehorn.1: saves mem_ziaskehorn_planet before firing mem_scfe_ziaskehorn.2"
    ]
    assert check_files(files) == []


def test_fix_11_is_left_out_once_the_mod_saves_first(game: Game) -> None:
    fixed, _ = cold_steel_mix.fix_ziaskehorn(
        _layers(game, {cold_steel_mix.MORE_EVENTS: {"events/a.txt": ZIASKEHORN}})
    )
    (data,) = fixed.values()
    again = data.decode() + "ship_event = { id = mem_scfe_ziaskehorn.2 }\n"
    layers = _layers(game, {"workshop:2": {"events/b.txt": again}})
    with pytest.raises(FixError, match="comes from workshop:2"):
        cold_steel_mix.fix_ziaskehorn(layers)
    layers = _layers(game, {cold_steel_mix.MORE_EVENTS: {"events/a.txt": again}})
    with pytest.raises(FixError, match="saves its targets before firing"):
        cold_steel_mix.fix_ziaskehorn(layers)


TRAITS = """leader_trait_iron_fist = {\n\tleader_class = { commander } # 4.5\n}
leader_trait_maniacal = {\n\tleader_class = { scientist }\n}
"""
GLACIER = """namespace = mem_stuck_in_glacier
ship_event = {
\tid = mem_stuck_in_glacier.22
\toption = {
\t\tcreate_leader = { class = scientist traits = { trait = leader_trait_maniacal } }
\t\tcreate_leader = {
\t\t\tCLASS = official
\t\t\ttraits = { trait = leader_trait_iron_fist }
\t\t}
\t}
}
"""


def test_fix_12_gives_the_leader_the_class_its_trait_needs(game: Game) -> None:
    layers = _layers(
        game,
        {
            GAME: {"common/traits/00_governor_traits.txt": TRAITS},
            cold_steel_mix.MORE_EVENTS: {"events/mem_stuck_in_glacier.txt": GLACIER},
        },
    )
    files, notes = cold_steel_mix.fix_glacier_leader(layers)
    (data,) = files.values()
    assert b"CLASS = commander\n" in data and b"official" not in data
    assert b"class = scientist" in data
    assert notes == [
        "mem_stuck_in_glacier.22: the official with leader_trait_iron_fist is a commander now"
    ]
    assert check_files(files) == []


def test_fix_12_is_left_out_when_every_leader_can_have_its_traits(game: Game) -> None:
    traits = TRAITS.replace("{ commander }", "{ commander official }")
    layers = _layers(
        game,
        {
            GAME: {"common/traits/00_governor_traits.txt": traits},
            cold_steel_mix.MORE_EVENTS: {"events/mem_stuck_in_glacier.txt": GLACIER},
        },
    )
    with pytest.raises(FixError, match="can have its traits now"):
        cold_steel_mix.fix_glacier_leader(layers)


# Fix 15: More Events Mod's old shield upkeep names

SHIELDS = "common/component_templates/mem_lex_utilities.txt"
SHIELD = "mem_SHIELD = { upkeep = { energy = @shield_l_t7_upkeep_energy } }\n# @shield_x_upkeep_y\n"
UPKEEP = "@defense_l_t7_upkeep_energy = 1.52\n"


def test_fix_15_defines_the_old_names_with_the_games_values(game: Game) -> None:
    layers = _layers(
        game,
        {
            GAME: {"common/scripted_variables/02_cost.txt": UPKEEP},
            cold_steel_mix.MORE_EVENTS: {SHIELDS: SHIELD},
        },
    )
    files, notes = cold_steel_mix.fix_shield_upkeep(layers)
    (data,) = files.values()
    assert data.endswith(b"@shield_l_t7_upkeep_energy = 1.52\n")
    assert b"shield_x" not in data
    assert notes == ["1 names: @shield_l_t7_upkeep_energy"]
    assert check_files(files) == []


def test_fix_15_is_left_out_once_the_old_names_are_defined(game: Game) -> None:
    old = "@shield_l_t7_upkeep_energy = 1\n"
    layers = _layers(
        game,
        {
            GAME: {"common/scripted_variables/02_cost.txt": UPKEEP + old},
            cold_steel_mix.MORE_EVENTS: {SHIELDS: SHIELD},
        },
    )
    with pytest.raises(FixError, match="No component uses"):
        cold_steel_mix.fix_shield_upkeep(layers)


# Fix 16: Ships in Scaling's mutation weapon ranges

CSV_HEAD = "# a comment;;\r\nkey;cost;range;end\r\n"
GAME_CSV = CSV_HEAD + "MEGA_L;44;100;\r\nGIGA_L;57;100;\r\nGIGA_XL;99;100;\r\nMEGA_S;11;60;\r\n"


def test_fix_16_sets_a_missed_range_as_the_mod_scales_the_rest(game: Game) -> None:
    scaled = CSV_HEAD + "MEGA_L;44;2;\r\nGIGA_L;57;17;\r\nGIGA_XL;99;17;\r\nMEGA_S;11;10;\r\n"
    path = cold_steel_mix.MUTATION_WEAPONS
    layers = _layers(
        game, {GAME: {path: GAME_CSV}, cold_steel_mix.SHIPS_IN_SCALING: {path: scaled}}
    )
    files, notes = cold_steel_mix.fix_mutation_ranges(layers)
    assert files == {path: scaled.replace("MEGA_L;44;2;", "MEGA_L;44;17;").encode()}
    assert notes == ["MEGA_L: range 2 → 17, as for the game's 100"]


def test_fix_16_is_left_out_once_every_range_follows_the_mods_scaling(game: Game) -> None:
    scaled = CSV_HEAD + "MEGA_L;44;17;\r\nGIGA_L;57;17;\r\nGIGA_XL;99;17;\r\nMEGA_S;11;10;\r\n"
    path = cold_steel_mix.MUTATION_WEAPONS
    layers = _layers(
        game, {GAME: {path: GAME_CSV}, cold_steel_mix.SHIPS_IN_SCALING: {path: scaled}}
    )
    with pytest.raises(FixError, match="follows its own scaling"):
        cold_steel_mix.fix_mutation_ranges(layers)


# Fix 17: Real Space's sealed Surveillance Supercomputer system

SPECIAL = "common/solar_system_initializers/special_system_initializers.txt"
SUPERCOMPUTER = """other_system = { }
surveillance_supercomputer_system = {
\tflags = { surveillance_supercomputer_system hostile_system FLAGS ancient_wonders_system }
\tplanet = { orbit_distance = @base_moon_distance }
}
"""


def test_fix_17_copies_the_system_without_the_seal_into_a_file_sorting_first(game: Game) -> None:
    layers = _layers(
        game,
        {
            GAME: {
                SPECIAL: SUPERCOMPUTER.replace("FLAGS", "crisis_spawn_exclude"),
                "common/scripted_variables/00_scripted_variables.txt": "@base_moon_distance = 10",
            },
            cold_steel_mix.REAL_SPACE: {
                SPECIAL: SUPERCOMPUTER.replace("FLAGS", "crisis_spawn_exclude sealed_system")
            },
        },
    )
    files, _ = cold_steel_mix.fix_supercomputer_seal(layers)
    (path,) = files
    assert path == (
        "common/solar_system_initializers/!!_stellaris_patcher_cold_steel_mix_supercomputer.txt"
    )
    data = files[path]
    assert b"sealed_system" not in data.partition(b"\n")[2]
    assert b"crisis_spawn_exclude ancient_wonders_system }" in data
    assert b"other_system" not in data
    assert check_files(files) == []


def test_fix_17_is_left_out_once_real_space_drops_the_seal(game: Game) -> None:
    unsealed = SUPERCOMPUTER.replace("FLAGS", "crisis_spawn_exclude")
    layers = _layers(
        game, {GAME: {SPECIAL: unsealed}, cold_steel_mix.REAL_SPACE: {SPECIAL: unsealed}}
    )
    with pytest.raises(FixError, match="isn't sealed now"):
        cold_steel_mix.fix_supercomputer_seal(layers)


# Fix 19: Ascension Worlds' trait and terraforming rule

SPECIES_TRAITS = "common/traits/04_species_traits.txt"
BUDDING = """trait_lithoid_budding = {\r
\ttriggered_planet_pop_group_modifier_for_species = {\r
\t\tpotential = { NOT = { has_deposit = d_lithoid_crater } }\r
\t\tDIVIDE\r
\t\tbonus_pop_growth = @budding_rate\r
\t}\r
\ttriggered_planet_pop_group_modifier_for_species = {\r
\t\tpotential = { has_deposit = d_lithoid_crater }\r
\t\tDIVIDE\r
\t\tbonus_pop_growth = 0.03\r
\t}\r
}\r
"""
RULES = "common/game_rules/00_rules.txt"
TERRAFORM = """can_terraform_planet = {
\tcustom_tooltip = { fail_text = terraform_fail_consecrated NOT = { has_modifier = c } }
LEGENDARY\tcustom_tooltip = { fail_text = "legendary_leader_planet_no_terraform" always = no }
\tcustom_tooltip = { fail_text = metal NOT = { owner? = { is_ai = no } } }
}
"""


def _ascension_worlds(game: Game, budding: str, rule: str) -> Layers:
    return _layers(
        game,
        {
            GAME: {
                SPECIES_TRAITS: BUDDING.replace("DIVIDE", "divide_over_pop_groups = no"),
                RULES: TERRAFORM.replace("LEGENDARY", ""),
                "common/scripted_variables/00_vars.txt": "@budding_rate = 0.02\n",
            },
            cold_steel_mix.ASCENSION_WORLDS: {
                SPECIES_TRAITS: budding,
                "common/game_rules/pd_terraformrulesreplace.txt": rule,
            },
        },
    )


def test_fix_19_adds_the_games_lines_but_keeps_the_mods_own_choice(game: Game) -> None:
    budding = BUDDING.replace("DIVIDE", "divide_over_pop_groups = no", 1).replace("DIVIDE", "")
    lines = TERRAFORM.replace("LEGENDARY\tcustom", "\t# custom").splitlines(keepends=True)
    rule = "".join(line for line in lines if "consecrated" not in line)
    files, notes = cold_steel_mix.fix_ascension_worlds(_ascension_worlds(game, budding, rule))
    trait = files["common/traits/!!_stellaris_patcher_cold_steel_mix_ascension_worlds.txt"]
    assert trait.count(b"divide_over_pop_groups = no") == 2 and b"\r" not in trait
    terraform = files["common/game_rules/zz_stellaris_patcher_cold_steel_mix_terraform.txt"]
    assert b"fail_text = terraform_fail_consecrated NOT = { has_modifier = c }" in terraform
    assert b"\t# custom_tooltip" in terraform  # still commented out
    assert notes == [
        "trait_lithoid_budding: 1 pop modifier gets the game's divide_over_pop_groups",
        "can_terraform_planet: adds terraform_fail_consecrated; keeps out "
        "legendary_leader_planet_no_terraform, as Ascension Worlds chose",
    ]
    assert check_files(files) == []


def test_fix_19_is_left_out_once_the_mods_copies_have_the_games_lines(game: Game) -> None:
    budding = BUDDING.replace("DIVIDE", "divide_over_pop_groups = no")
    rule = TERRAFORM.replace("LEGENDARY\tcustom", "\t# custom")
    with pytest.raises(FixError, match="match the game's now"):
        cold_steel_mix.fix_ascension_worlds(_ascension_worlds(game, budding, rule))


# Mods out of the playset


def test_a_fix_is_left_out_while_its_mods_are_out_of_the_playset(
    game: Game, monkeypatch: pytest.MonkeyPatch
) -> None:
    made: cold_steel_mix.Made = ({"a.txt": b"a"}, [])
    real_space, starbase = cold_steel_mix.REAL_SPACE, cold_steel_mix.STARBASE_EXTENDED
    fixes = (
        (3, "Three", lambda _: made, (starbase,)),
        (7, "Seven", lambda _: made, (real_space, starbase)),
    )
    monkeypatch.setattr(cold_steel_mix, "FIXES", fixes)
    three, seven = cold_steel_mix.plan(_layers(game, {real_space: {"a.txt": "a"}}))
    assert three.left_out == f"The playset has none of its mods now: {starbase}."
    assert seven.files == {"a.txt": b"a"}  # one of its mods is enough


def test_own_keys_include_the_workshop_copy_once_uploaded(
    game: Game, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
    assert cold_steel_mix.own_keys(game) == [cold_steel_mix.KEY]
    descriptor = Descriptor(name="Patch", remote_file_id="123")
    write_mod({}, cold_steel_mix.FOLDER, cold_steel_mix.LINK, descriptor, game)
    assert cold_steel_mix.own_keys(game) == [cold_steel_mix.KEY, "workshop:123"]


# The real playset


@pytest.mark.real_install
def test_every_fix_with_a_mod_in_the_real_cold_steel_mix_applies() -> None:
    try:
        game = find_game(DEFAULT_STEAM_DIRS)
    except GameNotFound:
        pytest.skip("Stellaris isn't installed here.")
    book = cold_steel.load_playsets()
    found = [p for p in book.playsets if p.name == cold_steel_mix.PLAYSET] if book else []
    if len(found) != 1:
        pytest.skip("Cold Steel has no Cold Steel Mix playset here.")
    layers = Layers.for_playset(found[0], game, skip=cold_steel_mix.own_keys(game))
    outcomes = cold_steel_mix.plan(layers)
    gone = "The playset has none of its mods now"
    assert [o.left_out for o in outcomes if o.left_out and not o.left_out.startswith(gone)] == []
    files = {p: d for o in outcomes for p, d in o.files.items()}
    assert check_files(files) == []
    order = [layer.key for layer in layers.layers]
    names = [layers.name(k) for k in cold_steel_mix.patched_mods(outcomes, order)]
    assert "Real Space - System Scale" in names
    assert all(d.startswith(BOM) for p, d in files.items() if p.endswith(".yml"))
