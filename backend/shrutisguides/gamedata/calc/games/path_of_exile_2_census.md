# Path of Exile 2 — the stat census

Measured from the built pack on 2026-09-21 by running every stat line the
planner would see through `path_of_exile_2.map_line`. Nothing here is
claimed; the table is generated from the mapper, so it says what the code
actually does.

## What there is

- **12,512 stat lines** across the kinds the planner counts, in **3,162 distinct normalised templates**.
- **6,879 lines are counted** (55.0%); the rest are kept, listed against the stat they
  talk about, and left out of the arithmetic.
- Lines by kind: affix 1,913, unique 3,009, node 6,058, rune 664, charm 39, flask 72, base 757.
- `jewel` contributes **0** lines: a jewel record holds a `can_roll` catalogue of what it
  *could* roll, and the plan picks the jewel rather than the roll, so there is nothing
  on it that a person has actually chosen.

### Counted by kind

| kind | lines | counted |
| --- | ---: | ---: |
| affix | 1,913 | 1,069 (56%) |
| unique | 3,009 | 1,168 (39%) |
| node | 6,058 | 4,000 (66%) |
| rune | 664 | 374 (56%) |
| charm | 39 | 0 (0%) |
| flask | 72 | 0 (0%) |
| base | 757 | 268 (35%) |

⚠ `unique` is the lowest of the four big kinds and that is the mapping working, not failing:
a unique body armour's `(700-800)% increased Armour` multiplies that body armour and is now
held back rather than counted into the character's pool. See **Whose number is it** below.

## What the character starts with, and what the pack does not say

`base_for` gives only what the pack records, which is less than it looks:

- **Starting attributes** are there — the Witch is strength 7, dexterity 7, intelligence 15 — and
  are used as the base of those three rows.
- **Base life and base mana are NOT recorded.** The class record holds `starting_attributes`,
  a mechanic summary, the tree position and the ascendancies, and nothing else: no starting
  life, no life per level, no mana per level. So no life base is set and a life total is the
  sum of what the plan adds. `base_for` reads `starting_life`, `starting_mana`, `per_level` and
  `starting_spirit` if the pack ever grows them, and invents nothing in the meantime.
- **Base spirit is not recorded either**, so the spirit row is what the plan adds. Spirit is a
  budget rather than a number that scales, and the planner spends it on what a build keeps
  running; the row is here so a person can see how much they have bought.
- **The resistance caps are set to 75%** for fire, cold, lightning and chaos, which is the
  game's own maximum, and lines that raise a cap go into their own row against it.
- **The campaign's resistance penalty is NOT in the pack.** The `progression` records hold the
  level cap, passive points, the acts and their level ranges, the endgame and the crafting
  systems — the only penalty any of them names is the experience loss on death. So no
  penalty is applied. A resistance total here is what the gear and the tree give, before
  whatever the campaign takes off; that is a real gap and it is not guessed at.
- **The level cap is 100**, read from `progression/levels.cap` rather than written in, and a
  plan asking for more is held to it.
- **An item's own armour, evasion and energy shield never reach the pool.** A base record keeps
  them as numbers under `stats` (`{"armour": {"armour": 115}}`) rather than as stat lines, and
  the collector walks lines. So those three rows are what the plan ADDS to a defence, not the
  defence.

Six stats are therefore declared in `INCOMPLETE_BASE` — life, mana, spirit, armour, evasion,
energy shield — so the panel marks each row approximate and gives the reason, rather than
showing a confident number with its largest term missing.

## How a line is read

Lowercase the sentence, collapse every number and every `{value}` and `#` to one `#`, drop the
punctuation that carries no meaning — `+`, `-` and `%` stay, because they are the difference
between an addition and a percentage. Then match the shape against an ordered list of
anchored patterns, the specific before the general. `increased` and `reduced` are both the
increased form and `reduced` is negative; `more` and `less` are both the more form and `less`
is negative; `faster` and `slower` are one entry the same way. An increase is passed as the
percentage written, because the pool already does `(base + added) × (1 + Σ increased) × each
more`, and each `more` gets a bucket of its own so they multiply against one another rather
than adding.

**One entry, a whole family.** Where the game says the same sentence with one word changed,
the pattern captures the word and the word names the row. That is how a few dozen entries
cover some hundreds of templates:

- a **status** and its four numbers — `#% increased Freeze Buildup`, `#% increased Withered
  Magnitude`, `#% increased Armour Break Duration`, `#% increased chance to Shock` — and the
  other side of each, what lands on this character (`#% reduced Poison Duration on you`);
- a **weapon** a bracket is scoped to — `Attack Speed with Bows`, `Critical Hit Chance with
  Daggers`, `Freeze Buildup with Quarterstaves` — each its own row, because this game never
  adds a scoped bracket to the global one;
- a **family of skills** — `Banner Skills have #% increased Area of Effect`, `Herald Skills
  deal #% increased Damage`, `#% increased Reservation Efficiency of Minion Skills`;
- **what a build fields** — minions, companions, totems, offerings, ballistas and the allies
  in a character's presence, all said the same way and each keeping rows of its own;
- an **element** — `#% of Physical Damage taken recouped as Life` is five sentences in one.

⚠ A wildcard is guarded. A sentence that goes on to state a condition (`while`, `if`, `per`,
`recently`, `against`) or to narrow the stat (`with Critical Hits`, `from equipped Shield`) is
refused, because the number is not the one the row is for. `#% increased Magnitude of Bleeding
you inflict` is bleeding magnitude; `…you inflict with Critical Hits` is not, and counting it
as though it were would credit a character with a bonus it has on some of its hits only.

## What is held back, and why

Three things are held back on purpose even though the wording matched:

- **A roll from a patch that has gone.** The pack keeps a unique's old rolls tagged `Pre 0.2.0`
  and the live one tagged `Current`; a line without `Current` is a fact about a past patch.
- **A version a plan has not chosen.** An item with several versions (Atziri's Splendour has
  an armour, an evasion and an energy-shield one) has all of them in the pack.
- **An increase that belongs to the item** — see below.

### Whose number is it

`350% increased Physical Damage` on a sword multiplies that sword and nothing else; summed
into the character's bracket it would state a number nobody has. The first pass could only
half-solve this and said so. It is solved now, from the pack and never from a hunch:

- a **rune** marks its own effects `local`;
- an **affix** carries the word in its id AND the game's own mod group beside it —
  `LocalPhysicalDamagePercent`, `LocalEvasionRating`, `LocalStunDuration`. The group catches
  27 affixes the id alone does not, the hybrid defence-and-spirit rolls among them, so both
  are read. `collect.chosen` carries the record's `group` and `type` on the source for this.
- a **unique** or a **base** says nothing either way, so **what the item is** decides. The pack
  records an item's type, and its base records say what a type carries: six types keep an
  `armour` block of their own (body armour, boots, focus, gloves, helmet, shield) and
  nineteen are held in a hand with damage of their own. So an increase to armour, evasion or
  energy shield written on a body armour is that body armour's, and the same sentence on
  **The Anvil**, which is an amulet, is the character's and is counted.

241 lines moved from counted to held by that last rule — every one of them a unique's or a
base's own defence, damage, attack speed, block chance, spirit or stun buildup. Coverage went
down and the numbers went right.

⚠ A **flat** line is never asked the question. `+40 to Evasion Rating` on a pair of boots adds
forty evasion to the boots, and the boots are on the character, so it reaches the pool either
way. Only `increased` and `more` are held.

## The templates the mapper claims

**650 templates, 7,590 lines, 60.7% of everything.** `stat` is the
canonical name it feeds (several means the line splits); `counted` is how many of those lines
actually reached the arithmetic, and where it is short of `lines` the last column says why in
our own words — so `133 lines, 130 counted, 3 of them: it is a roll from a patch that has been
replaced` is a template that maps cleanly with three old rolls sitting beside it in the pack.
Templates seen once are left out of this table; the tail below has the count.

