# SPDX-License-Identifier: AGPL-3.0-only
"""
Path of Exile 2 — its own words, matched into the vocabulary.

This game has no stat keys. Every line is a SENTENCE the game wrote, with
its numbers left as holes: `+{value} to maximum Life`, `#% increased Evasion
Rating`, `Adds (76-98) to (126-193) Fire Damage`. The pack holds about three
thousand distinct ones, so a lookup table is the wrong shape and this is a
pattern matcher instead.

Two steps. `normalise` lowercases a sentence, collapses every number and
every hole to one `#`, and drops the punctuation that carries no meaning —
`+`, `-` and `%` stay, because they are the difference between a flat
addition and a percentage. Then the normalised sentence is matched against
PATTERNS, an ORDERED list, each entry naming a canonical stat and a form.

⚠ The order is the design. Every pattern is anchored at both ends, and the
specific one comes first: `+# to level of all skills` is listed above
`+# to level of all <group> skills`, and `armour and evasion` above `armour`.
A sentence with a condition on it — `while stationary`, `if you have been hit
recently`, `against rare enemies` — matches nothing here on purpose: the
increase is not always on, so it is kept and left out of the arithmetic.

The algebra the game states is `(base + added) × (1 + Σ increased) × each
more`, which is the pool's arithmetic exactly, so an increase is passed as
the percentage the sentence says and nothing is pre-divided. `increased` and
`reduced` are both the increased form and `reduced` is negative; `more` and
`less` are both the more form and `less` is negative — the matched word
decides, which is why one pattern serves both.

⚠ Nothing is dropped. A sentence no pattern claims becomes a NOT-COUNTED
contribution that still carries its own text, filed against the stat it
talks about — `#% increased Armour while stationary` sits in the armour row
as a line that could not be counted, so a person reading their armour sees
the piece that is missing from it rather than nothing at all.

⚠ Three things are held back even when the wording matched, because they
are facts about something other than this character: a unique's old roll,
which the pack tags with the patch it was last seen in; one version of an
item that has several, when the plan has not said which; and an increase
that belongs to the ITEM — `350% increased Physical Damage` multiplies the
sword it is on and nothing else, and in the character's bracket it would
state a number nobody has.
"""
from __future__ import annotations

import re

from ..model import APPROXIMATE, COUNTED, NOT_COUNTED, Contribution

GAME = "path-of-exile-2"

# What a character has before a single point is spent. The caps are the
# game's own 75%; the campaign's resistance penalty is NOT here, because the
# pack does not record it and a penalty we guessed would be worse than none.
BASE = {"resistance-fire-max": 75.0, "resistance-cold-max": 75.0,
        "resistance-lightning-max": 75.0, "resistance-chaos-max": 75.0}

LEVEL_CAP = 100                        # the pack's own cap, read from `progression/levels` when present

# ⚠ Stats whose base this pack does not hold. However well their lines are
# counted the total is missing its largest term, so the row says so rather
# than showing a confident number. A class record here is starting
# attributes and nothing else; an item's own armour is recorded on the base
# as a number rather than as a stat line, so it never reaches the pool.
INCOMPLETE_BASE = {
    "life": "the pack records no starting life for a class, so this is what the plan grants and not a total",
    "mana": "the pack records no starting mana for a class, so this is what the plan grants and not a total",
    "spirit": "the pack records no starting spirit, so this is what the plan grants and not a total",
    "armour": "an item's own armour is on its base record rather than in its lines, so only what is added is here",
    "evasion": "an item's own evasion is on its base record rather than in its lines, so only what is added is here",
    "energy-shield": "an item's own energy shield is on its base record rather than in its lines, "
                     "so only what is added is here",
}


# ── one sentence, one shape ──────────────────────────────────────────────────

_BRACE = re.compile(r"\{[^}]*\}")                                   # {value}, {value2}, {variant:3}
_PAREN = re.compile(r"\(\s*[-+]?[0-9][0-9.,]*\s*(?:[-–]\s*[-+]?[0-9][0-9.,]*\s*)?\)")   # (30-40)
_NUM = re.compile(r"[0-9][0-9.,]*")
_SPAN = re.compile(r"#\s*[-–]\s*#")                                 # a range the steps above left behind
_DROP = re.compile(r"[^a-z0-9#+%\- ]+")                             # keep + - % : they are meaning, not punctuation
_SPACE = re.compile(r"\s+")


