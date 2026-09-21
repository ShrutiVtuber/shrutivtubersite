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

from ..model import APPROXIMATE, COUNTED, NOT_COUNTED, Contribution
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
BASE = {f"{r}-max": 70.0 for r in RESISTANCES}

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
    common = dict(source_kind=source.get("kind", ""), source_id=source.get("id", ""),
                  source_name=source.get("name", ""), text=text, place=source.get("place", ""))
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
        name = f"resistance-{element}" if element and element != "physical" else "resistance-all"
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
