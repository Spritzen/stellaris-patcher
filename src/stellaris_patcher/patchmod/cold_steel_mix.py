"""The Cold Steel Mix patch. What each fix does, and the report it comes from,
is in docs/patches/cold-steel-mix.md.

    outcomes = plan(layers)        # one per fix: its files, or why it was left out

Each fix is worked out from the files on disk every time (decision 14). Each
first checks that its cause is still there, and is left out with a reason when
an update has changed it. A fix that copies a file only does so when that file
still comes from the mod or game it expects, so it can't undo another mod's
newer copy.
"""

import math
import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

from stellaris_patcher.paradox.game import Game
from stellaris_patcher.paradox.localisation import keys, language
from stellaris_patcher.paradox.script import Entry, Node, children, scan, value_of
from stellaris_patcher.patchmod.layers import (
    GAME,
    LayerError,
    Layers,
    find_define,
    numbers,
    parse_file,
)
from stellaris_patcher.patchmod.write import BOM, mods_dir, winning_name, workshop_id

NAME = "Cold Steel Mix patch"
FOLDER = "cold_steel_mix_patch"  # in ~/.local/share/stellaris-patcher/mods/
LINK = "stellaris_patcher_cold_steel_mix"  # in the game's mod folder
KEY = f"local:{LINK}"  # Cold Steel's key for it
PLAYSET = "Cold Steel Mix"
TAIL = "stellaris_patcher_cold_steel_mix"  # the end of our own files' names

SYSTEM_SCALE = "workshop:1887282318"
STARBASE_EXTENDED = "workshop:3250900527"
REAL_SPACE = "workshop:937289339"
SHIPS_IN_SCALING = "workshop:1915620447"
CINEMATIC_CAMERA = "workshop:703156866"
PLANETARY_DIVERSITY = "workshop:819148835"
ASCENSION_WORLDS = "workshop:3241119393"  # Planetary Diversity - Ascension Worlds
MORE_EVENTS = "workshop:727000451"
MORE_ARCOLOGIES = "workshop:1732447147"  # Planetary Diversity - More Arcologies
SHRIMPAI = "workshop:2815767345"  # Smarter Hyper Relays: Improved AI (shrimpAI)
UI_OVERHAUL = "workshop:1623423360"  # UI Overhaul Dynamic


class FixError(Exception):
    """A fix doesn't apply any more, or its cause has changed."""


@dataclass(frozen=True)
class Outcome:
    number: int  # its number in the report that proposed it
    title: str
    files: dict[str, bytes] = field(default_factory=dict)
    notes: tuple[str, ...] = ()  # what it did, or parts it skipped
    left_out: str = ""  # why nothing was written, if so
    mods: tuple[str, ...] = ()  # the mods it patches, and once written those it NEEDS


type Made = tuple[dict[str, bytes], list[str]]


def workshop_key(game: Game) -> str:
    """The patch's Workshop copy, as Cold Steel keys it, or "" if it isn't
    uploaded. The id is the one the launcher saved after the upload."""
    found = workshop_id(mods_dir() / FOLDER / "descriptor.mod", game.mod_dir / f"{LINK}.mod")
    return f"workshop:{found}" if found else ""


def own_keys(game: Game) -> list[str]:
    """Every key the patch can have in a playset: local, and Workshop once uploaded.
    Building skips them all, or the patch would see its own files as another mod's."""
    return [k for k in (KEY, workshop_key(game)) if k]


def plan(layers: Layers) -> list[Outcome]:
    """A fix whose mods are all out of the playset is left out without looking:
    its cause went with them, and its files may be gone."""
    present = {layer.key for layer in layers.layers}
    outcomes: list[Outcome] = []
    for number, title, make, mods in FIXES:
        try:
            if not present.intersection(mods):
                raise FixError(f"The playset has none of its mods now: {', '.join(mods)}.")
            files, notes = make(layers)
        except FixError as why:
            outcomes.append(Outcome(number, title, left_out=str(why), mods=mods))
            continue
        needs = mods + NEEDS.get(number, ())
        outcomes.append(Outcome(number, title, files, tuple(notes), mods=needs))
    return outcomes


def patched_mods(outcomes: list[Outcome], order: Sequence[str]) -> list[str]:
    """The mods the written fixes patch, each once, in the playset's load order
    (`order`: its mod keys, as `Layers.layers` lists them)."""
    keys = {k for o in outcomes if not o.left_out for k in o.mods}
    return [k for k in order if k in keys]


def workshop_description(outcomes: list[Outcome], names: dict[str, str], version: str) -> str:
    """The Steam Workshop description, in Steam's BBCode: what's fixed and what's
    needed. `names` gives the required mods, in the order they're listed."""
    written = [o for o in outcomes if not o.left_out]
    required = "".join(f"[*]{name}\n" for name in names.values())
    grouped = {n for _, members in FIX_GROUPS for n in members}
    groups = [*FIX_GROUPS, ("Other", tuple(o.number for o in written if o.number not in grouped))]
    fixes = ""
    for heading, members in groups:
        titles = "".join(f"[*]{o.title}\n" for o in written if o.number in members)
        if titles:
            fixes += f"[h3]{heading}[/h3]\n[list]\n{titles}[/list]\n"
    waiting = "".join(f"[*]{problem}\n" for problem in LEFT_TO_AUTHORS)
    left = (
        "\n[h2]Known issues, waiting for the mod authors[/h2]\n"
        "These come from the mods themselves. The patch leaves them to their authors, "
        "whose next updates should fix them.\n"
        f"[list]\n{waiting}[/list]\n"
        if LEFT_TO_AUTHORS
        else ""
    )
    return (
        f"[h1]{NAME}[/h1]\n"
        f"Fixes clashes and breakages between the mods of the {PLAYSET} playset, "
        f"for Stellaris {version}.\n\n"
        "[h2]Load order[/h2]\n"
        "Load it last, after every mod below.\n\n"
        f"[h2]Required mods[/h2]\n[list]\n{required}[/list]\n\n"
        f"[h2]What it fixes[/h2]\n{fixes}"
        f"{left}"
    )


def _expect_winner(layers: Layers, path: str, layer: str, who: str) -> None:
    winner = layers.winner(path)
    if winner != layer:
        raise FixError(f"{path} now comes from {winner}, not {who}. Check it again.")


# 1. System Scale's old .asset copies


ASSETS = (
    "gfx/models/ships/megastructures/dyson_sphere/_dyson_sphere_entities.asset",
    "gfx/models/ships/megastructures/quantum_catapult/quantum_catapult_01.asset",
    "gfx/models/effects/_system_effects_entities.asset",
)


def fix_system_scale_assets(layers: Layers) -> Made:
    files: dict[str, bytes] = {}
    notes: list[str] = []
    for path in ASSETS:
        _expect_winner(layers, path, SYSTEM_SCALE, "Real Space - System Scale")
        game, mod = layers.read(GAME, path), layers.read(SYSTEM_SCALE, path)
        dropped = {e.name for e in _entities(game)} - {e.name for e in _entities(mod)}
        if not dropped:
            notes.append(f"{path}: System Scale's copy has every game entity now. Skipped.")
            continue
        files[path], factor = mirror_scale(game, mod)
        notes.append(f"{path}: {len(dropped)} entities back, newer ones scaled by {factor:g}")
    if not files:
        raise FixError("System Scale's copies have every game entity now.")
    return files, notes


@dataclass(frozen=True)
class _Entity:
    name: str
    entry: Entry
    name_entry: Entry
    scale: Entry | None  # its own `scale = ...`
    attaches: frozenset[str]  # the entities it attaches


def _entities(data: bytes) -> list[_Entity]:
    found: list[_Entity] = []
    for entry in scan(data):
        if entry.key != b"entity" or not entry.block:
            continue
        inner = children(data, entry)
        names = [c for c in inner if c.key == b"name" and not c.block]
        if not names:
            continue
        scale = next((c for c in inner if c.key == b"scale" and not c.block), None)
        attaches = frozenset(
            _text(data, a).strip('"')
            for block in inner
            if block.key == b"attach" and block.block
            for a in children(data, block)
        )
        found.append(_Entity(_text(data, names[0]).strip('"'), entry, names[0], scale, attaches))
    return found


def _part(name: str) -> str:
    """An entity's name without its style: humanoid_01_x_entity -> x_entity."""
    return re.sub(r"^[a-z]+_\d\d_", "", name)


def _variables(data: bytes) -> dict[str, Entry]:
    return {e.key.decode(): e for e in scan(data) if e.key.startswith(b"@") and not e.block}


def _text(data: bytes, entry: Entry) -> str:
    return data[entry.value : entry.end].decode("utf-8", "replace")


def _value(text: str | None, variables: dict[str, float]) -> float:
    if text is None:
        return 1.0
    if text.startswith("@"):
        if text not in variables:
            raise FixError(f"{text} isn't defined in the file.")
        return variables[text]
    return float(text)


def _number(value: float) -> str:
    return f"{value:.6g}"


def mirror_scale(game: bytes, mod: bytes) -> tuple[bytes, float]:
    """The game's copy of a graphics file, with the mod's sizes applied. Returns
    it and the factor the mod scales by.

    An entity the mod has takes the mod's scale. One it doesn't have, because
    the game added it later, follows the same part in the older styles:
    `toxoid_01_x_entity` is scaled when the mod scaled `humanoid_01_x_entity`.
    With no older style to follow, it's scaled unless another entity attaches
    it, as the mod leaves those alone. Raises FixError if the mod doesn't scale
    by one factor.
    """
    game_vars = {k: float(_text(game, e)) for k, e in _variables(game).items()}
    mod_vars = {k: float(_text(mod, e)) for k, e in _variables(mod).items()}
    ours = game_vars | mod_vars
    theirs = {e.name: e for e in _entities(mod)}
    entities = _entities(game)
    attached = frozenset().union(*(e.attaches for e in entities))

    def scale_text(data: bytes, entity: _Entity) -> str | None:
        return None if entity.scale is None else _text(data, entity.scale)

    ratios: set[float] = set()
    scaled: dict[str, set[bool]] = {}  # each part's name without its style: was it scaled?
    for entity in entities:
        if (other := theirs.get(entity.name)) is not None:
            was = _value(scale_text(game, entity), game_vars)
            now = _value(scale_text(mod, other), mod_vars)
            changed = not math.isclose(was, now)
            if changed:
                ratios.add(round(now / was, 6))
            scaled.setdefault(_part(entity.name), set()).add(changed)
    if len(ratios) != 1:
        raise FixError(f"The mod doesn't scale by one factor: {sorted(ratios)}.")
    factor = ratios.pop()

    edits: list[tuple[int, int, bytes]] = []
    for name, entry in _variables(game).items():
        if name in mod_vars and not math.isclose(mod_vars[name], game_vars[name]):
            edits.append((entry.value, entry.end, _text(mod, _variables(mod)[name]).encode()))
    header = "".join(f"{k} = {_number(v)}\n" for k, v in mod_vars.items() if k not in game_vars)

    for entity in entities:
        other = theirs.get(entity.name)
        follow = scaled.get(_part(entity.name), set())
        if other is not None:
            want = _value(scale_text(mod, other), mod_vars)
        elif follow == {False} or (not follow and entity.name in attached):
            continue
        elif follow == {True} or not follow:
            want = _value(scale_text(game, entity), game_vars) * factor
        else:
            raise FixError(f"The mod scales some {_part(entity.name)} but not others.")
        if math.isclose(_value(scale_text(game, entity), ours), want):
            continue
        named = [k for k, v in mod_vars.items() if math.isclose(v, want)]
        new = (named[0] if named else _number(want)).encode()
        if entity.scale is not None:
            edits.append((entity.scale.value, entity.scale.end, new))
        else:
            at = entity.name_entry.end
            edits.append((at, at, b"\n\tscale = " + new))

    out = bytearray(game)
    for start, end, new in sorted(edits, reverse=True):
        out[start:end] = new
    start = len(BOM) if game.startswith(BOM) else 0
    out[start:start] = header.encode()
    return bytes(out), factor


# 2. The Starlit Starbase design's citadel slots


DESIGNS = "common/global_ship_designs/biogenesis_ship_designs.txt"
STARLIT = "NAME_Starlit_Starbase"
CITADEL = "CITADEL_STARBASE_SECTION"


def fix_starlit_slots(layers: Layers) -> Made:
    _expect_winner(layers, DESIGNS, GAME, "the game")
    slots = section_slots(layers, CITADEL)
    data, notes = repoint_slots(layers.read(GAME, DESIGNS), STARLIT, CITADEL, slots)
    return {DESIGNS: data}, notes


def section_slots(layers: Layers, template: str) -> set[str]:
    """The component slots of a section template, as the game uses it: the
    first file by name that defines it wins."""
    for layer, path in layers.ordered("common/section_templates"):
        data = layers.read(layer, path)
        for entry in scan(data):
            if entry.block and value_of(data, entry, b"key") == template.encode():
                return _slots(data, entry)
    raise FixError(f"No section template is called {template}.")


def _slots(data: bytes, template: Entry) -> set[str]:
    """A template's named component slots, plus the utility slots it only
    counts: `large_utility_slots = 3` makes LARGE_UTILITY_1 to _3."""
    slots: set[str] = set()
    for child in children(data, template):
        if child.key == b"component_slot":
            if (name := value_of(data, child, b"name")) is not None:
                slots.add(name.decode().strip('"'))
        elif child.key.endswith(b"_utility_slots") and not child.block:
            kind = child.key.decode().removesuffix("_slots").upper()
            slots.update(f"{kind}_{i}" for i in range(1, int(_text(data, child)) + 1))
    return slots


def repoint_slots(
    data: bytes, design: str, template: str, slots: set[str]
) -> tuple[bytes, list[str]]:
    """The designs file with one design's components moved to slots the
    section has. A slot written with a leading zero, like MEDIUM_GUN_010, moves
    to MEDIUM_GUN_10, or is removed when there's no such slot. Any other slot
    the section lacks raises FixError."""
    found = [e for e in scan(data) if e.block and value_of(data, e, b"name") == design.encode()]
    if len(found) != 1:
        raise FixError(f"Found {len(found)} designs called {design}, not 1.")
    edits: list[tuple[int, int, bytes]] = []
    moved: list[str] = []
    removed: list[str] = []
    for section in children(data, found[0]):
        if section.key != b"section" or value_of(data, section, b"template") != template.encode():
            continue
        components = [c for c in children(data, section) if c.key == b"component"]
        used = {(value_of(data, c, b"slot") or b"").decode() for c in components}
        for component in components:
            slot = (value_of(data, component, b"slot") or b"").decode()
            if slot in slots:
                continue
            renamed = re.sub(r"_0(\d{2})$", r"_\1", slot)
            if renamed == slot:
                raise FixError(f"{design} uses {slot}, which {template} doesn't have.")
            if renamed in slots and renamed not in used:
                place = next(c for c in children(data, component) if c.key == b"slot")
                edits.append((place.value, place.end, f'"{renamed}"'.encode()))
                used.add(renamed)
                moved.append(f"{slot} → {renamed}")
            else:
                line_start = data.rfind(b"\n", 0, component.start) + 1
                line_end = data.find(b"\n", component.end)
                edits.append((line_start, len(data) if line_end == -1 else line_end + 1, b""))
                removed.append(slot)
    if not edits:
        raise FixError(f"Every slot {design} uses is in {template}. Nothing to fix.")
    out = bytearray(data)
    for start, end, new in sorted(edits, reverse=True):
        out[start:end] = new
    moves, drops = ", ".join(moved) or "none", ", ".join(removed) or "none"
    notes = [f"{design}: moved {moves}; removed {drops}"]
    return bytes(out), notes