def normalise(sentence: str) -> str:
    """A line as a shape: lowercase, every number a `#`, the signs kept."""
    s = str(sentence or "").lower()
    s = _BRACE.sub("#", s)
    s = _PAREN.sub("#", s)
    s = _NUM.sub("#", s)
    s = _SPAN.sub("#", s)
    s = _DROP.sub(" ", s)
    s = re.sub(r"\s*\+\s*", " +", s)
    return _SPACE.sub(" ", s).strip()


# ── the ordered list ─────────────────────────────────────────────────────────

_N = r"[+-]?#"                                      # a placeholder that may carry a sign
_D = r"(?P<dir>increased|reduced|more|less)"        # the word that decides form and sign

PATTERNS: list[tuple[re.Pattern, object, str]] = []


def _p(pattern: str, stat: object, form: str) -> None:
    """
    One entry: the shape, the canonical stat, the form.

    A TUPLE of stats splits the line — `+12% to all Elemental Resistances`
    is three contributions. A stat written with a `{group}` in it takes that
    group from the match, which is how one entry serves a whole family:
    `#% increased Freeze Buildup` and `#% increased Pin Buildup` are the
    same sentence with a different word in it, and each keeps its own row.
    """
    PATTERNS.append((re.compile("^" + pattern.replace("{n}", _N).replace("{d}", _D) + "$"), stat, form))


_ELEMENTS = (("fire", "resistance-fire"), ("cold", "resistance-cold"), ("lightning", "resistance-lightning"))
_ATTRS = ("strength", "dexterity", "intelligence")

# ── attributes ───────────────────────────────────────────────────────────────
# The pairs and `all` come before the singles, or `+# to strength and
# dexterity` would be read as strength alone.
_p(r"{n} to all attributes", _ATTRS, "flat")
_p(r"{n} to strength and dexterity", ("strength", "dexterity"), "flat")
_p(r"{n} to strength and intelligence", ("strength", "intelligence"), "flat")
_p(r"{n} to dexterity and intelligence", ("dexterity", "intelligence"), "flat")
for _a in _ATTRS:
    _p(rf"{{n}} to {_a}", _a, "flat")
    _p(rf"#% {{d}} {_a}", _a, "increased")
_p(r"#% {d} attributes", _ATTRS, "increased")

# ── the pools a character lives on ───────────────────────────────────────────
_p(r"{n} to maximum life", "life", "flat")
_p(r"#% {d} maximum life", "life", "increased")
_p(r"{n} to maximum mana", "mana", "flat")
_p(r"#% {d} maximum mana", "mana", "increased")
_p(r"{n} to spirit", "spirit", "flat")
_p(r"#% {d} spirit", "spirit", "increased")
_p(r"{n} to maximum energy shield", "energy-shield", "flat")
_p(r"#% {d} maximum energy shield", "energy-shield", "increased")
_p(r"#% {d} energy shield", "energy-shield", "increased")
_p(r"#% {d} life regeneration rate", "life-regeneration", "increased")
_p(r"# life regeneration per second", "life-regeneration", "flat")
_p(r"#% {d} mana regeneration rate", "mana-regeneration", "increased")
_p(r"#% {d} energy shield recharge rate", "energy-shield-recharge", "increased")
_p(r"#% faster start of energy shield recharge", "energy-shield-recharge-delay", "increased")

# ── what stops a hit ─────────────────────────────────────────────────────────
# The combined defences first: each is several contributions, and `armour`
# alone would otherwise swallow `armour and evasion`.
_p(r"#% {d} (?:global )?armour evasion and energy shield", ("armour", "evasion", "energy-shield"), "increased")
_p(r"#% {d} (?:global )?armour and evasion(?: rating)?", ("armour", "evasion"), "increased")
_p(r"#% {d} (?:global )?armour and energy shield", ("armour", "energy-shield"), "increased")
_p(r"#% {d} (?:global )?evasion(?: rating)? and energy shield", ("evasion", "energy-shield"), "increased")
_p(r"{n} to armour", "armour", "flat")
_p(r"#% {d} (?:global )?armour", "armour", "increased")
_p(r"{n} to evasion rating", "evasion", "flat")
_p(r"#% {d} (?:global )?evasion(?: rating)?", "evasion", "increased")
_p(r"{n}% to (?:maximum )?block chance", "block", "flat")
_p(r"#% {d} block chance", "block", "increased")
_p(r"{n} to stun threshold", "stun-threshold", "flat")
_p(r"#% {d} stun threshold", "stun-threshold", "increased")
_p(r"#% additional physical damage reduction", "damage-reduction", "flat")
_p(r"#% {d} amount of life leeched", "life-leech", "increased")
_p(r"#% {d} amount of mana leeched", "mana-leech", "increased")

