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

from ..damage import Hit, between
from ..model import APPROXIMATE, COUNTED, NOT_COUNTED, Contribution, Step, worst

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
    # "+3 to Fire Skills" raises a whole tab, not one skill; the param says which
    TABLE[f"{_e}-skills"] = ("skills-tab", "flat")

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


def _param(key: str, line: dict) -> str:
    """
    What a skill bonus is ABOUT. `+3 to Corpse Explosion` raises one skill;
    `+2 to Summoning` raises one tab; `+1 to Sorceress skills` raises a
    class's; `+1 to all skills` raises everything. The pack records the
    target beside the line, and without carrying it here every skill in a
    plan would take every bonus.
    """
    if key == "skill":
        return str(line.get("skill_id") or "")
    if key == "skill-tab":
        cls, tab = line.get("class_id"), line.get("skill_tab_id")
        return f"{cls}-{tab}" if cls and tab else str(tab or "")
    if key.endswith("-skills"):
        return key[: -len("-skills")]          # a class's name, or an element's
    return ""


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
                  source_name=source.get("name", ""), text=text, place=source.get("place", ""),
                  param=_param(key, line))
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


# ── what a skill hits for ────────────────────────────────────────────────────

def planned_points(plan: dict, skill_id: str) -> int:
    """The points a person put into a skill with their own hand."""
    picks = ((plan.get("sections") or {}).get("skills") or {}).get("picks") or []
    for p in picks:
        if isinstance(p, dict) and p.get("id") == skill_id:
            try:
                return max(0, int(p.get("points") or 0))
            except (TypeError, ValueError):
                return 0
    return 0


def _tab_matches(param: str, skill: dict) -> bool:
    """`+2 to Summoning` and `+3 to Fire Skills` both name a tab; the pack writes them differently."""
    if not param:
        return False
    group = str(skill.get("group_id") or "").lower()
    name = str(skill.get("group") or "").lower()
    p = param.lower()
    return p == group or p in group or p in name.replace(" ", "-")


def effective_rank(skill: dict, points: int, pool) -> tuple[int, list[Contribution]]:
    """
    The rank a skill actually reaches: the points a person spent, plus every
    bonus that is ABOUT this skill — all skills, this class's, this tab's,
    this one by name. A bonus meant for another tab is not counted, which is
    the whole reason a contribution carries what it is about.
    """
    rank, lines = float(points), []
    for c in pool.lines("skills-all"):
        rank += c.value
        lines.append(c)
    for c in pool.lines("skills-class"):
        if c.param and c.param == str(skill.get("class_id") or ""):
            rank += c.value
            lines.append(c)
    for c in pool.lines("skills-tab"):
        if _tab_matches(c.param, skill):
            rank += c.value
            lines.append(c)
    for c in pool.lines("skills-single"):
        if c.param and c.param == skill.get("id"):
            rank += c.value
            lines.append(c)
    return int(rank), lines


def damage_for(plan: dict, data, pool, pick: dict) -> Hit | None:
    """
    One skill's damage, aimed at the number the game's own tooltip shows.

    ⚠ Synergies count HARD POINTS only — the points a person spent, not the
    rank gear lifts the skill to. Counting the gear twice would inflate every
    number in the panel, and it is the mistake every hand-made spreadsheet
    makes.
    """
    skill = data.get(GAME, "skill", str(pick.get("id") or ""))
    if not skill:
        return None
    element = str(skill.get("damage_type") or "").lower()
    table = skill.get("ranks_or_levels") or []
    points = planned_points(plan, skill["id"])
    rank, rank_lines = effective_rank(skill, points, pool)
    hit = Hit(skill_id=skill["id"], skill_name=skill.get("name") or skill["id"], element=element, rank=rank)
    if points <= 0:
        hit.state, hit.why = NOT_COUNTED, "no points are planned into it"
        return hit

    key = next((k for k in (f"{element}_damage", "damage", "physical_damage", "magic_damage")
                if any(k in (r.get("values") or {}) for r in table)), "")
    if not key:
        hit.state, hit.why = NOT_COUNTED, "the pack records no damage for this skill — it may not deal any"
        return hit
    band, sureness = between(table, rank, key)
    if band is None:
        hit.state, hit.why = NOT_COUNTED, "the pack records no damage at any rank"
        return hit
    low, high = band
    hit.steps.append(Step("base", f"at rank {rank}" + (" (between the rows the pack records)" if sureness != COUNTED else ""),
                          rank, high, rank_lines))
    if sureness != COUNTED:
        hit.why = "the rank falls between the ranks the pack records, so the damage is read across them"

    # synergies: another skill's hard points, at so much a point
    synergy_pct, synergy_lines = 0.0, []
    for syn in (skill.get("synergies") or []):
        if not isinstance(syn, dict):
            continue
        sid, per = str(syn.get("skill_id") or ""), syn.get("per_point")
        if not sid or not isinstance(per, (int, float)):
            continue
        hard = planned_points(plan, sid)
        if hard:
            synergy_pct += hard * float(per)
            other = data.get(GAME, "skill", sid) or {}
            synergy_lines.append(Contribution(stat=f"damage-{element or 'physical'}", form="increased",
                                              value=hard * float(per), source_kind="skill", source_id=sid,
                                              source_name=other.get("name") or sid,
                                              text=f"{hard} points at {per}% a point"))

    # and whatever the gear adds to this element
    gear_pct, gear_lines = 0.0, []
    for c in pool.lines(f"damage-{element}") if element else ():
        if c.form == "increased" and c.state != NOT_COUNTED:
            gear_pct += c.value
            gear_lines.append(c)

    if synergy_pct or gear_pct:
        low *= 1 + (synergy_pct + gear_pct) / 100.0
        high *= 1 + (synergy_pct + gear_pct) / 100.0
        hit.steps.append(Step("increased", "synergies and gear", synergy_pct + gear_pct, high, synergy_lines + gear_lines))

    hit.low, hit.high = low, high
    hit.state = worst([sureness] + [c.state for c in rank_lines + gear_lines])
    return hit
