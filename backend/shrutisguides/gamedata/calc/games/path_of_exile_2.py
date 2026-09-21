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

⚠ That last one is decided from the pack and never from a hunch. A rune
marks its own effects `local`; an affix carries the word in its id and the
game's mod group beside it (`LocalPhysicalDamagePercent`); and a unique or
a base, which say nothing either way, are judged by WHAT THEY ARE — the
pack records an item's type, and only six types keep armour of their own
and nineteen keep damage. So `(700-800)% increased Armour` on a body
armour is held and the same sentence on The Anvil, an amulet, is counted.
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
# The same job for the sentences that say a speed instead of an amount:
# `debuffs on you expire 20% faster`, `20% slower start of Energy Shield
# recharge`. Slower is the negative of faster, exactly as reduced is of
# increased, so one entry again serves both.
_F = r"(?P<dir>faster|slower)"
# ⚠ A wildcard must not swallow a condition. Anchored patterns keep most of
# them out by themselves — `#% increased Armour while stationary` does not
# end in `armour` — but a wildcard whose tail is a fixed phrase can still
# reach over one: `effect of Arcane Surge on you per ten percent missing
# Mana` ends in words. Put this at the head of an open wildcard and the
# sentence is refused the moment it goes on to state a condition.
_STANDING = (r"(?!.*\b(?:while|whilst|during|if|when|whenever|unless|recently|against"
             r"|per|for each|for every|equal to|from equipped)\b)")
# A phrase that stops at the first word that turns a stat into a narrower
# one. `Magnitude of Bleeding you inflict with Critical Hits` is not
# bleeding magnitude — it is a bonus on some of a character's hits — and
# folding the two together would credit it with the wider number. The
# guard is checked word by word rather than over the whole remainder,
# because these sentences may end in an allowed tail (`you inflict`).
_STOP = r"(?:you|with|against|per|while|whilst|if|when|unless|recently|on|from)"
_WORD = rf"(?:(?!{_STOP}\b)[a-z][a-z-]*)"
_PHRASE = rf"{_WORD}(?: {_WORD})*"

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
    PATTERNS.append((re.compile("^" + pattern.replace("{n}", _N).replace("{d}", _D).replace("{f}", _F)
                                + "$"), stat, form))


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
_p(r"#% {f} start of energy shield recharge", "energy-shield-recharge-delay", "increased")

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
# ── ailments and statuses, in one wildcard per shape ─────────────────────────
# Freeze, ignite, shock, chill, poison, bleeding, stun, pin, electrocute,
# daze, blind, wither — the game says each of them the same four ways, so
# there are four entries rather than four dozen: BUILDUP is how fast it
# lands, THRESHOLD is how much a thing takes before it lands, MAGNITUDE is
# how hard it hits and DURATION is how long it stays. The word the sentence
# uses names the row, which is why `freeze buildup` and `pin buildup` keep a
# row each without either being written out here. `_STANDING` is what stops
# a wildcard reaching over a condition and counting a number that is not
# always on.
#
# ⚠ An ailment's duration IS its duration on the thing carrying it, so
# `increased Chill Duration on Enemies` and `increased Chill Duration` are
# one row and not two. `on you` is the other side of it — how long an
# ailment somebody else inflicts stays on this character — and that is a
# different number, so it keeps its own row.
_p(r"#% {d} magnitude of (?P<a>[a-z][a-z -]*) on you", "{a}-magnitude-on-you", "increased")
_p(rf"#% {{d}} magnitude of (?P<a>{_PHRASE})(?: you inflict)?", "{a}-magnitude", "increased")
_p(r"#% {d} (?P<a>flammability|ignite|exposure|blind|parried debuff) (?:magnitude|effect)", "{a}-magnitude", "increased")
_p(r"#% {d} (?P<a>[a-z][a-z -]*) magnitude", "{a}-magnitude", "increased")
_p(r"#% {d} (?P<a>[a-z][a-z ]*) buildup", "{a}-buildup", "increased")
_p(r"{n} to ailment threshold", "ailment-threshold", "flat")
_p(r"#% {d} (?P<a>[a-z][a-z ]*) threshold", "{a}-threshold", "increased")
_p(r"#% {d} endurance frenzy and power charge duration",
   ("endurance-charge-duration", "frenzy-charge-duration", "power-charge-duration"), "increased")