# ── resistances ──────────────────────────────────────────────────────────────
# The maximums come first: `maximum fire resistance` contains `fire
# resistance`, and read the other way round every cap would raise the
# resistance itself.
_p(r"{n}% to all maximum (?:elemental )?resistances",
   ("resistance-fire-max", "resistance-cold-max", "resistance-lightning-max"), "flat")
_p(r"{n}% to all elemental resistances", ("resistance-fire", "resistance-cold", "resistance-lightning"), "flat")
_p(r"{n}% to all resistances",
   ("resistance-fire", "resistance-cold", "resistance-lightning", "resistance-chaos"), "flat")
for _e, _r in _ELEMENTS:
    _p(rf"{{n}}% to maximum {_e} resistance", f"{_r}-max", "flat")
_p(r"{n}% to maximum chaos resistance", "resistance-chaos-max", "flat")
_p(r"{n}% to fire and cold resistances", ("resistance-fire", "resistance-cold"), "flat")
_p(r"{n}% to fire and lightning resistances", ("resistance-fire", "resistance-lightning"), "flat")
_p(r"{n}% to cold and lightning resistances", ("resistance-cold", "resistance-lightning"), "flat")
_p(r"{n}% to fire and chaos resistances", ("resistance-fire", "resistance-chaos"), "flat")
_p(r"{n}% to cold and chaos resistances", ("resistance-cold", "resistance-chaos"), "flat")
_p(r"{n}% to lightning and chaos resistances", ("resistance-lightning", "resistance-chaos"), "flat")
for _e, _r in _ELEMENTS:
    _p(rf"{{n}}% to {_e} resistance", _r, "flat")
_p(r"{n}% to chaos resistance", "resistance-chaos", "flat")

# ── what a character does ────────────────────────────────────────────────────
# `elemental` is three lines in one. The scoped brackets — spell, attack,
# minion — are their own stats because the game never adds them together.
_p(r"#% {d} elemental damage", ("damage-fire", "damage-cold", "damage-lightning"), "increased")
_p(r"#% {d} fire damage", "damage-fire", "increased")
_p(r"#% {d} cold damage", "damage-cold", "increased")
_p(r"#% {d} lightning damage", "damage-lightning", "increased")
_p(r"#% {d} (?:global )?physical damage", "damage-physical", "increased")
_p(r"#% {d} chaos damage", "damage-chaos", "increased")
_p(r"#% {d} spell damage", "damage-spell", "increased")
_p(r"#% {d} attack damage", "damage-attack", "increased")
_p(r"#% {d} damage", "damage", "increased")
# `Adds A to B` is a span, not a roll: the two ends are averaged and the line
# is marked approximate, because the pool carries one number per stat.
_p(r"adds # to # physical damage(?: to (?:attacks|spells))?", "damage-physical", "flat")
_p(r"adds # to # fire damage(?: to (?:attacks|spells))?", "damage-fire", "flat")
_p(r"adds # to # cold damage(?: to (?:attacks|spells))?", "damage-cold", "flat")
_p(r"adds # to # lightning damage(?: to (?:attacks|spells))?", "damage-lightning", "flat")
_p(r"adds # to # chaos damage(?: to (?:attacks|spells))?", "damage-chaos", "flat")
_p(r"damage penetrates #% fire resistance", "penetration-fire", "flat")
_p(r"damage penetrates #% cold resistance", "penetration-cold", "flat")
_p(r"damage penetrates #% lightning resistance", "penetration-lightning", "flat")
_p(r"damage penetrates #%(?: of enemy)? elemental resistances",
   ("penetration-fire", "penetration-cold", "penetration-lightning"), "flat")
_p(r"{n} to accuracy rating", "attack-rating", "flat")
_p(r"#% {d} accuracy rating", "attack-rating", "increased")
_p(r"{n}% to critical hit chance", "critical-chance", "flat")
_p(r"#% {d} critical hit chance", "critical-chance", "increased")
_p(r"{n}% to critical damage bonus", "critical-damage", "flat")
_p(r"#% {d} critical damage bonus", "critical-damage", "increased")

# ── minions, which are a build of their own ──────────────────────────────────
_p(r"minions deal #% {d} damage", "damage-minion", "increased")
_p(r"minions have #% {d} maximum life", "life-minion", "increased")

# ── how fast ─────────────────────────────────────────────────────────────────
_p(r"#% {d} attack speed", "speed-attack", "increased")
_p(r"#% {d} cast speed", "speed-cast", "increased")
_p(r"#% {d} attack and cast speed", ("speed-attack", "speed-cast"), "increased")
_p(r"#% {d} movement speed", "speed-movement", "increased")
_p(r"#% {d} skill speed", "speed-skill", "increased")
_p(r"#% {d} cooldown recovery rate", "cooldown-reduction", "increased")
_p(r"#% {d} mana cost efficiency", "resource-cost-reduction", "increased")
_p(r"#% {d} mana cost of skills", "resource-cost-reduction", "increased")

