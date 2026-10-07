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
from stellaris_patcher.patchmod.layers import GAME, Layers, find_define, numbers, parse_file
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


class FixError(Exception):
    """A fix doesn't apply any more, or its cause has changed."""


@dataclass(frozen=True)
class Outcome:
    number: int  # the row in the report's table
    title: str
    files: dict[str, bytes] = field(default_factory=dict)
    notes: tuple[str, ...] = ()  # what it did, or parts it skipped
    left_out: str = ""  # why nothing was written, if so
    mods: tuple[str, ...] = ()  # the mods it patches, by Cold Steel key


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
    outcomes: list[Outcome] = []
    for number, title, make, mods in FIXES:
        try:
            files, notes = make(layers)
        except FixError as why:
            outcomes.append(Outcome(number, title, left_out=str(why), mods=mods))
            continue
        outcomes.append(Outcome(number, title, files, tuple(notes), mods=mods))
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
    fixes = "".join(f"[*]{o.title}\n" for o in written)
    waiting = "".join(f"[*]{problem}\n" for problem in LEFT_TO_AUTHORS)
    return (
        f"[h1]{NAME}[/h1]\n"
        f"Fixes clashes and breakages between the mods of the {PLAYSET} playset, "
        f"for Stellaris {version}.\n\n"
        "[h2]Load order[/h2]\n"
        "Load it last, after every mod below.\n\n"
        f"[h2]Required mods[/h2]\n[list]\n{required}[/list]\n\n"
        f"[h2]What it fixes[/h2]\n[list]\n{fixes}[/list]\n\n"
        "[h2]Known issues, waiting for the mod authors[/h2]\n"
        "These come from the mods themselves. The patch leaves them to their authors, "
        "whose next updates should fix them.\n"
        f"[list]\n{waiting}[/list]\n"
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
    lines: list[str] = []
    for name in sorted(missing):
        values = {
            _text(layers.read(layer, path), entry)
            for layer, path in layers.ordered("common/ship_sizes")
            for entry in [_variables(layers.read(layer, path)).get(name)]
            if entry is not None
        }
        if len(values) != 1:
            raise FixError(f"{name} has {len(values)} values in other ship sizes, not 1.")
        lines.append(f"{name} = {values.pop()}\n")
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
    wanted = event_id.encode()
    for layer, path in layers.ordered("events"):
        data = layers.read(layer, path)
        if wanted not in data:
            continue
        for entry in scan(data):
            if entry.block and value_of(data, entry, b"id") == wanted:
                if layer != MORE_EVENTS:
                    raise FixError(f"{event_id} now comes from {layer}, not More Events Mod.")
                namespace = event_id.rpartition(".")[0]
                text = f"namespace = {namespace}\n\n".encode() + data[entry.start : entry.end]
                return text.replace(b"\r\n", b"\n") + b"\n"
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
    file_vars = _variables(data)
    shared = layers.defined("common/scripted_variables")
    header = ""
    for name in sorted({"@" + m.decode() for m in _VARIABLE.findall(_COMMENT.sub(b"", body))}):
        if name in file_vars:
            header += f"{name} = {_text(data, file_vars[name])}\n"
        elif name not in shared:
            raise FixError(f"{entry.key.decode()} uses {name}, which nothing defines.")
    text = (header + "\n" if header else "").encode() + body
    return text.replace(b"\r\n", b"\n") + b"\n"


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


# 19. Ascension Worlds' copies miss two of the game's fixes


BUDDING = "trait_lithoid_budding"
POP_MODIFIER = b"triggered_planet_pop_group_modifier_for_species"
DIVIDE = b"divide_over_pop_groups"
GAME_RULES = "common/game_rules"
TERRAFORM = "can_terraform_planet"


def fix_ascension_worlds(layers: Layers) -> Made:
    """Ascension Worlds' Lithoid Budding and terraforming rule, with the
    game's lines they lack. A check Ascension Worlds comments out on purpose
    stays out."""
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
        raise FixError("Ascension Worlds' trait and rule match the game's now.")
    return files, notes


def _budding(layers: Layers) -> tuple[str, bytes, str]:
    """Each of the trait's pop modifiers gets the game's `divide_over_pop_groups`
    where it lacks one. 4.5.2 gave the Massive Crater's its full bonus."""
    traits = layers.defined("common/traits")
    if traits.get(BUDDING, ("",))[0] != ASCENSION_WORLDS:
        raise FixError(f"{BUDDING} doesn't come from Ascension Worlds now.")
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
    note = f"{BUDDING}: {len(edits)} pop modifier gets the game's {DIVIDE.decode()}"
    return _first_file(layers, "common/traits", "ascension_worlds"), text, note


def _terraform(layers: Layers) -> tuple[str, bytes, str]:
    """The rule gets each of the game's custom tooltips it lacks, by fail
    text. One it has in a comment was taken out on purpose, and stays out."""
    found: tuple[str, bytes, Entry] | None = None
    for layer, path in layers.ordered(GAME_RULES):  # the last definition wins
        data = layers.read(layer, path)
        for entry in scan(data):
            if entry.key == TERRAFORM.encode() and entry.block:
                found = (layer, data, entry)
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


def _fail_text(data: bytes, check: Entry) -> str:
    if check.key != b"custom_tooltip" or not check.block:
        return ""
    return (value_of(data, check, b"fail_text") or b"").decode().strip('"')


# The playset's problems the patch leaves to the mods' authors, for the Workshop
# page. Each is a mod's own bug, too big to copy or soon to be fixed upstream.
# Drop a line once its mod has fixed it.
LEFT_TO_AUTHORS = (
    (
        "Planetary Diversity, Ascension Worlds and More Events Mod: their copies of the "
        "game's species traits predate 4.5.2. Unemployment Benefits and the Shroud-Warped "
        "leader's psionic unity count once per species trait again"
    ),
    (
        "Starbase Extended 3.0: its starbase window predates 4.5. It has no button from an "
        "orbital ring back to its planet, no design name or retrofit, no macro builder tab, "
        "and two lists have no scrollbar"
    ),
    (
        "Starbase Extended 3.0: six modules lose one of their two conditions, two bonuses "
        "check for buildings that don't exist, and one building's condition is broken. Some "
        "orbital ring sections, sounds and animations are missing, and its orbital ring "
        "hangar bay costs bio-ship empires energy, not food"
    ),
    "shrimpAI: a Nomadic empire can't build a Hyper Relay at its own waystation",
    (
        "Planetary Diversity: the AI doesn't yet value the Aquatic trait for species that "
        "prefer wet planets, as 4.5.2's AI does"
    ),
    "Dark UI: 4.5.2's new icons, such as the fleet deselect button, aren't dark yet",
)


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
        "Six missing names and tooltips",
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
        19,
        (
            "Ascension Worlds: Lithoid Budding gets its full bonus on a Massive Crater, and "
            "consecrated worlds and worlds being detoxified can't be terraformed, as in 4.5.2"
        ),
        fix_ascension_worlds,
        (ASCENSION_WORLDS,),
    ),
)
