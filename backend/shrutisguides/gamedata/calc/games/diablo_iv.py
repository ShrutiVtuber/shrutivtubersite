# SPDX-License-Identifier: AGPL-3.0-only
"""
Diablo IV — its own words, mapped into the vocabulary.

Diablo IV's pack speaks twice. A paragon node says `{"stat": "strength",
"attribute": "Strength_Core", "value": 5, "display": "+5"}` and a gear affix
says `{"stat": "Armor_Bonus", "unit": "flat", "min": 981, "max": 1225}` — the
same database, one name in the game's engine spelling and one in plain words.
Folding the case and turning `_` into `-` makes them one key, and the table
below is written in that folded spelling, so each entry serves both.

⚠ THE SCALE IS NOT IN THE NUMBER. `0.08` is eight percent on an affix and
eight hundredths of a percent on a paragon node, and nothing but the line's
other fields says which. Four rules settle it, in this order:

  1. `unit: "percent"` — the pack's own word for "this is a fraction". ×100.
  2. a `display` field — the pack has already written the number the way the
     game shows it (`"+2%"` beside `2.0`). Take it as it stands.
  3. neither, and the stat is one a person reads as a percentage — gem
     bonuses and set powers are written as fractions there. ×100.
  4. otherwise — a plain amount. Take it as it stands.

⚠ A RESISTANCE IS TWO DIFFERENT QUANTITIES. `+{value} All Resistances` at
325–400 is a resistance RATING; `+{value}% All Resistances` at 0.3 is thirty
percent. They differ only by `unit`, and turning a rating into a percentage
needs a level-and-difficulty formula this pack does not carry. So a
resistance line counts ONLY when its unit says `percent`; a rating is kept on
that same resistance's row as an uncounted line, where a person can see the
piece that is not in their number.

⚠ Greater affixes are not a different stat — they are the same affix rolled
higher, and the pack files them as their own record with bigger numbers
(`x2-armor-greater` beside `s04-armor`). Nothing here needs to know.
"""
from __future__ import annotations

from ..damage import Hit, between
from ..model import APPROXIMATE, COUNTED, NOT_COUNTED, Contribution, Step, worst
from ..vocabulary import stat as canonical

GAME = "diablo-iv"

# The character before anything is chosen. The five resistances start capped
# at 70% and some affixes raise that cap, so the cap is a row of its own that
# a maximum-resistance line adds to.
#
# ⚠ The base life and the class's starting attributes are NOT here, because
# they are not in the pack: a class record carries its resource, its
# specialisations and its prose, and no life table, no per-level growth and
# no starting attributes. Inventing them would put a made-up number under a
# real one, so life and the four attributes start at nothing and the panel
# shows exactly what a person's choices grant. See diablo_iv_census.md.
RESISTANCES = ("resistance-fire", "resistance-cold", "resistance-lightning", "resistance-poison", "resistance-shadow")
# physical is resisted too, and capped the same, but it is never one of "all"
ALL_RESISTED = RESISTANCES + ("resistance-physical",)
BASE = {f"{r}-max": 70.0 for r in ALL_RESISTED}

# Damage rows are read as a percentage of what the character would do with
# none of this: 100 is the unmodified skill, 480 is four-fold-and-some. Only
# the rows a plan actually has lines for are opened, so a bare plan does not
# grow seven empty damage rows.
#
# ⚠ Named one by one rather than by prefix: `damage-reduction` starts with
# the same six letters and is a percentage of its own, not a multiple of the
# character's output.
DAMAGE_BASE = 100.0
DAMAGE_ROWS = ("damage", "damage-physical", "damage-fire", "damage-cold",
               "damage-lightning", "damage-poison", "damage-shadow")

# Diablo IV's damage multipliers group. Inside one bucket they add; between
# buckets they multiply — which is exactly what `Pool` does with `more`
# contributions carrying a `bucket`. The pack names the grouping itself: a
# stat called `Bucketed_Multiplicative_*` is additive within its own bucket.
#
#   all               every skill's damage           +x% Damage
#   type              the element the hit deals      +x% Fire Damage
#   vulnerable        against a Vulnerable enemy
#   crowd-controlled  against a held enemy
#   elites            against an Elite
#   over-time         damage dealt over time
#   vs-over-time      against an enemy already burning, poisoned, bleeding
#   close / distant   by how far away the enemy is
#   fortified         while the character is Fortified
#   while-healthy     while the character is at high life
#   vs-healthy / vs-injured   by the enemy's life
#   skill:<tag>       one category of skills — traps, shouts, companions
#   × <a thing>       a standalone multiplier; see MULTIPLIERS below
BUCKETS: dict[str, str] = {
    "damage-percent-all-from-skills": "all", "bucketed-multiplicative-damage": "all",
    "damage-type-percent": "type", "bucketed-multiplicative-damage-type": "type",
    "bucketed-multiplicative-damage-type-fireholy": "type", "nonphysical-damage-percent": "type",
    "vulnerable-health-damage": "vulnerable", "bucketed-multiplicative-vulnerable-health-damage": "vulnerable",
    "damage-percent-bonus-vs-cc-all": "crowd-controlled", "damage-percent-bonus-vs-cc-target": "crowd-controlled",
    "damage-percent-bonus-vs-elites": "elites",
    "dot-dps-bonus-percent": "over-time", "bucketed-multiplicative-dot-damage": "over-time",
    "damage-percent-bonus-against-dot-type": "vs-over-time",
    "damage-bonus-to-near": "close", "damage-bonus-to-far": "distant",
    "damage-percent-bonus-when-fortified": "fortified",
    "damage-bonus-at-high-health": "while-healthy",
    "damage-bonus-to-high-health": "vs-healthy", "damage-bonus-to-low-health": "vs-injured",
    "damage-bonus-percent-to-weakened": "vs-weakened",
    "damage-percent-bonus-when-weapon-swapping": "on-weapon-swap",
}