# ── ranks ────────────────────────────────────────────────────────────────────
# `all skills` before `all <group> skills`, or every group would read as all.
_p(r"{n} to level of all skills", "skills-all", "flat")
_p(r"{n} to level of all [a-z ]+ skills?(?: gems)?", "skills-tab", "flat")
_p(r"{n} to level of [a-z ]+ skills", "skills-single", "flat")

# ── the rest ─────────────────────────────────────────────────────────────────
_p(r"#% {d} rarity of items found", "magic-find", "increased")
_p(r"#% {d} quantity of gold dropped by slain enemies", "gold-find", "increased")
_p(r"#% {d} light radius", "light-radius", "increased")
_p(r"has # sockets?", "sockets", "flat")

# ── the numbers this game has that the other two do not ──────────────────────
# These stay OUT of the shared vocabulary: no other pack says them, and a
# vocabulary that grew a bulge for one game would stop being shared. They
# are carried under their own ids, which is why the ids are written noun
# first — `projectile-damage`, not `damage-projectile` — so the name a
# person reads under `other` is the name the game uses.
_p(r"#% {d} area of effect", "area-of-effect", "increased")
_p(r"#% {d} area of effect for attacks", "attack-area-of-effect", "increased")
_p(r"#% {d} presence area of effect", "presence-area-of-effect", "increased")
_p(r"#% {d} attack area damage", "attack-area-damage", "increased")
_p(r"#% {d} spell area damage", "spell-area-damage", "increased")
_p(r"#% {d} area damage", "area-damage", "increased")
_p(r"#% {d} projectile damage", "projectile-damage", "increased")
_p(r"#% {d} projectile speed", "projectile-speed", "increased")
_p(r"#% {d} melee damage", "melee-damage", "increased")
_p(r"#% {d} thorns damage", "thorns-damage", "increased")
_p(r"#% {d} (?P<a>grenade|trap|hazard|totem|ballista|parry) damage", "{a}-damage", "increased")
_p(r"#% {d} elemental damage with attacks", "attack-elemental-damage", "increased")
_p(r"#% {d} damage with (?P<a>bows|crossbows|swords|axes|maces|flails|spears|daggers|claws|quarterstaves"
   r"|wands|sceptres|one handed weapons|two handed weapons|melee weapons)", "damage-with-{a}", "increased")
_p(r"#% {d} critical hit chance for spells", "spell-critical-chance", "increased")
_p(r"#% {d} critical hit chance for attacks", "attack-critical-chance", "increased")
_p(r"#% {d} critical spell damage bonus", "spell-critical-damage", "increased")
_p(r"#% {d} critical damage bonus for attack damage", "attack-critical-damage", "increased")
_p(r"#% {d} curse magnitudes?", "curse-magnitude", "increased")
_p(r"#% {d} magnitude of (?P<a>shock|chill|poison|bleeding|ignite|ailments) you inflict", "{a}-magnitude", "increased")
_p(r"#% {d} (?P<a>flammability|ignite|exposure|blind|parried debuff) (?:magnitude|effect)", "{a}-magnitude", "increased")
_p(r"#% {d} (?P<a>[a-z]+) buildup", "{a}-buildup", "increased")
_p(r"{n} to ailment threshold", "ailment-threshold", "flat")
_p(r"#% {d} (?P<a>elemental ailment|ailment|freeze|culling strike) threshold", "{a}-threshold", "increased")
_p(r"#% {d} (?P<a>poison|bleeding|ignite|shock|chill|freeze|pin|curse|minion|charm|flask effect"
   r"|skill effect|archon buff|parried debuff) duration", "{a}-duration", "increased")
_p(r"#% {d} chance to (?P<a>shock|freeze|ignite|poison|chill|electrocute|bleed)", "{a}-chance", "increased")
_p(r"#% {d} chance to inflict ailments", "ailment-chance", "increased")
_p(r"#% chance to (?P<a>poison|daze|maim|blind|pierce|bleed)(?: an enemy)?(?: on hit)?", "{a}-chance", "flat")
_p(r"#% chance to inflict bleeding on hit", "bleed-chance", "flat")
_p(r"causes #% {d} stun buildup", "stun-buildup", "increased")
_p(r"spell skills have #% {d} area of effect", "spell-area-of-effect", "increased")
_p(r"#% {d} area of effect of curses", "curse-area-of-effect", "increased")
_p(r"aura skills have #% {d} magnitudes", "aura-magnitude", "increased")
_p(r"meta skills gain #% {d} energy", "meta-skill-energy", "increased")
_p(r"# to # physical thorns damage", "thorns-damage", "flat")
# A share of damage a character gains as another kind. It converts, but the
# share itself is a percentage that adds up, so it is counted in its own row.
_p(r"(?:gain|spells gain) #% of (?:physical )?damage as extra (?P<a>fire|cold|lightning|chaos|physical) damage",
   "extra-{a}-damage", "flat")