_p(r"#% {d} duration of ignite shock and chill on enemies",
   ("ignite-duration", "shock-duration", "chill-duration"), "increased")
_p(r"#% {d} (?P<a>[a-z][a-z -]*) duration on you", "{a}-duration-on-you", "increased")
_p(r"#% {d} duration of (?P<a>[a-z][a-z -]*) on you", "{a}-duration-on-you", "increased")
_p(r"#% {d} (?P<a>[a-z][a-z -]*) duration(?: on enemies)?", "{a}-duration", "increased")
_p(r"#% {d} duration of (?P<a>[a-z][a-z -]*) on enemies", "{a}-duration", "increased")
_p(r"#% {d} chance to (?P<a>shock|freeze|ignite|poison|chill|electrocute|bleed)", "{a}-chance", "increased")
_p(r"#% {d} chance to inflict ailments", "ailment-chance", "increased")
_p(r"#% chance to (?P<a>poison|daze|maim|blind|pierce|bleed)(?: an enemy| enemies)?"
   r"(?: on hit)?(?: with attacks)?", "{a}-chance", "flat")
_p(r"#% chance to inflict bleeding on hit", "bleed-chance", "flat")
_p(r"causes #% {d} stun buildup", "stun-buildup", "increased")
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
_p(r"#% {d} effect of (?P<a>[a-z][a-z -]*) on you", "{a}-effect-on-you", "increased")
_p(r"#% {d} effect of your mark skills", "mark-effect", "increased")
_p(r"#% {d} speed of recoup effects", "recoup-speed", "increased")
_p(r"debuffs you inflict have #% {d} slow magnitude", "slow-magnitude", "increased")
_p(r"debuffs on you expire #% {f}", "debuff-expiry-speed", "increased")
_p(r"buffs on you expire #% {f}", "buff-expiry-speed", "increased")
_p(r"minions revive #% {f}", "minion-revive-speed", "increased")
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
# Minions, companions, totems, offerings, ballistas and the allies standing
# in a character's presence all have their own life, their own damage and
# their own resistances, and the game says all six the same way. So the
# alternation names them once and the captured word — singular, because a
# row reads better as `Minion attack speed` than `Minions attack speed` —
# becomes the head of the row. They are counted, in rows of their own: a
# summoner's whole plan is here and folding it into the character's damage
# would state something false.
#
# ⚠ `you and allies in your presence have …` is TWO facts. The character
# gets the number as well, so the line splits: the character's own row and
# the allies' row, neither of them guessed.
_WHO = r"(?P<w>minion|companion|totem|offering|ballista)s"
_ALLIES = r"allies in your presence"
_THEIRS = r"(?P<a>attack speed|cast speed|movement speed|skill speed|accuracy rating" \
        r"|area of effect|evasion rating|armour|maximum energy shield|duration|life regeneration rate)"

_p(r"minions deal #% {d} damage", "damage-minion", "increased")
_p(r"minions have #% {d} maximum life", "life-minion", "increased")
_p(r"minions have #% {d} attack and cast speed", ("minion-attack-speed", "minion-cast-speed"), "increased")
_p(rf"{_WHO} deal #% {{d}} damage", "{w}-damage", "increased")
_p(rf"{_WHO} have #% {{d}} maximum life", "{w}-life", "increased")
_p(rf"{_WHO} have #% {{d}} attack and cast speed", ("{w}-attack-speed", "{w}-cast-speed"), "increased")
_p(rf"{_WHO} have #% {{d}} cooldown recovery rate", "{w}-cooldown-recovery", "increased")
_p(rf"{_WHO} have #% {{d}} critical hit chance", "{w}-critical-chance", "increased")
_p(rf"{_WHO} have #% {{d}} critical damage bonus", "{w}-critical-damage", "increased")
_p(rf"{_WHO} have #% {{d}} {_THEIRS}", "{w}-{a}", "increased")
_p(rf"{_WHO} (?:cause|have) #% {{d}} (?P<a>[a-z][a-z ]*) buildup", "{w}-{a}-buildup", "increased")
_p(rf"{_WHO} have #% additional (?P<a>physical|elemental|chaos) damage reduction",
   "{w}-{a}-damage-reduction", "flat")