# The `[x]` multipliers a person sees in the game: each stands on its own
# rather than joining a bucket, so each gets a bucket named after the thing
# it came from and multiplies against every other.
#
# ⚠ Two standalone multipliers on ONE item would be summed rather than
# multiplied, because they would share that bucket name. No record in the
# 3.2.1 pack carries two, so nothing is wrong today; a pack that grows one
# wants the bucket keyed by stat as well.
MULTIPLIERS = {
    "multiplicative-damage-percent-all-from-skills", "multiplicative-damage-percent-bonus-per-skill-tag",
    "multiplicative-damage-type-percent", "multiplicative-nonphysical-damage-percent",
    "multiplicative-vulnerable-health-damage", "multiplicative-damage-percent-bonus-vs-cc-all",
    "multiplicative-damage-percent-bonus-vs-elites", "multiplicative-damage-bonus-to-near",
    "multiplicative-damage-bonus-at-high-health", "multiplicative-damage-bonus-to-high-health",
    "multiplicative-damage-bonus-to-low-health", "multiplicative-damage-percent-bonus-per-shapeshift-form",
    "multiplicative-damage-percent-bonus-while-shapeshifted", "multiplicative-damage-percent-bonus-while-volatile",
    "multiplicative-warlock-demonform-damage", "multiplicative-power-damage-percent",
    "multiplicative-damage-percent-bonus-vs-cc-target", "multiplicative-crit-damage-percent",
    "multiplicative-damage-percent-all-from-skills-2",
}

# A line whose stat carries a `param` names WHICH element, skill or category
# it touches. These are read in code rather than from the table, because the
# param picks the canonical stat or the bucket.
PARAMETERISED = {
    "resistance", "resistance-all", "resistance-bonus-percent", "bucketed-multiplicative-damage-type", "damage-type-percent",
    "multiplicative-damage-type-percent", "damage-percent-bonus-per-skill-tag",
    "multiplicative-damage-percent-bonus-per-skill-tag", "skill-rank", "skill-rank-skill-tag",
}

# Which socket family a place on the body is. A gem writes one bonus per
# family — a ruby is fire damage in a weapon, Strength in armour and fire
# resistance in jewellery — and only the one matching where it actually sits
# is a fact about this character.
SOCKETS = {"helm": "armor", "chest": "armor", "gloves": "armor", "pants": "armor", "boots": "armor",
           "amulet": "jewelry", "ring": "jewelry",
           "main-hand": "weapon", "off-hand": "weapon", "two-handed": "weapon",
           "dual-wield": "weapon", "ranged": "weapon"}

# The five elements a hit can be, and the resistance that meets it.
ELEMENTS = {"fire": "fire", "cold": "cold", "lightning": "lightning", "poison": "poison",
            "shadow": "shadow", "physical": "physical"}

# A resistance line is a rating unless its unit says percent — see the ⚠ at
# the top. These are the keys that ambiguity lands on.
RATING_KEYS = {"resistance", "resistance-all"}