_p(r"{n}% of armour also applies to (?P<a>fire|cold|lightning|chaos|elemental) damage",
   "armour-applies-to-{a}-damage", "flat")
_p(r"leech(?:es)? #% of physical (?:attack )?damage as life", "life-leech", "flat")
_p(r"leech(?:es)? #% of physical (?:attack )?damage as mana", "mana-leech", "flat")
_p(r"#% {d} effect of (?P<a>curses|arcane surge|archon buffs|chill|shock|socketed soul cores) on you",
   "{a}-effect-on-you", "increased")
_p(r"#% {d} magnitude of (?P<a>ignite|chill|shock|bleeding) on you", "{a}-magnitude-on-you", "increased")
_p(r"#% {d} effect of your mark skills", "mark-effect", "increased")
_p(r"#% {d} speed of recoup effects", "recoup-speed", "increased")
_p(r"debuffs you inflict have #% {d} slow magnitude", "slow-magnitude", "increased")
_p(r"debuffs on you expire #% faster", "debuff-expiry-speed", "increased")
_p(r"minions revive #% faster", "minion-revive-speed", "increased")
_p(r"#% {d} (?P<a>power|frenzy|endurance) charge duration", "{a}-charge-duration", "increased")
_p(r"#% {d} warcry speed", "warcry-speed", "increased")
_p(r"#% {d} warcry cooldown recovery rate", "warcry-cooldown-recovery", "increased")
_p(r"#% {d} totem placement speed", "totem-placement-speed", "increased")
_p(r"#% {d} totem life", "totem-life", "increased")
_p(r"#% {d} deflection rating", "deflection", "increased")
_p(r"#% {d} stun recovery", "stun-recovery", "increased")
_p(r"#% {d} runic ward regeneration rate", "runic-ward-regeneration", "increased")
_p(r"#% {d} spirit reservation efficiency", "spirit-reservation-efficiency", "increased")
_p(r"#% {d} life cost of skills", "life-cost-of-skills", "increased")
_p(r"#% {d} crossbow reload speed", "reload-speed", "increased")
_p(r"#% {d} glory generation", "glory-generation", "increased")
_p(r"#% {d} knockback distance", "knockback-distance", "increased")
_p(r"#% {d} slowing potency of debuffs on you", "slow-potency-on-you", "increased")
_p(r"(?:equipment and skill gems have )?#% {d} attribute requirements", "attribute-requirements", "increased")
_p(r"{n}% to quality of all skills", "skill-quality", "flat")
_p(r"#% of damage taken recouped as life", "damage-recouped-as-life", "flat")
_p(r"#% of damage taken recouped as mana", "damage-recouped-as-mana", "flat")
_p(r"#% of damage is taken from mana before life", "damage-taken-from-mana", "flat")
_p(r"regenerate #% of maximum life per second", "life-regeneration-percent", "flat")
_p(r"(?:has )?{n} charm slots?", "charm-slots", "flat")
_p(r"{n} to maximum rage", "maximum-rage", "flat")
_p(r"{n} to maximum runic ward", "maximum-runic-ward", "flat")
_p(r"{n} to maximum (?P<a>power|frenzy|endurance) charges", "maximum-{a}-charges", "flat")
_p(r"#% {d} (?:life |mana )?flask charges gained", "flask-charges-gained", "increased")
_p(r"#% {d} flask charges used", "flask-charges-used", "increased")
_p(r"#% {d} charm charges gained", "charm-charges-gained", "increased")
_p(r"#% {d} charm charges used", "charm-charges-used", "increased")
_p(r"#% {d} life and mana recovery from flasks", ("flask-life-recovery", "flask-mana-recovery"), "increased")
_p(r"#% {d} life recovery from flasks", "flask-life-recovery", "increased")
_p(r"#% {d} mana recovery from flasks", "flask-mana-recovery", "increased")
_p(r"#% {d} flask life recovery rate", "flask-life-recovery", "increased")
_p(r"#% {d} flask mana recovery rate", "flask-mana-recovery", "increased")

