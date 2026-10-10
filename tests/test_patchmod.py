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


def test_the_workshop_description_lists_needed_mods_once_and_written_fixes_by_group(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cold_steel_mix, "LEFT_TO_AUTHORS", ("A mod's own bug",))
    monkeypatch.setattr(cold_steel_mix, "FIX_GROUPS", (("Ships", (2, 3)), ("Empty", (4,))))
    outcomes = [
        cold_steel_mix.Outcome(1, "Fix one", mods=("w:1", "w:2")),
        cold_steel_mix.Outcome(2, "Fix two", mods=("w:2",)),
        cold_steel_mix.Outcome(3, "Fix three", left_out="gone", mods=("w:3",)),
    ]
    # In load order, not the order the fixes name them.
    assert cold_steel_mix.patched_mods(outcomes, ["w:3", "w:2", "w:1"]) == ["w:2", "w:1"]
    text = cold_steel_mix.workshop_description(outcomes, {"w:2": "Two", "w:1": "One"}, "v4.5.1")
    assert "[*]Two\n[*]One\n" in text
    # Grouped in FIX_GROUPS' order, with a fix in no group last, under "Other".
    assert (
        "[h2]What it fixes[/h2]\n"
        "[h3]Ships[/h3]\n[list]\n[*]Fix two\n[/list]\n"
        "[h3]Other[/h3]\n[list]\n[*]Fix one\n[/list]\n"
    ) in text
    assert "Fix three" not in text and "Empty" not in text
    waiting = text.partition("[h2]Known issues, waiting for the mod authors[/h2]")[2]
    assert "[*]A mod's own bug\n" in waiting


def test_each_fix_is_in_one_workshop_group() -> None:
    grouped = [n for _, members in cold_steel_mix.FIX_GROUPS for n in members]
    assert sorted(grouped) == sorted(f[0] for f in cold_steel_mix.FIXES)


def test_the_workshop_description_has_no_known_issues_section_when_none_are_left(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cold_steel_mix, "LEFT_TO_AUTHORS", ())
    text = cold_steel_mix.workshop_description([], {}, "v4.5.2")
    assert "Known issues" not in text and text.endswith("[h2]What it fixes[/h2]\n")


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


# Fix 18: trait resources filed under planet_pops

CATEGORIES = {
    "common/economic_categories/02_pop.txt": "planet_pops_traits = { parent = planet_pops }\n"
}
TRAIT = """trait_NAME = {\r
\tresources = {\r
\t\tcategory = CATEGORY\r
\t\tupkeep = { food = @food }\r
\t}\r
}\r
"""
TRAITS_COPY = "common/traits/!!_stellaris_patcher_cold_steel_mix_trait_categories.txt"


def _trait(name: str, category: str = "planet_pops") -> str:
    return TRAIT.replace("NAME", name).replace("CATEGORY", category)


def test_fix_18_files_each_traits_resources_under_planet_pops_traits(game: Game) -> None:
    layers = _layers(
        game,
        {
            GAME: CATEGORIES,
            cold_steel_mix.PLANETARY_DIVERSITY: {
                "common/traits/02_basic.txt": "@food = 1\n"
                + _trait("organic")
                + _trait("done", "planet_pops_traits"),
            },
            cold_steel_mix.MORE_EVENTS: {
                "common/traits/mem_grudge.txt": "@food = 1\n" + _trait("grudge"),
            },
        },
    )
    files, notes = cold_steel_mix.fix_trait_categories(layers)
    text = files[TRAITS_COPY]
    assert text.startswith(b"@food = 1\n\ntrait_organic = {")
    assert text.count(b"category = planet_pops_traits") == 2 and b"trait_done" not in text
    assert b"trait_grudge" in text and b"\r" not in text
    assert notes == [
        "2 traits (1 from Planetary Diversity, 1 from More Events Mod) use planet_pops_traits"
    ]
    assert check_files(files) == []


def test_fix_18_skips_a_trait_whose_variable_clashes(game: Game) -> None:
    layers = _layers(
        game,
        {
            GAME: CATEGORIES,
            cold_steel_mix.PLANETARY_DIVERSITY: {
                "common/traits/02_basic.txt": "@food = 1\n" + _trait("organic"),
                "common/traits/03_more.txt": "@food = 2\n" + _trait("lithoid"),
            },
        },
    )
    files, notes = cold_steel_mix.fix_trait_categories(layers)
    assert b"trait_lithoid" not in files[TRAITS_COPY]
    assert notes[1] == "trait_lithoid uses a variable another trait defines differently. Skipped."


def test_fix_18_is_left_out_once_every_trait_uses_planet_pops_traits(game: Game) -> None:
    traits = "@food = 1\n" + _trait("organic", "planet_pops_traits")
    pd = {"common/traits/a.txt": traits}
    layers = _layers(game, {GAME: CATEGORIES, cold_steel_mix.PLANETARY_DIVERSITY: pd})
    with pytest.raises(FixError, match="under planet_pops now"):
        cold_steel_mix.fix_trait_categories(layers)


def test_fix_18_is_left_out_if_the_game_drops_planet_pops_traits(game: Game) -> None:
    layers = _layers(
        game, {cold_steel_mix.PLANETARY_DIVERSITY: {"common/traits/a.txt": _trait("organic")}}
    )
    with pytest.raises(FixError, match="no planet_pops_traits category"):
        cold_steel_mix.fix_trait_categories(layers)


# Fix 19: Lithoid Budding, and Ascension Worlds' terraforming rule

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


LITHOID_BUDDING = "common/traits/!!_stellaris_patcher_cold_steel_mix_lithoid_budding.txt"
GAME_BUDDING = {
    SPECIES_TRAITS: BUDDING.replace("DIVIDE", "divide_over_pop_groups = no"),
    RULES: TERRAFORM.replace("LEGENDARY", ""),
    "common/scripted_variables/00_vars.txt": "@budding_rate = 0.02\n",
}