# 3. nsc_starbases.txt's missing variables


NSC_STARBASES = "common/ship_sizes/nsc_starbases.txt"
_VARIABLE = re.compile(rb"@(\w+)")
_COMMENT = re.compile(rb"#[^\n]*")


def fix_nsc_variables(layers: Layers) -> Made:
    _expect_winner(layers, NSC_STARBASES, STARBASE_EXTENDED, "Starbase Extended")
    data = layers.read(STARBASE_EXTENDED, NSC_STARBASES)
    used = {"@" + m.decode() for m in _VARIABLE.findall(_COMMENT.sub(b"", data))}
    missing = used - set(_variables(data)) - set(layers.defined("common/scripted_variables"))
    if not missing:
        raise FixError(f"{NSC_STARBASES} defines every variable it uses now.")
    lines = [f"{name} = {_ship_size_value(layers, name)}\n" for name in sorted(missing)]
    header = "# Defined here by the Cold Steel Mix patch: the game sets these per file.\n"
    body = data[len(BOM) :] if data.startswith(BOM) else data
    notes = [f"{NSC_STARBASES}: defined {', '.join(sorted(missing))}"]
    return {NSC_STARBASES: (header + "".join(lines) + "\n").encode() + body}, notes


# 4. System Scale's own zoom steps, beside its planet scales


def fix_planet_scales(layers: Layers) -> Made:
    """System Scale's own zoom steps and planet scales, in a file that sorts
    last. The game doesn't match Cinematic Camera's 13 steps to 13 planet
    scales (the fourth report), but takes 8 and 8 (decision 17). Settings that
    name a step by number follow System Scale too, or a step past the end
    breaks entering a system (the solid-background report)."""
    steps, zoom, planet, own = _zoom_mismatch(layers)
    lines = {
        "NCamera": [f"ZOOM_STEPS_SYSTEM_PERCENTAGES = {{ {' '.join(map(_number, own))} }}"],
        "NGraphics": [f"PLANET_SCALE_SYSTEM = {{ {' '.join(map(_number, planet))} }}"],
    }
    notes = [f"Zoom steps: {steps}'s {len(zoom)} → System Scale's {len(own)}"]
    for category, name, value in _step_settings(layers, len(own)):
        lines[category].append(f"{name} = {value}")
        notes.append(f"{name}: System Scale's {value}")
    text = "".join(
        f"{category} = {{\n" + "".join(f"\t{line}\n" for line in block) + "}\n"
        for category, block in lines.items()
    )
    return {_last_file(layers, "common/defines"): text.encode()}, notes


# Settings that name a system zoom step by number, counting from 0.
STEP_SETTINGS = (
    ("NCamera", "ENTER_SYSTEM_ZOOM_STEP"),
    ("NCamera", "FOCUS_START_ZOOM_STEP"),
    ("NCamera", "SYSTEM_FOCUS_PLANET_STEP"),
    ("NCamera", "ZOOM_STEPS_SHOW_FLEET_HEALTH_BARS"),
    ("NGraphics", "SYSTEM_LINE_ALPHA_FADE_STEP"),
)


def _step_settings(layers: Layers, count: int) -> list[tuple[str, str, str]]:
    """(category, name, value) for each step setting another mod overrides
    where System Scale sets its own. Raises FixError if a setting the game
    ends up with names a step past System Scale's `count`."""
    out: list[tuple[str, str, str]] = []
    for category, name in STEP_SETTINGS:
        found = layers.define(category, name)
        if found is None:
            continue
        layer, node = found
        own = _system_scale_define(layers, category, name)
        if own is not None and layer != SYSTEM_SCALE:
            node = own
            out.append((category, name, _value_text(own)))
        values = numbers(node) if isinstance(node.value, tuple) else [float(node.value)]
        if not all(0 <= v < count for v in values):
            raise FixError(f"{name} names step {_value_text(node)}, but there are {count} steps.")
    return out


def _system_scale_define(layers: Layers, category: str, name: str) -> Node | None:
    own = None
    for layer, path in layers.ordered("common/defines"):
        if layer == SYSTEM_SCALE:
            own = find_define(parse_file(layers.read(layer, path)), category, name) or own
    return own


def _value_text(node: Node) -> str:
    if isinstance(node.value, tuple):
        return "{ " + " ".join(n.value for n in node.value if isinstance(n.value, str)) + " }"
    return node.value


def _zoom_mismatch(layers: Layers) -> tuple[str, list[float], list[float], list[float]]:
    """Who sets the zoom steps, the steps, System Scale's planet scales and
    System Scale's own zoom steps. Raises FixError unless they still clash."""
    steps = layers.define("NCamera", "ZOOM_STEPS_SYSTEM_PERCENTAGES")
    scales = layers.define("NGraphics", "PLANET_SCALE_SYSTEM")
    if steps is None or scales is None:
        raise FixError("The zoom steps or the planet scales aren't defined.")
    zoom, planet = numbers(steps[1]), numbers(scales[1])
    if len(zoom) == len(planet):
        raise FixError("The zoom steps and the planet scales match now.")
    if scales[0] != SYSTEM_SCALE:
        raise FixError(f"The planet scales now come from {scales[0]}, not System Scale.")
    own = _system_scale_define(layers, "NCamera", "ZOOM_STEPS_SYSTEM_PERCENTAGES")
    if own is None or len(numbers(own)) != len(planet):
        raise FixError("System Scale's own zoom steps don't match its planet scales.")
    return steps[0], zoom, planet, numbers(own)


def _last_file(layers: Layers, folder: str, what: str = "") -> str:
    """A path in `folder` whose file name sorts after every other there."""
    rivals = [p.rpartition("/")[2] for _, p in layers.ordered(folder)]
    name = winning_name(rivals, f"{TAIL}_{what}.txt" if what else f"{TAIL}.txt", first=False)
    if name is None:
        raise FixError(f"No file name sorts after the other {folder} files.")
    return f"{folder}/{name}"


# 5. The game's Sol neighbours, by Real Space's names


INITIALIZERS = "common/solar_system_initializers"
# The game's name -> Real Space's system for the same star.
SOL_NEIGHBOURS = {
    "sol_neighbor_t1": "bernards_star_mediumsector",
    "sol_neighbor_t2": "procyon_mediumsector",
    "sol_neighbor_t1_no_guaranteed_colony": "alpha_centauri_mediumsector_no_col",
}
_INITIALIZER = re.compile(rb'\binitializer\s*=\s*"?(\w+)')


def fix_sol_neighbours(layers: Layers) -> Made:
    defined = layers.defined(INITIALIZERS)
    used: set[str] = set()
    for layer, path in layers.ordered(INITIALIZERS):
        data = _COMMENT.sub(b"", layers.read(layer, path))
        used.update(m.decode() for m in _INITIALIZER.findall(data))
    game = {  # the game's own definitions, even where a mod replaced their file
        e.key.decode(): (path, e)
        for path in layers.paths(GAME, INITIALIZERS)
        for e in scan(layers.read(GAME, path))
    }
    blocks: list[str] = []
    variables: dict[str, str] = {}
    notes: list[str] = []
    for old, new in SOL_NEIGHBOURS.items():
        if old in defined or old not in used:
            notes.append(f"{old}: defined, or not used, now. Skipped.")
            continue
        if new not in defined or defined[new][0] != REAL_SPACE:
            raise FixError(f"Real Space no longer defines {new}.")
        layer, path = defined[new]
        data = layers.read(layer, path)
        entry = next(e for e in scan(data) if e.key == new.encode())
        star = value_of(data, entry, b"name")
        game_path, game_entry = game[old]
        if star != value_of(layers.read(GAME, game_path), game_entry, b"name"):
            raise FixError(f"{new} isn't the same star as the game's {old} any more.")
        body = data[entry.value : entry.end]
        file_vars = _variables(data)
        for name in sorted({"@" + m.decode() for m in _VARIABLE.findall(_COMMENT.sub(b"", body))}):
            if name not in file_vars:
                raise FixError(f"{new} uses {name}, which its file doesn't define.")
            variables[name] = _text(data, file_vars[name])
        comment = f"# The game's {old}: a copy of Real Space's {new}"
        blocks.append(f"{comment}\n{old} = {body.decode()}\n")
        notes.append(f"{old} = Real Space's {new}")
    if not blocks:
        raise FixError("Every Sol neighbour is defined now, or not used.")
    header = "".join(f"{k} = {v}\n" for k, v in variables.items())
    text = header + "\n" + "\n".join(blocks)
    return {f"{INITIALIZERS}/{TAIL}_sol_neighbors.txt": text.encode()}, notes


# 6. More Events Mod's old name for Planetary Diversity's trigger


OLD_TRIGGER, NEW_TRIGGER = "is_pd_planet_for_aqua_trait", "pd_is_planet_for_aqua_trait"


def fix_pd_trigger(layers: Layers) -> Made:
    defined = layers.defined("common/scripted_triggers")
    if OLD_TRIGGER in defined:
        raise FixError(f"{OLD_TRIGGER} is defined now.")
    if NEW_TRIGGER not in defined:
        raise FixError(f"{NEW_TRIGGER} isn't defined any more.")
    text = (
        f"# More Events Mod still uses Planetary Diversity's old name.\n"
        f"{OLD_TRIGGER} = {{\n\t{NEW_TRIGGER} = yes\n}}\n"
    )
    notes = [f"{OLD_TRIGGER} calls {NEW_TRIGGER}"]
    return {f"common/scripted_triggers/{TAIL}.txt": text.encode()}, notes


# 7. Missing text


DEPOSITS = tuple(f"rs_d_dark_matter_deposit_{n}" for n in (1, 2, 3))
# key -> (text, the folder whose files must still name the key)
TEXT = {
    "fire_rate_reduction": ("Reduced Fire Rate", "common/static_modifiers"),
    "hp_increased": ("Increased Durability", "common/static_modifiers"),
    "nsc.requires.asteroid": ("Requires an asteroid in the system", "common/starbase_modules"),
}


def fix_text(layers: Layers) -> Made:
    have = layers.localisation()
    deposits = layers.defined("common/deposits")
    lines: dict[str, str] = {}
    for key in DEPOSITS:
        if key in deposits:
            data = layers.read(*deposits[key])
            entry = next(e for e in scan(data) if e.key == key.encode())
            amount = re.search(rb"sr_dark_matter\s*=\s*([\d.]+)", data[entry.value : entry.end])
            if amount:
                lines[key] = f"£sr_dark_matter£ +{amount.group(1).decode()}"
    for key, (text, folder) in TEXT.items():
        if _named(layers, folder, key):
            lines[key] = text
    notes = [f"{k}: already has text, skipped" for k in lines if k in have]
    lines = {k: v for k, v in lines.items() if k not in have}
    if not lines:
        raise FixError("Every key has text now, or nothing uses it.")
    body = "".join(f' {k}:0 "{v}"\n' for k, v in lines.items())
    notes.append(f"{len(lines)} keys: {', '.join(lines)}")
    path = f"localisation/english/{TAIL}_l_english.yml"
    return {path: BOM + b"l_english:\n" + body.encode()}, notes


def _named(layers: Layers, folder: str, key: str) -> bool:
    """`folder` defines `key`, or one of its files names it in quotes."""
    if key in layers.defined(folder):
        return True
    quoted = f'"{key}"'.encode()
    return any(quoted in layers.read(*found) for found in layers.ordered(folder))


# 10. Planetary Diversity's text calls a function the game no longer has


OLD_CALL = "[GetAdministratorPluralWithIcon]"
BUREAUCRATS = "bureaucrat_type_plural_with_icon"  # the game's own name for them
# The modifier gets the game's own text. The tooltips keep Planetary Diversity's,
# with the old call swapped for the game's key.
MODIFIER = "mod_planet_bureaucrats_unity_produces_mult"
NECRO_TOOLTIPS = (
    "pd_necro_planet_tooltip",
    "pd_aw_necro_planet_tooltip",
    "pd_aw_necro_city_planet_tooltip",
)


def fix_pd_bureaucrats(layers: Layers) -> Made:
    """A replace/ file, which beats text outside replace/ whatever its name.
    Each key is fixed when any English text outside replace/ still calls the
    old function, whichever wins. The long-session log shows Planetary
    Diversity's modifier text in play, though merge_rules.json says the game's
    file wins by sorting first."""
    texts, replaced = _english_texts(layers)
    game = {k: v[0][1] for k, v in _english_texts(layers, GAME)[0].items()}
    if BUREAUCRATS not in game:
        raise FixError(f"The game no longer has {BUREAUCRATS}.")
    lines: dict[str, str] = {}
    notes: list[str] = []
    for key in (MODIFIER, *NECRO_TOOLTIPS):
        if key in replaced:
            raise FixError(f"{key} is in a replace/ file now. Check it again.")
        broken = [text for _, text in texts.get(key, []) if OLD_CALL in text]
        if not broken:
            notes.append(f"{key}: doesn't call {OLD_CALL} now. Skipped.")
            continue
        if key == MODIFIER:
            if key not in game:
                raise FixError(f"The game has no text for {key} any more.")
            lines[key] = game[key]
            notes.append(f"{key}: the game's own text")
        else:
            lines[key] = broken[0].replace(OLD_CALL, f"${BUREAUCRATS}$")
            notes.append(f"{key}: {OLD_CALL} → ${BUREAUCRATS}$")
    if not lines:
        raise FixError(f"No text calls {OLD_CALL} now.")
    body = "".join(f' {k}:0 "{v}"\n' for k, v in lines.items())
    path = f"localisation/replace/{TAIL}_l_english.yml"
    return {path: BOM + b"l_english:\n" + body.encode()}, notes


def _english_texts(
    layers: Layers, only: str = ""
) -> tuple[dict[str, list[tuple[str, str]]], set[str]]:
    """Each English key outside replace/ to its (layer, text) definitions, by
    file name. Also every key some replace/ file defines. `only` limits both
    to one layer."""
    texts: dict[str, list[tuple[str, str]]] = {}
    replaced: set[str] = set()
    for layer, path in layers.ordered("localisation", ".yml"):
        if only and layer != only:
            continue
        data = layers.read(layer, path)
        if language(data) != "l_english":
            continue
        in_replace = "/replace/" in path.casefold()
        for entry in keys(data):
            key = entry.key.decode("utf-8", "replace")
            if in_replace:
                replaced.add(key)
                continue
            text = data[entry.value + 1 : entry.end].decode("utf-8", "replace")
            texts.setdefault(key, []).append((layer, text[: text.rfind('"')]))
    return texts, replaced