_p(rf"{_WHO} have {{n}}% to all elemental resistances",
   ("{w}-fire-resistance", "{w}-cold-resistance", "{w}-lightning-resistance"), "flat")
_p(rf"{_WHO} have {{n}}% to all maximum elemental resistances",
   ("{w}-fire-resistance-max", "{w}-cold-resistance-max", "{w}-lightning-resistance-max"), "flat")
_p(rf"{_WHO} (?:have|gain) {{n}}% to maximum (?P<a>fire|cold|lightning|chaos) resistances?",
   "{w}-{a}-resistance-max", "flat")
_p(rf"{_WHO} have {{n}}% to (?P<a>fire|cold|lightning|chaos) resistance", "{w}-{a}-resistance", "flat")
_p(rf"{_WHO} have {{n}} to accuracy rating", "{w}-accuracy-rating", "flat")
_p(rf"{_WHO} gain #% (?:of )?damage as extra (?P<a>fire|cold|lightning|chaos|physical) damage",
   "{w}-extra-{a}-damage", "flat")
_p(rf"{_ALLIES} deal #% {{d}} damage", "ally-damage", "increased")
_p(rf"{_ALLIES} deal # to # added (?:attack |spell )?(?P<a>fire|cold|lightning|chaos|physical) damage",
   "ally-added-{a}-damage", "flat")
_p(rf"{_ALLIES} gain #% of damage as extra (?P<a>fire|cold|lightning|chaos|physical) damage",
   "ally-extra-{a}-damage", "flat")
_p(rf"{_ALLIES} have #% {{d}} cooldown recovery rate", "ally-cooldown-recovery", "increased")
_p(rf"{_ALLIES} have #% {{d}} critical hit chance", "ally-critical-chance", "increased")
_p(rf"{_ALLIES} have #% {{d}} critical damage bonus", "ally-critical-damage", "increased")
_p(rf"{_ALLIES} have #% {{d}} {_THEIRS}", "ally-{a}", "increased")
_p(rf"{_ALLIES} have {{n}} to accuracy rating", "ally-accuracy-rating", "flat")
_p(rf"{_ALLIES} have {{n}}% to all elemental resistances",
   ("ally-fire-resistance", "ally-cold-resistance", "ally-lightning-resistance"), "flat")
_p(rf"{_ALLIES} have {{n}}% to (?P<a>fire|cold|lightning|chaos) resistance", "ally-{a}-resistance", "flat")
_p(rf"you and {_ALLIES} have #% {{d}} attack speed", ("speed-attack", "ally-attack-speed"), "increased")
_p(rf"you and {_ALLIES} have #% {{d}} cast speed", ("speed-cast", "ally-cast-speed"), "increased")
_p(rf"you and {_ALLIES} have #% {{d}} accuracy rating", ("attack-rating", "ally-accuracy-rating"), "increased")
_p(rf"you and {_ALLIES} have #% {{d}} cooldown recovery rate",
   ("cooldown-reduction", "ally-cooldown-recovery"), "increased")
_p(rf"you and {_ALLIES} have {{n}}% to (?P<a>fire|cold|lightning|chaos) resistance",
   ("resistance-{a}", "ally-{a}-resistance"), "flat")
_p(rf"you and {_ALLIES} have {{n}}% to all elemental resistances",
   ("resistance-fire", "resistance-cold", "resistance-lightning",
    "ally-fire-resistance", "ally-cold-resistance", "ally-lightning-resistance"), "flat")
_p(r"spells cast by totems have #% {d} cast speed", "totem-cast-speed", "increased")
_p(r"attacks used by totems have #% {d} attack speed", "totem-attack-speed", "increased")
_p(r"{n} to maximum number of summoned (?P<a>[a-z][a-z ]*)", "maximum-summoned-{a}", "flat")