# pack key → (canonical stat, form). A tuple of stats means the line splits.
# The keys are the folded spelling, so one entry serves `Armor_Bonus`, the
# paragon board's `armor`, and anything else that folds to the same word.
TABLE: dict[str, tuple[object, str]] = {
    # what a character is. Diablo IV spends none of these by hand — they come
    # from gear and the paragon board — so every line is an addition.
    "strength": ("strength", "flat"), "dexterity": ("dexterity", "flat"),
    "intelligence": ("intelligence", "flat"), "willpower": ("willpower", "flat"),
    "plus-all-stats": (("strength", "dexterity", "intelligence", "willpower"), "flat"),
    "all-stats-percent": (("strength", "dexterity", "intelligence", "willpower"), "increased"),
    "strength-percent": ("strength", "increased"), "dexterity-percent": ("dexterity", "increased"),
    "intelligence-percent": ("intelligence", "increased"), "willpower-percent": ("willpower", "increased"),
    # what keeps it alive
    "flat-hitpoints-max": ("life", "flat"),
    "flat-hitpoints-max-bonus-unscaled-by-player-health": ("life", "flat"),
    "hitpoints-max-percent": ("life", "increased"),
    "armor": ("armour", "flat"), "armor-percent": ("armour", "increased"),
    "block-chance": ("block", "flat"),
    "dodge-chance": ("dodge-chance", "flat"), "dodge-chance-bonus-additive": ("dodge-chance", "flat"),
    "no-damage-taken-flat-hitpoints-regen-per-second": ("life-regeneration", "flat"),
    "no-damage-taken-flat-hitpoints-regen-per-second-unscaled-by-player-health": ("life-regeneration", "flat"),
    # ⚠ Diablo IV MULTIPLIES its damage reductions together — two 20% sources
    # leave 64% of the hit, not 60%. The row sums them, which is the upper
    # bound, so every such line is marked approximate and the breakdown shows
    # the parts a person can multiply for themselves.
    "damage-reduction": ("damage-reduction", "flat"),
    "pet-damage-reduction-percent": ("damage-reduction", "flat"),
    # resistances written as a percentage by name; the ambiguous ones are in
    # RATING_KEYS and settled in code.
    "resistance-all-bonus-percent": (RESISTANCES, "flat"),
    # what it does to things. Every bucket lands on the `damage` row unless
    # the line names an element, and each bucket is its own step.
    "damage-percent-all-from-skills": ("damage", "more"),
    "bucketed-multiplicative-damage": ("damage", "more"),
    "nonphysical-damage-percent": ("damage", "more"),
    "vulnerable-health-damage": ("damage", "more"),
    "bucketed-multiplicative-vulnerable-health-damage": ("damage", "more"),
    "damage-percent-bonus-vs-cc-all": ("damage", "more"),
    "damage-percent-bonus-vs-cc-target": ("damage", "more"),
    "damage-percent-bonus-vs-elites": ("damage", "more"),
    "dot-dps-bonus-percent": ("damage", "more"),
    "bucketed-multiplicative-dot-damage": ("damage", "more"),
    "damage-percent-bonus-against-dot-type": ("damage", "more"),
    "damage-bonus-to-near": ("damage", "more"), "damage-bonus-to-far": ("damage", "more"),
    "damage-percent-bonus-when-fortified": ("damage", "more"),
    "damage-bonus-at-high-health": ("damage", "more"),
    "damage-bonus-to-high-health": ("damage", "more"), "damage-bonus-to-low-health": ("damage", "more"),
    "damage-bonus-percent-to-weakened": ("damage", "more"),
    "damage-percent-bonus-when-weapon-swapping": ("damage", "more"),
    # ⚠ Fire-and-holy is one affix over two elements and the vocabulary has no
    # holy; it is counted against fire and marked approximate, because half of
    # what it grants has nowhere honest to go.
    "bucketed-multiplicative-damage-type-fireholy": ("damage-fire", "more"),
    # the two headline crit rows a person reads. A crit multiplier that the
    # game writes `[x]` is a damage bucket instead — see MULTIPLIERS.
    "crit-percent": ("critical-chance", "flat"),
    "crit-damage-percent": ("critical-damage", "flat"),
    "bucketed-multiplicative-crit-damage": ("critical-damage", "flat"),
    "global-deadlystrikechance": ("critical-chance", "flat"),
    "weapon-damage-min": ("damage-min", "flat"),
    # how fast
    "attack-speed-percent": ("speed-attack", "flat"),
    "movement-bonus-run-speed": ("speed-movement", "flat"),
    "power-cooldown-reduction-percent-all": ("cooldown-reduction", "flat"),
    "resource-cost-reduction-percent-all": ("resource-cost-reduction", "flat"),
    # the class's resource. Diablo IV names it per class — Fury, Mana, Spirit,
    # Essence — so it is its own row rather than the vocabulary's `mana`,
    # which would mislabel six classes of eight.
    "resource-max": ("resource", "flat"), "resource-all-primary-max": ("resource", "flat"),
    # ranks
    "skill-rank-all": ("skills-all", "flat"),
    # the rest
    "combat-effect-chance": ("lucky-hit", "flat"),
    "gold-find": ("gold-find", "flat"),
}