# 11 and 12. More Events Mod's own event bugs. Each ships a mended copy of one
# event in a file that sorts first, as the first event with an id wins.


ZIASKEHORN = "mem_scfe_ziaskehorn.1"  # fires .2 before saving the planet .2 uses
GLACIER = "mem_stuck_in_glacier.22"  # makes an official with a commander trait
_EVENT_TARGET = re.compile(rb"event_target:(\w+)")


def fix_ziaskehorn(layers: Layers) -> Made:
    """Moves the planet's `save_event_target_as` above the call that fires the
    discovery event, so the discovery finds the planet and makes the dig site."""
    event = _event(layers, ZIASKEHORN)
    entry = next(e for e in scan(event) if e.block)
    moved: list[str] = []
    for block in (entry, *_blocks(event, entry)):
        inner = children(event, block)
        for i, fire in enumerate(inner):
            fired = value_of(event, fire, b"id") if fire.key.endswith(b"_event") else None
            if fired is None:
                continue
            needs = set(_EVENT_TARGET.findall(_event(layers, fired.decode())))
            late = [s for s in inner[i + 1 :] if _saves(event, s) & needs]
            if late:
                names = ", ".join(sorted(n.decode() for s in late for n in _saves(event, s)))
                event = _move_above(event, late, fire)
                moved.append(f"{ZIASKEHORN}: saves {names} before firing {fired.decode()}")
                break
        if moved:
            break
    if not moved:
        raise FixError(f"{ZIASKEHORN} saves its targets before firing the next event now.")
    return {_first_file(layers, "events", "ziaskehorn"): event}, moved


def fix_glacier_leader(layers: Layers) -> Made:
    """A leader made with a trait its class can't have gets the one class the
    trait allows, so it keeps the trait the mod gave it."""
    event = _event(layers, GLACIER)
    entry = next(e for e in scan(event) if e.block)
    traits = layers.defined("common/traits")
    edits: list[tuple[int, int, bytes]] = []
    notes: list[str] = []
    for leader in _blocks(event, entry):
        if leader.key != b"create_leader":
            continue
        inner = children(event, leader)
        cls = next((c for c in inner if c.key.lower() == b"class" and not c.block), None)
        given = [
            _text(event, t)
            for block in inner
            if block.key == b"traits" and block.block
            for t in children(event, block)
            if t.key == b"trait" and not t.block
        ]
        if cls is None or not given:
            continue
        now = _text(event, cls)
        allowed = set.intersection(*(_leader_classes(layers, traits, t) for t in given))
        if now in allowed:
            continue
        if len(allowed) != 1:
            raise FixError(f"{GLACIER}: no one class can have {', '.join(given)}.")
        new = allowed.pop()
        edits.append((cls.value, cls.end, new.encode()))
        notes.append(f"{GLACIER}: the {now} with {', '.join(given)} is a {new} now")
    if not edits:
        raise FixError(f"Every leader {GLACIER} makes can have its traits now.")
    out = bytearray(event)
    for start, end, new_value in sorted(edits, reverse=True):
        out[start:end] = new_value
    return {_first_file(layers, "events", "stuck_in_glacier"): bytes(out)}, notes


def _event(layers: Layers, event_id: str) -> bytes:
    """The event the game uses, the first by file name, with its namespace
    line before it and Unix line ends. Raises FixError
    unless More Events Mod's copy is the one used."""
    data, entry = _event_entry(layers, event_id)
    namespace = event_id.rpartition(".")[0]
    text = f"namespace = {namespace}\n\n".encode() + data[entry.start : entry.end]
    return text.replace(b"\r\n", b"\n") + b"\n"


def _event_entry(layers: Layers, event_id: str) -> tuple[bytes, Entry]:
    """The event the game uses, in the file it's in. Raises FixError unless
    More Events Mod's copy is the one used."""
    wanted = event_id.encode()
    for layer, path in layers.ordered("events"):
        data = layers.read(layer, path)
        if wanted not in data:
            continue
        for entry in scan(data):
            if entry.block and value_of(data, entry, b"id") == wanted:
                if layer != MORE_EVENTS:
                    raise FixError(f"{event_id} now comes from {layer}, not More Events Mod.")
                return data, entry
    raise FixError(f"No event is called {event_id} any more.")


def _first_file(layers: Layers, folder: str, what: str) -> str:
    """A path in `folder` whose file name sorts before every other there."""
    rivals = [p.rpartition("/")[2] for _, p in layers.ordered(folder)]
    name = winning_name(rivals, f"{TAIL}_{what}.txt", first=True)
    if name is None:
        raise FixError(f"No file name sorts before the other {folder} files.")
    return f"{folder}/{name}"


def _blocks(data: bytes, entry: Entry) -> list[Entry]:
    """Every named block inside `entry`, at any depth, in order."""
    found: list[Entry] = []
    for child in children(data, entry):
        if child.block:
            found += [child, *_blocks(data, child)]
    return found


def _saves(data: bytes, entry: Entry) -> set[bytes]:
    """The event targets `entry` saves, directly or in a block inside it."""
    saves = [entry] if not entry.block else [*children(data, entry), *_blocks(data, entry)]
    return {
        data[s.value : s.end].strip(b'"')
        for s in saves
        if s.key == b"save_event_target_as" and not s.block
    }


def _move_above(data: bytes, moving: list[Entry], above: Entry) -> bytes:
    """`data` with the whole lines of `moving` moved to just above `above`'s line.
    Each of `moving` comes after `above`."""
    at = data.rfind(b"\n", 0, above.start) + 1
    spans = []
    for entry in moving:
        start = data.rfind(b"\n", 0, entry.start) + 1
        end = data.find(b"\n", entry.end)
        spans.append((start, len(data) if end == -1 else end + 1))
    lifted = b"".join(data[s:e] for s, e in spans)
    out = bytearray(data)
    for start, end in sorted(spans, reverse=True):
        del out[start:end]
    out[at:at] = lifted
    return bytes(out)


def _leader_classes(layers: Layers, traits: dict[str, tuple[str, str]], trait: str) -> set[str]:
    """The leader classes the game lets have `trait`."""
    if trait not in traits:
        raise FixError(f"No trait is called {trait} any more.")
    data = layers.read(*traits[trait])
    entry = next(e for e in scan(data) if e.key == trait.encode())
    found = next((c for c in children(data, entry) if c.key == b"leader_class" and c.block), None)
    if found is None:
        raise FixError(f"{trait} doesn't say which leaders can have it.")
    start, end = found.inside
    return {w.decode() for w in _COMMENT.sub(b"", data[start:end]).split()}


def _copy(layers: Layers, data: bytes, entry: Entry, body: bytes) -> bytes:
    """`body`, a mended copy of `entry` from `data`, ready for a file of its
    own: Unix line ends, and the variables of `entry`'s file that it uses
    defined above it. Raises FixError for a variable nothing defines."""
    header = "".join(f"{n} = {v}\n" for n, v in _copied_variables(layers, data, entry, body))
    text = (header + "\n" if header else "").encode() + body
    return text.replace(b"\r\n", b"\n") + b"\n"


def _copied_variables(
    layers: Layers, data: bytes, entry: Entry, body: bytes
) -> list[tuple[str, str]]:
    """The variables of `entry`'s file that `body`, a copy of it, uses, with
    their values. Raises FixError for a variable nothing defines."""
    file_vars = _variables(data)
    shared = layers.defined("common/scripted_variables")
    found: list[tuple[str, str]] = []
    for name in sorted({"@" + m.decode() for m in _VARIABLE.findall(_COMMENT.sub(b"", body))}):
        if name in file_vars:
            found.append((name, _text(data, file_vars[name])))
        elif name not in shared:
            raise FixError(f"{entry.key.decode()} uses {name}, which nothing defines.")
    return found


def _game_entry(layers: Layers, folder: str, key: str) -> tuple[bytes, Entry]:
    """The game's own definition of `key`, even where a mod replaced its file."""
    for path in layers.paths(GAME, folder):
        data = layers.read(GAME, path)
        for entry in scan(data):
            if entry.key == key.encode() and entry.block:
                return data, entry
    raise FixError(f"The game has no {key} any more.")


def _edit(data: bytes, edits: list[tuple[int, int, bytes]]) -> bytes:
    out = bytearray(data)
    for start, end, new in sorted(edits, reverse=True):
        out[start:end] = new
    return bytes(out)


def _mended(data: bytes, entry: Entry, edits: list[tuple[int, int, bytes]]) -> bytes:
    """`entry`, key and all, with `edits` made inside it."""
    grown = sum(len(new) - (end - start) for start, end, new in edits)
    return _edit(data, edits)[entry.start : entry.end + grown]


# 15. More Events Mod's shield upkeep, by the names 4.5.2 renamed


COMPONENTS = "common/component_templates"
# 4.5.2: "Shield upkeep scripted variables are renamed to the shared
# @defense_<size>_t<N>_upkeep_* family."
_OLD_UPKEEP = re.compile(r"^@shield_(\w+_upkeep_\w+)$")


def fix_shield_upkeep(layers: Layers) -> Made:
    """Defines each old shield upkeep name a component still uses, with the
    game's value for its new name."""
    shared = layers.defined("common/scripted_variables")
    used: dict[str, set[str]] = {}  # old name -> the mods that use it
    for layer, path in layers.ordered(COMPONENTS):
        data = layers.read(layer, path)
        own = _variables(data)
        for match in _VARIABLE.findall(_COMMENT.sub(b"", data)):
            name = "@" + match.decode()
            if _OLD_UPKEEP.match(name) and name not in own and name not in shared:
                used.setdefault(name, set()).add(layer)
    if not used:
        raise FixError("No component uses an old shield upkeep name now.")
    game: dict[str, str] = {}
    for path in layers.paths(GAME, "common/scripted_variables"):
        data = layers.read(GAME, path)
        game |= {k: _text(data, e) for k, e in _variables(data).items()}
    lines: list[str] = []
    for old in sorted(used):
        new = _OLD_UPKEEP.sub(r"@defense_\1", old)
        if not re.fullmatch(r"[\d.]+", game.get(new, "")):
            raise FixError(f"The game has no number for {new}, which {old} became.")
        lines.append(f"{old} = {game[new]}\n")
    header = "# Old names some mods still use: the game's values for their 4.5.2 names.\n"
    notes = [f"{len(lines)} names: {', '.join(sorted(used))}"]
    return {
        f"common/scripted_variables/{TAIL}_shield_upkeep.txt": (header + "".join(lines)).encode()
    }, notes


# 16. Ships in Scaling's range for the Large Mega Bombard


MUTATION_WEAPONS = "common/component_templates/mutation_weapon_components.csv"


def fix_mutation_ranges(layers: Layers) -> Made:
    """Ships in Scaling's whole file, as a .csv is replaced only whole, with
    each range it missed set the way it scales the rest: to the range it gives
    every other weapon with the same game range, when at least two others
    agree. 4.5.2 gave the Large Mega Bombard its range, and Ships in Scaling's
    copy is older."""
    _expect_winner(layers, MUTATION_WEAPONS, SHIPS_IN_SCALING, "Ships in Scaling")
    data = layers.read(SHIPS_IN_SCALING, MUTATION_WEAPONS)
    mod, game = _csv(data), _csv(layers.read(GAME, MUTATION_WEAPONS))
    column = _csv_column(mod, "range")
    if _csv_column(game, "range") != column:
        raise FixError(f"{MUTATION_WEAPONS}'s columns differ from the game's.")
    pairs = [  # (key, the game's range, Ships in Scaling's range, its row)
        (key, game[key][0][column], cells[column], (cells, span))
        for key, (cells, span) in mod.items()
        if key in game and key != "key" and len(cells) > column and len(game[key][0]) > column
    ]
    edits: list[tuple[int, int, bytes]] = []
    notes: list[str] = []
    for key, was, now, (cells, (start, end)) in pairs:
        others = [n for k, w, n, _ in pairs if w == was and k != key]
        if len(others) < 2 or len(set(others)) != 1 or now == others[0]:
            continue
        want = others[0]
        line = b";".join(want if i == column else c for i, c in enumerate(cells))
        edits.append((start, end, line))
        notes.append(
            f"{key}: range {now.decode()} → {want.decode()}, as for the game's {was.decode()}"
        )
    if not edits:
        raise FixError("Every range in Ships in Scaling's copy follows its own scaling now.")
    return {MUTATION_WEAPONS: _edit(data, edits)}, notes


def _csv(data: bytes) -> dict[str, tuple[list[bytes], tuple[int, int]]]:
    """A component .csv's rows: the first cell to the cells and where the row
    is, without its line end. Comment lines are left out."""
    rows: dict[str, tuple[list[bytes], tuple[int, int]]] = {}
    at = 0
    for line in data.splitlines(keepends=True):
        text = line.rstrip(b"\r\n")
        if text.strip() and not text.lstrip(BOM).startswith(b"#"):
            cells = text.split(b";")
            rows.setdefault(
                cells[0].lstrip(BOM).decode("utf-8", "replace"), (cells, (at, at + len(text)))
            )
        at += len(line)
    return rows


def _csv_column(rows: dict[str, tuple[list[bytes], tuple[int, int]]], name: str) -> int:
    header = rows.get("key")
    if header is None or name.encode() not in header[0]:
        raise FixError(f"{MUTATION_WEAPONS} has no {name} column.")
    return header[0].index(name.encode())


# 17. Real Space's Surveillance Supercomputer system is still sealed


SUPERCOMPUTER = "surveillance_supercomputer_system"
SEALED = b"sealed_system"


def fix_supercomputer_seal(layers: Layers) -> Made:
    """Real Space's system, without the flag 4.5.2 took off the game's so jump
    drives can enter, in a file that sorts first: the first initializer by
    file name wins."""
    defined = layers.defined(INITIALIZERS)
    if SUPERCOMPUTER not in defined:
        raise FixError(f"No system is called {SUPERCOMPUTER} any more.")
    layer, path = defined[SUPERCOMPUTER]
    if layer != REAL_SPACE:
        raise FixError(f"{SUPERCOMPUTER} now comes from {layer}, not Real Space.")
    data = layers.read(layer, path)
    entry = next(e for e in scan(data) if e.key == SUPERCOMPUTER.encode() and e.block)
    if SEALED not in _flags(data, entry):
        raise FixError(f"Real Space's {SUPERCOMPUTER} isn't sealed now.")
    if SEALED in _flags(*_game_entry(layers, INITIALIZERS, SUPERCOMPUTER)):
        raise FixError(f"The game's {SUPERCOMPUTER} is sealed again.")
    flags = next(c for c in children(data, entry) if c.key == b"flags" and c.block)
    start, end = flags.inside
    unsealed = re.sub(rb"[ \t]*\b" + SEALED + rb"\b", b"", data[start:end])
    body = _mended(data, entry, [(start, end, unsealed)])
    comment = f"# Real Space's {SUPERCOMPUTER}, without {SEALED.decode()}, as in 4.5.2\n".encode()
    text = comment + _copy(layers, data, entry, body)
    return {_first_file(layers, INITIALIZERS, "supercomputer"): text}, [
        f"{SUPERCOMPUTER}: Real Space's copy, without {SEALED.decode()}"
    ]