# ── the weapon a bracket is scoped to ────────────────────────────────────────
# `20% increased Attack Speed with Bows` is not attack speed; it is a
# bracket of its own that a bow build lives in and a mace build never sees.
# The pack already keeps `damage with swords` in its own row for that
# reason, and speed, accuracy and the two critical numbers are the same
# sentence with a different noun, so they get one entry each.
_WEAPONS = (r"one handed melee weapons|two handed melee weapons|one handed weapons|two handed weapons"
            r"|melee weapons|unarmed attacks|bows|crossbows|swords|axes|maces|flails|spears|daggers|claws"
            r"|quarterstaves|wands|sceptres|staves|traps|bow skills")
_p(rf"#% {{d}} attack speed with (?P<a>{_WEAPONS})", "attack-speed-with-{a}", "increased")
_p(rf"#% {{d}} critical hit chance with (?P<a>{_WEAPONS})", "critical-chance-with-{a}", "increased")
_p(rf"#% {{d}} critical damage bonus with (?P<a>{_WEAPONS})", "critical-damage-with-{a}", "increased")
_p(rf"#% {{d}} accuracy rating with (?P<a>{_WEAPONS})", "attack-rating-with-{a}", "increased")
_p(rf"#% {{d}} (?P<b>[a-z][a-z ]*) buildup with (?P<a>{_WEAPONS})", "{b}-buildup-with-{a}", "increased")
_p(r"#% {d} damage with (?P<a>[a-z]+ skills|warcries|unarmed attacks)", "damage-with-{a}", "increased")


# ── the family of skills a bracket is scoped to ──────────────────────────────
# `Banner Skills have 20% increased Area of Effect`, `Herald Skills deal 15%
# increased Damage`, `30% increased Reservation Efficiency of Minion Skills`
# — the game names a family and then says an ordinary stat about it. One
# entry per shape, the family taken from the sentence, so a row reads
# `Banner area of effect` and is never confused with the character's own.
# The family is at most two words, which is what stops the capture running
# backwards over the front of a longer sentence.
_FAMILY = r"(?P<a>[a-z]+(?: [a-z]+)?)"
_p(rf"{_FAMILY} (?:skills|spells|attacks) deal #% {{d}} (?:spell |attack )?damage", "{a}-damage", "increased")
_p(rf"{_FAMILY} skills (?:have|gain) #% {{d}} (?P<b>area of effect|duration|use speed|skill effect duration"
   rf"|buff effect|aura magnitudes|maximum energy|seal gain frequency|cast speed|attack speed"
   rf"|reservation efficiency|magnitudes|damage)", "{a}-{b}", "increased")
_p(rf"#% {{d}} reservation efficiency of {_FAMILY} skills", "{a}-reservation-efficiency", "increased")
_p(r"#% {d} mana reservation efficiency(?: of skills)?", "mana-reservation-efficiency", "increased")
_p(rf"#% {{d}} cooldown recovery rate for {_FAMILY} skills", "{a}-cooldown-recovery", "increased")
_p(rf"#% {{d}} glory generation for {_FAMILY} skills", "{a}-glory-generation", "increased")
_p(rf"#% {{d}} attack and cast speed with {_FAMILY} skills",
   ("attack-speed-with-{a}-skills", "cast-speed-with-{a}-skills"), "increased")
_p(rf"#% {{d}} (?P<b>attack|cast|skill) speed with {_FAMILY} skills", "{b}-speed-with-{a}-skills", "increased")


# ── the element or the bracket a damage line is scoped to ────────────────────
# One entry covers five elements, because the sentence is the same sentence
# with the element swapped. A scoped one — `Attack Cold Damage` — is its own
# row for the reason the plain brackets are: this game never adds a scoped
# bracket to the global one.
_ELEM = r"(?P<a>fire|cold|lightning|chaos|physical|elemental)"
_p(rf"#% {{d}} (?P<b>attack|spell|melee|projectile|area) {_ELEM} damage", "{b}-{a}-damage", "increased")
_p(rf"#% of {_ELEM} damage taken recouped as life", "{a}-damage-recouped-as-life", "flat")
_p(rf"#% of {_ELEM} damage taken recouped as mana", "{a}-damage-recouped-as-mana", "flat")
_p(rf"#% of {_ELEM} damage taken recouped as energy shield", "{a}-damage-recouped-as-energy-shield", "flat")
_p(r"#% of damage taken recouped as life mana and energy shield",
   ("damage-recouped-as-life", "damage-recouped-as-mana", "damage-recouped-as-energy-shield"), "flat")