# Facts we hold and cannot put a number on. They are LISTED, never dropped.
#
# The long tail beyond this set — a class's own named mechanic, a seasonal
# socketable, an April Fools' joke affix — needs no entry: a key the table
# does not know is uncounted already, and keeps its own name in the panel.
# What is written out here is the DELIBERATE refusals, the lines that look
# mappable and are not.
UNCOUNTABLE = {
    # ⚠ The placeholder numbers an effect sentence is written around. A unique
    # says "deals {Affix_Value_1}% more damage for {Affix_Value_2} seconds";
    # the values are real and belong to the sentence, not to a stat.
    "affix-value-1", "affix-value-2", "affix-flat-value-1", "maxstacks",
    # ⚠ Cooldown reduction for ONE skill. Adding a Sorcerer's Teleport
    # reduction to her Ice Armor reduction produces a number that is true of
    # neither, so per-skill lines stay out and global ones count.
    "power-cooldown-reduction-percent", "skill-tag-cooldown-reduction-percent",
    "resource-cost-reduction-percent", "zero-resource-cost-per-skill-tag",
    # ⚠ Thorns, life on hit and life on kill are each written at two scales
    # under one name: a paragon node says 200 and an affix says 0.8, which is
    # a share of something the pack never names. Until the pack says which,
    # none of them can be added to the other.
    "thorns-flat", "thorns-flat-unscaled-by-player-health", "thorns-percent-bonus-while-fortified",
    "flat-hitpoints-on-hit", "flat-hitpoints-on-hit-unscaled-by-player-health",
    "flat-hitpoints-on-kill-unscaled-by-player-health",
    # ⚠ A weapon's own swing speed, not the character's attack speed stat: it
    # scales the weapon's damage-per-hit rather than joining the additive
    # attack-speed bracket, and mixing the two would overstate both.
    "weapon-speed", "weapon-speed-reduction",
    # grants a passive the plan has not chosen; the node's own stats are not
    # reachable from the line
    "item-granted-skill-tree-reward",
    # conditional and per-stack numbers: true only while something holds
    "overpower-damage-bonus-per-stack", "damage-bonus-percent-per-combo-point",
    "crit-percent-bonus-vs-cc-target", "crit-percent-bonus-to-low-health", "crit-percent-bonus-per-skill-tag",
    "crit-damage-percent-per-skill-tag", "attack-speed-percent-bonus-per-skill-tag",
    "attack-speed-percent-bonus-for-power", "damage-percent-bonus-while-affected-by-power",
    "pet-attack-speed-bonus-percent", "necroarmy-pet-type-attack-speed-bonus-pct",
    "necroarmy-all-pet-types-inherit-thorns-bonus-pct", "block-damage-percent",
    "damage-reduction-from-near", "global-damage-to-monster-family",
    "dot-dps-bonus-percent-per-damage-type", "combat-effect-chance-bonus-per-skill",
    "spiritborn-spirit", "paladin-aura-potency", "paladin-aura-potency-per-skill",
    "damage-percent-bonus-per-weapon-requirement", "damage-percent-bonus-per-shapeshift-form",
    "damage-percent-bonus-to-targets-affected-by-skill-tag", "damage-percent-bonus-while-volatile",
    "damage-increase-while-having-shield", "bonus-percent-per-power", "bonus-percent-per-power-2",
    "power-damage-percent", "chance-for-double-damage-per-power", "generic-chance-for-double-damage-per-skilltag",
    "generic-chance-for-hit-twice-per-skilltag", "damage-bonus-percent-on-dodge", "damage-bonus-on-elite-kill",
    "imbued-skill-damage-percent", "warlock-demonform-damage", "warlock-shadowform-damage",
    # recovery, resource flow and crowd control: real, and no canonical stat
    # names them yet
    "bonus-healing-received-percent", "blood-orb-pickup-healing-percent",
    "barrier-bonus-percent", "fortified-health-application", "cc-duration-reduction",
    "cc-duration-bonus-percent", "cc-duration-bonus-percent-per-type",
    "resource-gain-and-regen-bonus-percent-all-primary", "resource-gain-bonus-percent-all-primary",
    "resource-gain-bonus-percent-per-power", "resource-gain-bonus-percent-per-skill-tag",
    "resource-regen-per-second", "resource-on-kill", "global-resource-on-kill",
    "primary-resource-on-cast-per-skill-tag", "proc-resource-on-hit-percent-all-primary",
    "proc-resource-on-hit-flat-all-primary", "potion-max-doses",
    # things that happen rather than things that add up
    "on-hit-cc-proc-chance", "on-hit-vulnerable-proc-chance", "on-hit-vulnerable-proc-duration-seconds",
    "on-hit-weakened-proc-chance", "on-hit-weakened-proc-duration-seconds",
    "on-hit-execute-low-health-non-elite-chance", "proc-flat-element-damage-on-hit",
    "minions-fortify-on-attack-chance", "global-luckyhit-dot", "global-deadlystrikedamage",
    "evade-reduce-cooldown-on-attack", "evade-movement-speed", "evade-movement-speed-duration",
    "evade-max-charges", "evade-grants-attackspeed", "movement-bonus-on-elite-kill",
    "movement-bonus-on-elite-kill-duration", "mobility-grants-movementspeed",
    "power-duration-bonus-pct", "per-skill-tag-buff-duration-bonus-percent",
    "per-damage-type-buff-duration-bonus-percent", "custom-duration-bonus-per-skill-tag",
    "aoe-size-bonus-per-power", "percent-bonus-projectiles-per-power", "bonus-max-skill-charges-for-power",
    "trap-arm-time-reduction-seconds", "chill-progressive-bonus-slow-percent",
    # out of combat entirely
    "experience-bonus-percent", "experience-bonus-bucketed-and-penalized-at-max-level",
    "gold-pickup-radius", "set-item-discount", "shrine-elixir-duration-bonus",
    "unique-charm-count", "gem-attributes-multiplier", "hitpoints-cur-limit-mult",
}


def _key(raw: object) -> str:
    """
    The pack's two spellings of one stat, folded into one.

    ⚠ Only `-core` comes off the end. It is the paragon board's suffix on the
    four attribute names (`Strength_Core`) and marks nothing else. `-bonus`
    is NOT stripped here, because it is load-bearing in the middle of a name
    (`resistance-all-bonus-percent` is a percentage, `resistance-all-bonus` is
    a rating) — it is tried as a fallback in `_lookup`, where an explicit
    entry always wins and nothing can be merged by accident.
    """
    k = str(raw or "").strip().lower().replace("_", "-")
    return k[: -len("-core")] if k.endswith("-core") else k


def _lookup(key: str) -> str:
    """The key the tables know, or the key itself. A trailing `-bonus` is noise."""
    known = key in TABLE or key in UNCOUNTABLE or key in PARAMETERISED or key in MULTIPLIERS
    if not known and key.endswith("-bonus"):
        return key[: -len("-bonus")]
    return key


def _socket(place: str) -> str:
    """The socket family of a place on the body, or nothing if we cannot tell."""
    place = str(place or "").lower()
    for prefix, family in SOCKETS.items():
        if place == prefix or place.startswith(f"{prefix}-"):
            return family
    return ""


def _param(line: dict) -> str:
    """Which element, skill or category a line names, however the pack wrapped it."""
    p = line.get("param")
    if isinstance(p, dict):
        return str(p.get("id") or p.get("internal") or "")
    return str(p or "")


def _number(line: dict) -> tuple[float | None, str]:
    """The value to count, and how sure we are. A range counts at its best roll, and says so."""
    for field in ("value", "at_max_rank"):
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


def _percentage(stats: object, form: str) -> bool:
    """Whether the row this line lands on is read as a percentage."""
    if form in ("increased", "more"):
        return True
    first = stats[0] if isinstance(stats, tuple) else stats
    return canonical(str(first)).unit == "%"