def _flags(data: bytes, entry: Entry) -> set[bytes]:
    found = next((c for c in children(data, entry) if c.key == b"flags" and c.block), None)
    if found is None:
        return set()
    start, end = found.inside
    return set(_COMMENT.sub(b"", data[start:end]).split())


# 18. Trait resources still filed under planet_pops, which 4.5.2 keeps for species


POPS = b"planet_pops"
POPS_TRAITS = b"planet_pops_traits"
TRAIT_MODS = {
    PLANETARY_DIVERSITY: "Planetary Diversity",
    ASCENSION_WORLDS: "Ascension Worlds",
    MORE_EVENTS: "More Events Mod",
}
# 4.5.2: "The Shroud-Warped leader trait and the Unemployment Benefits modifier no
# longer scale with the number of traits a species has." An _add modifier applies
# once per resource table under its category, so each trait's table moved to
# planet_pops_traits. The archetype's stays on planet_pops.


def fix_trait_categories(layers: Layers) -> Made:
    """Copies of each trait in use that files its resources under planet_pops,
    with the game's planet_pops_traits instead, in a file that sorts first.
    A trait another fix copies is left to it."""
    if POPS_TRAITS.decode() not in layers.defined("common/economic_categories"):
        raise FixError(f"The game has no {POPS_TRAITS.decode()} category now.")
    copied_elsewhere = {BUDDING, AQUATIC}
    bodies: list[bytes] = []
    header: dict[str, str] = {}
    counts: dict[str, int] = {}  # mod name -> traits mended
    notes: list[str] = []
    for trait, (layer, path) in layers.defined("common/traits").items():
        data = layers.read(layer, path)
        entry = next((e for e in scan(data) if e.key == trait.encode() and e.block), None)
        if entry is None:
            continue
        edits = [
            (c.value, c.end, POPS_TRAITS)
            for table in children(data, entry)
            if table.key == b"resources" and table.block
            for c in children(data, table)
            if c.key == b"category" and data[c.value : c.end] == POPS
        ]
        if not edits:
            continue
        if trait in copied_elsewhere:
            notes.append(f"{trait} is copied by another fix. Skipped.")
            continue
        body = _mended(data, entry, edits)
        found = _copied_variables(layers, data, entry, body)
        if any(header.get(name, value) != value for name, value in found):
            notes.append(f"{trait} uses a variable another trait defines differently. Skipped.")
            continue
        header.update(found)
        bodies.append(body)
        mod = TRAIT_MODS.get(layer, layer)
        counts[mod] = counts.get(mod, 0) + 1
    if not bodies:
        raise FixError(f"No trait in use files its resources under {POPS.decode()} now.")
    top = "".join(f"{name} = {value}\n" for name, value in sorted(header.items()))
    text = ((top + "\n" if top else "").encode() + b"\n\n".join(bodies)).replace(b"\r\n", b"\n")
    mended = ", ".join(f"{n} from {mod}" for mod, n in counts.items())
    notes.insert(0, f"{sum(counts.values())} traits ({mended}) use {POPS_TRAITS.decode()}")
    return {_first_file(layers, "common/traits", "trait_categories"): text + b"\n"}, notes


# 19. Planetary Diversity's and Ascension Worlds' copies miss two of the game's fixes


BUDDING = "trait_lithoid_budding"
# Both ship a whole 04_species_traits.txt. Ascension Worlds' replaces Planetary Diversity's.
BUDDING_MODS = {PLANETARY_DIVERSITY: "Planetary Diversity", ASCENSION_WORLDS: "Ascension Worlds"}
POP_MODIFIER = b"triggered_planet_pop_group_modifier_for_species"
DIVIDE = b"divide_over_pop_groups"
GAME_RULES = "common/game_rules"
TERRAFORM = "can_terraform_planet"


def fix_ascension_worlds(layers: Layers) -> Made:
    """Lithoid Budding, from Planetary Diversity or Ascension Worlds, and
    Ascension Worlds' terraforming rule, with the game's lines they lack. A
    check Ascension Worlds comments out on purpose stays out."""
    files: dict[str, bytes] = {}
    notes: list[str] = []
    for part in (_budding, _terraform):
        try:
            path, data, note = part(layers)
        except FixError as why:
            notes.append(f"{why} Skipped.")
            continue
        files[path] = data
        notes.append(note)
    if not files:
        raise FixError("The trait and rule match the game's now.")
    return files, notes


def _budding(layers: Layers) -> tuple[str, bytes, str]:
    """Each of the trait's pop modifiers gets the game's `divide_over_pop_groups`
    where it lacks one. 4.5.2 gave the Massive Crater's its full bonus."""
    traits = layers.defined("common/traits")
    owner = traits.get(BUDDING, ("",))[0]
    if owner not in BUDDING_MODS:
        raise FixError(f"{BUDDING} doesn't come from Planetary Diversity or Ascension Worlds now.")
    data = layers.read(*traits[BUDDING])
    entry = next(e for e in scan(data) if e.key == BUDDING.encode() and e.block)
    game_data, game_entry = _game_entry(layers, "common/traits", BUDDING)
    theirs = [c for c in children(data, entry) if c.key == POP_MODIFIER and c.block]
    ours = [c for c in children(game_data, game_entry) if c.key == POP_MODIFIER and c.block]
    if len(theirs) != len(ours):
        raise FixError(f"{BUDDING} has {len(theirs)} pop modifiers, the game's {len(ours)}.")
    edits: list[tuple[int, int, bytes]] = []
    for mod, game in zip(theirs, ours, strict=True):
        want = next((c for c in children(game_data, game) if c.key == DIVIDE), None)
        if want is None or any(c.key == DIVIDE for c in children(data, mod)):
            continue
        after = next((c for c in children(data, mod) if c.key == b"potential"), None)
        at = after.end if after is not None else mod.inside[0]
        edits.append((at, at, b"\n\t\t" + game_data[want.start : want.end]))
    if not edits:
        raise FixError(f"{BUDDING}'s pop modifiers divide as the game's do now.")
    text = _copy(layers, data, entry, _mended(data, entry, edits))
    note = (
        f"{BUDDING}, from {BUDDING_MODS[owner]}: {len(edits)} pop modifier gets the game's "
        f"{DIVIDE.decode()}"
    )
    return _first_file(layers, "common/traits", "lithoid_budding"), text, note


def _terraform(layers: Layers) -> tuple[str, bytes, str]:
    """The rule gets each of the game's custom tooltips it lacks, by fail
    text. One it has in a comment was taken out on purpose, and stays out."""
    found = _game_rule(layers, TERRAFORM)
    if found is None or found[0] != ASCENSION_WORLDS:
        raise FixError(f"{TERRAFORM} doesn't come from Ascension Worlds now.")
    _, data, entry = found
    game_data, game_entry = _game_entry(layers, GAME_RULES, TERRAFORM)
    have = {_fail_text(data, c) for c in children(data, entry)}
    written = data[entry.start : entry.end]  # comments included
    added: dict[str, bytes] = {}  # fail text -> the game's check
    kept_out: list[str] = []
    for check in children(game_data, game_entry):
        text = _fail_text(game_data, check)
        if not text or text in have:
            continue
        if text.encode() in written:
            kept_out.append(text)
            continue
        added[text] = game_data[check.start : check.end]
    if not added:
        raise FixError(f"{TERRAFORM} has every game check it doesn't leave out on purpose now.")
    at = entry.inside[0]
    insert = b"".join(b"\n\t" + check + b"\n" for check in added.values())
    body = _mended(data, entry, [(at, at, insert)])
    note = f"{TERRAFORM}: adds {', '.join(added)}"
    if kept_out:
        note += f"; keeps out {', '.join(kept_out)}, as Ascension Worlds chose"
    return _last_file(layers, GAME_RULES, "terraform"), _copy(layers, data, entry, body), note


def _game_rule(layers: Layers, rule: str) -> tuple[str, bytes, Entry] | None:
    return _last_definition(layers, GAME_RULES, rule)


def _last_definition(layers: Layers, folder: str, key: str) -> tuple[str, bytes, Entry] | None:
    """The definition the game uses in a folder where the last by file name
    wins, with its layer and the file it's in."""
    found: tuple[str, bytes, Entry] | None = None
    for layer, path in layers.ordered(folder):
        data = layers.read(layer, path)
        for entry in scan(data):
            if entry.key == key.encode() and entry.block:
                found = (layer, data, entry)
    return found


def _fail_text(data: bytes, check: Entry) -> str:
    if check.key != b"custom_tooltip" or not check.block:
        return ""
    return (value_of(data, check, b"fail_text") or b"").decode().strip('"')


# 25. Lines in Planetary Diversity's translations the game can't read


TEXT_MODS = {
    PLANETARY_DIVERSITY: "Planetary Diversity",
    ASCENSION_WORLDS: "Ascension Worlds",
    MORE_ARCOLOGIES: "More Arcologies",
}
_LINE = re.compile(r'^\s*([^\s:#"]+)\s*:\s*\d*\s*"(.*)"\s*(?:#.*)?$')
_NO_CLOSE = re.compile(r'^\s*([^\s:#"]+)\s*:\s*\d*\s*"[^"]*$')
_NO_OPEN = re.compile(r'^\s*([^\s:#"]+)\s*:\s*\d*\s*()[^"\s][^"]*"$')


def fix_broken_text(layers: Layers) -> Made:
    """Each of the mods' localisation files with a line the game can't read,
    whole, with the line mended. A whole file at the same path replaces the
    mod's. A replace/ file couldn't: the mod's broken line would still be read."""
    present = {layer.key for layer in layers.layers}
    files: dict[str, bytes] = {}
    notes: list[str] = []
    for mod, name in TEXT_MODS.items():
        if mod not in present:
            continue
        english = [
            [e.key.decode("utf-8", "replace") for e in keys(layers.read(mod, path))]
            for path in layers.paths(mod, "localisation", ".yml")
            if language(layers.read(mod, path)) == "l_english"
        ]
        for path in layers.paths(mod, "localisation", ".yml"):
            data = layers.read(mod, path)
            if not language(data):
                continue
            try:
                mended, changes = mend_text(data, english)
            except FixError as why:
                notes.append(f"{path}: {why} Skipped.")
                continue
            if not changes:
                continue
            if (winner := layers.winner(path)) != mod:
                notes.append(f"{path} now comes from {winner}, not {name}. Skipped.")
                continue
            files[path] = mended
            notes += [f"{path}: {change}" for change in changes]
    if not files:
        raise FixError("The game can read every line of their text files now.")
    return files, notes


def mend_text(data: bytes, english: Sequence[list[str]]) -> tuple[bytes, list[str]]:
    """A localisation file with each line the game can't read mended, and what
    was done. Text that starts with its own key again, as a bad paste left in
    several of Planetary Diversity's translations, loses the copy. `english` is
    the mod's English keys, file by file, in order: a line of text with no key
    gets the key the English file has in its place. Raises FixError for a line
    no rule mends."""
    start = len(BOM) if data.startswith(BOM) else 0
    try:
        lines = data[start:].decode("utf-8").splitlines(keepends=True)
    except UnicodeDecodeError as error:
        raise FixError(f"Isn't UTF-8 at byte {error.start}.") from error
    bodies = [line.rstrip("\r\n") for line in lines]
    named = [
        found.group(1)
        if (found := _LINE.match(b) or _NO_CLOSE.match(b) or _NO_OPEN.match(b))
        else None
        for b in bodies
    ]
    have = {key for key in named if key}
    out: list[str] = []
    changes: list[str] = []
    header = False
    for i, (line, body) in enumerate(zip(lines, bodies, strict=True)):
        end, stripped, n = line[len(body) :], body.strip(), i + 1
        if not stripped or stripped.startswith("#"):
            out.append(line)
        elif not header:  # the language line
            header = True
            out.append(line)
        elif found := _LINE.match(body):
            key, value = found.group(1), found.group(2)
            doubled = re.match(rf'\s*{re.escape(key)}\s*:\s*\d*\s*"', value)
            if doubled:
                at = found.start(2)
                out.append(body[:at] + value[doubled.end() :] + body[found.end(2) :] + end)
                changes.append(f"line {n}: {key}'s text no longer starts with its own key")
            else:
                out.append(line)
        elif stripped == '"':
            changes.append(f"line {n}: a stray quote taken out")
        elif found := _NO_CLOSE.match(body):
            out.append(body.rstrip() + '"' + end)
            changes.append(f"line {n}: {found.group(1)}'s closing quote added")
        elif found := _NO_OPEN.match(body):
            at = found.start(2)
            out.append(body[:at] + '"' + body[at:] + end)
            changes.append(f"line {n}: {found.group(1)}'s opening quote added")
        else:
            before = next((k for k in reversed(named[:i]) if k), None)
            after = next((k for k in named[i + 1 :] if k), None)
            key = _english_key(english, before, after, have)
            if key is None:
                raise FixError(f"Line {n} has no key, and the English text doesn't say which.")
            indent, text = body[: len(body) - len(body.lstrip())], stripped.strip('"')
            out.append(f'{indent}{key}: "{text}"{end}')
            changes.append(f"line {n}: the text gets its key, {key}, from the English file")
    return data[:start] + "".join(out).encode(), changes


def _english_key(
    english: Sequence[list[str]], before: str | None, after: str | None, have: set[str]
) -> str | None:
    """The key an English file has between `before` and `after`, if this file lacks it."""
    for order in english:
        if before is None or before not in order:
            continue
        at = order.index(before) + 1
        if at < len(order) and order[at] not in have and order[at + 1 : at + 2] in ([after], []):
            return order[at]
    return None


# 26. More Events Mod's Under the Blanket story picks leaders the game won't give
# its traits, and starts for Fallen Empires


BLANKET_START = "mem_under_blanket.1"  # starts the story for any empire but a homicidal one
BLANKET_PICKS = "mem_under_blanket.2"  # picks its scientists, an autocracy's ruler and heir too
NORMAL_TRAIT = "can_leader_get_normal_trait"  # the game rule that refuses those two normal traits
NORMAL_TRAIT_CHECK = b"can_leader_get_normal_trait_trigger"  # the trigger the rule calls
NORMAL_EMPIRE = b"Root.Owner = { is_country_type = default }"  # as the game's Strange Worlds


def fix_under_blanket(layers: Layers) -> Made:
    """Copies of the story's first two events, in a file that sorts first. Its
    scientist picks leave out leaders the game won't give a normal trait, so the
    traits its endings give stick. It starts only for normal empires."""
    events: list[bytes] = []
    notes: list[str] = []
    for part in (_blanket_start, _blanket_picks):
        try:
            event, note = part(layers)
        except FixError as why:
            notes.append(f"{why} Skipped.")
            continue
        events.append(event)
        notes.append(note)
    if not events:
        raise FixError(
            "The story starts only for normal empires, and picks leaders who can take "
            "its traits, now."
        )
    namespace = BLANKET_PICKS.rpartition(".")[0]
    text = f"namespace = {namespace}\n\n".encode() + b"\n".join(events)
    return {_first_file(layers, "events", "under_blanket"): text}, notes


