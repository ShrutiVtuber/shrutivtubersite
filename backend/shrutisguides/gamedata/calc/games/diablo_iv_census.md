# Diablo IV — the stat vocabulary, measured before it was written

Counted on 21 Sep 2026 against the built pack for Diablo IV 3.2.1 (build
3.2.1.73552), Season 15. Every record of a stat-carrying kind was walked and
every line that names a `stat` was tallied — 18,507 lines across affixes,
uniques, aspects, gems, runewords, charms, sets, paragon nodes, glyphs and
item bases. The table below is what that count found, and `diablo_iv.py` was
written from it, commonest first.

**18,507 lines · 292 spellings · 233 keys once folded · 15,971 lines counted
(86.3%) · 2,536 listed and not counted (13.7%).**

## Two spellings, one stat

The pack speaks twice. A paragon node writes `{"stat": "strength",
"attribute": "Strength_Core", "value": 5, "display": "+5"}`; a gear affix
writes `{"stat": "Armor_Bonus", "unit": "flat", "min": 981, "max": 1225}`.
Lower-casing and turning `_` into `-` folds the two into one key and takes
292 spellings down to 233 — `Hitpoints_Max_Percent_Bonus` and
`hitpoints-max-percent-bonus` become one row, and one table entry serves
both.

Two suffixes come off, and only two:

- **`-core`** is stripped in `_key`. It is the paragon board's mark on the
  four attribute names and marks nothing else, so removing it is safe. (In
  this pack it only ever appears in a line's `attribute` field, never in
  `stat`, so the strip is belt and braces.)
- **`-bonus`** is stripped only as a *fallback* in `_lookup`, after the key
  as written has been tried. ⚠ It cannot be stripped outright: `-bonus` is
  load-bearing in the middle of a name, where `resistance-all-bonus-percent`
  is a percentage and `resistance-all-bonus` is a rating, and a blanket strip
  would merge two different quantities. As a fallback an explicit entry
  always wins, so nothing can be merged by accident. Twenty-six keys reach
  the table this way (`Armor_Bonus` → `armor`, `Crit_Percent_Bonus` →
  `crit-percent`, `Skill_Rank_Bonus` → `skill-rank`, and so on).

Nothing else is stripped. `_Unscaled_By_Player_Health`, `_All_Primary`,
`_Per_Skill_Tag` and `_All` each change what the line means and each has its
own entry.

## The census

Counted down to 95.5% of all lines; the tail is described below. "Form" is
how the line enters the arithmetic and "bucket" is which Diablo IV multiplier
group it joins. A dash means the line is kept and listed rather than added.

