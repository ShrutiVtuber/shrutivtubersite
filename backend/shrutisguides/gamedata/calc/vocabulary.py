# SPDX-License-Identifier: AGPL-3.0-only
"""
The stats a planner shows, named once for three games.

Each game says its own thing — Diablo II's `defense`, Diablo IV's `armor` and
Path of Exile 2's `armour` are one number to a person — so every pack's
wording is mapped into the canonical names here, and the panel groups them
the same way whichever game is open. A stat the vocabulary does not know is
not dropped: it is carried with its own name, grouped under `other`, and the
game's coverage note says how many there were.

⚠ A cap is a fact about the game, not a judgement about a person. Nothing
here scores anybody; `resistance-fire 68 of 75` is the same kind of sentence
as `12 of 38 met`.
"""
from __future__ import annotations

from dataclasses import dataclass

ATTRIBUTE = "attribute"
DEFENCE = "defence"
OFFENCE = "offence"
SPEED = "speed"
SKILLS = "skills"
UTILITY = "utility"
OTHER = "other"

# Panel order: what a character is, what keeps it alive, what it does, how
# fast, its ranks, the rest, and last the stats the vocabulary does not know.
GROUPS = (ATTRIBUTE, DEFENCE, OFFENCE, SPEED, SKILLS, UTILITY, OTHER)


@dataclass(frozen=True, slots=True)
class Stat:
    id: str
    name: str
    group: str
    unit: str = ""                 # "" a number · "%" a percentage · "s" seconds
    cap: str = ""                  # the id of the stat that caps this one, if any
    integer: bool = True


def _s(id: str, name: str, group: str, unit: str = "", cap: str = "", integer: bool = True) -> tuple[str, Stat]:
    return id, Stat(id, name, group, unit, cap, integer)