def _blanket_start(layers: Layers) -> tuple[bytes, str]:
    data, entry = _event_entry(layers, BLANKET_START)
    trigger = next((c for c in children(data, entry) if c.key == b"trigger" and c.block), None)
    if trigger is None:
        raise FixError(f"{BLANKET_START} has no trigger now.")
    if b"is_country_type" in _COMMENT.sub(b"", data[trigger.start : trigger.end]):
        raise FixError(f"{BLANKET_START} checks the empire's type now.")
    at = trigger.inside[0]
    body = _mended(data, entry, [(at, at, b"\n\t\t" + NORMAL_EMPIRE)])
    return _copy(layers, data, entry, body), f"{BLANKET_START}: starts only for normal empires"


def _blanket_picks(layers: Layers) -> tuple[bytes, str]:
    """Each block that picks a scientist gets the game's check beside it."""
    rule = _game_rule(layers, NORMAL_TRAIT)
    if rule is None or NORMAL_TRAIT_CHECK not in _COMMENT.sub(
        b"", rule[1][rule[2].start : rule[2].end]
    ):
        raise FixError(
            f"The game rule {NORMAL_TRAIT} doesn't call {NORMAL_TRAIT_CHECK.decode()} now."
        )
    if NORMAL_TRAIT_CHECK.decode() not in layers.defined("common/scripted_triggers"):
        raise FixError(f"Nothing defines {NORMAL_TRAIT_CHECK.decode()} now.")
    data, entry = _event_entry(layers, BLANKET_PICKS)
    immediate = next((c for c in children(data, entry) if c.key == b"immediate" and c.block), None)
    if immediate is None:
        raise FixError(f"{BLANKET_PICKS} has no immediate block now.")
    edits: list[tuple[int, int, bytes]] = []
    for block in _blocks(data, immediate):
        inner = children(data, block)
        if any(c.key == NORMAL_TRAIT_CHECK for c in inner):
            continue
        for c in inner:
            if c.key == b"leader_class" and not c.block and _text(data, c) == "scientist":
                before = data[data.rfind(b"\n", 0, c.start) + 1 : c.start]
                gap = b" " if before.strip() else b"\n" + before  # on its own line, or not
                edits.append((c.end, c.end, gap + NORMAL_TRAIT_CHECK + b" = yes"))
    if not edits:
        raise FixError(f"{BLANKET_PICKS} picks only leaders who can take normal traits now.")
    body = _mended(data, entry, edits)
    note = (
        f"{BLANKET_PICKS}: {len(edits)} scientist picks leave out an autocracy's ruler "
        f"and heir, who can't take normal traits ({NORMAL_TRAIT})"
    )
    return _copy(layers, data, entry, body), note


# 27. Planetary Diversity's Aquatic trait misses the game's 4.5.2 AI weight


AQUATIC = "trait_aquatic"
# 4.5.2: "The AI now values the Aquatic trait on species that use the Wet Climate
# Mods planet preference."
_HAS_TRAIT = re.compile(rb"has_trait\s*=\s*(\w+)")


def fix_aquatic(layers: Layers) -> Made:
    """A copy of Planetary Diversity's Aquatic trait with the game's AI weight,
    in a file that sorts first. Only while the two weights differ by the traits
    the game's checks and nothing else, so no choice of theirs is undone."""
    traits = layers.defined("common/traits")
    if traits.get(AQUATIC, ("",))[0] != PLANETARY_DIVERSITY:
        raise FixError(f"{AQUATIC} doesn't come from Planetary Diversity now.")
    data = layers.read(*traits[AQUATIC])
    entry = next(e for e in scan(data) if e.key == AQUATIC.encode() and e.block)
    game_data, game_entry = _game_entry(layers, "common/traits", AQUATIC)
    theirs = _ai_weight(data, entry)
    ours = _ai_weight(game_data, game_entry)
    their_text = _COMMENT.sub(b"", data[theirs.start : theirs.end])
    game_text = _COMMENT.sub(b"", game_data[ours.start : ours.end])
    added = sorted(set(_HAS_TRAIT.findall(game_text)) - set(_HAS_TRAIT.findall(their_text)))
    if not added:
        raise FixError(f"{AQUATIC}'s ai_weight checks every trait the game's does now.")
    without = _HAS_TRAIT.sub(lambda m: b"" if m[1] in added else m[0], game_text)
    if _weight_words(without) != _weight_words(their_text):
        raise FixError(f"{AQUATIC}'s ai_weight differs from the game's in more than its traits.")
    body = _mended(data, entry, [(theirs.start, theirs.end, game_data[ours.start : ours.end])])
    path = _first_file(layers, "common/traits", "aquatic")
    named = ", ".join(t.decode() for t in added)
    note = f"{AQUATIC}, from Planetary Diversity: its ai_weight gets the game's {named}"
    return {path: _copy(layers, data, entry, body)}, [note]


def _weight_words(text: bytes) -> list[bytes]:
    """`text`'s words, with NOT read as NOR: the game reads a NOT of several
    checks as NOR, and Planetary Diversity's copy has NOT of one."""
    return [b"NOR" if w == b"NOT" else w for w in text.split()]


def _ai_weight(data: bytes, entry: Entry) -> Entry:
    found = next((c for c in children(data, entry) if c.key == b"ai_weight" and c.block), None)
    if found is None:
        raise FixError(f"{AQUATIC} has no ai_weight in one of its copies now.")
    return found


# 28. shrimpAI's Hyper Relay misses the game's 4.5.2 clause for Nomadic empires


MEGASTRUCTURES = "common/megastructures"
HYPER_RELAY = "hyper_relay"
# 4.5.2: "Fixed Gateways, Hyper-Relays and the Grand Archive not being buildable by
# Nomadic empires in some cases." The game's surveyed-system check lets an empire
# build at its own waystation. shrimpAI's copy, from 4.5.1, doesn't.


def fix_hyper_relay(layers: Layers) -> Made:
    """A copy of shrimpAI's Hyper Relay, in a file that sorts last, with each
    clause it lacks from the game's own `possible` checks: in each custom
    tooltip's OR, matched by fail text. shrimpAI's own clauses stay."""
    found = _last_definition(layers, MEGASTRUCTURES, HYPER_RELAY)
    if found is None or found[0] != SHRIMPAI:
        raise FixError(f"{HYPER_RELAY} doesn't come from shrimpAI now.")
    _, data, entry = found
    game_data, game_entry = _game_entry(layers, MEGASTRUCTURES, HYPER_RELAY)
    theirs = _tooltip_ors(data, entry)
    edits: list[tuple[int, int, bytes]] = []
    added: list[str] = []
    for text, game_or in _tooltip_ors(game_data, game_entry).items():
        if text not in theirs:
            continue
        their_or = theirs[text]
        have = {_clause(data, c) for c in children(data, their_or)}
        anchor: Entry | None = None  # shrimpAI's copy of the game clause before it
        for clause in children(game_data, game_or):
            words = _clause(game_data, clause)
            if words in have:
                anchor = next(c for c in children(data, their_or) if _clause(data, c) == words)
                continue
            first = anchor or next(iter(children(data, their_or)), None)
            at = _line_end(data, anchor, their_or) if anchor else their_or.inside[0]
            indent = _indent(data, first) if first else b"\t"
            edits.append((at, at, b"\n" + indent + game_data[clause.start : clause.end]))
            added.append(text)
    if not edits:
        raise FixError(f"{HYPER_RELAY}'s checks have every clause the game's do now.")
    body = _mended(data, entry, edits)
    path = _last_file(layers, MEGASTRUCTURES, "hyper_relay")
    tooltips = ", ".join(sorted(set(added)))
    note = f"{HYPER_RELAY}, from shrimpAI: adds the game's clause to {tooltips}"
    return {path: _copy(layers, data, entry, body)}, [note]


def _tooltip_ors(data: bytes, entry: Entry) -> dict[str, Entry]:
    """Each custom tooltip's OR in `entry`'s `possible`, at any depth, by fail text."""
    possible = next((c for c in children(data, entry) if c.key == b"possible" and c.block), None)
    if possible is None:
        return {}
    found: dict[str, Entry] = {}
    for tooltip in _blocks(data, possible):
        text = _fail_text(data, tooltip)
        either = next((c for c in children(data, tooltip) if c.key == b"OR" and c.block), None)
        if text and either is not None:
            found[text] = either
    return found


def _clause(data: bytes, entry: Entry) -> bytes:
    """`entry`'s text without comments or spacing, to compare two copies."""
    return b"".join(_COMMENT.sub(b"", data[entry.start : entry.end]).split())


def _indent(data: bytes, entry: Entry) -> bytes:
    line = data.rfind(b"\n", 0, entry.start) + 1
    return data[line : entry.start]


def _line_end(data: bytes, entry: Entry, inside: Entry) -> int:
    """The end of `entry`'s line, past any comment on it, or `entry`'s own end
    when `inside` closes on that line."""
    end = data.find(b"\n", entry.end)
    if end == -1 or end > inside.inside[1]:
        return entry.end
    return end - 1 if data[end - 1 : end] == b"\r" else end


# 29. Starbase Extended's module bonuses check buildings nothing defines


STARBASE_MODULES = "common/starbase_modules"
STARBASE_BUILDINGS = "common/starbase_buildings"
# Each missing building, to Starbase Extended's own building of its kind (decision 46).
# Its Asteroid Mining checks mining_manager, and its Space Foundry and Space Factory
# check assembly_line_manufacturing. Mining Experts needs Asteroid Mining, and Chain
# Manufacturing boosts alloys and consumer goods.
SBX_BUILDINGS = {
    "mining_manager": "mining_experts",
    "assembly_line_manufacturing": "chain_manufacturing",
}
_HAS_BUILDING = re.compile(rb"\bhas_starbase_building\s*=\s*(\w+)")


def fix_sbx_bonus_buildings(layers: Layers) -> Made:
    """Copies of Starbase Extended's modules whose bonuses check a building
    nothing defines, checking its own building of that kind instead, in a file
    that sorts last. A missing building that's defined now is left alone."""
    buildings = layers.defined(STARBASE_BUILDINGS)
    swaps: dict[bytes, bytes] = {}
    skipped: list[str] = []
    for old, new in SBX_BUILDINGS.items():
        if old in buildings:
            skipped.append(f"{old} is defined now.")
        elif new not in buildings:
            skipped.append(f"Nothing defines {new} now.")
        else:
            swaps[old.encode()] = new.encode()
    if not swaps:
        raise FixError(" ".join(skipped))
    used: dict[bytes, tuple[str, bytes, Entry]] = {}  # the definition the game uses
    for layer, path in layers.ordered(STARBASE_MODULES):
        data = layers.read(layer, path)
        for entry in scan(data):
            if entry.block:
                used[entry.key] = (layer, data, entry)
    bodies: list[bytes] = []
    header: dict[str, str] = {}
    notes = [f"{why} Skipped." for why in skipped]
    for key, (layer, data, entry) in used.items():
        if layer != STARBASE_EXTENDED:
            continue
        found = [
            m
            for m in _HAS_BUILDING.finditer(data, entry.start, entry.end)
            if m[1] in swaps and b"#" not in data[data.rfind(b"\n", 0, m.start()) + 1 : m.start()]
        ]
        if not found:
            continue
        body = _mended(data, entry, [(m.start(1), m.end(1), swaps[m[1]]) for m in found])
        variables = _copied_variables(layers, data, entry, body)
        if any(header.get(name, value) != value for name, value in variables):
            notes.append(f"{key.decode()} uses a variable another module defines differently.")
            continue
        header.update(variables)
        bodies.append(body)
        olds = sorted({m[1].decode() for m in found})
        checks = ", ".join(f"{swaps[o.encode()].decode()} for {o}" for o in olds)
        notes.append(f"{key.decode()}, from Starbase Extended: checks {checks}")
    if not bodies:
        names = " or ".join(o.decode() for o in swaps)
        raise FixError(f"No Starbase Extended module in use checks {names} now.")
    top = "".join(f"{name} = {value}\n" for name, value in sorted(header.items()))
    text = ((top + "\n" if top else "").encode() + b"\n\n".join(bodies)).replace(b"\r\n", b"\n")
    return {_last_file(layers, STARBASE_MODULES, "sbx_buildings"): text + b"\n"}, notes


# 30. Starbase Extended's starbase window predates 4.5


SBX_VIEW = "interface/zzz_sbx_3_0_starbase_view.gui"
UIOD_VIEW = "interface/starbase_view.gui"
VIEW = b"starbase_view"
SLOT = b"starbase_view_current_component_grid_entry"  # one module or building slot
SLOT_GRIDS = (b"modules_grid", b"buildings_grid")
GRID_FIELDS = (b"slotSize", b"max_slots_horizontal")
# Starbase Extended swaps Upgrade and Station Details, so Upgrade isn't just above
# Dismantle (decision 47). The same swap in UI Overhaul Dynamic's header, worked out
# against its 4.5.2 window. Each element by the box it's directly in, its type and
# name: {field: (its value, ours)}.
_BOX, _TEXT, _BUTTON = b"containerWindowType", b"instantTextBoxType", b"buttonType"
BUTTON_SWAP: dict[tuple[bytes, bytes, bytes], dict[bytes, tuple[bytes, bytes]]] = {
    (b"starbase_tab", _BOX, b"upgrade_info"): {
        b"position": (b"{ x = -10 y = 40 }", b"{ x = 10 y = 75 }"),
        b"orientation": (b"upper_right", b"upper_left"),
        b"origo": (b"upper_right", b"upper_left"),
    },
    (b"upgrade_info", _TEXT, b"next_class_name"): {
        b"position": (b"{ x = 0 y = 4 }", b"{ x = 44 y = 4 }"),
        b"format": (b"right", b"left"),
    },
    (b"upgrade_info", _BUTTON, b"upgrade"): {
        b"position": (b"{ x = -35 y = 4 }", b"{ x = 4 y = 4 }"),
        b"orientation": (b"upper_right", b"upper_left"),
    },
    (b"class_info", _BUTTON, b"details"): {
        b"position": (b"{ x = 4 y = -35 }", b"{ x = -45 y = 4 }"),
        b"orientation": (b"lower_left", b"upper_right"),
    },
}
EMPTIED = (
    b"# Emptied by the Cold Steel Mix patch (fix 30): the game uses UI Overhaul Dynamic's\n"
    b"# starbase window, with Starbase Extended's slot sizes, from the patch's own file.\n"
)