def _scale(line: dict, stats: object, form: str) -> float:
    """
    What to multiply the pack's number by to reach the number a person reads.
    The four rules from the top of this file, in order.
    """
    if line.get("unit") == "percent":
        return 100.0                               # the pack's own word for "fraction"
    if line.get("display") is not None:
        return 1.0                                 # already written the way the game shows it
    if line.get("unit") is None and _percentage(stats, form):
        return 100.0                               # gem bonuses and set powers are fractions
    return 1.0


def base_for(plan: dict, data, pool) -> dict[str, float]:
    """
    What the character is before a single thing is chosen: the resistance
    caps, and a hundred percent of its own damage for every damage row the
    plan has lines for.

    ⚠ There is no base life and no starting attributes here because the pack
    has none. A Diablo IV class record carries its resource and its
    specialisations, not a life table — so the life row is what the plan
    grants and says so, rather than what the character has. The moment the
    pack grows `starting_life` and `per_level`, this is where it goes.

    The level is clamped to the cap the pack states (70 at 3.2.1), because a
    per-level line resolved against a level the game will not reach is a
    number about nobody.
    """
    base = dict(BASE)
    levels = data.get(GAME, "progression", "levels") or {}
    cap = levels.get("cap")
    if isinstance(cap, int) and cap > 0:
        pool.level = min(pool.level, cap)
    for sid in pool.stats():
        if sid in DAMAGE_ROWS:
            base[sid] = DAMAGE_BASE
    return base


# ⚠ Stats whose base this pack does not record. A Diablo IV character has
# life, and a great deal of it, before a single piece of gear — but no record
# in the pack says how much, and the census says so rather than inventing a
# table. The sum of the gear is therefore not "maximum life", and the row
# says as much instead of showing a confident number missing its largest
# term. Fill this in and delete the entry the day the pack carries the base.
INCOMPLETE_BASE = {
    "life": "the pack records no base life for a class, so this is what the plan grants and not a total",
}


def map_line(line: dict, source: dict) -> list[Contribution]:
    """One of a record's stat lines, as contributions."""
    raw = line.get("stat")
    key = _lookup(_key(raw))
    text = str(line.get("text") or line.get("display") or raw or "")[:160]
    # ⚠ Every line carries WHAT IT IS ABOUT. `+2 Ranks of Chain Lightning` and
    # `+2 Ranks of Fire Skills` are the same stat and the same number, and only
    # the param says which skill a plan may count them towards. Without it
    # every skill in a plan takes every rank bonus, which is the one mistake
    # the damage model exists to avoid.
    common = dict(source_kind=source.get("kind", ""), source_id=source.get("id", ""),
                  source_name=source.get("name", ""), text=text, place=source.get("place", ""),
                  param=_param(line))
    if not key:
        return []
    # ⚠ The collector turns an affix's best TIER into a line named after the
    # affix record itself, so that a pack whose affix states its own stat is
    # counted. Diablo IV's affixes carry their stats in a list instead, and
    # the top tier's numbers are already in it — so this echo is the same
    # fact twice, not a second one, and is passed over rather than counted or
    # listed.
    if key == _key(source.get("id")) and "unit" not in line and "display" not in line:
        return []
    # ⚠ A gem carries all three of its bonuses and says which socket each is
    # for. Only the one matching where the gem sits is a fact about this
    # character — the other two are facts about the gem. A place we cannot
    # read keeps every line, because losing a gem is worse than over-reading
    # one.
    socket = str(line.get("socket") or "")
    if socket and _socket(source.get("place", "")) not in ("", socket):
        return []

    value, sureness = _number(line)
    if key in UNCOUNTABLE:
        return [Contribution(stat=key, form="flat", value=float(value or 0.0), state=NOT_COUNTED, **common)]
    if key in PARAMETERISED or key in MULTIPLIERS:
        return _parameterised(key, line, value, sureness, source, common)
    if key not in TABLE:
        # a fact we hold and cannot compute with: its own row, its own name
        return [Contribution(stat=key, form="flat", value=float(value or 0.0), state=NOT_COUNTED, **common)]

    stats, form = TABLE[key]
    names = stats if isinstance(stats, tuple) else (stats,)
    if key in RATING_KEYS and line.get("unit") != "percent":
        # ⚠ A resistance rating, not a percentage — see the top of this file.
        return [Contribution(stat=n, form="flat", value=0.0, state=NOT_COUNTED, **common) for n in names]
    if value is None:
        # ⚠ We know which stat this is; we just have no number for it — a
        # glyph's legendary bonus names its stat and keeps the number in a
        # scaling table. It goes in THAT stat's row as an uncounted line, so
        # a person reading their damage sees the piece that could not be
        # counted towards it, rather than a phantom row beside the real one.
        return [Contribution(stat=n, form="flat", value=0.0, state=NOT_COUNTED, **common) for n in names]

    value *= _scale(line, stats, form)
    if key == "damage-reduction" or key == "pet-damage-reduction-percent":
        sureness = APPROXIMATE if sureness == COUNTED else sureness
    if key == "bucketed-multiplicative-damage-type-fireholy":
        sureness = APPROXIMATE if sureness == COUNTED else sureness
    bucket = BUCKETS.get(key, "")
    return [Contribution(stat=n, form=form, value=value, state=sureness, bucket=bucket, **common) for n in names]


