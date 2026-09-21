# SPDX-License-Identifier: AGPL-3.0-only
"""
Diablo II: Resurrected — its own words, mapped into the vocabulary.

The pack's stat keys are already clean (`enhanced-damage`, `all-resistances`),
so most of this is a table. What it is not is a guess: a key this table does
not know becomes a NOT-COUNTED contribution carrying its own text, so the
line shows in the breakdown and stays out of the arithmetic. The panel then
says how many such lines a plan has, which is the honest version of
"coverage".

⚠ One line may be several contributions. `all-resistances` is four; `+2 to
all skills` is one. The mapper returns a list, always.
"""
from __future__ import annotations

from ..model import APPROXIMATE, COUNTED, NOT_COUNTED, Contribution

GAME = "diablo-ii-resurrected"

# The caps a character starts with, and the base a level-1 character has.
BASE = {"resistance-fire-max": 75.0, "resistance-cold-max": 75.0, "resistance-lightning-max": 75.0,
        "resistance-poison-max": 75.0, "resistance-magic-max": 75.0, "block": 0.0}

# pack key → (canonical stat, form). A tuple of stats means the line splits.
TABLE: dict[str, tuple[object, str]] = {
    "strength": ("strength", "flat"), "dexterity": ("dexterity", "flat"),
    "vitality": ("vitality", "flat"), "energy": ("energy", "flat"), "enr": ("energy", "flat"),
    "all-attributes": (("strength", "dexterity", "vitality", "energy"), "flat"),
    "life": ("life", "flat"), "hp": ("life", "flat"), "mana": ("mana", "flat"),
    "maximum-life-percent": ("life", "increased"), "maximum-mana-percent": ("mana", "increased"),
    "replenish-life": ("life-regeneration", "flat"), "mana-regeneration": ("mana-regeneration", "flat"),
    "defense": ("armour", "flat"), "enhanced-defense": ("armour", "increased"),
    "defense-vs-missile": ("armour", "flat"), "defense-vs-melee": ("armour", "flat"),
    "chance-to-block": ("block", "flat"),
    "damage-reduced-percent": ("damage-reduction", "flat"), "magic-damage-reduced": ("damage-reduction", "flat"),
    "damage-reduced": ("damage-reduction", "flat"),
    "life-stolen-per-hit": ("life-leech", "flat"), "mana-stolen-per-hit": ("mana-leech", "flat"),
    "all-resistances": (("resistance-fire", "resistance-cold", "resistance-lightning", "resistance-poison"), "flat"),
    "fire-resistance": ("resistance-fire", "flat"), "cold-resistance": ("resistance-cold", "flat"),
    "lightning-resistance": ("resistance-lightning", "flat"), "poison-resistance": ("resistance-poison", "flat"),
    "magic-resistance": ("resistance-magic", "flat"),
    "maximum-all-resistances": (("resistance-fire-max", "resistance-cold-max", "resistance-lightning-max", "resistance-poison-max"), "flat"),
    "maximum-fire-resistance": ("resistance-fire-max", "flat"), "maximum-cold-resistance": ("resistance-cold-max", "flat"),
    "maximum-lightning-resistance": ("resistance-lightning-max", "flat"), "maximum-poison-resistance": ("resistance-poison-max", "flat"),
    "enhanced-damage": ("damage-physical", "increased"),
    "minimum-damage": ("damage-min", "flat"), "maximum-damage": ("damage-max", "flat"),
    "added-damage": ("damage", "flat"), "damage": ("damage", "flat"),
    "fire-damage": ("damage-fire", "flat"), "cold-damage": ("damage-cold", "flat"),
    "lightning-damage": ("damage-lightning", "flat"), "poison-damage": ("damage-poison", "flat"),
    "magic-damage": ("damage-magic", "flat"),
    "minimum-fire-damage": ("damage-fire", "flat"), "maximum-fire-damage": ("damage-fire", "flat"),
    "minimum-cold-damage": ("damage-cold", "flat"), "maximum-cold-damage": ("damage-cold", "flat"),
    "minimum-lightning-damage": ("damage-lightning", "flat"), "maximum-lightning-damage": ("damage-lightning", "flat"),
    "minimum-poison-damage": ("damage-poison", "flat"), "maximum-poison-damage": ("damage-poison", "flat"),
    "fire-skill-damage": ("damage-fire", "increased"), "cold-skill-damage": ("damage-cold", "increased"),
    "lightning-skill-damage": ("damage-lightning", "increased"), "poison-skill-damage": ("damage-poison", "increased"),
    "magic-skill-damage": ("damage-magic", "increased"),
    "attack-rating": ("attack-rating", "flat"), "attack-rating-percent": ("attack-rating", "increased"),
    "deadly-strike": ("critical-chance", "flat"),
    "enemy-fire-resistance": ("penetration-fire", "flat"), "enemy-cold-resistance": ("penetration-cold", "flat"),
    "enemy-lightning-resistance": ("penetration-lightning", "flat"), "enemy-poison-resistance": ("penetration-poison", "flat"),
    "enemy-magic-resistance": ("penetration-magic", "flat"), "enemy-physical-resistance": ("damage-physical", "increased"),
    "increased-attack-speed": ("speed-attack", "flat"), "faster-cast-rate": ("speed-cast", "flat"),
    "faster-hit-recovery": ("speed-recovery", "flat"), "faster-block-rate": ("speed-block", "flat"),
    "faster-run-walk": ("speed-movement", "flat"),
    "all-skills": ("skills-all", "flat"), "skill-tab": ("skills-tab", "flat"), "skill": ("skills-single", "flat"),
    "charged-skill": ("skills-single", "flat"), "skill-any-class": ("skills-all", "flat"),
    "magic-find": ("magic-find", "flat"), "extra-gold": ("gold-find", "flat"),
    "light-radius": ("light-radius", "flat"), "sockets": ("sockets", "flat"),
}
for _c in ("amazon", "assassin", "barbarian", "druid", "necromancer", "paladin", "sorceress", "warlock"):
    TABLE[f"{_c}-skills"] = ("skills-class", "flat")