def fix_starbase_view(layers: Layers) -> Made:
    """Starbase Extended's window file emptied, so UI Overhaul Dynamic's 4.5
    windows are used again, and a copy of its starbase window and slot, in a
    file that sorts last, with Starbase Extended's slot sizes and its swap of
    Upgrade and Station Details. Only while Starbase Extended's window lacks
    some of UI Overhaul Dynamic's elements."""
    definers = _gui_definers(layers, (VIEW, SLOT))
    if not definers or definers[-1] != (STARBASE_EXTENDED, SBX_VIEW):
        raise FixError(f"{VIEW.decode()} doesn't come from Starbase Extended's {SBX_VIEW} now.")
    _expect_winner(layers, UIOD_VIEW, UI_OVERHAUL, "UI Overhaul Dynamic")
    sbx = layers.read(STARBASE_EXTENDED, SBX_VIEW)
    sbx_view, sbx_slot = _gui_window(sbx, VIEW), _gui_window(sbx, SLOT)
    data = layers.read(UI_OVERHAUL, UIOD_VIEW)
    view, slot = _gui_window(data, VIEW), _gui_window(data, SLOT)
    if sbx_view is None or sbx_slot is None or view is None or slot is None:
        raise FixError(f"{SBX_VIEW} or {UIOD_VIEW} lacks {VIEW.decode()} or its slot now.")
    missing = sorted(_gui_names(data, view) - _gui_names(sbx, sbx_view))
    if not missing:
        raise FixError(
            f"Starbase Extended's {VIEW.decode()} has every element UI Overhaul's has now."
        )
    notes = [f"Starbase Extended's window lacks {', '.join(n.decode() for n in missing)}"]
    edits: list[tuple[int, int, bytes]] = []
    for grid in SLOT_GRIDS:
        theirs = _gui_element(sbx, sbx_view, b"gridBoxType", grid)
        ours = _gui_element(data, view, b"gridBoxType", grid)
        for setting in GRID_FIELDS:
            edits.append(_field_edit(data, ours, setting, _field_value(sbx, theirs, setting)))
    try:
        swap = _button_swap(data, view)
        notes.append("Upgrade and Station Details swap places, as in Starbase Extended")
    except FixError as why:
        swap = []
        notes.append(f"{why} The button swap is skipped.")
    view_body = _mended(data, view, edits + swap)
    slot_edits = [_field_edit(data, slot, b"size", _field_value(sbx, sbx_slot, b"size"))]
    for theirs in children(sbx, sbx_slot):
        scale = value_of(sbx, theirs, b"scale")
        named = value_of(sbx, theirs, b"name")
        if scale is None or named is None:
            continue
        ours = _gui_element(data, slot, theirs.key, named, deep=False)
        if any(c.key == b"scale" for c in children(data, ours)):
            slot_edits.append(_field_edit(data, ours, b"scale", scale))
            continue
        name_line = next(c for c in children(data, ours) if c.key == b"name")
        slot_edits.append(
            (name_line.end, name_line.end, b"\n" + _indent(data, name_line) + b"scale = " + scale)
        )
    slot_body = _mended(data, slot, slot_edits)
    file_vars = _variables(data)
    used = sorted({"@" + m.decode() for m in _VARIABLE.findall(view_body + slot_body)})
    header = b"".join(
        data[file_vars[n].start : file_vars[n].end] + b"\n" for n in used if n in file_vars
    )
    text = header + b"guiTypes = {\n\t" + view_body + b"\n\t" + slot_body + b"\n}\n"
    rivals = [p.rpartition("/")[2] for _, p in definers]
    file_name = winning_name(rivals, f"{TAIL}_starbase_view.gui", first=False)
    if file_name is None:
        raise FixError(f"No file name sorts after the other files with {VIEW.decode()}.")
    notes.append("Module and building slots take Starbase Extended's sizes")
    return {SBX_VIEW: EMPTIED, f"interface/{file_name}": text.replace(b"\r\n", b"\n")}, notes


def _button_swap(data: bytes, view: Entry) -> list[tuple[int, int, bytes]]:
    """`BUTTON_SWAP`'s edits to `view`. FixError if a value it changes isn't
    the one it was worked out against."""
    edits: list[tuple[int, int, bytes]] = []
    for (box, kind, name), fields in BUTTON_SWAP.items():
        element = _gui_element(data, _gui_element(data, view, _BOX, box), kind, name, deep=False)
        for key, (was, now) in fields.items():
            found = next((c for c in children(data, element) if c.key == key), None)
            if found is None or b" ".join(data[found.value : found.end].split()) != was:
                raise FixError(f"{name.decode()}'s {key.decode()} has changed.")
            edits.append((found.value, found.end, now))
    return edits


def _gui_definers(layers: Layers, names: Sequence[bytes]) -> list[tuple[str, str]]:
    """Each (layer, path) whose file defines a top-level window in `names`, in
    the order the game reads them: the last wins."""
    return [
        (layer, path)
        for layer, path in layers.ordered("interface", ".gui")
        if any(_gui_window(layers.read(layer, path), name) for name in names)
    ]


def _gui_window(data: bytes, name: bytes) -> Entry | None:
    return next(
        (
            w
            for types in scan(data)
            if types.key == b"guiTypes"
            for w in children(data, types)
            if w.block and value_of(data, w, b"name") == name
        ),
        None,
    )


def _gui_names(data: bytes, window: Entry) -> set[bytes]:
    return {n for b in _blocks(data, window) if (n := value_of(data, b, b"name")) is not None}


def _gui_element(data: bytes, window: Entry, kind: bytes, name: bytes, deep: bool = True) -> Entry:
    """The one element of type `kind` named `name` inside `window`: at any depth,
    or only directly inside it."""
    inside = _blocks(data, window) if deep else children(data, window)
    found = [e for e in inside if e.key == kind and value_of(data, e, b"name") == name]
    if len(found) != 1:
        raise FixError(
            f"{window.key.decode()} has {len(found)} {kind.decode()} {name.decode()} now."
        )
    return found[0]


def _field_value(data: bytes, element: Entry, field: bytes) -> bytes:
    found = next((c for c in children(data, element) if c.key == field), None)
    if found is None:
        raise FixError(f"An element has no {field.decode()} now.")
    return data[found.value : found.end]


def _field_edit(data: bytes, element: Entry, field: bytes, value: bytes) -> tuple[int, int, bytes]:
    found = next((c for c in children(data, element) if c.key == field), None)
    if found is None:
        raise FixError(f"An element has no {field.decode()} now.")
    return found.value, found.end, value


# 31. Starbase Extended's starbase models are old copies of the game's


SBX_MODELS = "gfx/models/ships/starbases"
_SOUND = re.compile(rb'\bsoundeffect\s*=\s*"?(\w+)')
_PARTICLE = re.compile(rb'\bparticle\s*=\s*"?(\w+)')
_NODE = re.compile(rb'\bnode\s*=\s*"?(\w+)')
_SOUND_NAME = re.compile(rb'\bsoundeffect\s*=\s*\{\s*name\s*=\s*"?(\w+)')
_PARTICLE_NAME = re.compile(rb'\bpdxparticle\s*=\s*\{\s*name\s*=\s*"?(\w+)')
_MESH_OBJECT = re.compile(rb"(?<!\[)\[([A-Za-z_]\w*)\x00")
_MESH_LOCATOR = re.compile(rb"(?<!\[)\[\[([A-Za-z_]\w*)\x00")
# SBX's new tiers sound like the game's tier they grow from.
NEW_TIERS = {b"stronghold": b"citadel", b"headquarters": b"citadel"}


@dataclass
class _Models:
    """What the game resolves for a starbase model, by name."""

    game: dict[bytes, tuple[bytes, Entry]]  # the game's own entities
    game_vars: dict[bytes, dict[str, Entry]]  # each game file's variables, by its data
    sounds: set[bytes]
    particles: set[bytes]
    meshes: dict[bytes, tuple[str, set[bytes]]]  # mesh -> its file, its animation ids
    slots: dict[str, set[bytes]]  # Starbase Extended's starbase sizes -> locators asked for
    others: set[bytes]  # entities a mod other than Starbase Extended defines
    dropped: dict[str, int] = field(default_factory=dict)  # what was left out, by kind
    older: dict[str, int] = field(default_factory=dict)  # the game's older lines, left out
    attached: int = 0  # attach points added


def fix_starbase_models(layers: Layers) -> Made:
    """Starbase Extended's model files, rebuilt at their own paths. Each copy of
    a game model is the game's 4.5 one with Starbase Extended's own additions
    that resolve: attach points, lights and sounds. References that don't
    resolve are left out, and a sound its new tiers lack comes from the
    Citadel's. Every starbase model gets the attach points Starbase Extended's
    sizes ask for and its mesh lacks, at its centre: game models in a file of
    their own that sorts last."""
    paths = [p for p in layers.paths(STARBASE_EXTENDED, SBX_MODELS, ".asset")]
    paths = [p for p in paths if layers.winner(p) == STARBASE_EXTENDED]
    if not paths:
        raise FixError(f"No {SBX_MODELS} file comes from Starbase Extended now.")
    models = _models(layers)
    files: dict[str, bytes] = {}
    rebuilt = 0
    sbx_names: set[bytes] = set()
    for path in paths:
        text, entities, changed, names = _rebuild_models(layers, models, path)
        sbx_names |= names
        rebuilt += entities
        if changed:
            files[path] = text
    copies: list[bytes] = []
    header: dict[str, bytes] = {}
    for name, (data, entry) in sorted(models.game.items()):
        if name in sbx_names or name in models.others:
            continue
        edits = _attach_points(layers, models, data, entry)
        if edits:
            copies.append(_mended(data, entry, edits))
            header.update(_used_vars(models, data, copies[-1]))
    if copies:
        rivals = [p.rpartition("/")[2] for _, p in layers.ordered(SBX_MODELS, ".asset")]
        file_name = winning_name(rivals, f"{TAIL}_attach_points.asset", first=False)
        if file_name is None:
            raise FixError(f"No file name sorts after the other {SBX_MODELS} files.")
        top = b"".join(f"{k} = ".encode() + v + b"\n" for k, v in sorted(header.items()))
        text = (top + b"\n" if top else b"") + b"\n\n".join(copies) + b"\n"
        files[f"{SBX_MODELS}/{file_name}"] = text.replace(b"\r\n", b"\n")
    if not files:
        raise FixError("Starbase Extended's models match the game's and resolve every name now.")
    left = ", ".join(f"{n} {kind}" for kind, n in sorted(models.dropped.items()))
    older = ", ".join(f"{n} {kind}" for kind, n in sorted(models.older.items()))
    notes = [
        f"{rebuilt} of Starbase Extended's models rebuilt, from the game's where it copies one",
        f"Left out, as nothing defines them: {left or 'nothing'}",
        f"Left out, as the game's model has its own: {older or 'nothing'}",
        f"{models.attached} attach points added. "
        f"{len(copies)} game models are copied to get theirs",
    ]
    return files, notes


def _models(layers: Layers) -> _Models:
    game: dict[bytes, tuple[bytes, Entry]] = {}
    game_vars: dict[bytes, dict[str, Entry]] = {}
    for path in layers.paths(GAME, "gfx/models", ".asset"):
        data = layers.read(GAME, path)
        for entry in scan(data):
            name = value_of(data, entry, b"name") if entry.key == b"entity" else None
            if name is not None:
                game.setdefault(name, (data, entry))
    sounds: set[bytes] = set()
    for layer, path in layers.files("sound", ".asset").values():
        sounds.update(_SOUND_NAME.findall(layers.read(layer, path)))
    particles: set[bytes] = set()
    meshes: dict[bytes, tuple[str, set[bytes]]] = {}
    for layer, path in layers.files("gfx", ".gfx").values():
        data = layers.read(layer, path)
        particles.update(_PARTICLE_NAME.findall(data))
        if b"pdxmesh" not in data:
            continue
        for types in scan(data):
            for mesh in children(data, types):
                name, file = value_of(data, mesh, b"name"), value_of(data, mesh, b"file")
                if mesh.key != b"pdxmesh" or name is None or file is None:
                    continue
                ids = {
                    value_of(data, a, b"id") or b""
                    for a in children(data, mesh)
                    if a.key == b"animation"
                }
                meshes[name] = (file.decode(), ids)
    sizes: dict[str, tuple[str, bytes, Entry]] = {}
    for layer, path in layers.ordered("common/ship_sizes"):
        data = layers.read(layer, path)
        for entry in scan(data):
            if entry.block:
                sizes[entry.key.decode()] = (layer, data, entry)
    slots: dict[str, set[bytes]] = {}
    for size, (layer, data, entry) in sizes.items():
        found = next((c for c in children(data, entry) if c.key == b"section_slots"), None)
        if layer == STARBASE_EXTENDED and found is not None:
            slots[size] = {v for s in children(data, found) if (v := value_of(data, s, b"locator"))}
    others: set[bytes] = set()
    for mod in [m.key for m in layers.layers[1:] if m.key != STARBASE_EXTENDED]:
        for path in layers.paths(mod, "gfx/models", ".asset"):
            data = layers.read(mod, path)
            others.update(
                n for e in scan(data) if e.key == b"entity" and (n := value_of(data, e, b"name"))
            )
    return _Models(game, game_vars, sounds, particles, meshes, slots, others)


def _rebuild_models(
    layers: Layers, models: _Models, path: str
) -> tuple[bytes, int, bool, set[bytes]]:
    """One of Starbase Extended's model files, rebuilt: its text, how many of
    its entities changed, whether the file did, and the entities it defines."""
    data = layers.read(STARBASE_EXTENDED, path)
    folder = path.rpartition("/")[0]
    header: dict[str, bytes] = {}
    bodies: list[bytes] = []
    names: set[bytes] = set()
    changed = 0
    dropped = False
    for entry in scan(data):
        if entry.key.startswith(b"@") and not entry.block:
            header[entry.key.decode()] = data[entry.value : entry.end]
        elif entry.key == b"animation" and entry.block:
            file = (value_of(data, entry, b"file") or b"").decode()
            if not any(layers.has(layer.key, f"{folder}/{file}") for layer in layers.layers):
                _count(models, "animation files")
                dropped = True
                continue
            bodies.append(data[entry.start : entry.end])
        elif entry.key == b"entity" and entry.block:
            name = value_of(data, entry, b"name") or b""
            names.add(name)
            body, game_data = _rebuilt_entity(layers, models, data, entry, name)
            if b"".join(_COMMENT.sub(b"", body).split()) != _clause(data, entry):
                changed += 1
            if game_data is not None:
                for key, value in _used_vars(models, game_data, body).items():
                    if header.setdefault(key, value).split() != value.split():
                        raise FixError(f"{path} defines {key} unlike the game's file.")
            bodies.append(body)
        else:
            bodies.append(data[entry.start : entry.end])
    top = b"".join(f"{k} = ".encode() + v.strip() + b"\n" for k, v in header.items())
    text = (top + b"\n" if top else b"") + b"\n\n".join(bodies) + b"\n"
    return text.replace(b"\r\n", b"\n"), changed, bool(changed) or dropped, names