_p(rf"#% of {_ELEM} damage prevented recouped as life", "{a}-damage-prevented-recouped-as-life", "flat")


# ── the rest of this game's own numbers ──────────────────────────────────────
# Each of these is one sentence the pack says often enough to earn an entry,
# and each keeps the game's own words as the name of its row.
_p(r"(?:hits )?break #% {d} armour", "armour-break", "increased")
_p(r"#% {d} armour break taken", "armour-break-taken", "increased")
_p(r"#% {d} effect of your mark skills", "mark-effect", "increased")
_p(r"#% {d} effect of (?P<a>" + _STANDING + r"[a-z][a-z -]*)", "{a}-effect", "increased")
_p(r"#% {d} (?P<a>[a-z][a-z ]*) area of effect", "{a}-area-of-effect", "increased")
_p(r"#% {d} (?P<a>[a-z]+) critical hit chance", "{a}-critical-chance", "increased")
_p(r"#% {d} (?P<a>[a-z]+) critical damage bonus", "{a}-critical-damage", "increased")
_p(r"{n}% to thorns critical hit chance", "thorns-critical-chance", "flat")
_p(r"#% {d} (?P<a>[a-z]+) attack speed", "{a}-attack-speed", "increased")
_p(r"#% {d} (?P<a>bolt|arrow|projectile) speed", "{a}-speed", "increased")
_p(r"#% {f} curse activation", "curse-activation-speed", "increased")
_p(r"damaging ailments deal damage #% {f}", "damaging-ailments-damage-speed", "increased")
_p(r"(?P<a>bleeding|ignite|poison|shock|chill|freeze)s? you inflict deals? damage #% {f}",
   "{a}-damage-speed", "increased")
_p(r"archon recovery period expires #% {f}", "archon-recovery-speed", "increased")
_p(r"leech life #% {f}", "life-leech-speed", "increased")
_p(r"#% {d} life recovery rate", "life-recovery-rate", "increased")
_p(r"#% {d} maximum runic ward", "maximum-runic-ward", "increased")
_p(r"#% {d} (?:crossbow )?reload speed", "reload-speed", "increased")
_p(r"#% {d} weapon swap speed", "weapon-swap-speed", "increased")
_p(r"#% {d} trap throwing speed", "trap-throwing-speed", "increased")
_p(r"#% {d} total power counted by warcries", "warcry-power", "increased")
_p(r"charms applied to you have #% {d} effect", "charm-effect", "increased")
_p(r"remnants you create have #% {d} effect", "remnant-effect", "increased")
_p(r"#% {d} experience gain", "experience-gain", "increased")
_p(r"#% {d} maximum darkness", "maximum-darkness", "increased")
_p(r"#% {d} block recovery", "block-recovery", "increased")
_p(r"#% {d} flask and charm charges gained", ("flask-charges-gained", "charm-charges-gained"), "increased")
_p(r"{n}% to maximum quality", "maximum-quality", "flat")
_p(r"{n} to maximum number of (?P<a>[a-z][a-z ]*)", "maximum-{a}", "flat")
_p(r"grants # passive skill points?", "passive-points", "flat")
_p(r"prevent {n}% of damage from deflected hits", "deflected-damage-prevented", "flat")
_p(r"#% of damage taken bypasses energy shield", "damage-bypassing-energy-shield", "flat")
_p(r"{n} physical damage taken from attack hits", "physical-damage-taken-from-attacks", "flat")
_p(r"{n} metres to (?P<a>" + _STANDING + r"[a-z][a-z ]*)", "{a}", "flat")
_p(r"{n} to weapon range", "weapon-range", "flat")
_p(r"reserves #% of life", "life-reserved", "flat")
_p(r"#% {d} movement speed penalty from using skills while moving", "skill-movement-speed-penalty", "increased")
_p(r"remnants can be collected from #% further away", "remnant-collection-range", "increased")
_p(rf"#% {{d}} (?P<b>projectile|attack|cast|skill) speed for {_FAMILY} skills", "{b}-speed-with-{a}-skills",
   "increased")
_p(rf"{_WHO} (?:deal|have) #% {{d}} (?P<a>damage|cooldown recovery rate|skill speed) (?:with|for) command skills",
   "{w}-command-skill-{a}", "increased")