for _e in ("fire", "cold", "lightning", "poison", "magic"):
    TABLE[f"{_e}-skills"] = ("skills-single", "flat")

# Facts we hold and cannot put a number on. They are LISTED, never silently dropped.
UNCOUNTABLE = {
    "cast-on-striking", "cast-when-struck", "cast-on-attack", "cast-on-kill", "cast-on-level-up", "cast-when-you-die",
    "aura-when-equipped", "crushing-blow", "open-wounds", "ignore-target-defense", "piercing-attack", "knockback",
    "slows-target", "freezes-target", "hit-blinds-target", "hit-causes-flee", "prevent-monster-heal", "reanimate-as",
    "indestructible", "ethereal", "cannot-be-frozen", "half-freeze-duration", "slain-monsters-rest-in-peace",
    "property-group", "charged", "random-skill", "random-class-skills", "explosive-arrows", "magic-arrows",
    "attacker-takes-damage", "attacker-takes-lightning-damage", "damage-taken-to-mana", "monster-defense-per-hit",
    "target-defense-percent", "poison-length-reduced", "poison-duration", "cold-duration", "requirements-reduced",
    "maximum-durability", "repairs-durability", "replenishes-quantity", "stack-size", "maximum-stamina",
    "stamina-recovery", "slower-stamina-drain", "experience-gained", "vendor-prices-reduced", "extra-blood",
    "finishing-moves-keep-charges", "life-after-kill", "mana-after-kill", "life-after-demon-kill",
    "damage-vs-undead", "damage-vs-demons", "attack-rating-vs-undead", "attack-rating-vs-demons",
    "fire-absorb", "cold-absorb", "lightning-absorb", "magic-absorb",
    "fire-absorb-percent", "cold-absorb-percent", "lightning-absorb-percent",
    "sunder-fire-immunity", "sunder-cold-immunity", "sunder-lightning-immunity",
    "sunder-poison-immunity", "sunder-physical-immunity", "sunder-magic-immunity",
}