def _rebuilt_entity(
    layers: Layers, models: _Models, data: bytes, entry: Entry, name: bytes
) -> tuple[bytes, bytes | None]:
    """The entity's new text, and the game file it's built on, if any. A new
    tier's model on the same mesh as the game's tier it grows from is built on
    that one, keeping its own name."""
    found = models.game.get(name)
    tier = next((name.replace(n, old) for n, old in NEW_TIERS.items() if n in name), b"")
    if found is None and tier in models.game and _mesh(*models.game[tier]) == _mesh(data, entry):
        found = models.game[tier]
    if found is None:
        sounds_from = models.game.get(tier)
        edits = _merge_block(models, _mesh(data, entry), data, entry, None, sounds_from)
        edits += _attach_points(layers, models, data, entry, edits)
        return _mended(data, entry, edits), None
    game_data, game_entry = found
    mesh = _mesh(game_data, game_entry) or _mesh(data, entry)
    edits = _merge_block(models, mesh, game_data, game_entry, (data, entry), None)
    edits += _attach_points(layers, models, game_data, game_entry, edits, (data, entry), name)
    return _mended(game_data, game_entry, edits), game_data


def _mesh(data: bytes, entity: Entry) -> bytes:
    return value_of(data, entity, b"pdxmesh") or b""


def _merge_block(
    models: _Models,
    mesh: bytes,
    data: bytes,
    block: Entry,
    extra: tuple[bytes, Entry] | None,
    sounds_from: tuple[bytes, Entry] | None,
) -> list[tuple[int, int, bytes]]:
    """Edits to `block`, the game's entity or one of its states (or Starbase
    Extended's own, when `extra` is None). `extra`'s children that resolve and
    `block` lacks are added, and its own values replace `block`'s. But its
    effects on a node `block`'s effects use, and its sounds where `block` has
    some, are the game's older ones: the game's stay. Children of `block` that
    don't resolve are left out. A state that loses its sounds gets
    `sounds_from`'s, from the same state."""
    edits: list[tuple[int, int, bytes]] = []
    own = children(data, block)
    for child in own:
        if kind := _broken(models, mesh, data, child):
            _count(models, kind)
            edits.append(_drop(data, child))
        elif child.key == b"state" and child.block and extra is None:
            twin = _twin(sounds_from, child, data) if sounds_from else None
            edits += _merge_block(models, mesh, data, child, None, None)
            if twin is not None and _lost_sounds(models, mesh, data, child):
                twin_data, twin_state = twin
                edits += _added(
                    data,
                    child,
                    [twin_data[e.start : e.end] for e in _start_events(twin_data, twin_state)],
                )
    if extra is None:
        return edits
    extra_data, extra_block = extra
    added: list[bytes] = []
    nodes = {n for c in own if c.key == b"event" for n in _NODE.findall(data[c.start : c.end])}
    sounds = any(c.key == b"start_event" for c in own)
    for child in children(extra_data, extra_block):
        if kind := _broken(models, mesh, extra_data, child):
            _count(models, kind)
            continue
        match = _match(data, own, extra_data, child)
        text = extra_data[child.start : child.end]
        if match is not None and _clause(data, match) == _clause(extra_data, child):
            continue
        if child.key == b"event" and nodes.intersection(_NODE.findall(text)):
            models.older["effects"] = models.older.get("effects", 0) + 1
        elif child.key == b"start_event" and sounds:
            models.older["sounds"] = models.older.get("sounds", 0) + 1
        elif match is None or child.key in (b"event", b"start_event"):
            added.append(_mended_child(models, mesh, extra_data, child))
        elif child.key == b"state" and child.block:
            edits += _merge_block(models, mesh, data, match, (extra_data, child), None)
        else:
            edits.append((match.start, match.end, text))
    return edits + _added(data, block, added)


def _mended_child(models: _Models, mesh: bytes, data: bytes, child: Entry) -> bytes:
    """`child`'s text, a block without the children inside it that don't resolve."""
    if not child.block:
        return data[child.start : child.end]
    return _mended(data, child, _merge_block(models, mesh, data, child, None, None))


def _twin(
    sounds_from: tuple[bytes, Entry], state: Entry, data: bytes
) -> tuple[bytes, Entry] | None:
    twin_data, twin_entity = sounds_from
    name = value_of(data, state, b"name")
    for child in children(twin_data, twin_entity):
        if child.key == b"state" and value_of(twin_data, child, b"name") == name:
            return twin_data, child
    return None


def _start_events(data: bytes, state: Entry) -> list[Entry]:
    return [c for c in children(data, state) if c.key == b"start_event" and c.block]


def _lost_sounds(models: _Models, mesh: bytes, data: bytes, state: Entry) -> bool:
    """`state` has sounds, and none of them resolve."""
    found = [e for e in _start_events(data, state) if _SOUND.search(data[e.start : e.end])]
    return bool(found) and all(_broken(models, mesh, data, e) == "sounds" for e in found)


def _match(data: bytes, own: list[Entry], extra_data: bytes, child: Entry) -> Entry | None:
    """`child`'s counterpart among `own`: by key and name for a named block,
    by key for a value, by text for any other block."""
    name = value_of(extra_data, child, b"name") if child.block else None
    for mine in own:
        if mine.key != child.key or mine.block != child.block:
            continue
        if not child.block or (name is not None and value_of(data, mine, b"name") == name):
            return mine
        if name is None and _clause(data, mine) == _clause(extra_data, child):
            return mine
    return None


def _broken(models: _Models, mesh: bytes, data: bytes, child: Entry) -> str:
    """What `child` asks for that nothing defines: "sounds", "particles" or
    "mesh animations", or "" if it all resolves."""
    text = data[child.start : child.end]
    if child.block and child.key in (b"event", b"start_event"):
        if any(s not in models.sounds for s in _SOUND.findall(text)):
            return "sounds"
        if any(p not in models.particles for p in _PARTICLE.findall(text)):
            return "particles"
        return ""
    ids = models.meshes.get(mesh, ("", set()))[1]
    if (
        child.key == b"animation"
        and not child.block
        and text.split(b"=", 1)[1].strip(b' \t"') not in ids
    ):
        return "mesh animations"
    return ""


def _count(models: _Models, kind: str) -> None:
    models.dropped[kind] = models.dropped.get(kind, 0) + 1


def _drop(data: bytes, child: Entry) -> tuple[int, int, bytes]:
    """An edit that takes `child` out, with its line if it has one to itself."""
    start = data.rfind(b"\n", 0, child.start) + 1
    end = data.find(b"\n", child.end)
    if data[start : child.start].strip() or (end != -1 and data[child.end : end].strip(b" \t\r")):
        return child.start, child.end, b""
    return start, len(data) if end == -1 else end + 1, b""


def _added(data: bytes, block: Entry, texts: list[bytes]) -> list[tuple[int, int, bytes]]:
    """An edit that adds `texts`, a line each, at the end of `block`."""
    if not texts:
        return []
    close = block.end - 1
    line = data.rfind(b"\n", 0, close) + 1
    if data[line:close].strip():  # the closing brace shares its line
        return [(close, close, b" " + b" ".join(texts) + b" ")]
    # A child on a line of its own shows the indent. Otherwise, one more than the block's line.
    own_line = (_indent(data, c) for c in children(data, block) if not _indent(data, c).strip())
    block_line = _indent(data, block)
    indent = next(own_line, block_line[: len(block_line) - len(block_line.lstrip())] + b"\t")
    return [(line, line, b"".join(indent + t + b"\n" for t in texts))]


def _attach_points(
    layers: Layers,
    models: _Models,
    data: bytes,
    entity: Entry,
    edits: Sequence[tuple[int, int, bytes]] = (),
    extra: tuple[bytes, Entry] | None = None,
    named: bytes = b"",
) -> list[tuple[int, int, bytes]]:
    """An edit that adds, at the model's centre, each locator Starbase
    Extended's size for this model asks for that its mesh and entity lack.
    `named` is the model's name, if not `entity`'s own."""
    name = (named or value_of(data, entity, b"name") or b"").decode()
    size = next((s for s in models.slots if name.endswith(f"_{s}_entity")), None)
    mesh = models.meshes.get(_mesh(data, entity))
    if size is None or mesh is None:
        return []
    have = {b"root", *_mesh_locators(layers, mesh[0])}
    texts = [data[e.start : e.end] for e in children(data, entity)] + [t for _, _, t in edits]
    if extra is not None:
        texts.append(extra[0][extra[1].start : extra[1].end])
    for text in texts:
        have.update(re.findall(rb'locator\s*=\s*\{\s*name\s*=\s*"?(\w+)', text))
    missing = sorted(models.slots[size] - have, key=lambda n: (len(n), n))
    models.attached += len(missing)
    lines = [b'locator = { name = "' + n + b'" position = { 0 0 0 } }' for n in missing]
    return _added(data, entity, lines)


def _mesh_locators(layers: Layers, path: str) -> set[bytes]:
    """The locators in a binary .mesh file: the `[[name` objects in its `[locator` object."""
    try:
        data = layers.read(layers.winner(path), path)
    except LayerError:
        return set()
    starts = [(m.start(), m[1]) for m in _MESH_OBJECT.finditer(data)]
    for i, (start, name) in enumerate(starts):
        if name == b"locator":
            end = starts[i + 1][0] if i + 1 < len(starts) else len(data)
            return set(_MESH_LOCATOR.findall(data, start, end))
    return set()


def _used_vars(models: _Models, data: bytes, body: bytes) -> dict[str, bytes]:
    """The variables of the game file `data` that `body` uses, with their values."""
    if data not in models.game_vars:  # only a few files are copied from
        models.game_vars[data] = _variables(data)
    file_vars = models.game_vars[data]
    used = {"@" + m.decode() for m in _VARIABLE.findall(_COMMENT.sub(b"", body))}
    return {n: data[e.value : e.end].strip() for n, e in file_vars.items() if n in used}


# 32. Starbase Extended's modules and buildings: duplicate blocks, broken checks, its hangar bay


SINGLE_BLOCKS = (b"potential", b"ai_weight")  # the game keeps one of each
HANGAR_BAY = "orbital_ring_hangar_bay"
# 4.5's lines Starbase Extended's copy of the hangar bay lacks: its hangars, by the
# kind of ships an empire uses, and its tooltips.
HANGAR_LINES = (
    b"triggered_component_set",
    b"show_component_tooltips",
    b"custom_tooltip_with_modifiers",
    b"show_tech_unlock_if",
)
_SYSTEM_SCOPE = re.compile(rb"\bsolar_system\s*=\s*\{")
_SYSTEM_EXISTS = re.compile(rb"\bexists\s*=\s*solar_system\b")


def fix_sbx_checks(layers: Layers) -> Made:
    """Starbase Extended's module and building files, whole at their own paths,
    with each object's checks mended: a second `potential` or `ai_weight`
    merged into the first, a `category` line taken out of a `potential`, and
    `exists = solar_system` before a `potential` scopes to the system, which
    an arkship's starbase lacks. Its hangar bay gets 4.5's hangars, bio-ship
    upkeep and tooltips. Whole files, so the game never reads the duplicate
    blocks (item 35). A module fix 29 copies is left to it."""
    files: dict[str, bytes] = {}
    notes: list[str] = []
    for folder in (STARBASE_MODULES, STARBASE_BUILDINGS):
        for path in layers.paths(STARBASE_EXTENDED, folder):
            if layers.winner(path) != STARBASE_EXTENDED:
                continue
            data = layers.read(STARBASE_EXTENDED, path)
            edits: list[tuple[int, int, bytes]] = []
            for entry in scan(data):
                if not entry.block:
                    continue
                if any(old.encode() in data[entry.start : entry.end] for old in SBX_BUILDINGS):
                    notes.append(f"{entry.key.decode()} is copied by fix 29. Skipped.")
                    continue
                mends, done = _check_edits(data, entry)
                if entry.key.decode() == HANGAR_BAY:
                    more, hangar = _hangar_edits(layers, data, entry)
                    mends += more
                    done += hangar
                if mends:
                    edits += mends
                    notes.append(f"{entry.key.decode()}: {', '.join(done)}")
            if edits:
                files[path] = _edit(data, edits).replace(b"\r\n", b"\n")
    if not files:
        raise FixError("Starbase Extended's modules and buildings have no checks to mend now.")
    return files, notes


def _used_definitions(layers: Layers, folder: str) -> dict[bytes, tuple[str, bytes, Entry]]:
    """Each object in a folder where the last definition by file name wins, as the game uses it."""
    used: dict[bytes, tuple[str, bytes, Entry]] = {}
    for layer, path in layers.ordered(folder):
        data = layers.read(layer, path)
        for entry in scan(data):
            if entry.block:
                used[entry.key] = (layer, data, entry)
    return used


def _check_edits(data: bytes, entry: Entry) -> tuple[list[tuple[int, int, bytes]], list[str]]:
    """The edits that mend one object's checks, and what each did."""
    edits: list[tuple[int, int, bytes]] = []
    done: list[str] = []
    for key in SINGLE_BLOCKS:
        blocks = [c for c in children(data, entry) if c.key == key and c.block]
        if not blocks:
            continue
        first, rest = blocks[0], blocks[1:]
        weights = {value_of(data, b, b"weight") for b in blocks} - {None}
        if len(weights) > 1:
            done.append(f"keeps its {len(blocks)} {key.decode()} blocks, whose weights differ")
            continue
        moved: list[bytes] = []
        stray = [c for c in children(data, first) if c.key == b"category"]
        for block in rest:
            for child in children(data, block):
                if child.key == b"category" and key == b"potential":
                    stray.append(child)
                elif child.key != b"weight":
                    moved.append(data[child.start : child.end])
            edits.append(_drop(data, block))
        if rest:
            done.append(f"merges its {len(blocks)} {key.decode()} blocks")
        if key != b"potential":
            edits += _added(data, first, moved)
            continue
        edits += [_drop(data, c) for c in stray if c.start > first.start and c.end < first.end]
        if stray:
            done.append("drops `category` from its potential, which isn't a trigger")
        checks = b"".join(data[b.start : b.end] for b in blocks)
        if _SYSTEM_SCOPE.search(checks) and not _SYSTEM_EXISTS.search(checks):
            at = first.inside[0]
            edits.append((at, at, b" exists = solar_system"))
            done.append("checks the starbase has a system first")
        edits += _added(data, first, moved)
    return edits, done


def _hangar_edits(
    layers: Layers, data: bytes, entry: Entry
) -> tuple[list[tuple[int, int, bytes]], list[str]]:
    """The game's 4.5 lines Starbase Extended's hangar bay lacks, and its bio-ship
    upkeep: the game's upkeeps in place of Starbase Extended's, when its one
    upkeep is the game's for other empires."""
    game_data, game_entry = _game_entry(layers, STARBASE_MODULES, HANGAR_BAY)
    theirs = children(game_data, game_entry)
    mine = {c.key for c in children(data, entry)}
    lacked = [c for c in theirs if c.key in HANGAR_LINES and c.key not in mine]
    edits = _added(data, entry, [game_data[c.start : c.end] for c in lacked])
    names = sorted({c.key.decode() for c in lacked})
    done = [f"gets the game's {', '.join(names)}"] if names else []
    resources = next((c for c in children(data, entry) if c.key == b"resources"), None)
    game_resources = next((c for c in theirs if c.key == b"resources"), None)
    if resources is None or game_resources is None:
        return edits, done
    upkeeps = [c for c in children(data, resources) if c.key == b"upkeep"]
    game_upkeeps = [c for c in children(game_data, game_resources) if c.key == b"upkeep"]
    untriggered = [u for u in upkeeps if not any(c.key == b"trigger" for c in children(data, u))]
    plain = [
        b"".join(_clause(game_data, c) for c in children(game_data, u) if c.key != b"trigger")
        for u in game_upkeeps
    ]
    if len(upkeeps) == 1 and len(untriggered) == 1 and len(game_upkeeps) > 1:
        body = b"".join(_clause(data, c) for c in children(data, upkeeps[0]))
        if body in plain:
            text = b"\n\t\t".join(game_data[u.start : u.end] for u in game_upkeeps)
            edits.append((upkeeps[0].start, upkeeps[0].end, text))
            done.append("costs the game's upkeep, food for bio-ship empires")
    return edits, done