# ── what a build fields, which is not the character ──────────────────────────
# Minions, companions and totems have their own life and their own damage.
# They are counted, in rows of their own: a summoner's whole plan is here
# and folding it into the character's damage would state something false.
_p(r"minions have #% {d} attack and cast speed", ("minion-attack-speed", "minion-cast-speed"), "increased")
_p(r"minions have #% {d} critical hit chance", "minion-critical-chance", "increased")
_p(r"minions have #% {d} critical damage bonus", "minion-critical-damage", "increased")
_p(r"minions have #% {d} area of effect", "minion-area-of-effect", "increased")
_p(r"minions have {n}% to all elemental resistances",
   ("minion-fire-resistance", "minion-cold-resistance", "minion-lightning-resistance"), "flat")
_p(r"minions have {n}% to chaos resistance", "minion-chaos-resistance", "flat")
_p(r"companions deal #% {d} damage", "companion-damage", "increased")
_p(r"companions have #% {d} maximum life", "companion-life", "increased")
_p(r"companions have #% {d} area of effect", "companion-area-of-effect", "increased")


# ── what a line that matched nothing is about ────────────────────────────────
# Order again: the first hit wins, so the compound words come before the
# plain ones. This does not count anything — it only decides which row an
# uncounted line is filed against, so the stat it talks about shows that
# something about it is missing from its total.
MENTIONS: list[tuple[re.Pattern, str]] = [
    (re.compile(p), s) for p, s in (
        (r"\bmaximum life\b", "life"), (r"\bmaximum mana\b", "mana"),
        (r"\benergy shield\b", "energy-shield"), (r"\bspirit\b", "spirit"),
        (r"\bminions?\b", "damage-minion"),
        (r"\barmour\b", "armour"), (r"\bevasion\b", "evasion"), (r"\bblock\b", "block"),
        (r"\bstun\b", "stun-threshold"),
        (r"maximum \w+ resistance", "resistance-fire-max"),
        (r"\bfire resistance\b", "resistance-fire"), (r"\bcold resistance\b", "resistance-cold"),
        (r"\blightning resistance\b", "resistance-lightning"), (r"\bchaos resistance\b", "resistance-chaos"),
        (r"\belemental resistances?\b", "resistance-fire"),
        (r"\bcritical\b", "critical-chance"), (r"\baccuracy\b", "attack-rating"),
        (r"\battack speed\b", "speed-attack"), (r"\bcast speed\b", "speed-cast"),
        (r"\bmovement speed\b", "speed-movement"), (r"\bcooldown\b", "cooldown-reduction"),
        (r"\bfire damage\b", "damage-fire"), (r"\bcold damage\b", "damage-cold"),
        (r"\blightning damage\b", "damage-lightning"), (r"\bphysical damage\b", "damage-physical"),
        (r"\bchaos damage\b", "damage-chaos"), (r"\bspell damage\b", "damage-spell"),
        (r"\battack damage\b", "damage-attack"), (r"\bdamage\b", "damage"),
        (r"\blife\b", "life"), (r"\bmana\b", "mana"),
        (r"\blevel of\b", "skills-single"),
    )
]

# Where a line goes when it names nothing the vocabulary knows. One row, not
# a thousand: a plan picks hundreds of sentences and each would otherwise
# make a row of its own and bury the panel.
OTHER_EFFECTS = "other-effects"

# Why a line was not counted, in our own words, for the panel and the census
# to say. First match wins, so the narrow reasons come first.
REASONS: list[tuple[re.Pattern, str]] = [
    (re.compile(p), why) for p, why in (
        (r"^(?:duration s|charges per use|max charges|recovers life|recovers mana)$",
         "the pack records it as a field of the flask, not as a stat line"),
        (r"\bany attribute\b", "the game lets a person pick which attribute and the plan does not record the pick"),
        (r"^grants skill\b", "it grants a skill rather than a number"),
        (r"\b(?:while|during|whilst) \b", "it only applies while something is true"),
        (r"\b(?:if|when|whenever|unless) \b", "it only applies if something is true"),
        (r"\brecently\b", "it only applies for a while after something happens"),
        (r"\bper\b|\bfor each\b|\bfor every\b|\bequal to\b", "it scales off another number the plan does not hold"),
        (r"\bchance to\b|\bchance for\b|\bchance when\b", "it is a chance of something happening, not an amount"),
        (r"\bgrants skill\b", "it grants a skill rather than a number"),
        (r"\bminions?\b|\ballies\b|\bcompanions?\b|\btotems?\b|\boffering", "it is somebody else's number, not the character's"),
        (r"\benemies\b|\benemy\b|\bagainst\b", "it changes what enemies have, not what the character has"),
        (r"\bconverted to\b|\bas extra\b|\balso applies\b|\btaken as\b", "it converts one number into another"),
        (r"\bon hit\b|\bon kill\b|\bon block\b|\bon critical\b", "it happens on an event rather than standing"),
        (r"\bcan (?:roll|be)\b|\bcan apply\b|\ballowed\b|\bmodifiers?$", "it is a rule about the item rather than a number"),
        (r"\bbuildup\b|\bmagnitude\b|\bthreshold\b|\bduration\b", "the vocabulary has no name for this number yet"),
    )
]