# ⚠ What a hit against this character is worth is the character's number, not
# the enemy's: a person reads it as a defence and the game writes it from the
# attacker's side. The row says whose it is in its own name.
_p(r"hits against you have #% {d} critical damage bonus", "critical-damage-against-you", "increased")
_p(r"hits have #% {d} critical hit chance against you", "critical-chance-against-you", "increased")
_p(r"enemies blinded by you have #% {d} critical hit chance", "blinded-enemy-critical-chance", "increased")
_p(r"take #% {d} damage from hits", "damage-taken-from-hits", "increased")
_p(r"take #% {d} damage over time", "damage-taken-over-time", "increased")
_p(r"#% {d} damage taken", "damage-taken", "increased")


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
        (r"\bon (?:melee |attack |spell |critical |axe |mace )*hit\b|\bon kill\b|\bon block\b"
         r"|\bon critical\b|\bwhen hit\b", "it happens on an event rather than standing"),
        (r"\bcan (?:roll|be)\b|\bcan apply\b|\ballowed\b|\bmodifiers?$", "it is a rule about the item rather than a number"),
        (r"\bfrom equipped\b|\bsocketed\b", "it multiplies another item's own number, not the character's"),
        (r"\bwith this weapon\b|\bthis item\b", "it multiplies the item's own number, not the character's"),
        (r"\bbuildup\b|\bmagnitude\b|\bthreshold\b|\bduration\b", "the vocabulary has no name for this number yet"),
    )
]


def why_not(sentence: str) -> str:
    """Our own words for why a sentence is held and not counted."""
    n = sentence if sentence == sentence.lower() else normalise(sentence)
    for rx, why in REASONS:
        if rx.search(n):
            return why
    # ⚠ The largest honest category of all. `Crushes enemies on hit`,
    # `Always Hits`, `Cannot be Frozen`, `Loads an additional bolt` —
    # every one of them is a real thing the item does and not one of
    # them is a quantity. `normalise` leaves a `#` wherever a number
    # was, so a shape without one never had a number to count.
    if "#" not in n:
        return "the sentence states a rule rather than a number"
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
        sign = -1 if word in ("reduced", "less", "slower") else 1
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


def local(line: dict, source: dict | None = None) -> bool:
    """
    Whether the PACK says outright that this line raises the item's own number.

    ⚠ This is the difference between `350% increased Physical Damage` on a
    sword — which multiplies that sword's damage and nothing else — and the
    same sentence on a passive, which multiplies everything. Summed into one
    bracket they would state a number nobody has.

    Three places say so and all three are read here: a rune marks its own
    effects with `local`; an affix carries the word in its id; and an affix
    also carries the game's own mod group, which is spelled `LocalEvasionRating`,
    `LocalPhysicalDamagePercent`, `LocalStunDuration`. The group catches
    twenty-seven affixes the id does not — the hybrid defence-and-spirit
    rolls among them — so both are read.
    """
    if line.get("local") is True:
        return True
    key = str(line.get("stat") or "")
    if " " not in key and "local" in key.lower():
        return True
    return str((source or {}).get("group") or "").lower().startswith("local")


# ── whose number an item's increase raises ───────────────────────────────────
# A unique's or a base's wording says nothing either way, so the ITEM decides,
# and the pack records what each item is. Every base of these six types keeps
# an `armour` block of its own — nothing else in the pack does — so an
# increase to armour, evasion or energy shield written on one of them raises
# that block and not the character's pool.
ITEM_DEFENCES = frozenset({"body-armour", "boots", "focus", "gloves", "helmet", "shield"})
# Held in a hand AND carrying damage of its own. Shields, focuses and quivers
# are held too and carry no damage, which is why the list is item types and
# not "whatever is in a hand".
ITEM_WEAPONS = frozenset({"bow", "claw", "crossbow", "dagger", "fishing-rod", "flail", "one-hand-axe",
                          "one-hand-mace", "one-hand-sword", "quarterstaff", "sceptre", "spear", "staff",
                          "talisman", "trap", "two-hand-axe", "two-hand-mace", "two-hand-sword", "wand"})