| normalised template | lines | counted | stat | form | what is held back, and why |
| --- | ---: | ---: | --- | --- | --- |
| `#% increased mana regeneration rate` | 133 | 130 | mana-regeneration | increased | 3 of them: it is a roll from a patch that has been replaced |
| `#% increased evasion rating` | 124 | 85 | evasion | increased | 39 of them: it multiplies this body-armour's own number, not the character's |
| `#% increased armour` | 122 | 79 | armour | increased | 43 of them: it is a roll from a patch that has been replaced |
| `#% increased attack speed` | 114 | 84 | speed-attack | increased | 30 of them: it multiplies this one-hand-mace's own number, not the character's |
| `+# to strength` | 113 | 109 | strength | flat | 4 of them: it is a roll from a patch that has been replaced |
| `+# to dexterity` | 103 | 99 | dexterity | flat | 4 of them: it is a roll from a patch that has been replaced |
| `#% increased physical damage` | 96 | 59 | damage-physical | increased | 37 of them: it is a roll from a patch that has been replaced |
| `+# to intelligence` | 95 | 92 | intelligence | flat | 3 of them: it is a roll from a patch that has been replaced |
| `#% faster start of energy shield recharge` | 87 | 83 | energy-shield-recharge-delay | increased | 4 of them: it is a roll from a patch that has been replaced |
| `#% increased movement speed` | 86 | 79 | speed-movement | increased | 7 of them: it is a roll from a patch that has been replaced |
| `+# to maximum life` | 84 | 77 | life | flat | 7 of them: it is a roll from a patch that has been replaced |
| `#% increased block chance` | 83 | 59 | block | increased | 24 of them: it is a roll from a patch that has been replaced |
| `#% increased attack damage` | 82 | 82 | damage-attack | increased |  |
| `#% increased maximum energy shield` | 81 | 79 | energy-shield | increased | 2 of them: the item has several versions and the plan does not record which one |
| `+# to maximum mana` | 81 | 75 | mana | flat | 6 of them: it is a roll from a patch that has been replaced |
| `#% increased critical hit chance` | 79 | 72 | critical-chance | increased | 7 of them: it is a roll from a patch that has been replaced |
| `#% increased spell damage` | 75 | 73 | damage-spell | increased | 2 of them: it is a roll from a patch that has been replaced |
| `#% increased stun threshold` | 66 | 64 | stun-threshold | increased | 2 of them: it is a roll from a patch that has been replaced |
| `minions deal #% increased damage` | 64 | 64 | damage-minion | increased |  |
| `#% increased cast speed` | 62 | 61 | speed-cast | increased | 1 of them: the item has several versions and the plan does not record which one |
| `+#% to fire resistance` | 61 | 52 | resistance-fire | flat | 9 of them: it is a roll from a patch that has been replaced |
| `+#% to lightning resistance` | 61 | 53 | resistance-lightning | flat | 8 of them: it is a roll from a patch that has been replaced |
| `#% increased accuracy rating` | 60 | 60 | attack-rating | increased |  |
| `#% increased elemental damage` | 60 | 59 | damage-fire + damage-cold + damage-lightning | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased stun buildup` | 60 | 58 | stun-buildup | increased | 2 of them: it is a roll from a patch that has been replaced |
| `+#% to cold resistance` | 60 | 55 | resistance-cold | flat | 5 of them: it is a roll from a patch that has been replaced |
| `#% increased freeze buildup` | 59 | 58 | freeze-buildup | increased | 1 of them: it is a roll from a patch that has been replaced |
| `#% increased lightning damage` | 59 | 58 | damage-lightning | increased | 1 of them: it is a roll from a patch that has been replaced |
| `#% increased area of effect for attacks` | 56 | 55 | attack-area-of-effect | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased fire damage` | 56 | 56 | damage-fire | increased |  |
| `+#% to chaos resistance` | 56 | 55 | resistance-chaos | flat | 1 of them: it is a roll from a patch that has been replaced |
| `#% increased skill effect duration` | 53 | 50 | skill-effect-duration | increased | 3 of them: the item has several versions and the plan does not record which one |
| `#% increased flammability magnitude` | 52 | 52 | flammability-magnitude | increased |  |
| `#% increased chaos damage` | 51 | 49 | damage-chaos | increased | 2 of them: the item has several versions and the plan does not record which one |
| `#% increased critical damage bonus` | 50 | 47 | critical-damage | increased | 3 of them: the item has several versions and the plan does not record which one |
| `#% reduced slowing potency of debuffs on you` | 49 | 46 | slow-potency-on-you | increased | 3 of them: the item has several versions and the plan does not record which one |
| `+#% of armour also applies to elemental damage` | 49 | 46 | armour-applies-to-elemental-damage | flat | 3 of them: the item has several versions and the plan does not record which one |
| `+# to all attributes` | 47 | 46 | strength + dexterity + intelligence | flat | 1 of them: it is a roll from a patch that has been replaced |
| `#% increased cold damage` | 46 | 45 | damage-cold | increased | 1 of them: it is a roll from a patch that has been replaced |
| `+#% to all elemental resistances` | 45 | 44 | resistance-fire + resistance-cold + resistance-lightning | flat | 1 of them: it is a roll from a patch that has been replaced |
| `#% increased rarity of items found` | 44 | 38 | magic-find | increased | 6 of them: it is a roll from a patch that has been replaced |
| `#% increased presence area of effect` | 43 | 43 | presence-area-of-effect | increased |  |
| `+# to maximum energy shield` | 43 | 42 | energy-shield | flat | 1 of them: it is a roll from a patch that has been replaced |
| `has # charm slot` | 43 | 43 | charm-slots | flat |  |
| `#% increased projectile damage` | 42 | 42 | projectile-damage | increased |  |
| `minions have #% increased maximum life` | 41 | 41 | life-minion | increased |  |
| `#% of damage taken recouped as life` | 40 | 38 | damage-recouped-as-life | flat | 2 of them: it is a roll from a patch that has been replaced |
| `#% increased critical hit chance for spells` | 39 | 38 | spell-critical-chance | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased life regeneration rate` | 39 | 38 | life-regeneration | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased armour and evasion` | 37 | 0 | armour + evasion | increased | it multiplies this body-armour's own number, not the character's |
| `#% increased armour and evasion rating` | 37 | 37 | armour + evasion | increased |  |
| `+# to accuracy rating` | 37 | 36 | attack-rating | flat | 1 of them: it is a roll from a patch that has been replaced |
| `#% increased cooldown recovery rate` | 36 | 34 | cooldown-reduction | increased | 2 of them: the item has several versions and the plan does not record which one |
| `#% increased chance to shock` | 35 | 35 | shock-chance | increased |  |
| `adds # to # physical damage` | 35 | 28 | damage-physical | flat | 7 of them: it is a roll from a patch that has been replaced |
| `#% increased elemental ailment threshold` | 34 | 33 | elemental-ailment-threshold | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased skill speed` | 33 | 32 | speed-skill | increased | 1 of them: the item has several versions and the plan does not record which one |
| `+# to spirit` | 33 | 31 | spirit | flat | 2 of them: it is a roll from a patch that has been replaced |
| `#% increased area of effect` | 32 | 32 | area-of-effect | increased |  |
| `damage penetrates #% lightning resistance` | 32 | 32 | penetration-lightning | flat |  |
| `# life regeneration per second` | 31 | 30 | life-regeneration | flat | 1 of them: it is a roll from a patch that has been replaced |
| `#% increased melee damage` | 31 | 31 | melee-damage | increased |  |
| `#% of damage is taken from mana before life` | 31 | 27 | damage-taken-from-mana | flat | 4 of them: the item has several versions and the plan does not record which one |
| `#% increased armour and energy shield` | 30 | 0 | armour + energy-shield | increased | it multiplies this body-armour's own number, not the character's |
| `#% increased amount of life leeched` | 29 | 28 | life-leech | increased | 1 of them: it is a roll from a patch that has been replaced |
| `#% increased energy shield` | 29 | 0 | energy-shield | increased | it multiplies this body-armour's own number, not the character's |
| `#% increased life recovery from flasks` | 29 | 29 | flask-life-recovery | increased |  |
| `#% increased ignite magnitude` | 28 | 26 | ignite-magnitude | increased | 2 of them: it is a roll from a patch that has been replaced |
| `#% chance to daze on hit` | 27 | 27 | daze-chance | flat |  |
| `#% chance to inflict bleeding on hit` | 27 | 24 | bleed-chance | flat | 3 of them: the item has several versions and the plan does not record which one |
| `#% increased maximum life` | 27 | 25 | life | increased | 2 of them: the item has several versions and the plan does not record which one |
| `break #% increased armour` | 27 | 27 | armour-break | increased |  |
| `#% increased curse magnitudes` | 26 | 26 | curse-magnitude | increased |  |
| `#% increased energy shield recharge rate` | 26 | 26 | energy-shield-recharge | increased |  |
| `+# to armour` | 26 | 23 | armour | flat | 3 of them: it is a roll from a patch that has been replaced |
| `+# to stun threshold` | 26 | 24 | stun-threshold | flat | 2 of them: it is a roll from a patch that has been replaced |
| `regenerate #% of maximum life per second` | 26 | 26 | life-regeneration-percent | flat |  |
| `#% increased chance to inflict ailments` | 25 | 24 | ailment-chance | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased magnitude of shock you inflict` | 25 | 24 | shock-magnitude | increased | 1 of them: the item has several versions and the plan does not record which one |
| `damage penetrates #% cold resistance` | 25 | 25 | penetration-cold | flat |  |
| `damage penetrates #% fire resistance` | 25 | 25 | penetration-fire | flat |  |
| `#% increased attack area damage` | 23 | 23 | attack-area-damage | increased |  |
| `#% increased critical hit chance for attacks` | 23 | 23 | attack-critical-chance | increased |  |
| `#% increased flask charges gained` | 23 | 20 | flask-charges-gained | increased | 3 of them: the item has several versions and the plan does not record which one |
| `#% increased magnitude of poison you inflict` | 23 | 23 | poison-magnitude | increased |  |
| `+# to evasion rating` | 23 | 22 | evasion | flat | 1 of them: it is a roll from a patch that has been replaced |
| `adds # to # physical damage to attacks` | 23 | 20 | damage-physical | flat | 3 of them: it is a roll from a patch that has been replaced |
| `gain #% of damage as extra cold damage` | 23 | 19 | extra-cold-damage | flat | 4 of them: the item has several versions and the plan does not record which one |
| `#% chance to poison on hit` | 22 | 19 | poison-chance | flat | 3 of them: it is a roll from a patch that has been replaced |
| `#% increased evasion and energy shield` | 22 | 0 | evasion + energy-shield | increased | it multiplies this body-armour's own number, not the character's |
| `#% increased projectile speed` | 22 | 22 | projectile-speed | increased |  |
| `#% reduced movement speed penalty from using skills while moving` | 22 | 21 | skill-movement-speed-penalty | increased | 1 of them: the item has several versions and the plan does not record which one |
| `+# to maximum rage` | 22 | 22 | maximum-rage | flat |  |
| `adds # to # lightning damage` | 22 | 17 | damage-lightning | flat | 5 of them: it is a roll from a patch that has been replaced |
| `#% chance to pierce an enemy` | 21 | 20 | pierce-chance | flat | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased totem damage` | 21 | 21 | totem-damage | increased |  |
| `+# to maximum runic ward` | 21 | 21 | maximum-runic-ward | flat |  |
| `companions deal #% increased damage` | 21 | 21 | companion-damage | increased |  |
| `gain #% of damage as extra fire damage` | 21 | 18 | extra-fire-damage | flat | 3 of them: the item has several versions and the plan does not record which one |
| `#% increased critical spell damage bonus` | 20 | 18 | spell-critical-damage | increased | 2 of them: it is a roll from a patch that has been replaced |
| `#% increased damage` | 20 | 20 | damage | increased |  |
| `#% increased mana cost efficiency` | 20 | 19 | resource-cost-reduction | increased | 1 of them: the item has several versions and the plan does not record which one |
| `adds # to # fire damage` | 20 | 18 | damage-fire | flat | 2 of them: it is a roll from a patch that has been replaced |
| `gain #% of damage as extra lightning damage` | 20 | 17 | extra-lightning-damage | flat | 3 of them: the item has several versions and the plan does not record which one |
| `meta skills gain #% increased energy` | 20 | 19 | meta-skill-energy | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased armour evasion and energy shield` | 19 | 3 | armour + evasion + energy-shield | increased | 16 of them: it is a roll from a patch that has been replaced |
| `#% increased elemental damage with attacks` | 19 | 19 | attack-elemental-damage | increased |  |
| `#% increased light radius` | 19 | 19 | light-radius | increased |  |
| `#% increased totem placement speed` | 19 | 19 | totem-placement-speed | increased |  |
| `#% increased warcry speed` | 19 | 19 | warcry-speed | increased |  |
| `companions have #% increased maximum life` | 19 | 19 | companion-life | increased |  |
| `empowered attacks deal #% increased damage` | 19 | 19 | empowered-damage | increased |  |
| `gain #% of damage as extra chaos damage` | 19 | 16 | extra-chaos-damage | flat | 3 of them: the item has several versions and the plan does not record which one |
| `remnants can be collected from #% further away` | 19 | 19 | remnant-collection-range | increased |  |
| `#% increased amount of mana leeched` | 18 | 18 | mana-leech | increased |  |
| `#% increased maximum mana` | 18 | 14 | mana | increased | 4 of them: it is a roll from a patch that has been replaced |
| `adds # to # cold damage` | 18 | 14 | damage-cold | flat | 4 of them: it is a roll from a patch that has been replaced |
| `aura skills have #% increased magnitudes` | 18 | 18 | aura-magnitude | increased |  |
| `hits against you have #% reduced critical damage bonus` | 18 | 17 | critical-damage-against-you | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased exposure effect` | 17 | 16 | exposure-magnitude | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased warcry cooldown recovery rate` | 17 | 17 | warcry-cooldown-recovery | increased |  |
| `+#% to maximum cold resistance` | 17 | 10 | resistance-cold-max | flat | 7 of them: the item has several versions and the plan does not record which one |
| `debuffs you inflict have #% increased slow magnitude` | 17 | 15 | slow-magnitude | increased | 2 of them: the item has several versions and the plan does not record which one |
| `#% increased charm charges gained` | 16 | 16 | charm-charges-gained | increased |  |
| `#% increased glory generation` | 16 | 16 | glory-generation | increased |  |
| `#% increased magnitude of bleeding you inflict` | 16 | 16 | bleeding-magnitude | increased |  |
| `#% increased magnitude of chill you inflict` | 16 | 15 | chill-magnitude | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased mana recovery from flasks` | 16 | 16 | flask-mana-recovery | increased |  |
| `causes #% increased stun buildup` | 16 | 1 | stun-buildup | increased | 15 of them: it multiplies this two-hand-mace's own number, not the character's |
| `#% increased damage with two handed weapons` | 15 | 15 | damage-with-two-handed-weapons | increased |  |
| `#% increased thorns damage` | 15 | 15 | thorns-damage | increased |  |
| `#% reduced effect of curses on you` | 15 | 15 | curses-effect-on-you | increased |  |
| `+#% to all maximum elemental resistances` | 15 | 13 | resistance-fire-max + resistance-cold-max + resistance-lightning-max | flat | 2 of them: it is a roll from a patch that has been replaced |
| `+#% to critical hit chance` | 15 | 13 | critical-chance | flat | 2 of them: it is a roll from a patch that has been replaced |
| `+#% to maximum lightning resistance` | 15 | 8 | resistance-lightning-max | flat | 7 of them: the item has several versions and the plan does not record which one |
| `debuffs on you expire #% faster` | 15 | 14 | debuff-expiry-speed | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased archon buff duration` | 14 | 14 | archon-buff-duration | increased |  |
| `#% increased effect of fully broken armour` | 14 | 14 | fully-broken-armour-effect | increased |  |
| `#% increased parried debuff magnitude` | 14 | 14 | parried-debuff-magnitude | increased |  |
| `#% increased pin buildup` | 14 | 14 | pin-buildup | increased |  |
| `#% reduced attack speed` | 14 | 7 | speed-attack | increased | 7 of them: it multiplies this two-hand-mace's own number, not the character's |
| `+#% to critical damage bonus` | 14 | 11 | critical-damage | flat | 3 of them: the item has several versions and the plan does not record which one |
| `+#% to maximum fire resistance` | 14 | 7 | resistance-fire-max | flat | 7 of them: the item has several versions and the plan does not record which one |
| `spell skills have #% increased area of effect` | 14 | 13 | spell-area-of-effect | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased curse duration` | 13 | 13 | curse-duration | increased |  |
| `#% increased duration of damaging ailments on enemies` | 13 | 13 | damaging-ailments-duration | increased |  |
| `#% increased effect of arcane surge on you` | 13 | 13 | arcane-surge-effect-on-you | increased |  |
| `#% increased effect of your mark skills` | 13 | 13 | mark-effect | increased |  |
| `#% increased immobilisation buildup` | 13 | 13 | immobilisation-buildup | increased |  |
| `#% increased magnitude of ailments you inflict` | 13 | 13 | ailments-magnitude | increased |  |
| `#% increased poison duration` | 13 | 13 | poison-duration | increased |  |
| `#% increased speed of recoup effects` | 13 | 12 | recoup-speed | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased totem life` | 13 | 13 | totem-life | increased |  |
| `minions revive #% faster` | 13 | 11 | minion-revive-speed | increased | 2 of them: the item has several versions and the plan does not record which one |
| `# to # physical thorns damage` | 12 | 12 | thorns-damage | flat |  |
| `#% increased area of effect of curses` | 12 | 11 | curse-area-of-effect | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased damage with swords` | 12 | 12 | damage-with-swords | increased |  |
| `#% increased knockback distance` | 12 | 12 | knockback-distance | increased |  |
| `#% increased life and mana recovery from flasks` | 12 | 12 | flask-life-recovery + flask-mana-recovery | increased |  |
| `+#% to block chance` | 12 | 12 | block | flat |  |
| `adds # to # chaos damage` | 12 | 11 | damage-chaos | flat | 1 of them: it is a roll from a patch that has been replaced |
| `minions have #% increased attack and cast speed` | 12 | 11 | minion-attack-speed + minion-cast-speed | increased | 1 of them: the item has several versions and the plan does not record which one |
| `triggered spells deal #% increased spell damage` | 12 | 11 | triggered-damage | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased chill duration on enemies` | 11 | 10 | chill-duration | increased | 1 of them: it is a roll from a patch that has been replaced |
| `#% increased damage with one handed weapons` | 11 | 11 | damage-with-one-handed-weapons | increased |  |
| `#% increased electrocute buildup` | 11 | 11 | electrocute-buildup | increased |  |
| `#% increased freeze threshold` | 11 | 11 | freeze-threshold | increased |  |
| `#% increased strength` | 11 | 8 | strength | increased | 3 of them: the item has several versions and the plan does not record which one |
| `#% of damage taken recouped as mana` | 11 | 11 | damage-recouped-as-mana | flat |  |
| `+# to level of all spell skills` | 11 | 11 | skills-tab | flat |  |
| `leeches #% of physical damage as life` | 11 | 10 | life-leech | flat | 1 of them: it is a roll from a patch that has been replaced |
| `minions have +#% to all elemental resistances` | 11 | 10 | minion-fire-resistance + minion-cold-resistance + minion-lightning-resistance | flat | 1 of them: the item has several versions and the plan does not record which one |
| `minions have +#% to chaos resistance` | 11 | 11 | minion-chaos-resistance | flat |  |
| `#% increased bleeding duration` | 10 | 10 | bleeding-duration | increased |  |
| `#% increased critical damage bonus for attack damage` | 10 | 10 | attack-critical-damage | increased |  |
| `#% increased damage with plant skills` | 10 | 10 | damage-with-plant-skills | increased |  |
| `#% increased effect of archon buffs on you` | 10 | 10 | archon-buffs-effect-on-you | increased |  |
| `#% increased flask effect duration` | 10 | 9 | flask-effect-duration | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased frenzy charge duration` | 10 | 10 | frenzy-charge-duration | increased |  |
| `#% increased hazard damage` | 10 | 10 | hazard-damage | increased |  |
| `#% increased parried debuff duration` | 10 | 10 | parried-debuff-duration | increased |  |
| `#% increased spirit` | 10 | 4 | spirit | increased | 6 of them: the pack's own mod group says it multiplies the item, not the character |
| `#% increased stun recovery` | 10 | 10 | stun-recovery | increased |  |
| `#% reduced presence area of effect` | 10 | 10 | presence-area-of-effect | increased |  |
| `+# to level of all lightning skills` | 10 | 2 | skills-tab | flat | 8 of them: the item has several versions and the plan does not record which one |
| `allies in your presence deal #% increased damage` | 10 | 10 | ally-damage | increased |  |
| `minions have #% increased critical hit chance` | 10 | 9 | minion-critical-chance | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased charm effect duration` | 9 | 9 | charm-effect-duration | increased |  |
| `#% increased crossbow reload speed` | 9 | 9 | reload-speed | increased |  |
| `#% increased damage with bows` | 9 | 9 | damage-with-bows | increased |  |
| `#% increased deflection rating` | 9 | 9 | deflection | increased |  |
| `#% increased life cost of skills` | 9 | 9 | life-cost-of-skills | increased |  |
| `#% increased life flask charges gained` | 9 | 9 | flask-charges-gained | increased |  |
| `#% increased minion duration` | 9 | 9 | minion-duration | increased |  |
| `#% increased reservation efficiency of herald skills` | 9 | 9 | herald-reservation-efficiency | increased |  |
| `#% increased runic ward regeneration rate` | 9 | 9 | runic-ward-regeneration | increased |  |
| `#% increased spirit reservation efficiency` | 9 | 5 | spirit-reservation-efficiency | increased | 4 of them: the item has several versions and the plan does not record which one |
| `#% reduced effect of chill on you` | 9 | 9 | chill-effect-on-you | increased |  |
| `#% reduced effect of shock on you` | 9 | 9 | shock-effect-on-you | increased |  |
| `#% reduced magnitude of ignite on you` | 9 | 9 | ignite-magnitude-on-you | increased |  |
| `#% reduced skill effect duration` | 9 | 9 | skill-effect-duration | increased |  |
| `+# to level of all cold skills` | 9 | 3 | skills-tab | flat | 6 of them: the item has several versions and the plan does not record which one |
| `+# to maximum power charges` | 9 | 8 | maximum-power-charges | flat | 1 of them: the item has several versions and the plan does not record which one |
| `+#% of armour also applies to lightning damage` | 9 | 9 | armour-applies-to-lightning-damage | flat |  |
| `attacks used by totems have #% increased attack speed` | 9 | 9 | totem-attack-speed | increased |  |
| `minions deal #% increased damage with command skills` | 9 | 9 | minion-command-skill-damage | increased |  |
| `minions have #% increased area of effect` | 9 | 9 | minion-area-of-effect | increased |  |
| `spells cast by totems have #% increased cast speed` | 9 | 9 | totem-cast-speed | increased |  |
| `#% chance to blind enemies on hit` | 8 | 8 | blind-chance | flat |  |
| `#% chance to blind enemies on hit with attacks` | 8 | 8 | blind-chance | flat |  |
| `#% faster curse activation` | 8 | 7 | curse-activation-speed | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased attack speed with bows` | 8 | 8 | attack-speed-with-bows | increased |  |
| `#% increased blind effect` | 8 | 8 | blind-magnitude | increased |  |
| `#% increased bolt speed` | 8 | 8 | bolt-speed | increased |  |
| `#% increased culling strike threshold` | 8 | 7 | culling-strike-threshold | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased damage with flails` | 8 | 8 | damage-with-flails | increased |  |
| `#% increased elemental infusion duration` | 8 | 8 | elemental-infusion-duration | increased |  |
| `#% increased flask life recovery rate` | 8 | 8 | flask-life-recovery | increased |  |
| `#% increased glory generation for banner skills` | 8 | 8 | banner-glory-generation | increased |  |
| `#% increased intelligence` | 8 | 5 | intelligence | increased | 3 of them: the item has several versions and the plan does not record which one |
| `#% increased power charge duration` | 8 | 8 | power-charge-duration | increased |  |
| `#% increased shock duration` | 8 | 8 | shock-duration | increased |  |
| `#% increased trap damage` | 8 | 8 | trap-damage | increased |  |
| `#% increased withered magnitude` | 8 | 8 | withered-magnitude | increased |  |
| `#% reduced charm charges used` | 8 | 8 | charm-charges-used | increased |  |
| `#% reduced light radius` | 8 | 8 | light-radius | increased |  |
| `#% reduced maximum mana` | 8 | 8 | mana | increased |  |
| `+# charm slot` | 8 | 5 | charm-slots | flat | 3 of them: it is a roll from a patch that has been replaced |
| `+# to level of all corrupted skill gems` | 8 | 8 | skills-tab | flat |  |
| `+# to level of all minion skills` | 8 | 7 | skills-tab | flat | 1 of them: it is a roll from a patch that has been replaced |
| `+#% of armour also applies to cold damage` | 8 | 8 | armour-applies-to-cold-damage | flat |  |
| `+#% of armour also applies to fire damage` | 8 | 8 | armour-applies-to-fire-damage | flat |  |
| `+#% to maximum block chance` | 8 | 7 | block | flat | 1 of them: it is a roll from a patch that has been replaced |
| `adds # to # lightning damage to attacks` | 8 | 4 | damage-lightning | flat | 4 of them: the pack records the wording but no number for it |
| `banner skills have #% increased area of effect` | 8 | 8 | banner-area-of-effect | increased |  |
| `channelling skills deal #% increased damage` | 8 | 8 | channelling-damage | increased |  |
| `damaging ailments deal damage #% faster` | 8 | 7 | damaging-ailments-damage-speed | increased | 1 of them: the item has several versions and the plan does not record which one |
| `equipment and skill gems have #% reduced attribute requirements` | 8 | 7 | attribute-requirements | increased | 1 of them: it is a roll from a patch that has been replaced |
| `has # sockets` | 8 | 8 | sockets | flat |  |
| `herald skills deal #% increased damage` | 8 | 8 | herald-damage | increased |  |
| `leeches #% of physical damage as mana` | 8 | 8 | mana-leech | flat |  |
| `mark skills have #% increased use speed` | 8 | 8 | mark-use-speed | increased |  |
| `minions have #% additional physical damage reduction` | 8 | 7 | minion-physical-damage-reduction | flat | 1 of them: the item has several versions and the plan does not record which one |
| `minions have #% increased cooldown recovery rate for command skills` | 8 | 8 | minion-command-skill-cooldown-recovery-rate | increased |  |
| `prevent +#% of damage from deflected hits` | 8 | 8 | deflected-damage-prevented | flat |  |
| `#% chance to maim on hit` | 7 | 7 | maim-chance | flat |  |
| `#% increased armour break duration` | 7 | 7 | armour-break-duration | increased |  |
| `#% increased damage with spears` | 7 | 7 | damage-with-spears | increased |  |
| `#% increased dexterity` | 7 | 5 | dexterity | increased | 2 of them: the item has several versions and the plan does not record which one |
| `#% increased grenade damage` | 7 | 7 | grenade-damage | increased |  |
| `#% increased ignite duration on enemies` | 7 | 6 | ignite-duration | increased | 1 of them: it is a roll from a patch that has been replaced |
| `#% increased spell area damage` | 7 | 7 | spell-area-damage | increased |  |
| `#% more global evasion rating and energy shield` | 7 | 0 | evasion + energy-shield | more | the pack's own mod group says it multiplies the item, not the character |
| `#% of damage taken recouped as life mana and energy shield` | 7 | 7 | damage-recouped-as-life + damage-recouped-as-mana + damage-recouped-as-energy-shield | flat |  |
| `#% reduced duration of bleeding on you` | 7 | 7 | bleeding-duration-on-you | increased |  |
| `+# to level of all fire skills` | 7 | 1 | skills-tab | flat | 6 of them: the item has several versions and the plan does not record which one |
| `+# to maximum frenzy charges` | 7 | 6 | maximum-frenzy-charges | flat | 1 of them: the item has several versions and the plan does not record which one |
| `+# to strength and intelligence` | 7 | 7 | strength + intelligence | flat |  |
| `+#% to quality of all skills` | 7 | 7 | skill-quality | flat |  |
| `+#% to thorns critical hit chance` | 7 | 5 | thorns-critical-chance | flat | 2 of them: it is a roll from a patch that has been replaced |
| `-#% to all elemental resistances` | 7 | 7 | resistance-fire + resistance-cold + resistance-lightning | flat |  |
| `allies in your presence have #% increased attack speed` | 7 | 7 | ally-attack-speed | increased |  |
| `allies in your presence have #% increased cast speed` | 7 | 7 | ally-cast-speed | increased |  |
| `ancestrally boosted attacks deal #% increased damage` | 7 | 7 | ancestrally-boosted-damage | increased |  |
| `banner skills have #% increased duration` | 7 | 7 | banner-duration | increased |  |
| `bleeding you inflict deals damage #% faster` | 7 | 7 | bleeding-damage-speed | increased |  |
| `offerings have #% increased maximum life` | 7 | 7 | offering-life | increased |  |
| `remnants you create have #% increased effect` | 7 | 7 | remnant-effect | increased |  |
| `#% increased area damage` | 6 | 6 | area-damage | increased |  |
| `#% increased attack and cast speed with lightning skills` | 6 | 6 | attack-speed-with-lightning-skills + cast-speed-with-lightning-skills | increased |  |
| `#% increased attack speed with daggers` | 6 | 6 | attack-speed-with-daggers | increased |  |
| `#% increased attack speed with quarterstaves` | 6 | 6 | attack-speed-with-quarterstaves | increased |  |
| `#% increased attack speed with spears` | 6 | 6 | attack-speed-with-spears | increased |  |
| `#% increased cooldown recovery rate for grenade skills` | 6 | 6 | grenade-cooldown-recovery | increased |  |
| `#% increased critical hit chance with daggers` | 6 | 6 | critical-chance-with-daggers | increased |  |
| `#% increased critical hit chance with flails` | 6 | 6 | critical-chance-with-flails | increased |  |
| `#% increased critical hit chance with traps` | 6 | 6 | critical-chance-with-traps | increased |  |
| `#% increased damage with crossbows` | 6 | 6 | damage-with-crossbows | increased |  |
| `#% increased damage with maces` | 6 | 6 | damage-with-maces | increased |  |
| `#% increased damage with warcries` | 6 | 6 | damage-with-warcries | increased |  |
| `#% increased magnitude of damaging ailments you inflict` | 6 | 6 | damaging-ailments-magnitude | increased |  |
| `#% increased parry damage` | 6 | 6 | parry-damage | increased |  |
| `#% increased quantity of gold dropped by slain enemies` | 6 | 5 | gold-find | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased reservation efficiency of minion skills` | 6 | 6 | minion-reservation-efficiency | increased |  |
| `#% increased total power counted by warcries` | 6 | 6 | warcry-power | increased |  |
| `#% reduced flask charges used` | 6 | 6 | flask-charges-used | increased |  |
| `#% reduced poison duration on you` | 6 | 6 | poison-duration-on-you | increased |  |
| `+# to level of all cold spell skills` | 6 | 5 | skills-tab | flat | 1 of them: it is a roll from a patch that has been replaced |
| `+# to maximum endurance charges` | 6 | 5 | maximum-endurance-charges | flat | 1 of them: the item has several versions and the plan does not record which one |
| `+#% of armour also applies to chaos damage` | 6 | 4 | armour-applies-to-chaos-damage | flat | 2 of them: the item has several versions and the plan does not record which one |
| `-#% to cold resistance` | 6 | 4 | resistance-cold | flat | 2 of them: it is a roll from a patch that has been replaced |
| `adds # to # fire damage to attacks` | 6 | 6 | damage-fire | flat |  |
| `archon recovery period expires #% faster` | 6 | 6 | archon-recovery-speed | increased |  |
| `charms applied to you have #% increased effect` | 6 | 5 | charm-effect | increased | 1 of them: the item has several versions and the plan does not record which one |
| `grants # passive skill point` | 6 | 6 | passive-points | flat |  |
| `invocated spells deal #% increased damage` | 6 | 6 | invocated-damage | increased |  |
| `minions have #% increased critical damage bonus` | 6 | 6 | minion-critical-damage | increased |  |
| `#% increased accuracy rating with one handed melee weapons` | 5 | 5 | attack-rating-with-one-handed-melee-weapons | increased |  |
| `#% increased attack speed with axes` | 5 | 5 | attack-speed-with-axes | increased |  |
| `#% increased attack speed with one handed melee weapons` | 5 | 5 | attack-speed-with-one-handed-melee-weapons | increased |  |
| `#% increased ballista damage` | 5 | 5 | ballista-damage | increased |  |
| `#% increased duration of ignite shock and chill on enemies` | 5 | 5 | ignite-duration + shock-duration + chill-duration | increased |  |
| `#% increased endurance charge duration` | 5 | 5 | endurance-charge-duration | increased |  |
| `#% increased flask mana recovery rate` | 5 | 5 | flask-mana-recovery | increased |  |
| `#% increased freeze buildup with quarterstaves` | 5 | 5 | freeze-buildup-with-quarterstaves | increased |  |
| `#% increased life recovery rate` | 5 | 5 | life-recovery-rate | increased |  |
| `#% increased parry hit area of effect` | 5 | 5 | parry-hit-area-of-effect | increased |  |
| `#% increased pin duration` | 5 | 5 | pin-duration | increased |  |
| `#% of damage taken bypasses energy shield` | 5 | 4 | damage-bypassing-energy-shield | flat | 1 of them: the item has several versions and the plan does not record which one |
| `#% of elemental damage taken recouped as energy shield` | 5 | 5 | elemental-damage-recouped-as-energy-shield | flat |  |
| `#% of physical damage prevented recouped as life` | 5 | 4 | physical-damage-prevented-recouped-as-life | flat | 1 of them: the item has several versions and the plan does not record which one |
| `#% reduced cast speed` | 5 | 5 | speed-cast | increased |  |
| `#% reduced duration of curses on you` | 5 | 3 | curses-duration-on-you | increased | 2 of them: the item has several versions and the plan does not record which one |
| `#% reduced ignite duration on you` | 5 | 5 | ignite-duration-on-you | increased |  |
| `#% reduced maximum life` | 5 | 4 | life | increased | 1 of them: it is a roll from a patch that has been replaced |
| `#% reduced rarity of items found` | 5 | 2 | magic-find | increased | 3 of them: the item has several versions and the plan does not record which one |
| `+# to level of all melee skills` | 5 | 5 | skills-tab | flat |  |
| `+# to maximum number of elemental infusions` | 5 | 5 | maximum-elemental-infusions | flat |  |
| `+# to strength and dexterity` | 5 | 5 | strength + dexterity | flat |  |
| `+#% to maximum quality` | 5 | 5 | maximum-quality | flat |  |
| `allies in your presence deal # to # added attack lightning damage` | 5 | 3 | ally-added-lightning-damage | flat | 2 of them: the item has several versions and the plan does not record which one |
| `allies in your presence have #% increased critical hit chance` | 5 | 5 | ally-critical-chance | increased |  |
| `buffs on you expire #% slower` | 5 | 5 | buff-expiry-speed | increased |  |
| `companions gain #% damage as extra chaos damage` | 5 | 5 | companion-extra-chaos-damage | flat |  |
| `companions have #% increased area of effect` | 5 | 5 | companion-area-of-effect | increased |  |
| `companions have +#% to all elemental resistances` | 5 | 5 | companion-fire-resistance + companion-cold-resistance + companion-lightning-resistance | flat |  |
| `damage penetrates #% of enemy elemental resistances` | 5 | 5 | penetration-fire + penetration-cold + penetration-lightning | flat |  |
| `gain #% of damage as extra physical damage` | 5 | 5 | extra-physical-damage | flat |  |
| `ignites you inflict deal damage #% faster` | 5 | 5 | ignite-damage-speed | increased |  |
| `leech #% of physical attack damage as life` | 5 | 5 | life-leech | flat |  |
| `leech life #% slower` | 5 | 5 | life-leech-speed | increased |  |
| `mark skills have #% increased skill effect duration` | 5 | 5 | mark-skill-effect-duration | increased |  |
| `offering skills have #% increased buff effect` | 5 | 5 | offering-buff-effect | increased |  |
| `offering skills have #% increased duration` | 5 | 5 | offering-duration | increased |  |
| `sealed skills have #% increased seal gain frequency` | 5 | 5 | sealed-seal-gain-frequency | increased |  |
| `warcry skills have #% increased area of effect` | 5 | 5 | warcry-area-of-effect | increased |  |
| `#% chance to poison on hit with attacks` | 4 | 4 | poison-chance | flat |  |
| `#% increased accuracy rating with bows` | 4 | 4 | attack-rating-with-bows | increased |  |
| `#% increased attack and cast speed with elemental skills` | 4 | 4 | attack-speed-with-elemental-skills + cast-speed-with-elemental-skills | increased |  |
| `#% increased attack cold damage` | 4 | 4 | attack-cold-damage | increased |  |
| `#% increased attack speed with swords` | 4 | 4 | attack-speed-with-swords | increased |  |
| `#% increased attribute requirements` | 4 | 4 | attribute-requirements | increased |  |
| `#% increased attributes` | 4 | 4 | strength + dexterity + intelligence | increased |  |
| `#% increased endurance frenzy and power charge duration` | 4 | 4 | endurance-charge-duration + frenzy-charge-duration + power-charge-duration | increased |  |
| `#% increased magnitude of non-damaging ailments you inflict` | 4 | 4 | non-damaging-ailments-magnitude | increased |  |
| `#% increased mana cost of skills` | 4 | 4 | resource-cost-reduction | increased |  |
| `#% increased mana flask charges gained` | 4 | 4 | flask-charges-gained | increased |  |
| `#% increased reservation efficiency of companion skills` | 4 | 4 | companion-reservation-efficiency | increased |  |
| `#% increased stun buildup with maces` | 4 | 4 | stun-buildup-with-maces | increased |  |
| `#% increased trap throwing speed` | 4 | 4 | trap-throwing-speed | increased |  |
| `#% of physical damage taken recouped as life` | 4 | 4 | physical-damage-recouped-as-life | flat |  |
| `#% reduced damage` | 4 | 4 | damage | increased |  |
| `#% reduced duration of ailments on you` | 4 | 4 | ailments-duration-on-you | increased |  |
| `#% reduced freeze duration on you` | 4 | 4 | freeze-duration-on-you | increased |  |
| `#% reduced movement speed` | 4 | 4 | speed-movement | increased |  |
| `#% reduced skill speed` | 4 | 4 | speed-skill | increased |  |
| `+# metres to melee strike range` | 4 | 4 | melee-strike-range | flat |  |
| `+# to dexterity and intelligence` | 4 | 4 | dexterity + intelligence | flat |  |
| `+# to level of all chaos spell skills` | 4 | 4 | skills-tab | flat |  |
| `+# to level of all fire spell skills` | 4 | 4 | skills-tab | flat |  |
| `+# to level of all lightning spell skills` | 4 | 4 | skills-tab | flat |  |
| `+# to level of all physical spell skills` | 4 | 4 | skills-tab | flat |  |
| `+# to level of all projectile skills` | 4 | 4 | skills-tab | flat |  |
| `+# to maximum number of summoned ballista totems` | 4 | 4 | maximum-summoned-ballista-totems | flat |  |
| `+# to maximum number of summoned totems` | 4 | 4 | maximum-summoned-totems | flat |  |
| `+#% to cold and lightning resistances` | 4 | 4 | resistance-cold + resistance-lightning | flat |  |
| `+#% to fire and cold resistances` | 4 | 4 | resistance-fire + resistance-cold | flat |  |
| `+#% to fire and lightning resistances` | 4 | 4 | resistance-fire + resistance-lightning | flat |  |
| `+#% to maximum chaos resistance` | 4 | 4 | resistance-chaos-max | flat |  |
| `-#% to fire resistance` | 4 | 4 | resistance-fire | flat |  |
| `adds # to # chaos damage to attacks` | 4 | 3 | damage-chaos | flat | 1 of them: it is a roll from a patch that has been replaced |
| `adds # to # cold damage to attacks` | 4 | 3 | damage-cold | flat | 1 of them: it is a roll from a patch that has been replaced |
| `adds # to # cold damage to spells` | 4 | 4 | damage-cold | flat |  |
| `adds # to # fire damage to spells` | 4 | 4 | damage-fire | flat |  |
| `adds # to # lightning damage to spells` | 4 | 4 | damage-lightning | flat |  |
| `allies in your presence deal # to # added attack cold damage` | 4 | 2 | ally-added-cold-damage | flat | 2 of them: the item has several versions and the plan does not record which one |
| `allies in your presence deal # to # added attack fire damage` | 4 | 2 | ally-added-fire-damage | flat | 2 of them: the item has several versions and the plan does not record which one |
| `allies in your presence have #% increased critical damage bonus` | 4 | 4 | ally-critical-damage | increased |  |
| `damage penetrates #% elemental resistances` | 4 | 4 | penetration-fire + penetration-cold + penetration-lightning | flat |  |
| `gain #% of physical damage as extra chaos damage` | 4 | 4 | extra-chaos-damage | flat |  |
| `minions have #% increased cooldown recovery rate` | 4 | 4 | minion-cooldown-recovery | increased |  |
| `spells gain #% of damage as extra chaos damage` | 4 | 4 | extra-chaos-damage | flat |  |
| `you and allies in your presence have #% increased attack speed` | 4 | 0 | speed-attack + ally-attack-speed | increased | the item has several versions and the plan does not record which one |
| `you and allies in your presence have #% increased cast speed` | 4 | 0 | speed-cast + ally-cast-speed | increased | the item has several versions and the plan does not record which one |
| `#% additional physical damage reduction` | 3 | 3 | damage-reduction | flat |  |
| `#% increased arrow speed` | 3 | 3 | arrow-speed | increased |  |
| `#% increased ballista critical damage bonus` | 3 | 3 | ballista-critical-damage | increased |  |
| `#% increased ballista critical hit chance` | 3 | 3 | ballista-critical-chance | increased |  |
| `#% increased ballista immobilisation buildup` | 3 | 3 | ballista-immobilisation-buildup | increased |  |
| `#% increased cast speed with cold skills` | 3 | 3 | cast-speed-with-cold-skills | increased |  |
| `#% increased critical damage bonus with daggers` | 3 | 3 | critical-damage-with-daggers | increased |  |
| `#% increased critical damage bonus with quarterstaves` | 3 | 3 | critical-damage-with-quarterstaves | increased |  |
| `#% increased critical damage bonus with spears` | 3 | 3 | critical-damage-with-spears | increased |  |
| `#% increased critical hit chance with crossbows` | 3 | 3 | critical-chance-with-crossbows | increased |  |
| `#% increased damage with axes` | 3 | 3 | damage-with-axes | increased |  |
| `#% increased damage with daggers` | 3 | 3 | damage-with-daggers | increased |  |
| `#% increased effect of puppet master` | 3 | 3 | puppet-master-effect | increased |  |
| `#% increased effect of socketed augment items` | 3 | 1 | socketed-augment-items-effect | increased | 2 of them: the pack's own mod group says it multiplies the item, not the character |
| `#% increased effect of socketed soul cores` | 3 | 1 | socketed-soul-cores-effect | increased | 2 of them: it is a roll from a patch that has been replaced |
| `#% increased flask and charm charges gained` | 3 | 3 | flask-charges-gained + charm-charges-gained | increased |  |
| `#% increased global armour evasion and energy shield` | 3 | 3 | armour + evasion + energy-shield | increased |  |
| `#% increased global physical damage` | 3 | 3 | damage-physical | increased |  |
| `#% increased hazard area of effect` | 3 | 3 | hazard-area-of-effect | increased |  |
| `#% increased hazard duration` | 3 | 3 | hazard-duration | increased |  |
| `#% increased maximum runic ward` | 3 | 3 | maximum-runic-ward | increased |  |
| `#% increased melee attack speed` | 3 | 3 | melee-attack-speed | increased |  |
| `#% increased projectile stun buildup` | 3 | 3 | projectile-stun-buildup | increased |  |
| `#% increased skill speed with channelling skills` | 3 | 3 | skill-speed-with-channelling-skills | increased |  |
| `#% increased spell physical damage` | 3 | 2 | spell-physical-damage | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased stun buildup with quarterstaves` | 3 | 3 | stun-buildup-with-quarterstaves | increased |  |
| `#% increased weapon swap speed` | 3 | 3 | weapon-swap-speed | increased |  |
| `#% less maximum life` | 3 | 2 | life | more | 1 of them: the item has several versions and the plan does not record which one |
| `#% reduced area of effect` | 3 | 3 | area-of-effect | increased |  |
| `#% reduced armour break taken` | 3 | 3 | armour-break-taken | increased |  |
| `#% reduced attribute requirements` | 3 | 1 | attribute-requirements | increased | 2 of them: the pack's own mod group says it multiplies the item, not the character |
| `#% reduced critical hit chance` | 3 | 3 | critical-chance | increased |  |
| `#% reduced elemental ailment duration on you` | 3 | 3 | elemental-ailment-duration-on-you | increased |  |
| `#% reduced projectile speed` | 3 | 3 | projectile-speed | increased |  |
| `#% reduced shock duration on you` | 3 | 3 | shock-duration-on-you | increased |  |
| `+# metres to dodge roll distance` | 3 | 3 | dodge-roll-distance | flat |  |
| `+# to level of all curse skills` | 3 | 3 | skills-tab | flat |  |
| `+# to level of all mark skills` | 3 | 3 | skills-tab | flat |  |
| `+# to level of all skills` | 3 | 3 | skills-all | flat |  |
| `+# to level of all trap skill gems` | 3 | 3 | skills-tab | flat |  |
| `+#% to all maximum resistances` | 3 | 3 | resistance-fire-max + resistance-cold-max + resistance-lightning-max | flat |  |
| `-# physical damage taken from attack hits` | 3 | 3 | physical-damage-taken-from-attacks | flat |  |
| `-#% to chaos resistance` | 3 | 3 | resistance-chaos | flat |  |
| `allies in your presence deal # to # added attack chaos damage` | 3 | 3 | ally-added-chaos-damage | flat |  |
| `allies in your presence gain #% of damage as extra chaos damage` | 3 | 1 | ally-extra-chaos-damage | flat | 2 of them: the item has several versions and the plan does not record which one |
| `allies in your presence have +#% to all elemental resistances` | 3 | 3 | ally-fire-resistance + ally-cold-resistance + ally-lightning-resistance | flat |  |
| `banner skills have #% increased aura magnitudes` | 3 | 3 | banner-aura-magnitudes | increased |  |
| `companions gain #% damage as extra cold damage` | 3 | 3 | companion-extra-cold-damage | flat |  |
| `companions have #% increased attack speed` | 3 | 3 | companion-attack-speed | increased |  |
| `companions have #% increased movement speed` | 3 | 3 | companion-movement-speed | increased |  |
| `detonator skills have #% increased area of effect` | 3 | 3 | detonator-area-of-effect | increased |  |
| `enemies blinded by you have #% reduced critical hit chance` | 3 | 3 | blinded-enemy-critical-chance | increased |  |
| `gain #% of physical damage as extra fire damage` | 3 | 3 | extra-fire-damage | flat |  |
| `hits have #% reduced critical hit chance against you` | 3 | 3 | critical-chance-against-you | increased |  |
| `invocated skills have #% increased maximum energy` | 3 | 3 | invocated-maximum-energy | increased |  |
| `leech life #% faster` | 3 | 3 | life-leech-speed | increased |  |
| `minions have #% increased movement speed` | 3 | 3 | minion-movement-speed | increased |  |
| `minions have +#% to cold resistance` | 3 | 3 | minion-cold-resistance | flat |  |
| `minions have +#% to fire resistance` | 3 | 3 | minion-fire-resistance | flat |  |
| `minions have +#% to lightning resistance` | 3 | 3 | minion-lightning-resistance | flat |  |
| `reserves #% of life` | 3 | 3 | life-reserved | flat |  |
| `take #% less damage from hits` | 3 | 2 | damage-taken-from-hits | more | 1 of them: it is a roll from a patch that has been replaced |
| `take #% less damage over time` | 3 | 2 | damage-taken-over-time | more | 1 of them: it is a roll from a patch that has been replaced |
| `you and allies in your presence have #% increased accuracy rating` | 3 | 0 | attack-rating + ally-accuracy-rating | increased | the item has several versions and the plan does not record which one |
| `you and allies in your presence have #% increased cooldown recovery rate` | 3 | 0 | cooldown-reduction + ally-cooldown-recovery | increased | the item has several versions and the plan does not record which one |
| `you and allies in your presence have +#% to chaos resistance` | 3 | 0 | resistance-chaos + ally-chaos-resistance | flat | the item has several versions and the plan does not record which one |
| `#% increased accuracy rating with spears` | 2 | 2 | attack-rating-with-spears | increased |  |
| `#% increased accuracy rating with two handed melee weapons` | 2 | 2 | attack-rating-with-two-handed-melee-weapons | increased |  |
| `#% increased attack and cast speed` | 2 | 2 | speed-attack + speed-cast | increased |  |
| `#% increased attack physical damage` | 2 | 2 | attack-physical-damage | increased |  |
| `#% increased attack speed with crossbows` | 2 | 2 | attack-speed-with-crossbows | increased |  |
| `#% increased attack speed with one handed weapons` | 2 | 2 | attack-speed-with-one-handed-weapons | increased |  |
| `#% increased block recovery` | 2 | 2 | block-recovery | increased |  |
| `#% increased critical damage bonus with bows` | 2 | 2 | critical-damage-with-bows | increased |  |
| `#% increased critical hit chance with one handed melee weapons` | 2 | 2 | critical-chance-with-one-handed-melee-weapons | increased |  |
| `#% increased critical hit chance with quarterstaves` | 2 | 2 | critical-chance-with-quarterstaves | increased |  |
| `#% increased critical hit chance with spears` | 2 | 2 | critical-chance-with-spears | increased |  |
| `#% increased damage taken` | 2 | 2 | damage-taken | increased |  |
| `#% increased damage with quarterstaves` | 2 | 2 | damage-with-quarterstaves | increased |  |
| `#% increased damage with unarmed attacks` | 2 | 2 | damage-with-unarmed-attacks | increased |  |
| `#% increased duration of elemental ailments on enemies` | 2 | 1 | elemental-ailments-duration | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased effect of jewel socket passive skills` | 2 | 1 | jewel-socket-passive-skills-effect | increased | 1 of them: it is a roll from a patch that has been replaced |
| `#% increased effect of small passive skills in radius` | 2 | 2 | small-passive-skills-in-radius-effect | increased |  |
| `#% increased effect of socketed runes` | 2 | 1 | socketed-runes-effect | increased | 1 of them: the pack's own mod group says it multiplies the item, not the character |
| `#% increased experience gain` | 2 | 2 | experience-gain | increased |  |
| `#% increased freeze duration on enemies` | 2 | 2 | freeze-duration | increased |  |
| `#% increased grenade area of effect` | 2 | 2 | grenade-area-of-effect | increased |  |
| `#% increased hazard immobilisation buildup` | 2 | 2 | hazard-immobilisation-buildup | increased |  |
| `#% increased hinder duration` | 2 | 2 | hinder-duration | increased |  |
| `#% increased magnitude of abyssal wasting you inflict` | 2 | 1 | abyssal-wasting-magnitude | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased magnitude of daze` | 2 | 2 | daze-magnitude | increased |  |
| `#% increased mana reservation efficiency of skills` | 2 | 2 | mana-reservation-efficiency | increased |  |
| `#% increased maximum darkness` | 2 | 2 | maximum-darkness | increased |  |
| `#% increased melee critical hit chance` | 2 | 2 | melee-critical-chance | increased |  |
| `#% increased projectile speed for spell skills` | 2 | 2 | projectile-speed-with-spell-skills | increased |  |
| `#% increased reload speed` | 2 | 0 | reload-speed | increased | the pack's own mod group says it multiplies the item, not the character |
| `#% increased stun duration` | 2 | 0 | stun-duration | increased | the pack's own mod group says it multiplies the item, not the character |
| `#% increased thorns critical damage bonus` | 2 | 2 | thorns-critical-damage | increased |  |
| `#% increased unarmed attack speed` | 2 | 2 | unarmed-attack-speed | increased |  |
| `#% less attack damage` | 2 | 2 | damage-attack | more |  |
| `#% less maximum mana` | 2 | 1 | mana | more | 1 of them: the item has several versions and the plan does not record which one |
| `#% less spirit` | 2 | 1 | spirit | more | 1 of them: the item has several versions and the plan does not record which one |
| `#% reduced chill duration on you` | 2 | 2 | chill-duration-on-you | increased |  |
| `#% reduced duration of ignite shock and chill on enemies` | 2 | 1 | ignite-duration + shock-duration + chill-duration | increased | 1 of them: it is a roll from a patch that has been replaced |
| `#% reduced effect of non-damaging ailments on you` | 2 | 2 | non-damaging-ailments-effect-on-you | increased |  |
| `#% reduced energy shield recharge rate` | 2 | 2 | energy-shield-recharge | increased |  |
| `#% reduced flask life recovery rate` | 2 | 2 | flask-life-recovery | increased |  |
| `#% reduced life recovery rate` | 2 | 2 | life-recovery-rate | increased |  |
| `#% reduced life regeneration rate` | 2 | 2 | life-regeneration | increased |  |
| `#% reduced poison duration` | 2 | 2 | poison-duration | increased |  |
| `#% reduced projectile speed for spell skills` | 2 | 2 | projectile-speed-with-spell-skills | increased |  |
| `#% reduced reload speed` | 2 | 0 | reload-speed | increased | it multiplies this crossbow's own number, not the character's |
| `#% reduced spirit` | 2 | 2 | spirit | increased |  |
| `#% slower start of energy shield recharge` | 2 | 2 | energy-shield-recharge-delay | increased |  |
| `+# charm slots` | 2 | 2 | charm-slots | flat |  |
| `+# to ailment threshold` | 2 | 2 | ailment-threshold | flat |  |
| `+# to level of all attack skills` | 2 | 2 | skills-tab | flat |  |
| `+# to level of all grenade skill gems` | 2 | 2 | skills-tab | flat |  |
| `+# to level of all hazard skill gems` | 2 | 2 | skills-tab | flat |  |
| `+# to level of all herald skill gems` | 2 | 2 | skills-tab | flat |  |
| `+# to level of all nova skill gems` | 2 | 2 | skills-tab | flat |  |
| `+# to level of all plant skill gems` | 2 | 2 | skills-tab | flat |  |
| `+# to level of all slam skill gems` | 2 | 2 | skills-tab | flat |  |
| `+# to level of all storm skill gems` | 2 | 2 | skills-tab | flat |  |
| `+# to level of all strike skill gems` | 2 | 2 | skills-tab | flat |  |
| `+# to level of all totem skill gems` | 2 | 2 | skills-tab | flat |  |
| `+# to level of all warcry skill gems` | 2 | 2 | skills-tab | flat |  |
| `+# to level of all wind skill gems` | 2 | 2 | skills-tab | flat |  |
| `+# to weapon range` | 2 | 2 | weapon-range | flat |  |
| `+#% to cold and chaos resistances` | 2 | 2 | resistance-cold + resistance-chaos | flat |  |
| `+#% to fire and chaos resistances` | 2 | 2 | resistance-fire + resistance-chaos | flat |  |
| `+#% to lightning and chaos resistances` | 2 | 2 | resistance-lightning + resistance-chaos | flat |  |
| `-# to maximum rage` | 2 | 2 | maximum-rage | flat |  |
| `-#% to all maximum elemental resistances` | 2 | 2 | resistance-fire-max + resistance-cold-max + resistance-lightning-max | flat |  |
| `allies in your presence deal # to # added attack physical damage` | 2 | 2 | ally-added-physical-damage | flat |  |
| `allies in your presence have +# to accuracy rating` | 2 | 2 | ally-accuracy-rating | flat |  |
| `gain #% of physical damage as extra cold damage` | 2 | 2 | extra-cold-damage | flat |  |
| `leech #% of physical attack damage as mana` | 2 | 2 | mana-leech | flat |  |
| `meta skills have #% increased reservation efficiency` | 2 | 2 | meta-reservation-efficiency | increased |  |
| `minions cause #% increased stun buildup` | 2 | 2 | minion-stun-buildup | increased |  |
| `minions have #% increased attack speed` | 2 | 2 | minion-attack-speed | increased |  |
| `minions have #% increased evasion rating` | 2 | 2 | minion-evasion-rating | increased |  |
| `minions have #% increased skill speed with command skills` | 2 | 2 | minion-command-skill-skill-speed | increased |  |
| `minions have +#% to all maximum elemental resistances` | 2 | 2 | minion-fire-resistance-max + minion-cold-resistance-max + minion-lightning-resistance-max | flat |  |
| `minions have +#% to maximum cold resistances` | 2 | 2 | minion-cold-resistance-max | flat |  |
| `minions have +#% to maximum fire resistances` | 2 | 2 | minion-fire-resistance-max | flat |  |
| `minions have +#% to maximum lightning resistances` | 2 | 2 | minion-lightning-resistance-max | flat |  |
| `offering skills have #% increased area of effect` | 2 | 2 | offering-area-of-effect | increased |  |
| `remnants you create have #% reduced effect` | 2 | 2 | remnant-effect | increased |  |
| `shapeshift skills have #% increased skill effect duration` | 2 | 2 | shapeshift-skill-effect-duration | increased |  |
| `slam skills have #% increased area of effect` | 2 | 2 | slam-area-of-effect | increased |  |
| `totems have #% additional physical damage reduction` | 2 | 2 | totem-physical-damage-reduction | flat |  |