STATS: dict[str, Stat] = dict([
    # the four or five a character is made of
    _s("strength", "Strength", ATTRIBUTE),
    _s("dexterity", "Dexterity", ATTRIBUTE),
    _s("intelligence", "Intelligence", ATTRIBUTE),
    _s("vitality", "Vitality", ATTRIBUTE),
    _s("energy", "Energy", ATTRIBUTE),
    _s("willpower", "Willpower", ATTRIBUTE),
    # what keeps a character alive
    _s("life", "Maximum life", DEFENCE),
    _s("mana", "Maximum mana", DEFENCE),
    # Diablo IV names its resource per class — Fury, Mana, Spirit, Essence,
    # Ferocity — so `mana` would mislabel six classes of the eight.
    _s("resource", "Maximum resource", DEFENCE),
    _s("energy-shield", "Energy shield", DEFENCE),
    _s("armour", "Armour", DEFENCE),
    _s("evasion", "Evasion", DEFENCE),
    _s("block", "Block chance", DEFENCE, "%"),
    # Diablo IV has Dodge Chance AND Block Chance on the same character, and
    # dodge is a chance rather than a rating, so neither `block` nor
    # `evasion` is the same number.
    _s("dodge-chance", "Dodge chance", DEFENCE, "%", integer=False),
    _s("life-regeneration", "Life regeneration", DEFENCE),
    _s("mana-regeneration", "Mana regeneration", DEFENCE),
    _s("damage-reduction", "Damage reduction", DEFENCE, "%"),
    _s("life-leech", "Life leech", DEFENCE, "%", integer=False),
    _s("mana-leech", "Mana leech", DEFENCE, "%", integer=False),
    # resistances, each against its own cap
    _s("resistance-fire", "Fire resistance", DEFENCE, "%", cap="resistance-fire-max"),
    _s("resistance-cold", "Cold resistance", DEFENCE, "%", cap="resistance-cold-max"),
    _s("resistance-lightning", "Lightning resistance", DEFENCE, "%", cap="resistance-lightning-max"),
    _s("resistance-poison", "Poison resistance", DEFENCE, "%", cap="resistance-poison-max"),
    _s("resistance-chaos", "Chaos resistance", DEFENCE, "%", cap="resistance-chaos-max"),
    _s("resistance-magic", "Magic resistance", DEFENCE, "%", cap="resistance-magic-max"),
    # ⚠ Diablo IV resists physical like any element, and it is not "all": a
    # line naming it must not be spread across the other five.
    _s("resistance-physical", "Physical resistance", DEFENCE, "%", cap="resistance-physical-max"),
    _s("resistance-physical-max", "Physical resistance cap", DEFENCE, "%"),
    # Shadow is Diablo IV's fifth element and is neither chaos nor magic: it
    # has its own resistance on the character sheet and its own damage type.
    _s("resistance-shadow", "Shadow resistance", DEFENCE, "%", cap="resistance-shadow-max"),
    _s("resistance-fire-max", "Fire resistance cap", DEFENCE, "%"),
    _s("resistance-cold-max", "Cold resistance cap", DEFENCE, "%"),
    _s("resistance-lightning-max", "Lightning resistance cap", DEFENCE, "%"),
    _s("resistance-poison-max", "Poison resistance cap", DEFENCE, "%"),
    _s("resistance-chaos-max", "Chaos resistance cap", DEFENCE, "%"),
    _s("resistance-magic-max", "Magic resistance cap", DEFENCE, "%"),
    _s("resistance-shadow-max", "Shadow resistance cap", DEFENCE, "%"),
    # what it does to things
    _s("damage", "Damage", OFFENCE),
    _s("damage-min", "Minimum damage", OFFENCE),
    _s("damage-max", "Maximum damage", OFFENCE),
    _s("damage-physical", "Physical damage", OFFENCE),
    _s("damage-fire", "Fire damage", OFFENCE),
    _s("damage-cold", "Cold damage", OFFENCE),
    _s("damage-lightning", "Lightning damage", OFFENCE),
    _s("damage-poison", "Poison damage", OFFENCE),
    _s("damage-chaos", "Chaos damage", OFFENCE),
    _s("damage-magic", "Magic damage", OFFENCE),
    _s("damage-shadow", "Shadow damage", OFFENCE),
    _s("attack-rating", "Attack rating", OFFENCE),
    _s("critical-chance", "Critical strike chance", OFFENCE, "%", integer=False),
    _s("critical-damage", "Critical strike damage", OFFENCE, "%"),
    _s("penetration-fire", "Enemy fire resistance", OFFENCE, "%"),
    _s("penetration-cold", "Enemy cold resistance", OFFENCE, "%"),
    _s("penetration-lightning", "Enemy lightning resistance", OFFENCE, "%"),
    _s("penetration-poison", "Enemy poison resistance", OFFENCE, "%"),
    _s("penetration-magic", "Enemy magic resistance", OFFENCE, "%"),
    # how fast
    _s("speed-attack", "Attack speed", SPEED, "%"),
    _s("speed-cast", "Cast speed", SPEED, "%"),
    _s("speed-recovery", "Hit recovery", SPEED, "%"),
    _s("speed-block", "Block rate", SPEED, "%"),
    _s("speed-movement", "Movement speed", SPEED, "%"),
    _s("cooldown-reduction", "Cooldown reduction", SPEED, "%"),
    _s("resource-cost-reduction", "Resource cost reduction", SPEED, "%"),
    # ranks
    _s("skills-all", "All skills", SKILLS),
    _s("skills-class", "Class skills", SKILLS),
    _s("skills-tab", "Skill tab", SKILLS),
    _s("skills-single", "Single skill", SKILLS),
    # the rest
    # Diablo IV's Lucky Hit Chance: the chance a hit rolls for every
    # "Lucky Hit:" effect the character carries. Nothing else names it.
    _s("lucky-hit", "Lucky hit chance", UTILITY, "%", integer=False),
    _s("magic-find", "Magic find", UTILITY, "%"),
    _s("gold-find", "Gold find", UTILITY, "%"),
    _s("light-radius", "Light radius", UTILITY),
    _s("sockets", "Sockets", UTILITY),
    # Seven Path of Exile 2 brought that nothing above says. Each is here
    # because an unnamed stat lands in `other`, and these are not other: a
    # person reads them in the same breath as life, armour and fire damage.
    #
    # ⚠ Spirit is a budget, not a number that grows — a build spends it on
    # what it keeps running — but it is a pool beside life and mana and it
    # belongs where they are.
    #
    # ⚠ Spell and attack damage are two brackets this game never adds
    # together, so they cannot both be `damage`; minion damage and minion
    # life are the character's build and not the character's body, and a
    # summoner has no other row to read.
    _s("spirit", "Spirit", DEFENCE),
    _s("stun-threshold", "Stun threshold", DEFENCE),
    _s("life-minion", "Minion life", DEFENCE),
    _s("damage-spell", "Spell damage", OFFENCE, "%"),
    _s("damage-attack", "Attack damage", OFFENCE, "%"),
    _s("damage-minion", "Minion damage", OFFENCE, "%"),
    _s("speed-skill", "Skill speed", SPEED, "%"),
])