def _parameterised(key: str, line: dict, value: float | None, sureness: str,
                   source: dict, common: dict) -> list[Contribution]:
    """
    A line whose `param` says which element, skill or category it touches.
    The param picks the stat (a resistance, an element's damage) or the
    bucket (one category of skills), so it cannot come from a flat table.
    """
    param = _param(line)
    element = ELEMENTS.get(param.lower(), "")

    if key in ("resistance", "resistance-all", "resistance-bonus-percent"):
        # ⚠ Physical is a resistance of its own in this game, not "all of
        # them". Letting it fall through to the unnamed case spread one line
        # across five rows and told a person they had resistances they do not.
        name = f"resistance-{element}" if element else "resistance-all"
        if name == "resistance-all":
            names = RESISTANCES               # an unnamed element is every element
        else:
            names = (name,)
        if key in RATING_KEYS and line.get("unit") != "percent":
            return [Contribution(stat=n, form="flat", value=0.0, state=NOT_COUNTED, **common) for n in names]
        if value is None:
            return [Contribution(stat=n, form="flat", value=0.0, state=NOT_COUNTED, **common) for n in names]
        value *= _scale(line, names, "flat")
        return [Contribution(stat=n, form="flat", value=value, state=sureness, **common) for n in names]

    if key in ("skill-rank", "skill-rank-skill-tag"):
        # a rank in one skill, or in a whole category of them
        name = "skills-single" if key == "skill-rank" else "skills-tab"
        if value is None:
            return [Contribution(stat=name, form="flat", value=0.0, state=NOT_COUNTED, **common)]
        return [Contribution(stat=name, form="flat", value=value * _scale(line, name, "flat"),
                             state=sureness, **common)]

    # everything else here is damage: the param picks the row or the bucket.
    if key in MULTIPLIERS:
        # ⚠ a `[x]` multiplier stands alone, so its bucket is the thing it
        # came from and it multiplies against every other bucket
        stat_id, bucket = "damage", f"× {source.get('name') or source.get('id') or 'a thing'}"
        if "type" in key and element and element != "physical":
            stat_id = f"damage-{element}"
    elif key in ("bucketed-multiplicative-damage-type", "damage-type-percent"):
        stat_id = f"damage-{element}" if element else "damage"
        bucket = "type"
    else:                                          # damage with one category of skills
        stat_id, bucket = "damage", f"skill:{param.lower().replace('_', '-')}" if param else "skill"

    if value is None:
        return [Contribution(stat=stat_id, form="more", value=0.0, state=NOT_COUNTED, bucket=bucket, **common)]
    return [Contribution(stat=stat_id, form="more", value=value * _scale(line, stat_id, "more"),
                         state=sureness, bucket=bucket, **common)]


# ── what a skill hits for ────────────────────────────────────────────────────
#
# ⚠ WHAT THE PACK ACTUALLY CARRIES, measured before this was written. A skill's
# `ranks_or_levels` is one row per rank 1–15 and the row's `values` hold
# `damage_pct` — a single number, never a pair, and that number is A PERCENTAGE
# OF WEAPON DAMAGE for the skill's FIRST PAYLOAD. 164 of the pack's 194 actives
# and ultimates carry one. The other 30 either deal no damage at all (Ice
# Armor, the Paladin auras, the shouts) or have a formula the extraction could
# not evaluate because it reads runtime state, and both say so below rather
# than guess.
#
# ⚠ AND THE PACK CARRIES NO WEAPON DAMAGE. A base record holds the type's
# attacks per second and its speed implicit and nothing else, because Diablo
# IV's weapon damage is an item-power formula rather than a number per type.
# So what this model reaches is the skill's percentage — scaled to the rank the
# plan reaches and multiplied by the bonuses that are about this skill — and
# NOT a damage figure. Every hit is approximate and says which half is missing.
# `weapon_damage` below is the one place to change the day a pack carries it.

# The tags that say what a hit lands as. No skill in the 3.2.1 pack carries two
# of them, so the first found is the skill's element.
#
# ⚠ `holy` is here and is deliberately NOT in ELEMENTS: the vocabulary has no
# holy row, so a Paladin's hit names its element truthfully while reading the
# plain `damage` row — which is where the pack files holy multipliers anyway.
ELEMENT_TAGS = ("fire", "cold", "lightning", "poison", "shadow", "holy", "physical")

# The per-rank value a skill's damage is written under.
DAMAGE_KEY = "damage_pct"

# Where a weapon sits. An off-hand is a focus, a totem or a shield and swings
# at nothing, so it is not one of these.
WEAPON_HANDS = ("main-hand", "two-handed", "dual-wield", "ranged")

# What a base's damage would be called, in each of the spellings a pack might
# reasonably use. None of them is in the 3.2.1 pack; see `weapon_damage`.
WEAPON_DAMAGE_KEYS = (("damage_min", "damage_max"), ("min_damage", "max_damage"),
                      ("weapon_damage_min", "weapon_damage_max"))


def _tag(param: str) -> str:
    """
    One skill category, however the pack spelled it.

    ⚠ The same category reaches us under two names. An affix writes
    `{"kind": "skill-tag", "id": "trap"}`; a paragon node writes the engine's
    own `"Skill_Trap"`. Folding the case, the underscores and a leading
    `skill-` makes them one word — and without that a plan's traps affix and
    its traps node would read as two unrelated categories.
    """
    t = str(param or "").strip().lower().replace("_", "-")
    return t[len("skill-"):] if t.startswith("skill-") else t