| key (folded) | lines | running % | canonical stat · form · bucket | why not, where it is not counted |
|---|---:|---:|---|---|
| `intelligence` | 3058 | 16.52 | intelligence·flat |  |
| `willpower` | 2872 | 32.04 | willpower·flat |  |
| `dexterity` | 2775 | 47.04 | dexterity·flat |  |
| `strength` | 2648 | 61.34 | strength·flat |  |
| `plus-all-stats` | 744 | 65.36 | dexterity·flat; intelligence·flat; strength·flat; willpower·flat |  |
| `affix-value-1` | 685 | 69.07 | — | the placeholder a unique's or aspect's effect sentence is written around, not a stat |
| `hitpoints-max-percent` | 488 | 71.70 | life·increased |  |
| `resistance-all-bonus-percent` | 471 | 74.25 | resistance-cold·flat; resistance-fire·flat; resistance-lightning·flat; resistance-poison·flat; resistance-shadow·flat |  |
| `armor-percent` | 454 | 76.70 | armour·increased |  |
| `damage-percent-bonus-per-skill-tag` | 311 | 78.38 | damage·more·skill; damage·more·skill:<tag> |  |
| `damage-percent-all-from-skills` | 283 | 79.91 | damage·more·all |  |
| `skill-rank` | 260 | 81.32 | skills-single·flat |  |
| `power-cooldown-reduction-percent` | 172 | 82.24 | — | cooldown reduction for ONE named skill; adding two skills' reductions describes neither |
| `item-granted-skill-tree-reward` | 134 | 82.97 | — | grants a passive node the plan has not chosen; the node's own stats are not reachable from the line |
| `skill-rank-skill-tag` | 123 | 83.63 | skills-tab·flat |  |
| `attack-speed-percent` | 121 | 84.29 | speed-attack·flat |  |
| `bonus-healing-received-percent` | 118 | 84.92 | — | a real Diablo IV stat that no canonical name covers yet |
| `resistance` | 110 | 85.52 | resistance-fire·flat; resistance-lightning·flat; resistance-poison·flat; — |  |
| `vulnerable-health-damage` | 106 | 86.09 | damage·more·vulnerable |  |
| `damage-type-percent` | 105 | 86.66 | damage·more·type |  |
| `crit-damage-percent` | 99 | 87.19 | critical-damage·flat |  |
| `affix-value-2` | 88 | 87.67 | — | as above |
| `bonus-percent-per-power` | 84 | 88.12 | — | 'bonus percent' of an unnamed quantity, per skill |
| `skill-tag-cooldown-reduction-percent` | 69 | 88.50 | — | cooldown reduction for one category of skills; as above |
| `bucketed-multiplicative-damage-type` | 66 | 88.85 | damage-cold·more·type; damage-fire·more·type; damage-lightning·more·type; damage-physical·more·type; damage-poison·more·type; damage-shadow·more·type; damage·more·type |  |
| `power-damage-percent` | 65 | 89.20 | — | damage with one named skill |
| `combat-effect-chance` | 63 | 89.54 | lucky-hit·flat |  |
| `damage-percent-bonus-vs-elites` | 63 | 89.88 | damage·more·elites |  |
| `nonphysical-damage-percent` | 62 | 90.22 | damage·more·type |  |
| `resource-max` | 62 | 90.55 | resource·flat |  |
| `multiplicative-damage-percent-all-from-skills` | 53 | 90.84 | damage·more·× <the thing it came from>; — |  |
| `crit-percent` | 50 | 91.11 | critical-chance·flat |  |
| `damage-percent-bonus-vs-cc-all` | 48 | 91.37 | damage·more·crowd-controlled |  |
| `multiplicative-damage-percent-bonus-per-skill-tag` | 43 | 91.60 | damage·more·× <the thing it came from>; — |  |
| `damage-percent-bonus-against-dot-type` | 41 | 91.82 | damage·more·vs-over-time |  |
| `damage-percent-bonus-when-fortified` | 41 | 92.05 | damage·more·fortified |  |
| `power-cooldown-reduction-percent-all` | 40 | 92.26 | cooldown-reduction·flat |  |
| `flat-hitpoints-max-bonus-unscaled-by-player-health` | 36 | 92.46 | life·flat |  |
| `movement-bonus-run-speed` | 36 | 92.65 | speed-movement·flat |  |
| `thorns-flat` | 35 | 92.84 | — | ⚠ written at two scales under one name — see the note below |
| `on-hit-cc-proc-chance` | 34 | 93.02 | — | a thing that happens on a hit, not a thing that adds up |
| `bucketed-multiplicative-damage` | 32 | 93.20 | damage·more·all |  |
| `overpower-damage-bonus-per-stack` | 31 | 93.36 | — | true only per stack of something the line does not count |
| `dodge-chance` | 28 | 93.52 | dodge-chance·flat |  |
| `damage-percent-bonus-while-affected-by-power` | 28 | 93.67 | — | true only while a named buff is running |
| `damage-bonus-to-near` | 28 | 93.82 | damage·more·close |  |
| `cc-duration-reduction` | 27 | 93.96 | — | no canonical name covers control-effect duration |
| `no-damage-taken-flat-hitpoints-regen-per-second` | 27 | 94.11 | life-regeneration·flat |  |
| `resistance-all` | 25 | 94.25 | resistance-cold·flat; resistance-fire·flat; resistance-lightning·flat; resistance-poison·flat; resistance-shadow·flat; — |  |
| `proc-flat-element-damage-on-hit` | 25 | 94.38 | — | a thing that happens on a hit |
| `block-chance` | 25 | 94.52 | block·flat |  |
| `resource-gain-bonus-percent-per-power` | 25 | 94.65 | — | resource gain from one named skill |
| `multiplicative-damage-type-percent` | 24 | 94.78 | — |  |
| `barrier-bonus-percent` | 23 | 94.90 | — | no canonical name covers Barrier |
| `chance-for-double-damage-per-power` | 23 | 95.03 | — | a chance, per named skill |
| `damage-bonus-to-low-health` | 23 | 95.15 | damage·more·vs-injured |  |
| `resource-on-kill` | 22 | 95.27 | — | a thing that happens on a kill |
| `weapon-damage-min` | 22 | 95.39 | damage-min·flat |  |
| `resource-all-primary-max` | 21 | 95.50 | resource·flat |  |

## The tail that is not in the table above

174 keys share the last 832 lines (4.5%). Of those lines:

- **223 are counted.** They are the same stats as above met less often —
  `armor` as a flat number (18), `damage-bonus-to-far` (15),
  `resource-cost-reduction-percent-all` (14), `damage-reduction` (11),
  `skill-rank-all` (11), `bucketed-multiplicative-crit-damage` (11),
  `all-stats-percent` (9), the three single-attribute percentages, and the
  rest of the damage buckets. Every one has a table entry.