## The tail: what no pattern claims, and why

**2,512 templates, 4,922 lines (39.3% of everything).** Every one of them is
kept, filed against the stat it talks about, and left out of the arithmetic. This is the work
list, and most of it is finished work: a line that cannot be counted honestly is a correct
answer, not a gap.

| why it is not counted | lines | templates |
| --- | ---: | ---: |
| it grants a skill rather than a number | 597 | 189 |
| it scales off another number the plan does not hold | 558 | 266 |
| it only applies if something is true | 555 | 323 |
| no pattern claims this wording yet | 531 | 414 |
| it only applies while something is true | 493 | 269 |
| the sentence states a rule rather than a number | 456 | 351 |
| it changes what enemies have, not what the character has | 348 | 210 |
| the game lets a person pick which attribute and the plan does not record the pick | 293 | 1 |
| it is a chance of something happening, not an amount | 292 | 130 |
| it converts one number into another | 140 | 74 |
| the pack records it as a field of the flask, not as a stat line | 111 | 5 |
| it is a rule about the item rather than a number | 107 | 38 |
| it is somebody else's number, not the character's | 105 | 76 |
| the vocabulary has no name for this number yet | 100 | 67 |
| it happens on an event rather than standing | 89 | 25 |
| it multiplies another item's own number, not the character's | 82 | 33 |
| it multiplies the item's own number, not the character's | 40 | 21 |
| it only applies for a while after something happens | 25 | 20 |