def why_not(sentence: str) -> str:
    """Our own words for why a sentence is held and not counted."""
    n = sentence if sentence == sentence.lower() else normalise(sentence)
    for rx, why in REASONS:
        if rx.search(n):
            return why
    return "no pattern claims this wording yet"


def match(sentence: str) -> tuple[tuple[str, ...], str, int] | None:
    """
    The canonical stats a normalised sentence feeds, its form, and its sign.

    The FIRST pattern to match wins, which is why the list is ordered and
    every pattern anchored. `increased` and `reduced` both mean the
    increased form and `more` and `less` both mean the more form; the word
    the sentence used decides the form and the sign, so one entry does the
    work of four.
    """
    for rx, stat, form in PATTERNS:
        m = rx.match(sentence)
        if not m:
            continue
        caught = m.groupdict()
        word = caught.get("dir") or ""
        if word in ("more", "less"):
            form = "more"
        sign = -1 if word in ("reduced", "less") else 1
        stats = stat if isinstance(stat, tuple) else (stat,)
        return tuple(_fill(s, caught) for s in stats), form, sign
    return None


def _fill(stat: str, caught: dict) -> str:
    """A stat named after the word the sentence used: `{a}-buildup` with `freeze` in it."""
    if "{" not in stat:
        return stat
    return stat.format(**{k: str(v or "").strip().replace(" ", "-") for k, v in caught.items()})


# ── the numbers ──────────────────────────────────────────────────────────────

def _best(v: object) -> tuple[float | None, str]:
    """One rolled value: the best roll, and whether collapsing the range cost us anything."""
    if isinstance(v, dict):
        lo, hi = v.get("min"), v.get("max")
        if isinstance(hi, (int, float)) and not isinstance(hi, bool):
            return float(hi), (APPROXIMATE if isinstance(lo, (int, float)) and lo != hi else COUNTED)
        if isinstance(lo, (int, float)) and not isinstance(lo, bool):
            return float(lo), COUNTED
        return None, NOT_COUNTED
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v), COUNTED
    return None, NOT_COUNTED


def _written(sentence: str) -> list[float]:
    """The numbers the sentence writes out itself — a fixed line carries no fields."""
    return [float(x.replace(",", "")) for x in re.findall(r"[-+]?[0-9][0-9.]*", str(sentence or ""))]


def _number(line: dict, sentence: str, span: bool) -> tuple[float | None, str]:
    """
    The value to count, and how far to trust it.

    ⚠ A SPAN is two numbers, not a range of one: `Adds 76 to 193 Fire Damage`
    is a low end and a high end, and the pool holds one number per stat. It
    is counted at the middle of the two and marked approximate, which is the
    model's own word for a range collapsed.
    """
    values = line.get("values") if isinstance(line.get("values"), list) else []
    if span:
        ends: list[tuple[float | None, str]] = []
        if len(values) >= 2:
            ends = [_best(values[0]), _best(values[1])]
        elif line.get("min") is not None or line.get("max") is not None:
            ends = [_best(line.get("min")), _best(line.get("max"))]
        else:
            written = _written(sentence)
            ends = [(written[0], COUNTED), (written[1], COUNTED)] if len(written) >= 2 else []
        if len(ends) == 2 and ends[0][0] is not None and ends[1][0] is not None:
            return (ends[0][0] + ends[1][0]) / 2.0, APPROXIMATE
        return None, NOT_COUNTED
    if values:
        return _best(values[0])
    for field in ("value", "max", "min"):
        if field in line:
            got, state = _best(line.get(field))
            if got is not None:
                if field == "max" and isinstance(line.get("min"), (int, float)) and line["min"] != line["max"]:
                    state = APPROXIMATE                     # the best roll, and the pack keeps both ends
                return got, state
    written = _written(sentence)
    return (written[0], COUNTED) if written else (None, NOT_COUNTED)