def tags_of(skill: dict) -> set[str]:
    """
    Every category a skill belongs to: its own tags, and the tree cluster it
    sits in. The cluster is already among the tags in this pack; it is taken
    from `group` as well so a pack that stops writing it loses nothing.

    ⚠ `core` and `primary-core` are TWO CATEGORIES and neither is short for the
    other. `core` is the tree cluster — 43 skills. `primary-core` is the game's
    own flag for what counts as a Core skill to an affix, and the pack writes
    the affix to match: "+x% Ranks of Primary Core Skills". Ball Lightning
    carries `mastery` and `primary-core` both — it sits in the Mastery cluster
    and the game treats it as a Core skill — so folding one name into the other
    would be wrong in both directions. They are matched exactly.
    """
    out = {_tag(t) for t in (skill.get("tags") or []) if t}
    out.add(_tag(str(skill.get("group") or "").replace(" ", "-")))
    return {t for t in out if t}


def element_of(skill: dict) -> str:
    """What this skill's damage lands as, from its own tags."""
    tags = tags_of(skill)
    return next((e for e in ELEMENT_TAGS if e in tags), "")


def planned_ranks(plan: dict, skill_id: str) -> int:
    """
    The ranks a person put into a skill with their own hand.

    ⚠ A skill in the plan always has at least one. Diablo IV spends a point the
    moment a skill is taken, and the plan's own field starts at one — so a pick
    that names no number is one rank, not none. A skill that is not in the plan
    is nought, which is how the caller tells the two apart.
    """
    for p in ((plan.get("sections") or {}).get("skills") or {}).get("picks") or []:
        if isinstance(p, dict) and p.get("id") == skill_id:
            try:
                return max(1, int(p.get("ranks") or 1))
            except (TypeError, ValueError):
                return 1
    return 0


def effective_rank(skill: dict, ranks: int, pool) -> tuple[int, list[Contribution], int]:
    """
    The rank a skill actually reaches: the ranks a person spent, plus every
    bonus that is ABOUT this skill — all skills, one of the categories it is
    in, or this skill by name. A bonus meant for another skill or another
    category is not taken, which is the whole reason a contribution carries
    what it is about.

    ⚠ Capped at the skill's own `max_rank`. Diablo IV stops a skill at fifteen
    however much a plan piles on and the pack says so twice — on the skill and
    in `progression.max_rank_per_active_skill`. Reading a rank table past its
    last row would invent damage the game does not give. The third value is the
    rank the plan asked for where the cap bit, and nought where it did not.
    """
    tags = tags_of(skill)
    rank, lines = float(max(0, int(ranks))), []

    def take(c: Contribution) -> None:
        if pool.holds(c):
            lines.append(c)

    for c in pool.lines("skills-all"):
        take(c)
    for c in pool.lines("skills-tab"):
        if _tag(c.param) in tags:
            take(c)
    for c in pool.lines("skills-single"):
        if c.param and c.param == skill.get("id"):
            take(c)
    rank += sum(c.value for c in lines)

    cap = int(skill.get("max_rank") or 0)
    if cap > 0 and rank > cap:
        return cap, lines, int(rank)
    return int(rank), lines, 0


def banded(table: list[dict], key: str) -> list[dict]:
    """
    A Diablo IV rank table in the shape the shared reader wants.

    ⚠ Diablo II writes a rank's damage as a low and a high; Diablo IV writes
    ONE number, because what varies behind it is the weapon and not the skill.
    `between` reads pairs, so the one number is handed to it as both ends. It
    is not a range and must never be drawn as one.
    """
    rows = []
    for r in table or []:
        v = (r.get("values") or {}).get(key)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            rows.append({"rank": r.get("rank"), "values": {key: [float(v), float(v)]}})
    return rows


def bucket_name(bucket: str) -> str:
    """
    One multiplier group's name, with a category's two spellings folded into
    one — see `_tag`.

    ⚠ This is load-bearing arithmetic and not tidiness. Buckets ADD inside
    themselves and MULTIPLY against each other, so a plan whose amulet says
    `skill:lightning` and whose paragon node says `skill:skill-lightning` would
    otherwise have its one category counted as two and multiplied together. The
    mapper still writes both spellings, because a bucket's name is also what
    the panel labels the step with and the pack's own word is the honest label
    there; here, where the two are added up, they have to be one.
    """
    return f"skill:{_tag(bucket[len('skill:'):])}" if bucket.startswith("skill:") else bucket


def bucket_applies(bucket: str, tags: set[str]) -> bool:
    """
    Whether one of Diablo IV's multiplier groups belongs in this skill's
    tooltip number.

    Three do. `all` is every skill's damage. `type` has already been narrowed
    by the row it was read from, so reaching it here means it names this
    skill's element or no element at all. `skill:<tag>` counts only where the
    skill is in that category.

    ⚠ Everything else is left out, and for two different reasons. The buckets
    named after the enemy or a passing state — vulnerable, elites, fortified,
    close — are what the tooltip is the damage BEFORE; counting them would give
    a number nobody can check against their own screen. And a standalone `[x]`
    multiplier is filed under the item it came from rather than the thing it
    waits on, so this cannot tell an unconditional one from a conditional one
    and will not guess. Both kinds are named in the hit's `why`, and the
    panel's own damage row still multiplies every one of them.
    """
    if bucket in ("all", "type"):
        return True
    if bucket.startswith("skill:"):
        return _tag(bucket[len("skill:"):]) in tags
    return False


def planned_weapon(plan: dict, data) -> tuple[dict, str]:
    """The base in the plan's weapon hand, and the place it sits in."""
    gear = (plan.get("sections") or {}).get("gear") or {}
    if not isinstance(gear, dict):
        return {}, ""
    for place, choice in gear.items():
        p = str(place or "").lower()
        if not isinstance(choice, dict) or not any(p == h or p.startswith(f"{h}-") for h in WEAPON_HANDS):
            continue
        rec = data.get(GAME, "base", str(choice.get("base") or "")) or {}
        if rec:
            return rec, str(place)
    return {}, ""