def base_for(plan: dict, data, pool) -> dict[str, float]:
    """
    What the character is before a single piece of gear: the class's starting
    attributes, and the life and mana its level and its vitality and energy
    have bought. Without this every defensive number is only what the gear
    grants, which reads as a total and is not one.

    ⚠ Attributes resolve first, because life is bought with vitality: the
    pool is asked for the gear's contribution, and the class's own table
    turns the result into life and mana.
    """
    cls = data.get(GAME, "class", str(plan.get("class_id") or "")) or {}
    level = max(1, int(plan.get("level") or 1))
    start = cls.get("starting_attributes") or {}
    per_level = cls.get("per_level") or {}
    per_point = cls.get("per_point") or {}
    base = dict(BASE)
    for a in ("strength", "dexterity", "vitality", "energy"):
        base[a] = float(start.get(a) or 0)
    vitality = pool.total("vitality", base=base["vitality"]).value
    energy = pool.total("energy", base=base["energy"]).value
    base["life"] = (float(cls.get("starting_life") or 0)
                    + (level - 1) * float(per_level.get("life") or 0)
                    + max(0.0, vitality - base["vitality"]) * float(per_point.get("life_per_vitality") or 0))
    base["mana"] = (float(cls.get("starting_mana") or 0)
                    + (level - 1) * float(per_level.get("mana") or 0)
                    + max(0.0, energy - base["energy"]) * float(per_point.get("mana_per_energy") or 0))
    base["block"] = float(cls.get("base_block_pct") or 0)
    return base


def _number(line: dict) -> tuple[float | None, str]:
    """The value to count, and how sure we are. A range counts at its best roll, and says so."""
    for field in ("value",):
        v = line.get(field)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return float(v), COUNTED
    lo, hi = line.get("min"), line.get("max")
    if isinstance(hi, (int, float)) and not isinstance(hi, bool):
        if isinstance(lo, (int, float)) and lo != hi:
            return float(hi), APPROXIMATE          # the best roll; the pack keeps both ends
        return float(hi), COUNTED
    if isinstance(lo, (int, float)) and not isinstance(lo, bool):
        return float(lo), COUNTED
    return None, NOT_COUNTED


def map_line(line: dict, source: dict) -> list[Contribution]:
    """One of a record's stat lines, as contributions."""
    key = str(line.get("stat") or "").strip()
    text = str(line.get("text") or line.get("stat") or "")[:160]
    common = dict(source_kind=source.get("kind", ""), source_id=source.get("id", ""),
                  source_name=source.get("name", ""), text=text, place=source.get("place", ""))
    if not key:
        return []
    value, sureness = _number(line)
    per_level = key.endswith("-per-level")
    lookup = key[: -len("-per-level")] if per_level else key
    if lookup in UNCOUNTABLE or key in UNCOUNTABLE or lookup not in TABLE:
        # a fact we hold and cannot compute with: its own row, its own name
        return [Contribution(stat=lookup, form="flat", value=float(value or 0.0), state=NOT_COUNTED, **common)]
    stats, form = TABLE[lookup]
    if value is None:
        # ⚠ We know which stat this is; we just have no number for it. It goes
        # in THAT stat's row as an uncounted line, so a person reading their
        # armour sees the piece that could not be counted towards it — rather
        # than a phantom "Defense" row beside the real "Armour" one.
        names = stats if isinstance(stats, tuple) else (stats,)
        return [Contribution(stat=n, form="flat", value=0.0, state=NOT_COUNTED, **common) for n in names]
    if per_level:
        form = "per_level"
    names = stats if isinstance(stats, tuple) else (stats,)
    return [Contribution(stat=n, form=form, value=value, state=sureness, **common) for n in names]