ITEM_SPIRIT = frozenset({"sceptre"})          # the only base with a `spirit` block
ITEM_BLOCK = frozenset({"shield"})            # the only base with a block chance

# The stats whose sentences the pack's own affix groups mark `Local…`. Each
# of them exists twice in this game — the item's number and the character's —
# and only these ever mean the item's.
ITEM_OWN_DEFENCE = frozenset({"armour", "evasion", "energy-shield"})
ITEM_OWN_WEAPON = frozenset({"damage-physical", "speed-attack", "reload-speed",
                             "stun-duration", "stun-buildup"})


def the_items_own(stats: tuple[str, ...], form: str, source: dict | None = None) -> bool:
    """
    Whether an increase written on this item raises the item's own number.

    ⚠ `(700-800)% increased Armour` on a unique body armour multiplies that
    body armour; the same sentence on an amulet multiplies the character's
    whole pool, and The Anvil really does say it. So the item decides, and
    the pack says what the item is. A FLAT line is not asked about: `+40 to
    Evasion Rating` on a pair of boots adds forty evasion to the boots and
    the boots are on the character, so it reaches the pool either way.
    """
    if form not in ("increased", "more") or not stats:
        return False
    item = str((source or {}).get("type") or "")
    named = set(stats)
    return bool(item) and (
        (named <= ITEM_OWN_DEFENCE and item in ITEM_DEFENCES)
        or (named <= ITEM_OWN_WEAPON and item in ITEM_WEAPONS)
        or (named == {"spirit"} and item in ITEM_SPIRIT)
        or (named == {"block"} and item in ITEM_BLOCK))


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


# ── a sentence with a condition on it ────────────────────────────────────────
#
# ⚠ `_STANDING` deliberately refuses a wildcard that would reach over a
# condition, which is right — but it left every conditional line uncounted,
# and there are more of those than of any other kind. They are not uncertain:
# we know exactly what "40% increased Damage while you have Fortify" is
# worth. What we do not know is whether Fortify is up. So the sentence is cut
# in two — what it grants, and what it waits on — the head goes through the
# ordinary patterns, and the tail becomes an assumption the plan may make.

_CONDITIONAL = re.compile(r"\b(?:while|whilst|during|if|when|whenever|unless)\b")
# words that carry no meaning in an assumption's name
_EMPTY = ("while", "whilst", "during", "if", "when", "whenever", "unless",
          "you", "your", "have", "has", "are", "is", "been", "be", "a", "an", "the")


def condition_id(clause: str) -> str:
    """`while you have Fortify` and `if you have Fortify` are one assumption."""
    words = re.findall(r"[a-z]+", clause.lower())
    while words and words[0] in _EMPTY:
        words.pop(0)
    return "-".join(words)[:120]


def split_condition(shape: str) -> tuple[str, str]:
    """A conditional sentence in two: what it grants, and the assumption it waits on."""
    m = _CONDITIONAL.search(shape)
    if not m or m.start() == 0:
        return "", ""
    head = shape[: m.start()].strip(" ,")
    return (head, condition_id(shape[m.start():])) if head else ("", "")


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
    condition = ""
    if found is None:
        head, waits_on = split_condition(shape)
        if head and waits_on:
            again = match(head)
            if again is not None:
                found, condition = again, waits_on
    value, sureness = _number(line, sentence, span="# to #" in shape)

    held = (found is None or value is None or bool(superseded(line))
            or (found[1] in ("increased", "more")
                and (local(line, source) or the_items_own(found[0], found[1], source))))
    if held:
        # A fact we hold and cannot add up: filed against the stat it talks
        # about, so that stat's row shows the piece missing from its total.
        stat = found[0][0] if found else _filed(shape)
        return [Contribution(stat=stat, form="flat", value=0.0, state=NOT_COUNTED, **common)]

    stats, form, sign = found
    # ⚠ Every `more` multiplier in this game applies on its own, so each gets
    # a bucket of its own: the pool adds only what shares one.
    bucket = ":".join((source.get("kind", ""), source.get("id", ""), common["place"], text)) if form == "more" else ""
    return [Contribution(stat=s, form=form, value=sign * value, state=sureness, bucket=bucket,
                         condition=condition, **common) for s in stats]


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