### The biggest unclaimed templates

Everything left that the pack says four times or more, largest first. There is nothing in
this list a pattern could take without inventing a meaning for it.

| normalised template | lines | why |
| --- | ---: | --- |
| `+# to any attribute` | 293 | the game lets a person pick which attribute and the plan does not record the pick |
| `grants skill raise shield` | 171 | it grants a skill rather than a number |
| `gain deflection rating equal to #% of evasion rating` | 64 | it scales off another number the plan does not hold |
| `grants skill parry` | 61 | it grants a skill rather than a number |
| `grants skill spear throw` | 47 | it grants a skill rather than a number |
| `charges per use` | 31 | the pack records it as a field of the flask, not as a stat line |
| `duration s` | 31 | the pack records it as a field of the flask, not as a stat line |
| `max charges` | 31 | the pack records it as a field of the flask, not as a stat line |
| `gain additional stun threshold equal to #% of maximum energy shield` | 30 | it scales off another number the plan does not hold |
| `gain # rage on melee hit` | 27 | it happens on an event rather than standing |
| `#% of skill mana costs converted to life costs` | 24 | it converts one number into another |
| `gain # life per enemy killed` | 22 | it scales off another number the plan does not hold |
| `gain additional ailment threshold equal to #% of maximum energy shield` | 18 | it scales off another number the plan does not hold |
| `gain # mana per enemy killed` | 17 | it scales off another number the plan does not hold |
| `gain # rage when hit by an enemy` | 17 | it only applies if something is true |
| `projectiles have #% chance to chain an additional time from terrain` | 16 | it is a chance of something happening, not an amount |
| `#% increased damage while your companion is in your presence` | 15 | it only applies while something is true |
| `+#% surpassing chance to fire an additional arrow` | 15 | it is a chance of something happening, not an amount |
| `#% chance for spell skills to fire # additional projectiles` | 14 | it is a chance of something happening, not an amount |
| `#% increased damage with hits against enemies that are on low life` | 14 | it changes what enemies have, not what the character has |
| `recover #% of maximum life on kill` | 13 | it happens on an event rather than standing |
| `recover #% of maximum mana on kill` | 13 | it happens on an event rather than standing |
| `#% chance for attack hits to apply incision` | 12 | it is a chance of something happening, not an amount |
| `#% increased armour evasion and energy shield from equipped shield` | 12 | it multiplies another item's own number, not the character's |
| `#% increased melee strike range with this weapon` | 12 | it multiplies the item's own number, not the character's |
| `#% increased armour evasion and energy shield while your companion is in your presence` | 11 | it only applies while something is true |
| `#% increased movement speed while sprinting` | 11 | it only applies while something is true |
| `can roll ring modifiers` | 11 | it is a rule about the item rather than a number |
| `catalysts can be applied to this item` | 11 | it is a rule about the item rather than a number |
| `#% chance to build an additional combo on hit` | 10 | it is a chance of something happening, not an amount |
| `#% increased bonuses gained from equipped quiver` | 10 | it multiplies another item's own number, not the character's |
| `#% increased damage while shapeshifted` | 10 | it only applies while something is true |
| `flasks gain # charges per second` | 10 | it scales off another number the plan does not hold |
| `grants skill level # skeletal warrior minion` | 10 | it grants a skill rather than a number |
| `life flasks gain # charges per second` | 10 | it scales off another number the plan does not hold |
| `strikes deal splash damage` | 10 | the sentence states a rule rather than a number |
| `#% chance to gain volatility on kill` | 9 | it is a chance of something happening, not an amount |
| `#% increased energy shield from equipped focus` | 9 | it multiplies another item's own number, not the character's |
| `#% increased stun threshold if you haven t been stunned recently` | 9 | it only applies if something is true |
| `mana flasks gain # charges per second` | 9 | it scales off another number the plan does not hold |
| `projectiles have #% chance for an additional projectile when forking` | 9 | it only applies if something is true |
| `recovers life` | 9 | the pack records it as a field of the flask, not as a stat line |
| `recovers mana` | 9 | the pack records it as a field of the flask, not as a stat line |
| `#% increased attack damage while surrounded` | 8 | it only applies while something is true |
| `#% increased mana regeneration rate while stationary` | 8 | it only applies while something is true |
| `#% of spell mana cost converted to life cost` | 8 | it converts one number into another |
| `#% surpassing chance to gain a puppet master stack whenever you use a command skill` | 8 | it only applies if something is true |
| `projectiles deal #% increased damage with hits against enemies further than #m` | 8 | it changes what enemies have, not what the character has |
| `wind skills which can be boosted by elemental ground surfaces count` | 8 | it is a rule about the item rather than a number |
| `#% chance to chain an additional time` | 7 | it is a chance of something happening, not an amount |
| `#% chance when you gain a power charge to gain an additional power charge` | 7 | it only applies if something is true |
| `#% increased damage against enemies with fully broken armour` | 7 | it changes what enemies have, not what the character has |
| `#% increased damage with hits against enemies affected by elemental ailments` | 7 | it changes what enemies have, not what the character has |
| `#% increased projectile speed with this weapon` | 7 | it multiplies the item's own number, not the character's |
| `#% increased skill speed while shapeshifted` | 7 | it only applies while something is true |
| `#% increased stun threshold while parrying` | 7 | it only applies while something is true |
| `+# suffix modifier allowed` | 7 | it is a rule about the item rather than a number |
| `crushes enemies on hit` | 7 | it changes what enemies have, not what the character has |
| `gain # life per enemy hit with attacks` | 7 | it scales off another number the plan does not hold |
| `grants skill level # purity of fire` | 7 | it grants a skill rather than a number |
| `you take #% of damage from blocked hits` | 7 | no pattern claims this wording yet |
| `#% chance to cause bleeding on hit` | 6 | it is a chance of something happening, not an amount |
| `#% chance when you gain a frenzy charge to gain an additional frenzy charge` | 6 | it only applies if something is true |
| `#% chance when you gain an endurance charge to gain an additional endurance charge` | 6 | it only applies if something is true |
| `#% increased attack damage while moving` | 6 | it only applies while something is true |
| `#% increased attack damage while you have an ally in your presence` | 6 | it only applies while something is true |
| `#% increased damage with hits against blinded enemies` | 6 | it changes what enemies have, not what the character has |
| `#% increased magnitude of damaging ailments you inflict with critical hits` | 6 | the vocabulary has no name for this number yet |
| `#% increased mana regeneration rate while moving` | 6 | it only applies while something is true |
| `#% increased maximum energy shield if you ve consumed a power charge recently` | 6 | it only applies if something is true |
| `#% increased melee damage if you ve dealt a projectile attack hit in the past eight seconds` | 6 | it only applies if something is true |
| `#% increased spell damage if you have consumed an elemental infusion recently` | 6 | it only applies if something is true |
| `-# prefix modifier allowed` | 6 | it is a rule about the item rather than a number |
| `-# suffix modifier allowed` | 6 | it is a rule about the item rather than a number |
| `causes enemies to explode on critical kill for #% of their life as physical damage` | 6 | it changes what enemies have, not what the character has |
| `charms gain # charges per second` | 6 | it scales off another number the plan does not hold |
| `grants skill level # chaos bolt` | 6 | it grants a skill rather than a number |
| `grants skill level # purity of ice` | 6 | it grants a skill rather than a number |
| `grants skill level # purity of lightning` | 6 | it grants a skill rather than a number |
| `has +# to evasion rating per player level has +# to maximum energy shield per player level` | 6 | it scales off another number the plan does not hold |
| `loads an additional bolt` | 6 | the sentence states a rule rather than a number |
| `projectiles have #% increased critical hit chance against enemies further than #m` | 6 | it changes what enemies have, not what the character has |
| `recover #% of maximum life for each endurance charge consumed` | 6 | it scales off another number the plan does not hold |
| `#% chance for lightning skills to chain an additional time` | 5 | it is a chance of something happening, not an amount |
| `#% faster start of energy shield recharge while shapeshifted` | 5 | it only applies while something is true |
| `#% increased armour from equipped body armour` | 5 | it multiplies another item's own number, not the character's |
| `#% increased armour if you ve consumed an endurance charge recently` | 5 | it only applies if something is true |
| `#% increased armour while bleeding` | 5 | it only applies while something is true |
| `#% increased armour while stationary` | 5 | it only applies while something is true |
| `#% increased armour while surrounded` | 5 | it only applies while something is true |
| `#% increased attack damage against rare or unique enemies` | 5 | it changes what enemies have, not what the character has |
| `#% increased attack damage while on low life` | 5 | it only applies while something is true |
| `#% increased attack speed per # dexterity` | 5 | it scales off another number the plan does not hold |
| `#% increased attack speed while a rare or unique enemy is in your presence` | 5 | it only applies while something is true |
| `#% increased damage against immobilised enemies` | 5 | it changes what enemies have, not what the character has |
| `#% increased duration` | 5 | the vocabulary has no name for this number yet |
| `#% increased elemental damage while shapeshifted` | 5 | it only applies while something is true |
| `#% increased energy shield from equipped body armour` | 5 | it multiplies another item's own number, not the character's |
| `#% increased evasion rating while surrounded` | 5 | it only applies while something is true |
| `#% increased life regeneration rate while stationary` | 5 | it only applies while something is true |
| `#% increased projectile damage if you ve dealt a melee hit in the past eight seconds` | 5 | it only applies if something is true |
| `#% increased spell damage with spells that cost life` | 5 | no pattern claims this wording yet |
| `#% of flask recovery applied instantly` | 5 | no pattern claims this wording yet |
| `#% of maximum life converted to energy shield` | 5 | it converts one number into another |
| `#% reduced flask charges used from mana flasks` | 5 | no pattern claims this wording yet |
| `+# intelligence requirement` | 5 | no pattern claims this wording yet |
| `+#% of armour also applies to elemental damage while shapeshifted` | 5 | it only applies while something is true |
| `+#% surpassing chance to fire an additional projectile` | 5 | it is a chance of something happening, not an amount |
| `attack skills deal #% increased damage while holding a shield` | 5 | it only applies while something is true |
| `culling strike` | 5 | the sentence states a rule rather than a number |
| `grants skill level # firebolt` | 5 | it grants a skill rather than a number |
| `grenade skills fire an additional projectile` | 5 | the sentence states a rule rather than a number |
| `inherent rage loss starts # second later` | 5 | no pattern claims this wording yet |
| `projectiles deal #% increased damage with hits against enemies within #m` | 5 | it changes what enemies have, not what the character has |
| `recover # life when you block` | 5 | it only applies if something is true |
| `skills which create fissures have a #% chance to create an additional fissure` | 5 | it is a chance of something happening, not an amount |
| `temporary minion skills have +# to limit of minions summoned` | 5 | it is somebody else's number, not the character's |
| `warcries empower an additional attack` | 5 | the sentence states a rule rather than a number |
| `you can apply an additional curse` | 5 | it is a rule about the item rather than a number |
| `your other modifiers to rarity of items found do not apply` | 5 | the sentence states a rule rather than a number |
| `# mana gained when you block` | 4 | it only applies if something is true |
| `#% chance for flasks you use to not consume charges` | 4 | it is a chance of something happening, not an amount |
| `#% chance for mace slam skills you use yourself to cause an additional aftershock` | 4 | it is a chance of something happening, not an amount |
| `#% chance for slam skills you use yourself to cause an additional aftershock` | 4 | it is a chance of something happening, not an amount |
| `#% chance that if you would gain endurance charges you instead gain up to maximum endurance charges` | 4 | it only applies if something is true |
| `#% chance that if you would gain frenzy charges you instead gain up to your maximum number of frenzy charges` | 4 | it only applies if something is true |
| `#% chance that if you would gain power charges you instead gain up to` | 4 | it only applies if something is true |
| `#% chance to create an additional remnant` | 4 | it is a chance of something happening, not an amount |
| `#% chance to gain a charge when you kill an enemy` | 4 | it only applies if something is true |
| `#% chance to gain arcane surge when you deal a critical hit` | 4 | it only applies if something is true |
| `#% chance to not destroy corpses when consuming corpses` | 4 | it only applies if something is true |
| `#% chance when a charm is used to use another charm without consuming charges` | 4 | it only applies if something is true |
| `#% increased area of effect of ancestrally boosted attacks` | 4 | no pattern claims this wording yet |
| `#% increased armour and evasion rating while leeching` | 4 | it only applies while something is true |
| `#% increased armour while shapeshifted` | 4 | it only applies while something is true |
| `#% increased attack speed while dual wielding` | 4 | it only applies while something is true |
| `#% increased critical damage bonus if you ve consumed a power charge recently` | 4 | it only applies if something is true |
| `#% increased damage against immobilised enemies while shapeshifted` | 4 | it only applies while something is true |
| `#% increased damage if you have consumed a corpse recently` | 4 | it only applies if something is true |
| `#% increased damage with hits against burning enemies` | 4 | it changes what enemies have, not what the character has |
| `#% increased evasion rating from equipped body armour` | 4 | it multiplies another item's own number, not the character's |
| `#% increased evasion rating if you have been hit recently` | 4 | it only applies if something is true |
| `#% increased evasion rating if you ve consumed a frenzy charge recently` | 4 | it only applies if something is true |
| `#% increased evasion rating while moving` | 4 | it only applies while something is true |
| `#% increased evasion rating while sprinting` | 4 | it only applies while something is true |
| `#% increased magnitude of bleeding you inflict against enemies affected by incision` | 4 | it changes what enemies have, not what the character has |
| `#% increased spell damage while wielding a melee weapon` | 4 | it only applies while something is true |
| `#% increased stun threshold while channelling` | 4 | it only applies while something is true |
| `#% of damage from hits is taken from your damageable companion s life before you` | 4 | it is somebody else's number, not the character's |
| `#% of lightning damage converted to cold damage` | 4 | it converts one number into another |
| `#% of physical damage taken as fire damage` | 4 | it converts one number into another |
| `#% of your base life regeneration is granted to allies in your presence` | 4 | it is somebody else's number, not the character's |
| `#% reduced charges per use` | 4 | it scales off another number the plan does not hold |
| `#% reduced projectile range` | 4 | no pattern claims this wording yet |
| `#has +# to evasion rating per player level` | 4 | it scales off another number the plan does not hold |
| `+# prefix modifier allowed` | 4 | it is a rule about the item rather than a number |
| `always hits` | 4 | the sentence states a rule rather than a number |
| `attacks have added physical damage equal to #% of maximum life` | 4 | it scales off another number the plan does not hold |
| `break armour on critical hit with spells equal to #% of physical damage dealt` | 4 | it scales off another number the plan does not hold |
| `corrupting will always result in change` | 4 | the sentence states a rule rather than a number |
| `gain #% of maximum energy shield as additional freeze threshold` | 4 | the vocabulary has no name for this number yet |
| `grants skill level # decompose` | 4 | it grants a skill rather than a number |
| `grants skill level # heart of ice` | 4 | it grants a skill rather than a number |
| `grants skill level # lightning bolt` | 4 | it grants a skill rather than a number |
| `grants skill level # sigil of power` | 4 | it grants a skill rather than a number |
| `inflict abyssal wasting on hit` | 4 | it happens on an event rather than standing |
| `inherent loss of rage is #% slower` | 4 | no pattern claims this wording yet |
| `minions gain #% of their maximum life as extra maximum energy shield` | 4 | it is somebody else's number, not the character's |
| `other modifiers to movement speed except for sprinting do not apply` | 4 | the sentence states a rule rather than a number |
| `recover #% of maximum mana when you consume a power charge` | 4 | it only applies if something is true |
| `recover #% of missing life before being hit by an enemy` | 4 | it changes what enemies have, not what the character has |
| `recover #% of your maximum life when an enemy dies in your presence` | 4 | it only applies if something is true |
| `recover #% of your maximum mana when an enemy dies in your presence` | 4 | it only applies if something is true |
| `targets can be affected by +# of your poisons at the same time` | 4 | it is a rule about the item rather than a number |
| `totems gain +#% to all maximum elemental resistances` | 4 | it is somebody else's number, not the character's |
| `your maximum number of power charges` | 4 | the sentence states a rule rather than a number |