def weapon_damage(plan: dict, data) -> tuple[tuple[float, float] | None, str]:
    """
    What the weapon in the plan's hand hits for — and today, nothing.

    ⚠ THE PACK CARRIES NO WEAPON DAMAGE, and the census says so outright rather
    than make one up: a base holds `attacks_per_second_base` and a speed
    implicit, because Diablo IV's damage is an item-power formula and not a
    number per type. So every skill that scales off the weapon — which is every
    skill with a `damage_pct` — comes out as a percentage and is approximate.
    This is the one place to change the day a pack carries the number.
    """
    rec, place = planned_weapon(plan, data)
    stats = rec.get("stats") or {}
    name = str(rec.get("name") or place or "")
    for lo_key, hi_key in WEAPON_DAMAGE_KEYS:
        lo, hi = stats.get(lo_key), stats.get(hi_key)
        if isinstance(lo, (int, float)) and isinstance(hi, (int, float)) and not isinstance(lo, bool):
            return (float(lo), float(hi)), name
    return None, name


def damage_for(plan: dict, data, pool, pick: dict) -> Hit | None:
    """
    One skill's damage, aimed at the number the game's own tooltip shows: what
    the skill does before anything about the thing it hits.

    The working is the rank the plan reaches, the percentage the pack records
    at that rank, and then the multiplier buckets that are about THIS skill —
    every skill's damage, this skill's element, a category this skill is in.
    Nothing about the enemy, nothing that waits on a state, no simulation.
    """
    skill = data.get(GAME, "skill", str(pick.get("id") or ""))
    if not skill:
        return None
    element = element_of(skill)
    tags = tags_of(skill)
    ranks = planned_ranks(plan, skill["id"]) or max(1, int(pick.get("ranks") or 1))
    rank, rank_lines, asked = effective_rank(skill, ranks, pool)
    hit = Hit(skill_id=skill["id"], skill_name=skill.get("name") or skill["id"], element=element, rank=rank)

    if not (skill.get("ranks_or_levels") or []):
        hit.state = NOT_COUNTED
        hit.why = ("the pack records no per-rank table for this skill — its damage is a formula about "
                   "things the data does not carry, such as attack speed or what is equipped")
        return hit
    table = banded(skill.get("ranks_or_levels") or [], DAMAGE_KEY)
    if not table:
        hit.state = NOT_COUNTED
        hit.why = "the pack's rank table for this skill records no damage — it may not deal any"
        return hit

    band, sureness = between(table, rank, DAMAGE_KEY)
    percent = band[1]
    hit.steps.append(Step("base", f"rank {rank} of {skill.get('max_rank') or rank}", rank, percent, rank_lines))

    # the multipliers, one step per bucket: inside a bucket they add, between
    # buckets they multiply — Diablo IV's whole damage model
    applied: dict[str, list[Contribution]] = {}
    left_out: list[Contribution] = []
    for row in ["damage"] + ([f"damage-{element}"] if element else []):
        for c in pool.lines(row):
            if c.form != "more" or c.state == NOT_COUNTED or not pool.holds(c):
                continue
            if bucket_applies(c.bucket, tags):
                applied.setdefault(bucket_name(c.bucket), []).append(c)
            else:
                left_out.append(c)
    running = percent
    for bucket, group in applied.items():
        amount = sum(c.value for c in group)
        running *= 1 + amount / 100.0
        hit.steps.append(Step("more", bucket, amount, running, group))

    why: list[str] = []
    weapon, weapon_name = weapon_damage(plan, data)
    if weapon is None:
        hit.low = hit.high = running
        why.append("the pack records no weapon damage, so this is the skill's percentage of a weapon "
                   "and not a damage number")
        states = [APPROXIMATE]
    else:
        hit.low, hit.high = running / 100.0 * weapon[0], running / 100.0 * weapon[1]
        hit.steps.append(Step("more", f"{weapon_name}'s damage", weapon[1], hit.high))
        states = [COUNTED]

    if sureness != COUNTED:
        why.append("the rank falls between the rows the pack records, so the damage is read across them")
    if asked:
        why.append(f"the plan reaches rank {asked} and the pack caps this skill at {rank}, "
                   f"so the ranks past the cap are not counted")
    # ⚠ Three different reasons a multiplier is not in the number, and the
    # panel says which. A person who cannot see WHY a bonus they bought is
    # missing will assume the whole number is wrong.
    buckets = sorted({c.bucket for c in left_out})
    standalone = [b for b in buckets if b.startswith("× ")]
    categories = [b for b in buckets if b.startswith("skill:")]
    unnamed = [b for b in buckets if b == "skill"]
    situational = [b for b in buckets if b not in standalone + categories + unnamed]
    if situational:
        why.append("left out, being about the thing hit or a state that must hold: " + ", ".join(situational))
    if categories:
        why.append("left out, naming a category this skill is not in: "
                   + ", ".join(b[len("skill:"):] for b in categories))
    if unnamed:
        why.append("a damage bonus to one category of skills is left out, because the pack did not "
                   "record which category")
    if standalone:
        why.append(f"{len(standalone)} standalone [x] multipliers are left out — each is filed under the "
                   "thing it came from, which does not say what it waits on")

    hit.why = "; ".join(why)
    hit.state = worst(states + [sureness] + [c.state for c in rank_lines] +
                      [c.state for g in applied.values() for c in g])
    return hit