- **469 are refused on purpose.** They are named in `UNCOUNTABLE` with the
  reason beside them: procs and on-hit effects, per-skill and per-category
  numbers, durations, per-stack conditions, resource flow, and the things
  that happen outside combat (experience, gold pickup radius, vendor
  discounts).
- **140 are unknown to the table and keep their own names.** Two thirds of
  those are the `multiplicative-*` family declared by a legendary glyph's
  bonus, which names its stat and keeps the number in a scaling block the
  line does not carry — so we know which stat and have no number, and the
  line joins that stat's own row as uncounted rather than inventing a row.
  The rest are one-off named mechanics: eight Season 15 Soul Splinter
  socketables (`s15-socketable-andariel` and its seven siblings, 32 lines),
  a handful of per-class powers (`sorc-hydra-bonus-heads`,
  `rogue-maxpoisontraps`, `barb-berserking-attackspeed`,
  `necro-evade-leavesdesecratedground`), three April Fools' unique affixes,
  and one line whose key in the pack is the string `-1`.

Nothing in the tail is dropped. Every line reaches the panel; the ones that
cannot be added say so.

## Six things the pack gets wrong if you trust the number

**1 · The scale is not in the number.** `0.08` is eight percent on an affix
and eight hundredths of a percent on a paragon node. Four rules settle it, in
order: `unit: "percent"` means a fraction and is multiplied by 100; a
`display` field means the pack already wrote the number the way the game
shows it; neither of those on a stat a person reads as a percentage means a
fraction again (gem bonuses and set powers are written that way); anything
else is a plain amount. Getting this wrong is a factor of a hundred, in
either direction.

**2 · A resistance is two different quantities.** `+{value} All Resistances`
at 325–400 is a resistance RATING. `+{value}% All Resistances` at `0.3` is
thirty percent. They differ only by `unit`, and turning a rating into a
percentage needs a level-and-difficulty formula this pack does not carry. So
a resistance line counts only when its unit says `percent` — 4 lines of the
135 that land on the two ambiguous keys — and a rating is kept on that same resistance's row as an uncounted line,
where a person can see the piece that is not in their number. That is the
largest single refusal after the placeholder values, and the honest one: a
made-up conversion would put a wrong number under a right one.

**3 · Thorns, life on hit and life on kill are written at two scales under
one name.** A paragon node says `thorns-flat: 200`; an affix says
`Thorns_Flat: 0.8`, which is a share of something the pack never names. The
same split hits `Flat_Hitpoints_On_Hit` (0.0387) against its
`_Unscaled_By_Player_Health` twin. Until the pack says which is which, none
of them can be added to the other, so all three are listed rather than
counted.

**4 · A weapon's own speed is not attack speed.** `weapon-speed-bonus: 0.1`
on an axe base is how fast that weapon swings relative to its class, which
scales damage per hit. It does not join the additive attack-speed bracket,
and mixing the two would overstate both.

**5 · The collector echoes an affix's best tier as a line named after the
affix.** `calc/collect.py` turns an affix's highest tier into a line whose
`stat` is the affix record's own id, for packs whose affix states its stat at
the top level. Diablo IV's affixes carry their stats in a list instead, and
that list already holds the top tier's numbers — so the echo is the same fact
twice, not a second one. `map_line` recognises it (the key equals the source
id, and the line has neither `unit` nor `display`) and passes over it, rather
than counting it twice or listing 1,339 phantom uncounted lines.

**6 · A gem carries all three of its bonuses.** A royal ruby's record holds
fire damage for a weapon socket, Strength for an armour socket and fire
resistance for a jewellery socket, and the line says which is which. Counting
all three gave a Sorcerer with three rubies in her jewellery +180 Strength
and +66% fire damage she does not have. `map_line` reads the line's `socket`
against the place the gem sits in and keeps only the one that matches; a
place it cannot read keeps every line, because losing a gem is worse than
over-reading one.

## The multiplier buckets

Diablo IV's damage bonuses add inside a group and multiply between groups,
which is exactly what `Pool` does with `more` contributions that carry a
`bucket`. The pack names the grouping itself: a stat called
`Bucketed_Multiplicative_*` is additive within its own bucket, and the `[x]`
bonuses a person sees in the game are the separate `multiplicative-*` family.

The buckets, and the pack keys that join them:

| bucket | what it is | keys |
|---|---|---|
| `all` | every skill's damage | `damage-percent-all-from-skills`, `bucketed-multiplicative-damage` |
| `type` | the element the hit deals | `damage-type-percent`, `bucketed-multiplicative-damage-type`, `nonphysical-damage-percent`, `bucketed-multiplicative-damage-type-fireholy` |
| `vulnerable` | against a Vulnerable enemy | `vulnerable-health-damage`, `bucketed-multiplicative-vulnerable-health-damage` |
| `crowd-controlled` | against a held enemy | `damage-percent-bonus-vs-cc-all`, `damage-percent-bonus-vs-cc-target` |
| `elites` | against an Elite | `damage-percent-bonus-vs-elites` |
| `over-time` | damage dealt over time | `dot-dps-bonus-percent`, `bucketed-multiplicative-dot-damage` |
| `vs-over-time` | against an enemy already burning, poisoned, bleeding | `damage-percent-bonus-against-dot-type` |
| `close` · `distant` | by how far away the enemy is | `damage-bonus-to-near`, `damage-bonus-to-far` |
| `fortified` | while the character is Fortified | `damage-percent-bonus-when-fortified` |
| `while-healthy` | while the character is at high life | `damage-bonus-at-high-health` |
| `vs-healthy` · `vs-injured` · `vs-weakened` | by the enemy's state | `damage-bonus-to-high-health`, `damage-bonus-to-low-health`, `damage-bonus-percent-to-weakened` |
| `on-weapon-swap` | just after swapping weapons | `damage-percent-bonus-when-weapon-swapping` |
| `skill:<tag>` | one category of skills — traps, shouts, companions | `damage-percent-bonus-per-skill-tag` |
| `× <the thing it came from>` | a standalone `[x]` multiplier | the `multiplicative-*` family |

A `[x]` multiplier stands on its own rather than joining a bucket, so its
bucket is named after the thing it came from and it multiplies against every
other. ⚠ Two standalone multipliers on one item would share that name and be
summed rather than multiplied; no record in the 3.2.1 pack carries two, so
nothing is wrong today, but a pack that grows one wants the bucket keyed by
stat as well.

⚠ Critical strike damage does not join the damage buckets. It is a row a
person reads, and folding it into the damage product would assume every hit
crits. The additive crit lines go to `critical-damage`; only a `[x]` crit
multiplier is a damage bucket.

⚠ Damage reduction is summed and marked APPROXIMATE. Diablo IV multiplies
its reductions together — two 20% sources leave 64% of the hit, not 60% — so
the row is an upper bound and the breakdown shows the parts a person can
multiply for themselves.

⚠ `Bucketed_Multiplicative_Damage_Type_FireHoly` is one affix over two
elements and the vocabulary has no holy. It counts against fire and is marked
APPROXIMATE, because half of what it grants has nowhere honest to go.

## What `base_for` can and cannot give

**It gives** the five resistance caps at 70% — raised on the same row by any
source that raises them — and 100 for each damage row the plan has lines for,
so a damage total reads as a percentage of what the character would do with
none of this. It also clamps the plan's level to the cap the pack states.

**It cannot give the base life or the starting attributes, because the pack
does not have them.** A Diablo IV class record
(`d.get("diablo-iv", "class", "sorcerer")`) carries `resource`, `resources`,
`mechanic_summary`, `specializations`, `notes` and `source` — and no life
table, no per-level growth, no starting attributes. A search of every record
in the pack for `base_life`, `starting_life`, `starting_attributes`,
`base_hitpoints` or `life_per` returns one hit, and it is an affix id. So
life and the four attributes start at nothing and the panel shows exactly
what a person's choices grant, which is a smaller number than their character
sheet and an honest one. Inventing a starting life would put a made-up number
under a real one. The moment the pack grows `starting_life` and `per_level`,
`base_for` is where they go — the Diablo II module already does it that way.

The resistance cap of 70% is not in the pack either; it is stated in
`BASE` as the game's rule, with the affixes that raise it adding to the same
row.

**What the pack does record**, and `base_for` reads: `progression/levels`
gives `cap: 70` (with the history 100 → 60 → 70 across patches 1.0, 2.0 and
3.0), and `progression/paragon` gives a separate budget of 342 points — 300
from paragon levels plus 42 from Season 15's season rank — unlocking at
character level 70, across 5 equipped boards of 10 per class.

## Two notes for whoever wires this up

- `calc/collect.py` reaches an affix's `stats`, `tiers`, a unique's
  `affixes`, a gem's `bonuses`, a runeword's and a set's `stats` and an item
  base's `implicit`. It does **not** reach an aspect's `values`, a charm's
  `fixed_affixes`, or a glyph's `bonus_attributes`, because those field names
  are not in its list. `map_line` handles all of them correctly when it is
  handed one; nothing in this module needs changing when `collect` grows the
  names.
- Six canonical stats were added to `vocabulary.py` for this pack:
  `resource` (Diablo IV names its resource per class, so `mana` would
  mislabel six of eight), `dodge-chance` (a character has dodge AND block,
  and dodge is a chance rather than a rating), `resistance-shadow` with its
  cap and `damage-shadow` (shadow is the fifth element and is neither chaos
  nor magic), and `lucky-hit` (nothing else names Lucky Hit Chance).