### Where the tail stops

The remainder is genuinely one-off: after the table above, what is left averages under one
and a half lines per template. A catch-all entry — `#% increased <anything>` — would take all
of it and report ninety-something per cent, and it would be a lie: it would file a thousand
one-line rows under names nobody set a target for, and it would count conditional and
scoped sentences as though they were always on. The coverage number here means *this line is
in the arithmetic*, and it is kept meaning that.

## What the vocabulary grew

Seven names for the pools and brackets this game has and the other two do not: `spirit` and
`stun-threshold` (pools a person reads beside life and mana), `damage-spell` and
`damage-attack` (two brackets this game never adds together, so neither can be `damage`),
`damage-minion` and `life-minion` (a summoner's whole build has no other row), and
`speed-skill`.

And, this pass, **the ailments and the statuses** — as a family and by a loop rather than as
two hundred entries written out. A status is not decoration in an action RPG: it is a way of
killing and a way of dying, and a person builds at it. **1,006 counted contributions** land
on these rows in this pack, more than land on armour. Buildup, chance, magnitude and duration
are what a character does to something else, so they are offence; threshold and the `on you` numbers
are how much a character takes before a status lands and how bad it is once it has, so they
are defence. Unnamed, every one of them sat in `other`, under the rows nobody aims at.

⚠ Only that family is promoted. Everything else this game says alone is still carried under
its own id — `presence-area-of-effect`, `runic-ward-regeneration`, `charm-slots`, the scoped
brackets like `attack-speed-with-bows` — written noun first, so the name a person reads under
`other` is the name the game uses. A stat with no second game to agree with belongs there.

## A known consequence, stated plainly

A stat that only ever receives increases and has no base — movement speed, spell damage,
minion damage — totals **zero**, because the pool multiplies a base it does not have. The
working still shows the bracket, so `Movement speed 0.00, increased −7` reads as what it is:
we know the modifiers and not the number they modify. The alternative was to write in a
baseline of 100 for every percentage stat, and that would be a number nobody recorded.