# ── the ailments and the statuses ────────────────────────────────────────────
# ⚠ These earn canonical names, and here is the argument, because a shared
# vocabulary that grows a bulge for one game stops being shared.
#
# A status is not decoration in an action RPG; it is a way of killing and a
# way of dying, and a person builds AT it. A freeze build aims at freeze
# buildup the way a crit build aims at critical strike chance, and reads the
# number in the same breath. Path of Exile 2 alone puts nine hundred stat
# lines on these rows — more than it puts on armour — and left unnamed every
# one of them lands in `other`, under the rows nobody set a target for.
#
# The numbers are the same numbers for every status and the game says them
# the same way, so this is a loop and not two hundred entries written out. BUILDUP is how fast
# it lands, CHANCE is how often, MAGNITUDE is how hard it hits, DURATION is
# how long it stays — all four are what a character does to something else,
# so they are offence. THRESHOLD is how much this character takes before the
# status lands on THEM, and the `on you` numbers are how bad it is once it
# has: those are defence. A status a pack never mentions costs nothing here —
# `grouped` only ever draws the rows a plan actually has.
#
# ⚠ Only the family is promoted. Everything else one game says alone — the
# presence radius, the runic ward, the glory — stays under its own id in
# `other`, which is where a stat with no second game to agree with belongs.
_STATUSES = ("ignite", "freeze", "shock", "chill", "poison", "bleed", "bleeding", "stun", "daze",
             "blind", "pin", "electrocute", "immobilisation", "maim", "withered", "hinder", "slow",
             "exposure", "flammability", "curse", "curses", "ailment", "ailments",
             "elemental-ailment", "elemental-ailments", "damaging-ailments", "non-damaging-ailments")
for _status in _STATUSES:
    _read = _status.replace("-", " ").capitalize()
    for _suffix, _what, _group, _unit in (
            ("chance", "chance", OFFENCE, "%"), ("buildup", "buildup", OFFENCE, "%"),
            ("magnitude", "magnitude", OFFENCE, "%"), ("duration", "duration", OFFENCE, "%"),
            ("threshold", "threshold", DEFENCE, ""),
            ("duration-on-you", "duration on you", DEFENCE, "%"),
            ("magnitude-on-you", "magnitude on you", DEFENCE, "%"),
            ("effect-on-you", "effect on you", DEFENCE, "%")):
        # setdefault: a status already named by hand above keeps that name
        STATS.setdefault(f"{_status}-{_suffix}", Stat(f"{_status}-{_suffix}", f"{_read} {_what}",
                                                      _group, _unit, integer=False))


def stat(id: str) -> Stat:
    """The canonical stat, or one invented from the id so an unknown line still has a name and a group."""
    known = STATS.get(id)
    if known:
        return known
    return Stat(id, id.replace("-", " ").strip().capitalize(), OTHER, "%" if id.endswith(("-percent", "-pct")) else "")


def grouped(ids: list[str]) -> list[tuple[str, list[Stat]]]:
    """The stats in panel order, grouped, for a page to draw."""
    out: list[tuple[str, list[Stat]]] = []
    for g in GROUPS:
        in_group = [stat(i) for i in ids if stat(i).group == g]
        if in_group:
            out.append((g, in_group))
    return out