# 33. Starbase Extended's orbital ring shield and armour modules have no sections


SECTION_TEMPLATES = "common/section_templates"
# Each section its modules name and nothing defines, to the one to copy: its ring
# anchorage section, as its starbase shield and armour modules use its anchorage.
RING_SECTIONS = {
    b"SHIELD_ORBITAL_RING_SECTION": b"ANCHORAGE_ORBITAL_RING_SECTION",
    b"ARMOR_ORBITAL_RING_SECTION": b"ANCHORAGE_ORBITAL_RING_SECTION",
}


def fix_ring_sections(layers: Layers) -> Made:
    """Each section in RING_SECTIONS a module uses and nothing defines, as a copy
    of Starbase Extended's ring anchorage section under its own key."""
    templates: dict[bytes, tuple[bytes, Entry]] = {}
    for layer, path in layers.ordered(SECTION_TEMPLATES):
        data = layers.read(layer, path)
        for entry in scan(data):
            key = value_of(data, entry, b"key") if entry.block else None
            if key is not None:
                templates.setdefault(key, (data, entry))  # the first definition wins
    used = {
        value_of(data, entry, b"section") or b""
        for _, data, entry in _used_definitions(layers, STARBASE_MODULES).values()
    }
    bodies: list[bytes] = []
    notes: list[str] = []
    for missing, model in RING_SECTIONS.items():
        if missing in templates or missing not in used or model not in templates:
            continue
        data, entry = templates[model]
        found = next(c for c in children(data, entry) if c.key == b"key")
        body = _mended(data, entry, [(found.value, found.end, b'"' + missing + b'"')])
        bodies.append(body.replace(b"\r\n", b"\n"))
        notes.append(f"{missing.decode()}, as a copy of {model.decode()}")
    if not bodies:
        raise FixError("Every orbital ring section a module uses is defined now.")
    return {
        _first_file(layers, SECTION_TEMPLATES, "ring_sections"): b"\n\n".join(bodies) + b"\n"
    }, notes


# 34. Starbase Extended's starbase sizes predate 4.5


SHIP_SIZES = "common/ship_sizes"
# Values 4.5 changed or added on every starbase size: how big each counts for, its map
# icon, and the flags the game reads. Starbase Extended's own balance (hit points,
# armour, costs, slots) stays. Its swarm and marauder sizes, which it doesn't
# rebalance, differ from the game's in these alone.
SIZE_FIELDS = (
    b"size_multiplier",
    b"combat_size_multiplier",
    b"fleet_slot_size",
    b"map_counter_icon",
    b"is_orbital_ring",
    b"flip_control_on_disable",
)
# The game's conditions for building a size, such as 4.5's "not at a waystation or an
# arkship" on the Ion Cannon. Those Starbase Extended's copy lacks are added.
CONSTRUCTION = b"potential_construction"
# Starbase Extended's sizes above the Citadel take the Citadel's values.
NEW_SIZES = {
    b"starbase_stronghold": "starbase_citadel",
    b"starbase_headquarters": "starbase_citadel",
}


def fix_starbase_sizes(layers: Layers) -> Made:
    """Copies of Starbase Extended's starbase sizes with the game's 4.5 values for
    SIZE_FIELDS, in a file that sorts last. Its new sizes take the Citadel's."""
    bodies: list[bytes] = []
    header: dict[str, str] = {}
    changed: list[str] = []
    for key, (layer, data, entry) in _used_definitions(layers, SHIP_SIZES).items():
        if layer != STARBASE_EXTENDED:
            continue
        try:
            game_data, game_entry = _game_entry(
                layers, SHIP_SIZES, NEW_SIZES.get(key, key.decode())
            )
        except FixError:
            continue
        game_vars = _variables(game_data)
        edits: list[tuple[int, int, bytes]] = []
        added: list[bytes] = []
        for field_name in SIZE_FIELDS:
            want = next((c for c in children(game_data, game_entry) if c.key == field_name), None)
            if want is None or want.block:
                continue
            value = game_data[want.value : want.end].strip()
            if value.startswith(b"@") and value.decode() in game_vars:
                value = game_data[
                    game_vars[value.decode()].value : game_vars[value.decode()].end
                ].strip()
            have = next((c for c in children(data, entry) if c.key == field_name), None)
            if have is None:
                added.append(field_name + b" = " + value)
            elif data[have.value : have.end].strip() != value:
                edits.append((have.value, have.end, value))
        if key not in NEW_SIZES:
            edits += _construction_edits(data, entry, game_data, game_entry)
        if not edits and not added:
            continue
        body = _mended(data, entry, edits + _added(data, entry, added))
        for name, number in _size_variables(layers, data, entry, body):
            if header.setdefault(name, number) != number:
                raise FixError(f"{name} has two values in Starbase Extended's sizes.")
        bodies.append(body)
        changed.append(key.decode())
    if not bodies:
        raise FixError("Starbase Extended's starbase sizes have the game's 4.5 values now.")
    top = "".join(f"{n} = {v}\n" for n, v in sorted(header.items()))
    text = ((top + "\n" if top else "").encode() + b"\n\n".join(bodies)).replace(b"\r\n", b"\n")
    note = (
        f"{len(changed)} sizes get the game's 4.5 values and construction conditions, "
        "the new tiers the Citadel's values"
    )
    return {_last_file(layers, SHIP_SIZES, "starbase_sizes"): text + b"\n"}, [note]


def _construction_edits(
    data: bytes, entry: Entry, game_data: bytes, game_entry: Entry
) -> list[tuple[int, int, bytes]]:
    """An edit adding the game's construction conditions Starbase Extended's size lacks."""
    mine = next((c for c in children(data, entry) if c.key == CONSTRUCTION and c.block), None)
    theirs = next((c for c in children(game_data, game_entry) if c.key == CONSTRUCTION), None)
    if mine is None or theirs is None or not theirs.block:
        return []
    have = {_clause(data, c) for c in children(data, mine)}
    lacked = [c for c in children(game_data, theirs) if _clause(game_data, c) not in have]
    return _added(data, mine, [game_data[c.start : c.end] for c in lacked])


def _size_variables(
    layers: Layers, data: bytes, entry: Entry, body: bytes
) -> list[tuple[str, str]]:
    """The variables `body`, a copy of a ship size, uses, with their values: from
    its own file, or the one value the other ship size files give it."""
    file_vars = _variables(data)
    shared = layers.defined("common/scripted_variables")
    found: list[tuple[str, str]] = []
    for name in sorted({"@" + m.decode() for m in _VARIABLE.findall(_COMMENT.sub(b"", body))}):
        if name in file_vars:
            found.append((name, _text(data, file_vars[name])))
        elif name not in shared:
            found.append((name, _ship_size_value(layers, name)))
    return found


def _ship_size_value(layers: Layers, name: str) -> str:
    """The one value the ship size files give a variable. The game sets these per file."""
    values = {
        _text(data, entry)
        for layer, path in layers.ordered(SHIP_SIZES)
        for data in [layers.read(layer, path)]
        for entry in [_variables(data).get(name)]
        if entry is not None
    }
    if len(values) != 1:
        raise FixError(f"{name} has {len(values)} values in other ship sizes, not 1.")
    return values.pop()


# The playset's problems the patch leaves to the mods' authors, for the Workshop
# page. Each is a mod's own bug, too big to copy or soon to be fixed upstream.
# Drop a line once its mod has fixed it.
LEFT_TO_AUTHORS: tuple[str, ...] = ()


# The headings the Workshop page lists the fixes under, in order, by fix number.
# A fix in none of them is listed last, under "Other".
FIX_GROUPS: tuple[tuple[str, tuple[int, ...]], ...] = (
    ("Species and traits", (18, 19, 27)),
    ("Events and stories", (6, 11, 12, 26)),
    ("Galaxy and systems", (5, 17, 28)),
    ("Ships and starbases", (2, 3, 15, 16, 29, 30, 31, 32, 33, 34)),
    ("Graphics and camera", (1, 4)),
    ("Text and translations", (7, 10, 25)),
)


# Mods a fix's written files need loaded before the patch, beyond those it patches:
# fix 30 ships UI Overhaul Dynamic's window. They join the patch's dependencies.
NEEDS: dict[int, tuple[str, ...]] = {30: (UI_OVERHAUL,)}


# Each fix: its row in the report, what it does for the player (shown on the Workshop
# page), how it's made, and the mods it patches.
FIXES: tuple[tuple[int, str, Callable[[Layers], Made], tuple[str, ...]], ...] = (
    (
        1,
        (
            "Newer-style Dyson spheres, quantum catapults, Starlit systems and Voidspawn "
            "storms have models again, at System Scale's size"
        ),
        fix_system_scale_assets,
        (SYSTEM_SCALE,),
    ),
    (
        2,
        "The Starlit Starbase design gets 12 of its 13 guns in Starbase Extended's citadel",
        fix_starlit_slots,
        (STARBASE_EXTENDED,),
    ),
    (
        3,
        "Two Starbase Extended starbase sizes get their build-block radius and formation priority",
        fix_nsc_variables,
        (STARBASE_EXTENDED,),
    ),
    (
        4,
        "The system view uses System Scale's own 8 zoom steps, in place of Cinematic Camera's "
        "13: planet sizes match them again, and entering a system no longer breaks the view",
        fix_planet_scales,
        (SYSTEM_SCALE, CINEMATIC_CAMERA),
    ),
    (
        5,
        (
            "Sol starts from Planetary Diversity and More Events Mod get their neighbour "
            "systems with Real Space"
        ),
        fix_sol_neighbours,
        (REAL_SPACE, PLANETARY_DIVERSITY, MORE_EVENTS),
    ),
    (
        6,
        "A More Events Mod anomaly recognises Planetary Diversity's ocean worlds again",
        fix_pd_trigger,
        (PLANETARY_DIVERSITY, MORE_EVENTS),
    ),
    (
        7,
        "Missing names and tooltips",
        fix_text,
        (REAL_SPACE, SHIPS_IN_SCALING, STARBASE_EXTENDED),
    ),
    (
        10,
        "Planetary Diversity's bureaucrat unity bonus and necro world tooltips name the jobs again",
        fix_pd_bureaucrats,
        (PLANETARY_DIVERSITY, ASCENSION_WORLDS),
    ),
    (
        11,
        "More Events Mod's Ziaskehorn dig site is made when it's discovered",
        fix_ziaskehorn,
        (MORE_EVENTS,),
    ),
    (
        12,
        "More Events Mod's glacier AI leader with Iron Fist keeps the trait, as a commander",
        fix_glacier_leader,
        (MORE_EVENTS,),
    ),
    (
        15,
        "More Events Mod's three Progenitor shields cost upkeep again, at the game's 4.5.2 rates",
        fix_shield_upkeep,
        (MORE_EVENTS,),
    ),
    (
        16,
        "Space fauna's Large Mega Bombard gets its 4.5.2 range, at Ships in Scaling's scale",
        fix_mutation_ranges,
        (SHIPS_IN_SCALING,),
    ),
    (
        17,
        "Fleets with a jump drive can enter the Surveillance Supercomputer system, as in 4.5.2",
        fix_supercomputer_seal,
        (REAL_SPACE,),
    ),
    (
        18,
        (
            "Unemployment Benefits and the Shroud-Warped leader's psionic unity count once per "
            "pop again, not once per species trait, as in 4.5.2"
        ),
        fix_trait_categories,
        (PLANETARY_DIVERSITY, ASCENSION_WORLDS, MORE_EVENTS),
    ),
    (
        19,
        (
            "Lithoid Budding gets its full bonus on a Massive Crater and, with Ascension Worlds, "
            "consecrated worlds and worlds being detoxified can't be terraformed, as in 4.5.2"
        ),
        fix_ascension_worlds,
        (PLANETARY_DIVERSITY, ASCENSION_WORLDS),
    ),
    (
        25,
        (
            "Planetary Diversity's, Ascension Worlds' and More Arcologies' translations: broken "
            "lines are mended, so the game reads them"
        ),
        fix_broken_text,
        (PLANETARY_DIVERSITY, ASCENSION_WORLDS, MORE_ARCOLOGIES),
    ),
    (
        26,
        (
            "More Events Mod's Under the Blanket story gives its leader their trait: it no "
            "longer picks an autocracy's ruler or heir, and Fallen Empires don't start it"
        ),
        fix_under_blanket,
        (MORE_EVENTS,),
    ),
    (
        27,
        (
            "The AI values the Aquatic trait for species with Wet Climate Mods, as in 4.5.2, "
            "with Planetary Diversity's Aquatic trait"
        ),
        fix_aquatic,
        (PLANETARY_DIVERSITY,),
    ),
    (
        28,
        (
            "Nomadic empires can build a Hyper Relay at their own waystation before surveying "
            "the whole system, as in 4.5.2, with Smarter Hyper Relays"
        ),
        fix_hyper_relay,
        (SHRIMPAI,),
    ),
    (
        29,
        (
            "Starbase Extended's Asteroid Mining, Space Foundry and Space Factory get their "
            "bonuses from Mining Experts and Chain Manufacturing"
        ),
        fix_sbx_bonus_buildings,
        (STARBASE_EXTENDED,),
    ),
    (
        30,
        (
            "Starbase Extended's starbase window is UI Overhaul Dynamic's 4.5 window again, "
            "with room for every slot, and Upgrade away from Dismantle"
        ),
        fix_starbase_view,
        (STARBASE_EXTENDED,),
    ),
    (
        31,
        (
            "Starbases explode, light up and sound as in 4.5 with Starbase Extended, and every "
            "starbase model has the attach points its sections need"
        ),
        fix_starbase_models,
        (STARBASE_EXTENDED,),
    ),
    (
        32,
        (
            "Starbase Extended's modules and buildings keep all their conditions, its buildings "
            "work at arkships, and its orbital ring hangar bay has 4.5's hangars and bio-ship "
            "upkeep"
        ),
        fix_sbx_checks,
        (STARBASE_EXTENDED,),
    ),
    (
        33,
        "Starbase Extended's orbital ring shield and armour modules have a section",
        fix_ring_sections,
        (STARBASE_EXTENDED,),
    ),
    (
        34,
        (
            "Starbase Extended's starbase sizes count, and show on the map, as 4.5's do. "
            "Its Stronghold and HQ as the Citadel"
        ),
        fix_starbase_sizes,
        (STARBASE_EXTENDED,),
    ),
)