def _ascension_worlds(game: Game, budding: str, rule: str) -> Layers:
    return _layers(
        game,
        {
            GAME: GAME_BUDDING,
            cold_steel_mix.PLANETARY_DIVERSITY: {SPECIES_TRAITS: BUDDING.replace("DIVIDE", "")},
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
    trait = files[LITHOID_BUDDING]
    assert trait.count(b"divide_over_pop_groups = no") == 2 and b"\r" not in trait
    terraform = files["common/game_rules/zz_stellaris_patcher_cold_steel_mix_terraform.txt"]
    assert b"fail_text = terraform_fail_consecrated NOT = { has_modifier = c }" in terraform
    assert b"\t# custom_tooltip" in terraform  # still commented out
    assert notes == [
        "trait_lithoid_budding, from Ascension Worlds: 1 pop modifier gets the game's "
        "divide_over_pop_groups",
        "can_terraform_planet: adds terraform_fail_consecrated; keeps out "
        "legendary_leader_planet_no_terraform, as Ascension Worlds chose",
    ]
    assert check_files(files) == []


def test_fix_19_mends_planetary_diversitys_budding_while_ascension_worlds_is_off(
    game: Game,
) -> None:
    budding = BUDDING.replace("DIVIDE", "divide_over_pop_groups = no", 1).replace("DIVIDE", "")
    layers = _layers(
        game, {GAME: GAME_BUDDING, cold_steel_mix.PLANETARY_DIVERSITY: {SPECIES_TRAITS: budding}}
    )
    files, notes = cold_steel_mix.fix_ascension_worlds(layers)
    assert list(files) == [LITHOID_BUDDING]
    assert files[LITHOID_BUDDING].count(b"divide_over_pop_groups = no") == 2
    assert notes == [
        "trait_lithoid_budding, from Planetary Diversity: 1 pop modifier gets the game's "
        "divide_over_pop_groups",
        "can_terraform_planet doesn't come from Ascension Worlds now. Skipped.",
    ]
    assert check_files(files) == []


def test_fix_19_is_left_out_once_the_mods_copies_have_the_games_lines(game: Game) -> None:
    budding = BUDDING.replace("DIVIDE", "divide_over_pop_groups = no")
    rule = TERRAFORM.replace("LEGENDARY\tcustom", "\t# custom")
    with pytest.raises(FixError, match="match the game's now"):
        cold_steel_mix.fix_ascension_worlds(_ascension_worlds(game, budding, rule))


# Fix 25: broken lines in Planetary Diversity's translations

PD_GERMAN = "localisation/german/pd_l_german.yml"
ARCOLOGIES_GERMAN = "localisation/german/arcs_l_german.yml"
ARCOLOGIES_ENGLISH = '﻿l_english:\n drone: "Drone"\n drone_desc: "Drones."\n drone_add: "+1"\n'


def test_fix_25_mends_each_broken_line_and_keeps_the_rest(game: Game) -> None:
    pd_german = (
        "﻿l_german:\r\n"
        " # a comment\r\n"
        ' factory: "Fabrik"\r\n'
        ' foundry: Giesserei"\r\n'
        ' obsidian_desc: " obsidian_desc: "A humid world."\r\n'
        '"\r\n'
        ' ethane: "Ethan Ozeanwelt\r\n'
    )
    arcologies_german = 'l_german:\ndrone: "Drohne"\nDrohnen."\ndrone_add: "+1"\n'
    layers = _layers(
        game,
        {
            cold_steel_mix.PLANETARY_DIVERSITY: {PD_GERMAN: pd_german},
            cold_steel_mix.MORE_ARCOLOGIES: {
                ARCOLOGIES_GERMAN: "﻿" + arcologies_german,
                "localisation/english/arcs_l_english.yml": ARCOLOGIES_ENGLISH,
            },
        },
    )
    files, notes = cold_steel_mix.fix_broken_text(layers)
    assert files == {
        PD_GERMAN: BOM
        + (
            b"l_german:\r\n"
            b" # a comment\r\n"
            b' factory: "Fabrik"\r\n'
            b' foundry: "Giesserei"\r\n'
            b' obsidian_desc: "A humid world."\r\n'
            b' ethane: "Ethan Ozeanwelt"\r\n'
        ),
        ARCOLOGIES_GERMAN: BOM
        + b'l_german:\ndrone: "Drohne"\ndrone_desc: "Drohnen."\ndrone_add: "+1"\n',
    }
    assert notes == [
        f"{PD_GERMAN}: line 4: foundry's opening quote added",
        f"{PD_GERMAN}: line 5: obsidian_desc's text no longer starts with its own key",
        f"{PD_GERMAN}: line 6: a stray quote taken out",
        f"{PD_GERMAN}: line 7: ethane's closing quote added",
        f"{ARCOLOGIES_GERMAN}: line 3: the text gets its key, drone_desc, from the English file",
    ]
    assert check_files(files) == []


def test_fix_25_is_left_out_once_every_line_reads(game: Game) -> None:
    layers = _layers(
        game,
        {
            cold_steel_mix.PLANETARY_DIVERSITY: {PD_GERMAN: 'l_german:\n a:0 "A" # fine\n'},
            cold_steel_mix.MORE_ARCOLOGIES: {
                "localisation/english/arcs_l_english.yml": ARCOLOGIES_ENGLISH,
            },
        },
    )
    with pytest.raises(FixError, match="every line"):
        cold_steel_mix.fix_broken_text(layers)


def test_fix_25_skips_a_file_with_a_line_no_rule_mends(game: Game) -> None:
    polish = "localisation/polish/pd_l_polish.yml"
    texts = {PD_GERMAN: 'l_german:\n a: "A"\nkeyless text\n', polish: 'l_polish:\n a: "A\n'}
    layers = _layers(game, {cold_steel_mix.PLANETARY_DIVERSITY: texts})
    files, notes = cold_steel_mix.fix_broken_text(layers)
    assert list(files) == [polish]
    assert notes == [
        f"{PD_GERMAN}: Line 3 has no key, and the English text doesn't say which. Skipped.",
        f"{polish}: line 2: a's closing quote added",
    ]


def test_fix_25_mends_ascension_worlds_from_its_own_english_file(game: Game) -> None:
    french = "localisation/french/aw_l_french.yml"
    english = 'l_english:\n ap_flooded: "Flooded"\n ap_flooded_tooltip: "Water."\n'
    texts = {
        "localisation/english/aw_l_english.yml": english,
        french: 'l_french:\n ap_flooded: "Inondé"\n "Eau."\n',
    }
    layers = _layers(game, {cold_steel_mix.ASCENSION_WORLDS: texts})
    files, notes = cold_steel_mix.fix_broken_text(layers)
    assert files == {
        french: 'l_french:\n ap_flooded: "Inondé"\n ap_flooded_tooltip: "Eau."\n'.encode()
    }
    assert notes == [
        f"{french}: line 3: the text gets its key, ap_flooded_tooltip, from the English file"
    ]


# Fix 26: More Events Mod's Under the Blanket story

NORMAL_TRAIT_RULE = {
    "common/game_rules/00_rules.txt": (
        "can_leader_get_normal_trait = {\n\tcan_leader_get_normal_trait_trigger = yes\n}\n"
    ),
    "common/scripted_triggers/03_paragon.txt": (
        "can_leader_get_normal_trait_trigger = { NOT = { is_heir = yes } }\n"
    ),
}
BLANKET = """namespace = mem_under_blanket\r
carrier_event = {\r
\tid = mem_under_blanket.1\r
\ttrigger = {\r
\t\tRoot.Owner = { NOT = { is_homicidal = yes } }\r
\t}\r
}\r
carrier_event = {\r
\tid = mem_under_blanket.2\r
\timmediate = {\r
\t\tIF = {\r
\t\t\tlimit = { Root.Owner = { any_owned_leader = { leader_class = scientist } } }\r
\t\t\tRoot.Owner = {\r
\t\t\t\trandom_owned_leader = {\r
\t\t\t\t\tlimit = {\r
\t\t\t\t\t\tleader_class = scientist\r
\t\t\t\t\t}\r
\t\t\t\t\tsave_event_target_as = mem_under_blanket_expert_leader\r
\t\t\t\t}\r
\t\t\t}\r
\t\t}\r
\t}\r
\toption = {\r
\t\tRoot.Owner = { random_owned_leader = { limit = { leader_class = scientist } } }\r
\t}\r
}\r
"""


def test_fix_26_picks_leaders_who_can_take_traits_for_normal_empires_only(
    game: Game,
) -> None:
    mem = cold_steel_mix.MORE_EVENTS
    layers = _layers(
        game, {GAME: dict(NORMAL_TRAIT_RULE), mem: {"events/mem_under_blanket.txt": BLANKET}}
    )
    files, notes = cold_steel_mix.fix_under_blanket(layers)
    (path,) = files
    assert path == "events/!!_stellaris_patcher_cold_steel_mix_under_blanket.txt"
    data = files[path]
    assert data.startswith(b"namespace = mem_under_blanket\n\ncarrier_event = {\n")
    assert b"\r" not in data and data.count(b"namespace") == 1
    assert b"\t\tRoot.Owner = { is_country_type = default }\n" in data
    # Both picks in the immediate block, the one on its own line indented like it.
    assert (
        b"any_owned_leader = { leader_class = scientist can_leader_get_normal_trait_trigger" in data
    )
    assert b"\t\t\t\t\t\tleader_class = scientist\n\t\t\t\t\t\tcan_leader_get_normal_trait" in data
    assert data.count(b"can_leader_get_normal_trait_trigger") == 2  # the option is left alone
    assert notes == [
        "mem_under_blanket.1: starts only for normal empires",
        "mem_under_blanket.2: 2 scientist picks leave out an autocracy's ruler and heir, "
        "who can't take normal traits (can_leader_get_normal_trait)",
    ]
    assert check_files(files) == []


def test_fix_26_is_left_out_once_the_mod_checks_both(game: Game) -> None:
    mem = cold_steel_mix.MORE_EVENTS
    checked = BLANKET.replace(
        "is_homicidal = yes } }", "is_homicidal = yes } is_country_type = default }"
    )
    checked = checked.replace(
        "leader_class = scientist",
        "leader_class = scientist can_leader_get_normal_trait_trigger = yes",
    )
    layers = _layers(
        game, {GAME: dict(NORMAL_TRAIT_RULE), mem: {"events/mem_under_blanket.txt": checked}}
    )
    with pytest.raises(FixError, match="starts only for normal empires, and picks"):
        cold_steel_mix.fix_under_blanket(layers)


def test_fix_26_skips_the_picks_once_the_game_rule_changes(game: Game) -> None:
    rule = {
        **NORMAL_TRAIT_RULE,
        "common/game_rules/00_rules.txt": "can_leader_get_normal_trait = { always = yes }\n",
    }
    layers = _layers(
        game,
        {GAME: rule, cold_steel_mix.MORE_EVENTS: {"events/mem_under_blanket.txt": BLANKET}},
    )
    files, notes = cold_steel_mix.fix_under_blanket(layers)
    (data,) = files.values()
    assert b"is_country_type = default" in data and b"mem_under_blanket.2" not in data
    assert notes[1] == (
        "The game rule can_leader_get_normal_trait doesn't call "
        "can_leader_get_normal_trait_trigger now. Skipped."
    )


# Fix 27: Planetary Diversity's Aquatic trait and the game's AI weight

BASIC_TRAITS = "common/traits/02_species_traits_basic_characteristics.txt"
AQUATIC = """trait_aquatic = {\r
\tcost = 2\r
\tinline_script = "traits/pd_aquatic_allowed_planet_classes"\r
\tai_weight = {\r
\t\tweight = 1\r
\t\tmodifier = {\r
\t\t\tfactor = 0\r
\t\t\tNOT = { has_trait = trait_pc_ocean_preference }\r
\t\t}\r
\t}\r
}\r
"""
GAME_AQUATIC = """trait_aquatic = {
\tcost = 2
\tai_weight = {
\t\tweight = 1
\t\tmodifier = {
\t\t\tfactor = 0
\t\t\tNOR = {
\t\t\t\thas_trait = trait_pc_ocean_preference
\t\t\t\thas_trait = trait_cyborg_climate_adjustment_wet
\t\t\t}
\t\t}
\t}
}
"""
AQUATIC_COPY = "common/traits/!!_stellaris_patcher_cold_steel_mix_aquatic.txt"


def _aquatic(game: Game, aquatic: str) -> Layers:
    return _layers(
        game,
        {
            GAME: {BASIC_TRAITS: GAME_AQUATIC},
            cold_steel_mix.PLANETARY_DIVERSITY: {BASIC_TRAITS: aquatic},
        },
    )


def test_fix_27_gives_the_trait_the_games_ai_weight_and_keeps_the_rest(game: Game) -> None:
    files, notes = cold_steel_mix.fix_aquatic(_aquatic(game, AQUATIC))
    trait = files[AQUATIC_COPY]
    assert b"has_trait = trait_cyborg_climate_adjustment_wet" in trait
    assert b"pd_aquatic_allowed_planet_classes" in trait and b"\r" not in trait
    assert notes == [
        "trait_aquatic, from Planetary Diversity: its ai_weight gets the game's "
        "trait_cyborg_climate_adjustment_wet"
    ]
    assert check_files(files) == []


def test_fix_27_is_left_out_once_the_mod_checks_the_games_traits(game: Game) -> None:
    with pytest.raises(FixError, match="checks every trait the game's does now"):
        cold_steel_mix.fix_aquatic(_aquatic(game, GAME_AQUATIC))


def test_fix_27_is_left_out_if_the_mods_weight_is_its_own(game: Game) -> None:
    aquatic = AQUATIC.replace("weight = 1", "weight = 5")
    with pytest.raises(FixError, match="in more than its traits"):
        cold_steel_mix.fix_aquatic(_aquatic(game, aquatic))


# Fix 28: shrimpAI's Hyper Relay and the game's clause for Nomadic empires

GAME_RELAY_FILE = "common/megastructures/14_hyper_relay.txt"
SHRIMPAI_RELAY_FILE = "common/megastructures/zzz_shrimpai_hyper_relay_overwrite.txt"
WAYSTATION = """
\t\t\t\tany_starbase_in_system = {
\t\t\t\t\tis_waystation_starbase = yes
\t\t\t\t}"""
RELAY = """hyper_relay = {\r
\tresources = { cost = { alloys = @shrimpai_alloys_cost } }\r
\tpossible = {\r
\t\tcustom_tooltip = {\r
\t\t\tfail_text = "requires_surveyed_system"\r
\t\t\tOR = {\r
\t\t\t\tshrimpai_is_starless = yes # OVERWRITE wild space support\r
\t\t\t\tNOT = { any_system_planet = { is_surveyed = no } }WAYSTATION\r
\t\t\t\tAND = { exists = starbase }\r
\t\t\t}\r
\t\t}\r
\t}\r
}\r
"""
RELAY_COPY = "common/megastructures/zzzz_stellaris_patcher_cold_steel_mix_hyper_relay.txt"


def _relay(game: Game, shrimpai: str) -> Layers:
    game_relay = RELAY.replace("\r", "").replace("@shrimpai_alloys_cost", "500")
    return _layers(
        game,
        {
            GAME: {
                GAME_RELAY_FILE: game_relay.replace(
                    "\t\t\t\tshrimpai_is_starless = yes # OVERWRITE wild space support\n", ""
                ).replace("WAYSTATION", WAYSTATION)
            },
            cold_steel_mix.SHRIMPAI: {
                SHRIMPAI_RELAY_FILE: shrimpai,
                "common/scripted_variables/shrimpai.txt": "@shrimpai_alloys_cost = 500\n",
            },
        },
    )


def test_fix_28_adds_the_games_waystation_clause_and_keeps_shrimpais_own(game: Game) -> None:
    files, notes = cold_steel_mix.fix_hyper_relay(_relay(game, RELAY.replace("WAYSTATION", "")))
    relay = files[RELAY_COPY]
    assert b"} }\n\t\t\t\tany_starbase_in_system = {\n\t\t\t\t\tis_waystation_starbase" in relay
    assert b"shrimpai_is_starless = yes # OVERWRITE wild space support\n" in relay
    assert b"@shrimpai_alloys_cost" in relay and b"\r" not in relay
    assert notes == [
        "hyper_relay, from shrimpAI: adds the game's clause to requires_surveyed_system"
    ]
    assert check_files(files) == []


def test_fix_28_is_left_out_once_shrimpai_has_the_games_clauses(game: Game) -> None:
    with pytest.raises(FixError, match="every clause the game's do now"):
        cold_steel_mix.fix_hyper_relay(_relay(game, RELAY.replace("WAYSTATION", WAYSTATION)))


# Fix 29: Starbase Extended's module bonuses and the buildings nothing defines

SBX_MODULES = "common/starbase_modules/sbx_3_0_starbase_modules.txt"
SBX_BUILDINGS = "common/starbase_buildings/sbx_3_0_starbase_buildings.txt"
SBX_MINING = """asteroid_mining = {\r
\tresources = {\r
\t\tproduces = { minerals = 10 }\r
\t\tproduces = { trigger = { has_starbase_building = mining_manager } minerals = 2 }\r
\t\t# produces = { trigger = { has_starbase_building = mining_manager } }\r
\t}\r
}\r
"""
SBX_FOUNDRY = """space_foundry = {
\tresources = {
\t\tcost = { alloys = @foundry_cost }
\t\tproduces = { trigger = { has_starbase_building = assembly_line_manufacturing } alloys = 1 }
\t\tupkeep = { trigger = { has_starbase_building = assembly_line_manufacturing } energy = 1 }
\t}
}
"""
SBX_GUNS = "gun_battery = { potential = { has_starbase_building = crew_quarters } }\n"
SBX_BUILDING_LIST = "mining_experts = { }\nchain_manufacturing = { }\n"
SBX_MODULES_COPY = "common/starbase_modules/zz_stellaris_patcher_cold_steel_mix_sbx_buildings.txt"


def _sbx_modules(game: Game, buildings: str = SBX_BUILDING_LIST, **later: str) -> Layers:
    modules = "@foundry_cost = 75\n" + SBX_MINING + SBX_FOUNDRY + SBX_GUNS
    mods = {
        GAME: {"common/starbase_buildings/00_starbase_buildings.txt": "crew_quarters = { }\n"},
        cold_steel_mix.STARBASE_EXTENDED: {SBX_MODULES: modules, SBX_BUILDINGS: buildings},
    }
    if later:
        mods["workshop:9"] = {f"common/starbase_modules/{n}.txt": t for n, t in later.items()}
    return _layers(game, mods)


def test_fix_29_points_the_bonuses_at_starbase_extendeds_own_buildings(game: Game) -> None:
    files, notes = cold_steel_mix.fix_sbx_bonus_buildings(_sbx_modules(game))
    copy = files[SBX_MODULES_COPY]
    assert copy.startswith(b"@foundry_cost = 75\n\nasteroid_mining = {\n")
    assert copy.count(b"has_starbase_building = mining_experts }") == 1
    assert b"# produces = { trigger = { has_starbase_building = mining_manager } }" in copy
    assert copy.count(b"has_starbase_building = chain_manufacturing }") == 2
    assert b"assembly_line" not in copy and b"gun_battery" not in copy and b"\r" not in copy
    assert notes == [
        "asteroid_mining, from Starbase Extended: checks mining_experts for mining_manager",
        "space_foundry, from Starbase Extended: checks chain_manufacturing for "
        "assembly_line_manufacturing",
    ]
    assert check_files(files) == []


def test_fix_29_leaves_a_module_another_mod_replaces(game: Game) -> None:
    layers = _sbx_modules(game, zzz_other="space_foundry = { }\n")
    files, notes = cold_steel_mix.fix_sbx_bonus_buildings(layers)
    assert b"space_foundry" not in files[SBX_MODULES_COPY.replace("zz_", "zzzz_")]
    assert len(notes) == 1


def test_fix_29_skips_a_missing_building_once_its_defined(game: Game) -> None:
    buildings = SBX_BUILDING_LIST + "mining_manager = { }\n"
    files, notes = cold_steel_mix.fix_sbx_bonus_buildings(_sbx_modules(game, buildings))
    assert b"asteroid_mining" not in files[SBX_MODULES_COPY]
    assert notes[0] == "mining_manager is defined now. Skipped."


def test_fix_29_is_left_out_once_every_building_is_defined(game: Game) -> None:
    buildings = SBX_BUILDING_LIST + "mining_manager = { }\nassembly_line_manufacturing = { }\n"
    with pytest.raises(FixError, match="mining_manager is defined now"):
        cold_steel_mix.fix_sbx_bonus_buildings(_sbx_modules(game, buildings))


def test_fix_29_is_left_out_once_no_module_checks_them(game: Game) -> None:
    layers = _sbx_modules(game, zzz_other="asteroid_mining = { }\nspace_foundry = { }\n")
    with pytest.raises(FixError, match="checks mining_manager or assembly_line_manufacturing"):
        cold_steel_mix.fix_sbx_bonus_buildings(layers)


# Fix 30: Starbase Extended's starbase window

VIEW_GUI = """@list_width = 430\r
@unused = 1\r
guiTypes = {\r
\tcontainerWindowType = {\r
\t\tname = "starbase_view"\r
\t\tcontainerWindowType = {\r
\t\t\tname = "starbase_tab"\r
\t\t\tcontainerWindowType = {\r
\t\t\t\tname = "class_info"\r
\t\t\t\tbackground = { name = "class_info" spriteType = "GFX_dark" }\r
\t\t\t\tbuttonType = { name = "details" position = { x = 4 y = -35 } orientation = lower_left }\r
\t\t\t\tbuttonType = { name = "dismantle" position = { x = -35 y = 39 } }\r
\t\t\t}\r
\t\t\tcontainerWindowType = {\r
\t\t\t\tname = "upgrade_info"\r
\t\t\t\tposition = { x = -10 y = 40 }\r
\t\t\t\torientation = upper_right\r
\t\t\t\torigo = upper_right\r
\t\t\t\tinstantTextBoxType = {\r
\t\t\t\t\tname = "next_class_name" position = { x = 0 y = 4 } format = right\r
\t\t\t\t}\r
\t\t\t\tbuttonType = { name = "upgrade" position = UPGRADE orientation = upper_right }\r
\t\t\t}\r
\t\t\tcontainerWindowType = {\r
\t\t\t\tname = "capacity_info"\r
\t\t\t\tbuttonType = { name = "upgrade" position = { x = 1 y = 1 } }\r
\t\t\t}\r
\t\t\tgridBoxType = { name = "modules_grid" slotSize = SLOT max_slots_horizontal = ROW }\r
\t\t\tgridBoxType = { name = "buildings_grid" slotSize = SLOT max_slots_horizontal = ROW }\r
\t\t\tbuttonType = { name = "open_planet" size = { x = @list_width y = 1 } }\r
\t\t}\r
\t}\r
\tcontainerWindowType = {\r
\t\tname = "starbase_view_current_component_grid_entry"\r
\t\tsize = SLOT\r
\t\ticonType = {\r
\t\t\tname = "icon"SCALE\r
\t\t\tspriteType = "GFX_spaceport_modules"\r
\t\t}\r
\t\ticonType = { name = "progressbar" position = { x = 3 y = 42 } }\r
\t}\r
\tcontainerWindowType = { name = "starbase_side_view" }\r
}\r
"""
UIOD_GUI = (
    VIEW_GUI.replace("SLOT", "{ width = 60 height = 60 }").replace("ROW", "5").replace("SCALE", "")
)
SBX_FULL = (
    VIEW_GUI.replace("SLOT", "{ width = 34 height = 34 }")
    .replace("ROW", "7")
    .replace("SCALE", "\r\n\t\t\tscale = 0.6 # smaller")
    .replace("UPGRADE", "{ x = 9 y = 40 }")
)
SBX_GUI = SBX_FULL.replace(
    '\t\t\tbuttonType = { name = "open_planet" size = { x = @list_width y = 1 } }\r\n', ""
)
VIEW_COPY = "interface/zzzz_stellaris_patcher_cold_steel_mix_starbase_view.gui"


def _views(game: Game, uiod: str = UIOD_GUI, sbx: str = SBX_GUI) -> Layers:
    return _layers(
        game,
        {
            cold_steel_mix.UI_OVERHAUL: {
                "interface/starbase_view.gui": uiod.replace("UPGRADE", "{ x = -35 y = 4 }"),
                "interface/Ω_bottom.gui": "guiTypes = { containerWindowType = { name = x } }\n",
            },
            cold_steel_mix.STARBASE_EXTENDED: {cold_steel_mix.SBX_VIEW: sbx},
        },
    )


def test_fix_30_ships_ui_overhauls_window_with_starbase_extendeds_slots(game: Game) -> None:
    files, notes = cold_steel_mix.fix_starbase_view(_views(game))
    assert files[cold_steel_mix.SBX_VIEW] == cold_steel_mix.EMPTIED
    view = files[VIEW_COPY]
    assert view.startswith(b"@list_width = 430\nguiTypes = {\n\tcontainerWindowType = {")
    assert view.count(b"slotSize = { width = 34 height = 34 } max_slots_horizontal = 7") == 2
    assert b'name = "icon"\n\t\t\tscale = 0.6\n\t\t\tspriteType' in view
    assert b'name = "details" position = { x = -45 y = 4 } orientation = upper_right' in view
    assert b'name = "upgrade" position = { x = 4 y = 4 } orientation = upper_left' in view
    assert b'name = "upgrade" position = { x = 1 y = 1 }' in view  # the other upgrade button
    assert b"position = { x = 10 y = 75 }\n\t\t\t\torientation = upper_left" in view
    assert b"starbase_side_view" not in view and b"\r" not in view
    assert notes == [
        "Starbase Extended's window lacks open_planet",
        "Upgrade and Station Details swap places, as in Starbase Extended",
        "Module and building slots take Starbase Extended's sizes",
    ]
    assert check_files(files) == []


def test_fix_30_skips_the_button_swap_once_ui_overhauls_header_changes(game: Game) -> None:
    uiod = UIOD_GUI.replace("format = right", "format = center")
    files, notes = cold_steel_mix.fix_starbase_view(_views(game, uiod=uiod))
    assert b'name = "details" position = { x = 4 y = -35 }' in files[VIEW_COPY]
    assert b"max_slots_horizontal = 7" in files[VIEW_COPY]
    assert notes[1] == "next_class_name's format has changed. The button swap is skipped."


def test_fix_30_is_left_out_once_starbase_extendeds_window_has_ui_overhauls_elements(
    game: Game,
) -> None:
    with pytest.raises(FixError, match="has every element UI Overhaul's has now"):
        cold_steel_mix.fix_starbase_view(_views(game, sbx=SBX_FULL))


# Fix 31: Starbase Extended's starbase models

STARBASES = "gfx/models/ships/starbases"
SBX_ASSET = f"{STARBASES}/_starbase_entities_SBX_3_0_x.asset"
GAME_ENTITIES = """@flowmap_speed = 0.17
@unused = 2
entity = {
\tname = "humanoid_01_starbase_starport_entity"
\tpdxmesh = "port_mesh"
\tcull_radius = 14
\tstate = { name = "idle" state_time = 5 }
\tstate = { name = "death" looping = no
\t\tevent = { time = 1.7 node = "root" particle = "boom" sound = { soundeffect = "explode" } }
\t}
}
entity = {
\tname = "aquatic_01_starbase_citadel_section_entity"
\tpdxmesh = "sea_mesh"
\tuv_animation_speed = @flowmap_speed
\tstate = { name = "idle" state_time = 5
\t\tevent = { time = 0 node = "light_locator_01" particle = "sea_light" }
\t\tstart_event = { sound = { soundeffect = "sea_idle" } }
\t}
}
entity = {
\tname = "toxoid_01_starbase_citadel_entity"
\tpdxmesh = "tox_mesh"
\tstate = { name = "death" looping = no
\t\tevent = { time = 1.7 node = "root" particle = "boom" }
\t}
}
entity = {
\tname = "avian_01_starbase_starport_entity"
\tpdxmesh = "port_mesh"
}
"""
SBX_ENTITIES = """@flowmap_speed = 0.17\r
entity = {\r
\tname = "humanoid_01_starbase_starport_entity"\r
\tpdxmesh = "port_mesh"\r
\tlocator = { name = "medium_gun_01" position = { 0 0 0 } }\r
}\r
entity = {
\tname = "aquatic_01_starbase_citadel_section_entity"
\tpdxmesh = "sea_mesh"
\tstate = { name = "idle" state_time = 5
\t\tevent = { time = 0 node = "light_locator_01" particle = "boom" }
\t\tevent = { time = 0 node = "extra_node" particle = "sea_light" }
\t\tevent = { time = 0 node = "engine" particle = "sea_core" }
\t\tstart_event = { sound = { soundeffect = "old_hum" } }
\t\tstart_event = { sound = { soundeffect = "amb_sea_hum" } }
\t}
}
entity = {
\tname = "toxoid_01_starbase_stronghold_entity"
\tpdxmesh = "tox_mesh"
\tlocator = { name = "medium_gun_02" position = { 0 0 0 } }
}
entity = {
\tname = "synthetics_01_starbase_stronghold_entity"
\tpdxmesh = "syn_mesh"
\tstate = { name = "idle" animation = "idle" state_time = 2 }
}
animation = { name = "fe_idle_animation" file = "fe_idle.anim" }
animation = { name = "tox_idle_animation" file = "tox_idle.anim" }
"""
MESHES = """objectTypes = {
\tpdxmesh = { name = "port_mesh" file = "gfx/models/ships/starbases/port.mesh" }
\tpdxmesh = { name = "sea_mesh" file = "gfx/models/ships/starbases/sea.mesh" }
\tpdxmesh = { name = "tox_mesh" file = "gfx/models/ships/starbases/tox.mesh" }
\tpdxmesh = { name = "syn_mesh" file = "gfx/models/ships/starbases/syn.mesh" }
}
"""
PARTICLES = (
    'objectTypes = { pdxparticle = { name = "boom" } pdxparticle = { name = "sea_light" } }\n'
)
SOUNDS = "soundeffect = { name = explode }\nsoundeffect = { name = sea_idle }\n"
SOUNDS += "soundeffect = { name = old_hum }\n"
SLOTS = """starbase_starport = {
\tsection_slots = { "core" = { locator = "part1" } "1" = { locator = "part4" } }
}
"""
ATTACH_COPY = f"{STARBASES}/zz_stellaris_patcher_cold_steel_mix_attach_points.asset"


def _mesh(*locators: str) -> bytes:
    """A binary .mesh with these locators, as the game writes them."""
    head = b"@@b@!\x08pdxasseti\x02\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00[locator\x00"
    point = b"!\x01pf\x03\x00\x00\x00" + bytes(12) + b"!\x01qf\x04\x00\x00\x00" + bytes(16)
    return head + b"".join(b"[[" + n.encode() + b"\x00" + point for n in locators)


def _starbase_models(game: Game, sbx: str = SBX_ENTITIES, slots: str = SLOTS) -> Layers:
    layers = _layers(
        game,
        {
            GAME: {
                f"{STARBASES}/_starbase_entities.asset": GAME_ENTITIES,
                f"{STARBASES}/_starbase_meshes.gfx": MESHES,
                f"{STARBASES}/tox_idle.anim": "",
                "gfx/particles/_particles.gfx": PARTICLES,
                "sound/sounds.asset": SOUNDS,
            },
            cold_steel_mix.STARBASE_EXTENDED: {
                SBX_ASSET: sbx,
                "common/ship_sizes/sbx_3_0_starbases.txt": slots,
            },
        },
    )
    for name in ("port", "sea", "tox", "syn"):
        (game.install_dir / STARBASES / f"{name}.mesh").write_bytes(_mesh("part1", "part2"))
    return layers


def _entity(data: bytes, name: str) -> bytes:
    entry = next(e for e in scan(data) if value_of(data, e, b"name") == name.encode())
    return data[entry.start : entry.end]


def test_fix_31_builds_starbase_extendeds_models_on_the_games(game: Game) -> None:
    files, notes = cold_steel_mix.fix_starbase_models(_starbase_models(game))
    models = files[SBX_ASSET]
    assert models.startswith(b"@flowmap_speed = 0.17\n\nentity = {") and b"\r" not in models
    port = _entity(models, "humanoid_01_starbase_starport_entity")
    assert b'particle = "boom"' in port and b"cull_radius = 14" in port  # the game's 4.5 lines
    assert b'"medium_gun_01"' in port  # Starbase Extended's own
    assert b'locator = { name = "part4" position = { 0 0 0 } }' in port
    assert b'"part1" position' not in port  # the mesh has it
    sea = _entity(models, "aquatic_01_starbase_citadel_section_entity")
    assert b"uv_animation_speed = @flowmap_speed" in sea and b'"sea_idle"' in sea
    assert b'node = "extra_node"' in sea  # a node the game's model doesn't use
    assert b'particle = "boom"' not in sea  # the game's own effect on that node stays
    assert b"old_hum" not in sea and b"amb_sea_hum" not in sea and b"sea_core" not in sea
    tox = _entity(models, "toxoid_01_starbase_stronghold_entity")
    assert b'particle = "boom"' in tox and b'"medium_gun_02"' in tox  # built on the citadel
    assert b'animation = "idle"' not in _entity(models, "synthetics_01_starbase_stronghold_entity")
    assert b"fe_idle" not in models and b"tox_idle.anim" in models
    attach = files[ATTACH_COPY]
    assert attach.startswith(b'entity = {\n\tname = "avian_01_starbase_starport_entity"')
    assert b'locator = { name = "part4" position = { 0 0 0 } }' in attach
    assert notes == [
        "4 of Starbase Extended's models rebuilt, from the game's where it copies one",
        "Left out, as nothing defines them: 1 animation files, 1 mesh animations, "
        "1 particles, 1 sounds",
        "Left out, as the game's model has its own: 1 effects, 1 sounds",
        "2 attach points added. 1 game models are copied to get theirs",
    ]
    assert check_files(files) == []


def test_fix_31_is_left_out_once_the_models_match_the_games(game: Game) -> None:
    same = GAME_ENTITIES.replace("@unused = 2\n", "")
    layers = _starbase_models(game, sbx=same, slots=SLOTS.replace("part4", "part2"))
    with pytest.raises(FixError, match="match the game's and resolve every name now"):
        cold_steel_mix.fix_starbase_models(layers)


# Fix 32: Starbase Extended's module and building checks

GAME_HANGAR = """orbital_ring_hangar_bay = {
\tresources = {
\t\tupkeep = { trigger = { owner? = { country_uses_bio_ships = no } } energy = 1 }
\t\tupkeep = { trigger = { owner? = { country_uses_bio_ships = yes } } food = 1 }
\t}
\ttriggered_component_set = { component_set = SCOUT_HANGAR_1 }
\tshow_component_tooltips = yes
}
"""
SBX_MODULES_TEXT = """orbital_ring_hangar_bay = {
\tresources = {
\t\tcost = { alloys = 50 }
\t\tupkeep = { energy = 1 }
\t}
\tai_weight = {
\t\tweight = 100
\t\tmodifier = { factor = 0.5 }
\t}
\tai_weight = {
\t\tweight = 100
\t\tmodifier = { factor = 2 }
\t}
}
gun_battery = {
\tpotential = {
\t\thas_starbase_size >= starbase_starport
\t}
\tpotential = { count_starbase_modules = { type = gun_battery count < 5 } }
}
asteroid_mining = {
\tresources = { produces = { trigger = { has_starbase_building = mining_manager } } }
}
pd_battery = { potential = { exists = owner } }
"""
SBX_BUILDINGS_TEXT = """research_computers = {
\tpotential = { solar_system = { any_system_planet = { is_owned_by = from } } }
}
financial_space_center = {
\tpotential = {
\t\tcategory = starbase_buildings
\t\thas_starbase_size >= starbase_starhold
\t}
}
crew_quarters = { potential = { exists = solar_system solar_system = { } } }
"""


def _sbx_checks(
    game: Game, modules: str = SBX_MODULES_TEXT, buildings: str = SBX_BUILDINGS_TEXT
) -> Layers:
    return _layers(
        game,
        {
            GAME: {"common/starbase_modules/01_orbital_ring_weapon_modules.txt": GAME_HANGAR},
            cold_steel_mix.STARBASE_EXTENDED: {SBX_MODULES: modules, SBX_BUILDINGS: buildings},
        },
    )


def test_fix_32_mends_starbase_extendeds_files_whole(game: Game) -> None:
    files, notes = cold_steel_mix.fix_sbx_checks(_sbx_checks(game))
    assert set(files) == {SBX_MODULES, SBX_BUILDINGS}  # at its own paths, so its files are gone
    modules = files[SBX_MODULES]
    hangar = _entity_text(modules, b"orbital_ring_hangar_bay")
    assert hangar.count(b"ai_weight") == 1 and hangar.count(b"weight = 100") == 1
    assert b"factor = 0.5" in hangar and b"factor = 2" in hangar
    assert b"food = 1" in hangar and b"cost = { alloys = 50 }" in hangar
    assert b"SCOUT_HANGAR_1" in hangar and b"show_component_tooltips = yes" in hangar
    guns = _entity_text(modules, b"gun_battery")
    assert guns.count(b"potential") == 1 and b"count < 5" in guns
    assert b"mining_manager" in _entity_text(modules, b"asteroid_mining")  # left to fix 29
    assert (
        _entity_text(modules, b"pd_battery") == b"pd_battery = { potential = { exists = owner } }"
    )
    buildings = files[SBX_BUILDINGS]
    assert b"potential = { exists = solar_system solar_system = {" in buildings
    assert b"category" not in _entity_text(buildings, b"financial_space_center")
    crew = b"crew_quarters = { potential = { exists = solar_system solar_system = { } } }"
    assert _entity_text(buildings, b"crew_quarters") == crew  # it checks for the system already
    assert notes == [
        "orbital_ring_hangar_bay: merges its 2 ai_weight blocks, gets the game's "
        "show_component_tooltips, triggered_component_set, costs the game's upkeep, food for "
        "bio-ship empires",
        "gun_battery: merges its 2 potential blocks",
        "asteroid_mining is copied by fix 29. Skipped.",
        "research_computers: checks the starbase has a system first",
        "financial_space_center: drops `category` from its potential, which isn't a trigger",
    ]
    assert check_files(files) == []


def test_fix_32_is_left_out_once_the_checks_are_mended(game: Game) -> None:
    layers = _sbx_checks(
        game, modules="pd_battery = { potential = { exists = owner } }\n", buildings=""
    )
    with pytest.raises(FixError, match="no checks to mend now"):
        cold_steel_mix.fix_sbx_checks(layers)


def _entity_text(data: bytes, key: bytes) -> bytes:
    entry = next(e for e in scan(data) if e.key == key)
    return data[entry.start : entry.end]


# Fix 33: Starbase Extended's orbital ring shield and armour sections

RING_TEMPLATES = """ship_section_template = {
\tkey = "ANCHORAGE_ORBITAL_RING_SECTION"
\tship_size = orbital_ring_tier_1
\tentity = "orbital_ring_anchorage_section_entity"
}
"""
RING_MODULES = 'orbital_ring_shield_module = { section = "SHIELD_ORBITAL_RING_SECTION" }\n'


def _ring_sections(game: Game, templates: str = RING_TEMPLATES) -> Layers:
    return _layers(
        game,
        {
            cold_steel_mix.STARBASE_EXTENDED: {
                "common/section_templates/!!!_sbx_3_0_orbital_ring_sections.txt": templates,
                SBX_MODULES: RING_MODULES,
            }
        },
    )


def test_fix_33_defines_a_used_ring_section_as_the_anchorages(game: Game) -> None:
    files, notes = cold_steel_mix.fix_ring_sections(_ring_sections(game))
    (sections,) = files.values()
    assert b'key = "SHIELD_ORBITAL_RING_SECTION"' in sections
    assert b"orbital_ring_anchorage_section_entity" in sections
    assert b"ARMOR" not in sections  # no module uses it
    assert notes == ["SHIELD_ORBITAL_RING_SECTION, as a copy of ANCHORAGE_ORBITAL_RING_SECTION"]
    assert check_files(files) == []


def test_fix_33_is_left_out_once_the_section_is_defined(game: Game) -> None:
    defined = RING_TEMPLATES + RING_TEMPLATES.replace("ANCHORAGE", "SHIELD")
    with pytest.raises(FixError, match="is defined now"):
        cold_steel_mix.fix_ring_sections(_ring_sections(game, defined))


# Fix 34: Starbase Extended's starbase sizes

GAME_SIZES = """@citadel_size = 100
starbase_citadel = {
\tsize_multiplier = @citadel_size
\tcombat_size_multiplier = 100
\tmap_counter_icon = ship_counter_128
}
ion_cannon = {
\tfleet_slot_size = 40
\tpotential_construction = {
\t\tis_scope_type = starbase
\t\tis_arkship_starbase = no
\t}
}
"""
SBX_SIZES = """@build_block_radius_starbase = 20
starbase_citadel = {
\tmax_hitpoints = 240000
\tsize_multiplier = 4
\tcombat_size_multiplier = 50
}
ion_cannon = {
\tfleet_slot_size = 8
\tpotential_construction = {
\t\tis_scope_type = starbase
\t}
}
"""
NSC_SIZES = (
    "starbase_stronghold = {\n\tsize_multiplier = 4\n\tradius = @build_block_radius_starbase\n}\n"
)
SIZES_COPY = "common/ship_sizes/zz_stellaris_patcher_cold_steel_mix_starbase_sizes.txt"


def _sizes(game: Game, sbx: str = SBX_SIZES, nsc: str = NSC_SIZES) -> Layers:
    return _layers(
        game,
        {
            GAME: {"common/ship_sizes/00_starbases.txt": GAME_SIZES},
            cold_steel_mix.STARBASE_EXTENDED: {
                "common/ship_sizes/sbx_3_0_starbases.txt": sbx,
                cold_steel_mix.NSC_STARBASES: nsc,
            },
        },
    )


def test_fix_34_gives_starbase_extendeds_sizes_the_games_values(game: Game) -> None:
    files, notes = cold_steel_mix.fix_starbase_sizes(_sizes(game))
    sizes = files[SIZES_COPY]
    assert sizes.startswith(b"@build_block_radius_starbase = 20\n\n")
    citadel = _entity_text(sizes, b"starbase_citadel")
    assert b"size_multiplier = 100" in citadel and b"combat_size_multiplier = 100" in citadel
    assert b"map_counter_icon = ship_counter_128" in citadel
    assert b"max_hitpoints = 240000" in citadel  # Starbase Extended's own
    stronghold = _entity_text(sizes, b"starbase_stronghold")
    assert b"size_multiplier = 100" in stronghold and b"ship_counter_128" in stronghold
    ion = _entity_text(sizes, b"ion_cannon")
    assert b"fleet_slot_size = 40" in ion and b"is_arkship_starbase = no" in ion
    assert notes == [
        "3 sizes get the game's 4.5 values and construction conditions, the new tiers the "
        "Citadel's values"
    ]
    assert check_files(files) == []


def test_fix_34_is_left_out_once_the_sizes_have_the_games_values(game: Game) -> None:
    same = GAME_SIZES.replace("@citadel_size", "100").replace("@100 = 100\n", "")
    with pytest.raises(FixError, match=r"have the game's 4\.5 values now"):
        cold_steel_mix.fix_starbase_sizes(_sizes(game, sbx=same, nsc=""))


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


def test_a_written_fix_also_needs_the_mods_its_files_come_from(
    game: Game, monkeypatch: pytest.MonkeyPatch
) -> None:
    made: cold_steel_mix.Made = ({"a.txt": b"a"}, [])
    starbase, ui = cold_steel_mix.STARBASE_EXTENDED, cold_steel_mix.UI_OVERHAUL
    monkeypatch.setattr(cold_steel_mix, "FIXES", ((30, "Thirty", lambda _: made, (starbase,)),))
    (thirty,) = cold_steel_mix.plan(_layers(game, {ui: {"a.txt": "a"}}))
    assert thirty.left_out.startswith("The playset has none of its mods now")
    (thirty,) = cold_steel_mix.plan(_layers(game, {ui: {"a.txt": "a"}, starbase: {"b.txt": "b"}}))
    assert thirty.mods == (starbase, ui)


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