def local(line: dict) -> bool:
    """
    Whether the line raises the ITEM's own number rather than the character's.

    ⚠ This is the difference between `350% increased Physical Damage` on a
    sword — which multiplies that sword's damage and nothing else — and the
    same sentence on a passive, which multiplies everything. Summed into one
    bracket they would state a number nobody has. The pack marks a rune's
    effects outright and writes `local` into an affix's id; a unique's or a
    base's wording says nothing either way, and the census says so.
    """
    if line.get("local") is True:
        return True
    key = str(line.get("stat") or "")
    return " " not in key and "local" in key.lower()


def _wording(line: dict) -> str:
    """The sentence to match on: the game's words, wherever the pack put them."""
    stat = str(line.get("stat") or "")
    text = str(line.get("text") or "")
    if " " in stat:
        return stat                     # a unique, a node, a rune: the line IS the sentence
    return text or stat                 # an affix: the id is a slug and the wording is in the text


_PATCH = re.compile(r"^(?:pre |current$)", re.I)


def superseded(line: dict) -> str:
    """
    Why a line is not this character's, in our own words — or nothing.

    The pack keeps a unique's old rolls beside its current one and tags them
    with the patch they were last seen in, and it keeps the several versions
    of an item that has them. Either way the line is a fact we hold about
    some other item than the one in the plan.
    """
    variants = line.get("variants")
    if not isinstance(variants, list) or not variants or "Current" in variants:
        return ""
    if all(_PATCH.match(str(v)) for v in variants):
        return "it is a roll from a patch that has been replaced"
    return "the item has several versions and the plan does not record which one"


def map_line(line: dict, source: dict) -> list[Contribution]:
    """One of a record's stat lines, as contributions."""
    sentence = _wording(line)
    if not sentence:
        return []
    text = str(line.get("text") or sentence)[:160]
    common = dict(source_kind=source.get("kind", ""), source_id=source.get("id", ""),
                  source_name=source.get("name", ""), text=text, place=source.get("place", ""))
    shape = normalise(sentence)
    found = match(shape)
    value, sureness = _number(line, sentence, span="# to #" in shape)

    held = (found is None or value is None or bool(superseded(line))
            or (local(line) and found[1] in ("increased", "more")))
    if held:
        # A fact we hold and cannot add up: filed against the stat it talks
        # about, so that stat's row shows the piece missing from its total.
        stat = found[0][0] if found else _filed(shape)
        return [Contribution(stat=stat, form="flat", value=0.0, state=NOT_COUNTED, **common)]

    stats, form, sign = found
    # ⚠ Every `more` multiplier in this game applies on its own, so each gets
    # a bucket of its own: the pool adds only what shares one.
    bucket = ":".join((source.get("kind", ""), source.get("id", ""), common["place"], text)) if form == "more" else ""
    return [Contribution(stat=s, form=form, value=sign * value, state=sureness, bucket=bucket, **common) for s in stats]


def _filed(shape: str) -> str:
    """The row an uncounted sentence belongs in — the stat it talks about, or the one catch-all."""
    for rx, stat in MENTIONS:
        if rx.search(shape):
            return stat
    return OTHER_EFFECTS


# ── what the character is before anything is chosen ──────────────────────────

def base_for(plan: dict, data, pool) -> dict[str, float]:
    """
    The class's own numbers at the planned level, and the caps.

    ⚠ This pack records a class's STARTING ATTRIBUTES and nothing else: there
    is no starting life, no life per level and no base spirit in it, so those
    bases are absent rather than invented, and a life total here is the sum
    of what the plan adds. The census says so.
    """
    cls = data.get(GAME, "class", str(plan.get("class_id") or "")) or {}
    levels = data.get(GAME, "progression", "levels") or {}
    cap = levels.get("cap") if isinstance(levels.get("cap"), int) else LEVEL_CAP
    level = max(1, min(int(cap or LEVEL_CAP), int(plan.get("level") or 1)))
    base = dict(BASE)
    start = cls.get("starting_attributes") or {}
    for a in _ATTRS:
        if isinstance(start.get(a), (int, float)) and not isinstance(start.get(a), bool):
            base[a] = float(start[a])
    # Present only if the pack grows them; a base we made up would read as a
    # fact and it would not be one.
    per_level = cls.get("per_level") or {}
    for pool_stat, started, each in (("life", "starting_life", "life"), ("mana", "starting_mana", "mana")):
        if isinstance(cls.get(started), (int, float)):
            base[pool_stat] = float(cls[started]) + (level - 1) * float(per_level.get(each) or 0)
    if isinstance(cls.get("starting_spirit"), (int, float)):
        base["spirit"] = float(cls["starting_spirit"])
    return base
