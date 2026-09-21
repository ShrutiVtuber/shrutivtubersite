# Path of Exile 2 — the stat census

Measured from the built pack on 2026-09-21 by running every stat line the
planner would see through `path_of_exile_2.map_line`. Nothing here is
claimed; the table is generated from the mapper, so it says what the code
actually does.

## What there is

- **12,512 stat lines** across the kinds the planner counts, in **3,162 distinct normalised templates**.
- **6,122 lines are counted** (48.9%); the rest are kept, listed against the stat they
  talk about, and left out of the arithmetic.
- Lines by kind: affix 1,913, unique 3,009, node 6,058, rune 664, charm 39, flask 72, base 757.
- `jewel` contributes **0** lines: a jewel record holds a `can_roll` catalogue of what it
  *could* roll, and the plan picks the jewel rather than the roll, so there is nothing
  on it that a person has actually chosen.

### Counted by kind

| kind | lines | counted |
| --- | ---: | ---: |
| affix | 1,913 | 842 (44%) |
| unique | 3,009 | 1,345 (45%) |
| node | 6,058 | 3,355 (55%) |
| rune | 664 | 333 (50%) |
| charm | 39 | 0 (0%) |
| flask | 72 | 0 (0%) |
| base | 757 | 247 (33%) |

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
is negative. An increase is passed as the percentage written, because the pool already does
`(base + added) × (1 + Σ increased) × each more`, and each `more` gets a bucket of its own so
they multiply against one another rather than adding.

Three things are held back on purpose even though the wording matched:

- **A roll from a patch that has gone.** The pack keeps a unique's old rolls tagged `Pre 0.2.0`
  and the live one tagged `Current`; a line without `Current` is a fact about a past patch.
- **A version a plan has not chosen.** An item with several versions (Atziri's Splendour has
  an armour, an evasion and an energy-shield one) has all of them in the pack.
- **An increase that belongs to the item.** `350% increased Physical Damage` on a sword
  multiplies that sword and nothing else. The pack marks a rune's effects outright and writes
  `local` into an affix's id, so those are caught. ⚠ A **unique's** or a **base's** wording says
  nothing either way, so a unique body armour's `(700-800)% increased Armour` is counted as
  though it were global. That is the largest known overstatement in this mapping.

## The templates

Every template the mapper claims, plus every template seen twice or more: **1,331 rows,
10,681 lines, 85.4% of everything**. `stat` is the canonical name it
feeds (several means the line splits); where there is none, the last column says why in our
own words. A template can be both — counted when the roll is current, held when it is not —
and the counts say which — a reason in the last column is about the lines NOT counted, so
`133 lines, 130 counted, 3 of them: a roll from a patch that has been replaced` is a template
that maps cleanly and has three old rolls in the pack beside it.

| normalised template | lines | counted | stat | form | what is held back, and why |
| --- | ---: | ---: | --- | --- | --- |
| `+# to any attribute` | 293 | 0 |  |  | the game lets a person pick which attribute and the plan does not record the pick |
| `grants skill raise shield` | 171 | 0 |  |  | it grants a skill rather than a number |
| `#% increased mana regeneration rate` | 133 | 130 | mana-regeneration | increased | 3 of them: it is a roll from a patch that has been replaced |
| `#% increased evasion rating` | 124 | 116 | evasion | increased | 8 of them: the item has several versions and the plan does not record which one |
| `#% increased armour` | 122 | 107 | armour | increased | 15 of them: it is a roll from a patch that has been replaced |
| `#% increased attack speed` | 114 | 110 | speed-attack | increased | 4 of them: it multiplies the item's own number, not the character's |
| `+# to strength` | 113 | 109 | strength | flat | 4 of them: it is a roll from a patch that has been replaced |
| `+# to dexterity` | 103 | 99 | dexterity | flat | 4 of them: it is a roll from a patch that has been replaced |
| `#% increased physical damage` | 96 | 82 | damage-physical | increased | 14 of them: it is a roll from a patch that has been replaced |
| `+# to intelligence` | 95 | 92 | intelligence | flat | 3 of them: it is a roll from a patch that has been replaced |
| `#% faster start of energy shield recharge` | 87 | 83 | energy-shield-recharge-delay | increased | 4 of them: it is a roll from a patch that has been replaced |
| `#% increased movement speed` | 86 | 79 | speed-movement | increased | 7 of them: it is a roll from a patch that has been replaced |
| `+# to maximum life` | 84 | 77 | life | flat | 7 of them: it is a roll from a patch that has been replaced |
| `#% increased block chance` | 83 | 69 | block | increased | 14 of them: it is a roll from a patch that has been replaced |
| `#% increased attack damage` | 82 | 82 | damage-attack | increased |  |
| `#% increased maximum energy shield` | 81 | 79 | energy-shield | increased | 2 of them: the item has several versions and the plan does not record which one |
| `+# to maximum mana` | 81 | 75 | mana | flat | 6 of them: it is a roll from a patch that has been replaced |
| `#% increased critical hit chance` | 79 | 72 | critical-chance | increased | 7 of them: it is a roll from a patch that has been replaced |
| `#% increased spell damage` | 75 | 73 | damage-spell | increased | 2 of them: it is a roll from a patch that has been replaced |
| `#% increased stun threshold` | 66 | 64 | stun-threshold | increased | 2 of them: it is a roll from a patch that has been replaced |
| `gain deflection rating equal to #% of evasion rating` | 64 | 0 |  |  | it scales off another number the plan does not hold |
| `minions deal #% increased damage` | 64 | 64 | damage-minion | increased |  |
| `#% increased cast speed` | 62 | 61 | speed-cast | increased | 1 of them: the item has several versions and the plan does not record which one |
| `+#% to fire resistance` | 61 | 52 | resistance-fire | flat | 9 of them: it is a roll from a patch that has been replaced |
| `+#% to lightning resistance` | 61 | 53 | resistance-lightning | flat | 8 of them: it is a roll from a patch that has been replaced |
| `grants skill parry` | 61 | 0 |  |  | it grants a skill rather than a number |
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
| `grants skill spear throw` | 47 | 0 |  |  | it grants a skill rather than a number |
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
| `#% increased armour and evasion` | 37 | 31 | armour + evasion | increased | 6 of them: it is a roll from a patch that has been replaced |
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
| `charges per use` | 31 | 0 |  |  | the pack records it as a field of the flask, not as a stat line |
| `duration s` | 31 | 0 |  |  | the pack records it as a field of the flask, not as a stat line |
| `max charges` | 31 | 0 |  |  | the pack records it as a field of the flask, not as a stat line |
| `#% increased armour and energy shield` | 30 | 23 | armour + energy-shield | increased | 7 of them: it is a roll from a patch that has been replaced |
| `gain additional stun threshold equal to #% of maximum energy shield` | 30 | 0 |  |  | it scales off another number the plan does not hold |
| `#% increased amount of life leeched` | 29 | 28 | life-leech | increased | 1 of them: it is a roll from a patch that has been replaced |
| `#% increased energy shield` | 29 | 25 | energy-shield | increased | 4 of them: it multiplies the item's own number, not the character's |
| `#% increased life recovery from flasks` | 29 | 29 | flask-life-recovery | increased |  |
| `#% increased ignite magnitude` | 28 | 26 | ignite-magnitude | increased | 2 of them: it is a roll from a patch that has been replaced |
| `#% chance to daze on hit` | 27 | 27 | daze-chance | flat |  |
| `#% chance to inflict bleeding on hit` | 27 | 24 | bleed-chance | flat | 3 of them: the item has several versions and the plan does not record which one |
| `#% increased maximum life` | 27 | 25 | life | increased | 2 of them: the item has several versions and the plan does not record which one |
| `break #% increased armour` | 27 | 0 |  |  | no pattern claims this wording yet |
| `gain # rage on melee hit` | 27 | 0 |  |  | no pattern claims this wording yet |
| `#% increased curse magnitudes` | 26 | 26 | curse-magnitude | increased |  |
| `#% increased energy shield recharge rate` | 26 | 26 | energy-shield-recharge | increased |  |
| `+# to armour` | 26 | 23 | armour | flat | 3 of them: it is a roll from a patch that has been replaced |
| `+# to stun threshold` | 26 | 24 | stun-threshold | flat | 2 of them: it is a roll from a patch that has been replaced |
| `regenerate #% of maximum life per second` | 26 | 26 | life-regeneration-percent | flat |  |
| `#% increased chance to inflict ailments` | 25 | 24 | ailment-chance | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased magnitude of shock you inflict` | 25 | 24 | shock-magnitude | increased | 1 of them: the item has several versions and the plan does not record which one |
| `damage penetrates #% cold resistance` | 25 | 25 | penetration-cold | flat |  |
| `damage penetrates #% fire resistance` | 25 | 25 | penetration-fire | flat |  |
| `#% of skill mana costs converted to life costs` | 24 | 0 |  |  | it converts one number into another |
| `#% increased attack area damage` | 23 | 23 | attack-area-damage | increased |  |
| `#% increased critical hit chance for attacks` | 23 | 23 | attack-critical-chance | increased |  |
| `#% increased flask charges gained` | 23 | 20 | flask-charges-gained | increased | 3 of them: the item has several versions and the plan does not record which one |
| `#% increased magnitude of poison you inflict` | 23 | 23 | poison-magnitude | increased |  |
| `+# to evasion rating` | 23 | 22 | evasion | flat | 1 of them: it is a roll from a patch that has been replaced |
| `adds # to # physical damage to attacks` | 23 | 20 | damage-physical | flat | 3 of them: it is a roll from a patch that has been replaced |
| `gain #% of damage as extra cold damage` | 23 | 19 | extra-cold-damage | flat | 4 of them: the item has several versions and the plan does not record which one |
| `#% chance to poison on hit` | 22 | 19 | poison-chance | flat | 3 of them: it is a roll from a patch that has been replaced |
| `#% increased evasion and energy shield` | 22 | 17 | evasion + energy-shield | increased | 5 of them: it multiplies the item's own number, not the character's |
| `#% increased projectile speed` | 22 | 22 | projectile-speed | increased |  |
| `#% reduced movement speed penalty from using skills while moving` | 22 | 0 |  |  | it only applies while something is true |
| `+# to maximum rage` | 22 | 22 | maximum-rage | flat |  |
| `adds # to # lightning damage` | 22 | 17 | damage-lightning | flat | 5 of them: it is a roll from a patch that has been replaced |
| `gain # life per enemy killed` | 22 | 0 |  |  | it scales off another number the plan does not hold |
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
| `#% increased armour evasion and energy shield` | 19 | 7 | armour + evasion + energy-shield | increased | 12 of them: it is a roll from a patch that has been replaced |
| `#% increased elemental damage with attacks` | 19 | 19 | attack-elemental-damage | increased |  |
| `#% increased light radius` | 19 | 19 | light-radius | increased |  |
| `#% increased totem placement speed` | 19 | 19 | totem-placement-speed | increased |  |
| `#% increased warcry speed` | 19 | 19 | warcry-speed | increased |  |
| `companions have #% increased maximum life` | 19 | 19 | companion-life | increased |  |
| `empowered attacks deal #% increased damage` | 19 | 0 |  |  | no pattern claims this wording yet |
| `gain #% of damage as extra chaos damage` | 19 | 16 | extra-chaos-damage | flat | 3 of them: the item has several versions and the plan does not record which one |
| `remnants can be collected from #% further away` | 19 | 0 |  |  | it is a rule about the item rather than a number |
| `#% increased amount of mana leeched` | 18 | 18 | mana-leech | increased |  |
| `#% increased maximum mana` | 18 | 14 | mana | increased | 4 of them: it is a roll from a patch that has been replaced |
| `adds # to # cold damage` | 18 | 14 | damage-cold | flat | 4 of them: it is a roll from a patch that has been replaced |
| `aura skills have #% increased magnitudes` | 18 | 18 | aura-magnitude | increased |  |
| `gain additional ailment threshold equal to #% of maximum energy shield` | 18 | 0 |  |  | it scales off another number the plan does not hold |
| `hits against you have #% reduced critical damage bonus` | 18 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased exposure effect` | 17 | 16 | exposure-magnitude | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased warcry cooldown recovery rate` | 17 | 17 | warcry-cooldown-recovery | increased |  |
| `+#% to maximum cold resistance` | 17 | 10 | resistance-cold-max | flat | 7 of them: the item has several versions and the plan does not record which one |
| `debuffs you inflict have #% increased slow magnitude` | 17 | 15 | slow-magnitude | increased | 2 of them: the item has several versions and the plan does not record which one |
| `gain # mana per enemy killed` | 17 | 0 |  |  | it scales off another number the plan does not hold |
| `gain # rage when hit by an enemy` | 17 | 0 |  |  | it only applies if something is true |
| `#% increased charm charges gained` | 16 | 16 | charm-charges-gained | increased |  |
| `#% increased glory generation` | 16 | 16 | glory-generation | increased |  |
| `#% increased magnitude of bleeding you inflict` | 16 | 16 | bleeding-magnitude | increased |  |
| `#% increased magnitude of chill you inflict` | 16 | 15 | chill-magnitude | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased mana recovery from flasks` | 16 | 16 | flask-mana-recovery | increased |  |
| `causes #% increased stun buildup` | 16 | 11 | stun-buildup | increased | 5 of them: it multiplies the item's own number, not the character's |
| `projectiles have #% chance to chain an additional time from terrain` | 16 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% increased damage while your companion is in your presence` | 15 | 0 |  |  | it only applies while something is true |
| `#% increased damage with two handed weapons` | 15 | 15 | damage-with-two-handed-weapons | increased |  |
| `#% increased thorns damage` | 15 | 15 | thorns-damage | increased |  |
| `#% reduced effect of curses on you` | 15 | 15 | curses-effect-on-you | increased |  |
| `+#% surpassing chance to fire an additional arrow` | 15 | 0 |  |  | it is a chance of something happening, not an amount |
| `+#% to all maximum elemental resistances` | 15 | 13 | resistance-fire-max + resistance-cold-max + resistance-lightning-max | flat | 2 of them: it is a roll from a patch that has been replaced |
| `+#% to critical hit chance` | 15 | 13 | critical-chance | flat | 2 of them: it is a roll from a patch that has been replaced |
| `+#% to maximum lightning resistance` | 15 | 8 | resistance-lightning-max | flat | 7 of them: the item has several versions and the plan does not record which one |
| `debuffs on you expire #% faster` | 15 | 14 | debuff-expiry-speed | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% chance for spell skills to fire # additional projectiles` | 14 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% increased archon buff duration` | 14 | 14 | archon-buff-duration | increased |  |
| `#% increased damage with hits against enemies that are on low life` | 14 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased effect of fully broken armour` | 14 | 0 |  |  | no pattern claims this wording yet |
| `#% increased parried debuff magnitude` | 14 | 14 | parried-debuff-magnitude | increased |  |
| `#% increased pin buildup` | 14 | 14 | pin-buildup | increased |  |
| `#% reduced attack speed` | 14 | 14 | speed-attack | increased |  |
| `+#% to critical damage bonus` | 14 | 11 | critical-damage | flat | 3 of them: the item has several versions and the plan does not record which one |
| `+#% to maximum fire resistance` | 14 | 7 | resistance-fire-max | flat | 7 of them: the item has several versions and the plan does not record which one |
| `spell skills have #% increased area of effect` | 14 | 13 | spell-area-of-effect | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased curse duration` | 13 | 13 | curse-duration | increased |  |
| `#% increased duration of damaging ailments on enemies` | 13 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased effect of arcane surge on you` | 13 | 13 | arcane-surge-effect-on-you | increased |  |
| `#% increased effect of your mark skills` | 13 | 13 | mark-effect | increased |  |
| `#% increased immobilisation buildup` | 13 | 13 | immobilisation-buildup | increased |  |
| `#% increased magnitude of ailments you inflict` | 13 | 13 | ailments-magnitude | increased |  |
| `#% increased poison duration` | 13 | 13 | poison-duration | increased |  |
| `#% increased speed of recoup effects` | 13 | 12 | recoup-speed | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased totem life` | 13 | 13 | totem-life | increased |  |
| `minions revive #% faster` | 13 | 11 | minion-revive-speed | increased | 2 of them: the item has several versions and the plan does not record which one |
| `recover #% of maximum life on kill` | 13 | 0 |  |  | it happens on an event rather than standing |
| `recover #% of maximum mana on kill` | 13 | 0 |  |  | it happens on an event rather than standing |
| `# to # physical thorns damage` | 12 | 12 | thorns-damage | flat |  |
| `#% chance for attack hits to apply incision` | 12 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% increased area of effect of curses` | 12 | 11 | curse-area-of-effect | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased armour evasion and energy shield from equipped shield` | 12 | 0 |  |  | no pattern claims this wording yet |
| `#% increased damage with swords` | 12 | 12 | damage-with-swords | increased |  |
| `#% increased knockback distance` | 12 | 12 | knockback-distance | increased |  |
| `#% increased life and mana recovery from flasks` | 12 | 12 | flask-life-recovery + flask-mana-recovery | increased |  |
| `#% increased melee strike range with this weapon` | 12 | 0 |  |  | no pattern claims this wording yet |
| `+#% to block chance` | 12 | 12 | block | flat |  |
| `adds # to # chaos damage` | 12 | 11 | damage-chaos | flat | 1 of them: it is a roll from a patch that has been replaced |
| `minions have #% increased attack and cast speed` | 12 | 11 | minion-attack-speed + minion-cast-speed | increased | 1 of them: the item has several versions and the plan does not record which one |
| `triggered spells deal #% increased spell damage` | 12 | 0 |  |  | no pattern claims this wording yet |
| `#% increased armour evasion and energy shield while your companion is in your presence` | 11 | 0 |  |  | it only applies while something is true |
| `#% increased chill duration on enemies` | 11 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased damage with one handed weapons` | 11 | 11 | damage-with-one-handed-weapons | increased |  |
| `#% increased electrocute buildup` | 11 | 11 | electrocute-buildup | increased |  |
| `#% increased freeze threshold` | 11 | 11 | freeze-threshold | increased |  |
| `#% increased movement speed while sprinting` | 11 | 0 |  |  | it only applies while something is true |
| `#% increased strength` | 11 | 8 | strength | increased | 3 of them: the item has several versions and the plan does not record which one |
| `#% of damage taken recouped as mana` | 11 | 11 | damage-recouped-as-mana | flat |  |
| `+# to level of all spell skills` | 11 | 11 | skills-tab | flat |  |
| `can roll ring modifiers` | 11 | 0 |  |  | it is a rule about the item rather than a number |
| `catalysts can be applied to this item` | 11 | 0 |  |  | it is a rule about the item rather than a number |
| `leeches #% of physical damage as life` | 11 | 10 | life-leech | flat | 1 of them: it is a roll from a patch that has been replaced |
| `minions have +#% to all elemental resistances` | 11 | 10 | minion-fire-resistance + minion-cold-resistance + minion-lightning-resistance | flat | 1 of them: the item has several versions and the plan does not record which one |
| `minions have +#% to chaos resistance` | 11 | 11 | minion-chaos-resistance | flat |  |
| `#% chance to build an additional combo on hit` | 10 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% increased bleeding duration` | 10 | 10 | bleeding-duration | increased |  |
| `#% increased bonuses gained from equipped quiver` | 10 | 0 |  |  | no pattern claims this wording yet |
| `#% increased critical damage bonus for attack damage` | 10 | 10 | attack-critical-damage | increased |  |
| `#% increased damage while shapeshifted` | 10 | 0 |  |  | it only applies while something is true |
| `#% increased damage with plant skills` | 10 | 0 |  |  | no pattern claims this wording yet |
| `#% increased effect of archon buffs on you` | 10 | 10 | archon-buffs-effect-on-you | increased |  |
| `#% increased flask effect duration` | 10 | 9 | flask-effect-duration | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased frenzy charge duration` | 10 | 10 | frenzy-charge-duration | increased |  |
| `#% increased hazard damage` | 10 | 10 | hazard-damage | increased |  |
| `#% increased parried debuff duration` | 10 | 10 | parried-debuff-duration | increased |  |
| `#% increased spirit` | 10 | 6 | spirit | increased | 4 of them: it multiplies the item's own number, not the character's |
| `#% increased stun recovery` | 10 | 10 | stun-recovery | increased |  |
| `#% reduced presence area of effect` | 10 | 10 | presence-area-of-effect | increased |  |
| `+# to level of all lightning skills` | 10 | 2 | skills-tab | flat | 8 of them: the item has several versions and the plan does not record which one |
| `allies in your presence deal #% increased damage` | 10 | 0 |  |  | it is somebody else's number, not the character's |
| `flasks gain # charges per second` | 10 | 0 |  |  | it scales off another number the plan does not hold |
| `grants skill level # skeletal warrior minion` | 10 | 0 |  |  | it grants a skill rather than a number |
| `life flasks gain # charges per second` | 10 | 0 |  |  | it scales off another number the plan does not hold |
| `minions have #% increased critical hit chance` | 10 | 9 | minion-critical-chance | increased | 1 of them: the item has several versions and the plan does not record which one |
| `strikes deal splash damage` | 10 | 0 |  |  | no pattern claims this wording yet |
| `#% chance to gain volatility on kill` | 9 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% increased charm effect duration` | 9 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% increased crossbow reload speed` | 9 | 9 | reload-speed | increased |  |
| `#% increased damage with bows` | 9 | 9 | damage-with-bows | increased |  |
| `#% increased deflection rating` | 9 | 9 | deflection | increased |  |
| `#% increased energy shield from equipped focus` | 9 | 0 |  |  | no pattern claims this wording yet |
| `#% increased life cost of skills` | 9 | 9 | life-cost-of-skills | increased |  |
| `#% increased life flask charges gained` | 9 | 9 | flask-charges-gained | increased |  |
| `#% increased minion duration` | 9 | 9 | minion-duration | increased |  |
| `#% increased reservation efficiency of herald skills` | 9 | 0 |  |  | no pattern claims this wording yet |
| `#% increased runic ward regeneration rate` | 9 | 9 | runic-ward-regeneration | increased |  |
| `#% increased spirit reservation efficiency` | 9 | 5 | spirit-reservation-efficiency | increased | 4 of them: the item has several versions and the plan does not record which one |
| `#% increased stun threshold if you haven t been stunned recently` | 9 | 0 |  |  | it only applies if something is true |
| `#% reduced effect of chill on you` | 9 | 9 | chill-effect-on-you | increased |  |
| `#% reduced effect of shock on you` | 9 | 9 | shock-effect-on-you | increased |  |
| `#% reduced magnitude of ignite on you` | 9 | 9 | ignite-magnitude-on-you | increased |  |
| `#% reduced skill effect duration` | 9 | 9 | skill-effect-duration | increased |  |
| `+# to level of all cold skills` | 9 | 3 | skills-tab | flat | 6 of them: the item has several versions and the plan does not record which one |
| `+# to maximum power charges` | 9 | 8 | maximum-power-charges | flat | 1 of them: the item has several versions and the plan does not record which one |
| `+#% of armour also applies to lightning damage` | 9 | 9 | armour-applies-to-lightning-damage | flat |  |
| `attacks used by totems have #% increased attack speed` | 9 | 0 |  |  | it is somebody else's number, not the character's |
| `mana flasks gain # charges per second` | 9 | 0 |  |  | it scales off another number the plan does not hold |
| `minions deal #% increased damage with command skills` | 9 | 0 |  |  | it is somebody else's number, not the character's |
| `minions have #% increased area of effect` | 9 | 9 | minion-area-of-effect | increased |  |
| `projectiles have #% chance for an additional projectile when forking` | 9 | 0 |  |  | it only applies if something is true |
| `recovers life` | 9 | 0 |  |  | the pack records it as a field of the flask, not as a stat line |
| `recovers mana` | 9 | 0 |  |  | the pack records it as a field of the flask, not as a stat line |
| `spells cast by totems have #% increased cast speed` | 9 | 0 |  |  | it is somebody else's number, not the character's |
| `#% chance to blind enemies on hit` | 8 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% chance to blind enemies on hit with attacks` | 8 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% faster curse activation` | 8 | 0 |  |  | no pattern claims this wording yet |
| `#% increased attack damage while surrounded` | 8 | 0 |  |  | it only applies while something is true |
| `#% increased attack speed with bows` | 8 | 0 |  |  | no pattern claims this wording yet |
| `#% increased blind effect` | 8 | 8 | blind-magnitude | increased |  |
| `#% increased bolt speed` | 8 | 0 |  |  | no pattern claims this wording yet |
| `#% increased culling strike threshold` | 8 | 7 | culling-strike-threshold | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased damage with flails` | 8 | 8 | damage-with-flails | increased |  |
| `#% increased elemental infusion duration` | 8 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% increased flask life recovery rate` | 8 | 8 | flask-life-recovery | increased |  |
| `#% increased glory generation for banner skills` | 8 | 0 |  |  | no pattern claims this wording yet |
| `#% increased intelligence` | 8 | 5 | intelligence | increased | 3 of them: the item has several versions and the plan does not record which one |
| `#% increased mana regeneration rate while stationary` | 8 | 0 |  |  | it only applies while something is true |
| `#% increased power charge duration` | 8 | 8 | power-charge-duration | increased |  |
| `#% increased shock duration` | 8 | 8 | shock-duration | increased |  |
| `#% increased trap damage` | 8 | 8 | trap-damage | increased |  |
| `#% increased withered magnitude` | 8 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% of spell mana cost converted to life cost` | 8 | 0 |  |  | it converts one number into another |
| `#% reduced charm charges used` | 8 | 8 | charm-charges-used | increased |  |
| `#% reduced light radius` | 8 | 8 | light-radius | increased |  |
| `#% reduced maximum mana` | 8 | 8 | mana | increased |  |
| `#% surpassing chance to gain a puppet master stack whenever you use a command skill` | 8 | 0 |  |  | it only applies if something is true |
| `+# charm slot` | 8 | 5 | charm-slots | flat | 3 of them: it is a roll from a patch that has been replaced |
| `+# to level of all corrupted skill gems` | 8 | 8 | skills-tab | flat |  |
| `+# to level of all minion skills` | 8 | 7 | skills-tab | flat | 1 of them: it is a roll from a patch that has been replaced |
| `+#% of armour also applies to cold damage` | 8 | 8 | armour-applies-to-cold-damage | flat |  |
| `+#% of armour also applies to fire damage` | 8 | 8 | armour-applies-to-fire-damage | flat |  |
| `+#% to maximum block chance` | 8 | 7 | block | flat | 1 of them: it is a roll from a patch that has been replaced |
| `adds # to # lightning damage to attacks` | 8 | 4 | damage-lightning | flat | 4 of them: the pack records the wording but no number for it |
| `banner skills have #% increased area of effect` | 8 | 0 |  |  | no pattern claims this wording yet |
| `channelling skills deal #% increased damage` | 8 | 0 |  |  | no pattern claims this wording yet |
| `damaging ailments deal damage #% faster` | 8 | 0 |  |  | no pattern claims this wording yet |
| `equipment and skill gems have #% reduced attribute requirements` | 8 | 7 | attribute-requirements | increased | 1 of them: it is a roll from a patch that has been replaced |
| `has # sockets` | 8 | 8 | sockets | flat |  |
| `herald skills deal #% increased damage` | 8 | 0 |  |  | no pattern claims this wording yet |
| `leeches #% of physical damage as mana` | 8 | 8 | mana-leech | flat |  |
| `mark skills have #% increased use speed` | 8 | 0 |  |  | no pattern claims this wording yet |
| `minions have #% additional physical damage reduction` | 8 | 0 |  |  | it is somebody else's number, not the character's |
| `minions have #% increased cooldown recovery rate for command skills` | 8 | 0 |  |  | it is somebody else's number, not the character's |
| `prevent +#% of damage from deflected hits` | 8 | 0 |  |  | no pattern claims this wording yet |
| `projectiles deal #% increased damage with hits against enemies further than #m` | 8 | 0 |  |  | it changes what enemies have, not what the character has |
| `wind skills which can be boosted by elemental ground surfaces count` | 8 | 0 |  |  | it is a rule about the item rather than a number |
| `#% chance to chain an additional time` | 7 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% chance to maim on hit` | 7 | 7 | maim-chance | flat |  |
| `#% chance when you gain a power charge to gain an additional power charge` | 7 | 0 |  |  | it only applies if something is true |
| `#% increased armour break duration` | 7 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% increased damage against enemies with fully broken armour` | 7 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased damage with hits against enemies affected by elemental ailments` | 7 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased damage with spears` | 7 | 7 | damage-with-spears | increased |  |
| `#% increased dexterity` | 7 | 5 | dexterity | increased | 2 of them: the item has several versions and the plan does not record which one |
| `#% increased grenade damage` | 7 | 7 | grenade-damage | increased |  |
| `#% increased ignite duration on enemies` | 7 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased projectile speed with this weapon` | 7 | 0 |  |  | no pattern claims this wording yet |
| `#% increased skill speed while shapeshifted` | 7 | 0 |  |  | it only applies while something is true |
| `#% increased spell area damage` | 7 | 7 | spell-area-damage | increased |  |
| `#% increased stun threshold while parrying` | 7 | 0 |  |  | it only applies while something is true |
| `#% more global evasion rating and energy shield` | 7 | 0 | evasion + energy-shield | more | it multiplies the item's own number, not the character's |
| `#% of damage taken recouped as life mana and energy shield` | 7 | 0 |  |  | no pattern claims this wording yet |
| `#% reduced duration of bleeding on you` | 7 | 0 |  |  | the vocabulary has no name for this number yet |
| `+# suffix modifier allowed` | 7 | 0 |  |  | it is a rule about the item rather than a number |
| `+# to level of all fire skills` | 7 | 1 | skills-tab | flat | 6 of them: the item has several versions and the plan does not record which one |
| `+# to maximum frenzy charges` | 7 | 6 | maximum-frenzy-charges | flat | 1 of them: the item has several versions and the plan does not record which one |
| `+# to strength and intelligence` | 7 | 7 | strength + intelligence | flat |  |
| `+#% to quality of all skills` | 7 | 7 | skill-quality | flat |  |
| `+#% to thorns critical hit chance` | 7 | 0 |  |  | no pattern claims this wording yet |
| `-#% to all elemental resistances` | 7 | 7 | resistance-fire + resistance-cold + resistance-lightning | flat |  |
| `allies in your presence have #% increased attack speed` | 7 | 0 |  |  | it is somebody else's number, not the character's |
| `allies in your presence have #% increased cast speed` | 7 | 0 |  |  | it is somebody else's number, not the character's |
| `ancestrally boosted attacks deal #% increased damage` | 7 | 0 |  |  | no pattern claims this wording yet |
| `banner skills have #% increased duration` | 7 | 0 |  |  | the vocabulary has no name for this number yet |
| `bleeding you inflict deals damage #% faster` | 7 | 0 |  |  | no pattern claims this wording yet |
| `crushes enemies on hit` | 7 | 0 |  |  | it changes what enemies have, not what the character has |
| `gain # life per enemy hit with attacks` | 7 | 0 |  |  | it scales off another number the plan does not hold |
| `grants skill level # purity of fire` | 7 | 0 |  |  | it grants a skill rather than a number |
| `offerings have #% increased maximum life` | 7 | 0 |  |  | it is somebody else's number, not the character's |
| `remnants you create have #% increased effect` | 7 | 0 |  |  | no pattern claims this wording yet |
| `you take #% of damage from blocked hits` | 7 | 0 |  |  | no pattern claims this wording yet |
| `#% chance to cause bleeding on hit` | 6 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% chance when you gain a frenzy charge to gain an additional frenzy charge` | 6 | 0 |  |  | it only applies if something is true |
| `#% chance when you gain an endurance charge to gain an additional endurance charge` | 6 | 0 |  |  | it only applies if something is true |
| `#% increased area damage` | 6 | 6 | area-damage | increased |  |
| `#% increased attack and cast speed with lightning skills` | 6 | 0 |  |  | no pattern claims this wording yet |
| `#% increased attack damage while moving` | 6 | 0 |  |  | it only applies while something is true |
| `#% increased attack damage while you have an ally in your presence` | 6 | 0 |  |  | it only applies while something is true |
| `#% increased attack speed with daggers` | 6 | 0 |  |  | no pattern claims this wording yet |
| `#% increased attack speed with quarterstaves` | 6 | 0 |  |  | no pattern claims this wording yet |
| `#% increased attack speed with spears` | 6 | 0 |  |  | no pattern claims this wording yet |
| `#% increased cooldown recovery rate for grenade skills` | 6 | 0 |  |  | no pattern claims this wording yet |
| `#% increased critical hit chance with daggers` | 6 | 0 |  |  | no pattern claims this wording yet |
| `#% increased critical hit chance with flails` | 6 | 0 |  |  | no pattern claims this wording yet |
| `#% increased critical hit chance with traps` | 6 | 0 |  |  | no pattern claims this wording yet |
| `#% increased damage with crossbows` | 6 | 6 | damage-with-crossbows | increased |  |
| `#% increased damage with hits against blinded enemies` | 6 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased damage with maces` | 6 | 6 | damage-with-maces | increased |  |
| `#% increased damage with warcries` | 6 | 0 |  |  | no pattern claims this wording yet |
| `#% increased magnitude of damaging ailments you inflict` | 6 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% increased magnitude of damaging ailments you inflict with critical hits` | 6 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% increased mana regeneration rate while moving` | 6 | 0 |  |  | it only applies while something is true |
| `#% increased maximum energy shield if you ve consumed a power charge recently` | 6 | 0 |  |  | it only applies if something is true |
| `#% increased melee damage if you ve dealt a projectile attack hit in the past eight seconds` | 6 | 0 |  |  | it only applies if something is true |
| `#% increased parry damage` | 6 | 6 | parry-damage | increased |  |
| `#% increased quantity of gold dropped by slain enemies` | 6 | 5 | gold-find | increased | 1 of them: the item has several versions and the plan does not record which one |
| `#% increased reservation efficiency of minion skills` | 6 | 0 |  |  | it is somebody else's number, not the character's |
| `#% increased spell damage if you have consumed an elemental infusion recently` | 6 | 0 |  |  | it only applies if something is true |
| `#% increased total power counted by warcries` | 6 | 0 |  |  | no pattern claims this wording yet |
| `#% reduced flask charges used` | 6 | 6 | flask-charges-used | increased |  |
| `#% reduced poison duration on you` | 6 | 0 |  |  | the vocabulary has no name for this number yet |
| `+# to level of all cold spell skills` | 6 | 5 | skills-tab | flat | 1 of them: it is a roll from a patch that has been replaced |
| `+# to maximum endurance charges` | 6 | 5 | maximum-endurance-charges | flat | 1 of them: the item has several versions and the plan does not record which one |
| `+#% of armour also applies to chaos damage` | 6 | 4 | armour-applies-to-chaos-damage | flat | 2 of them: the item has several versions and the plan does not record which one |
| `-# prefix modifier allowed` | 6 | 0 |  |  | it is a rule about the item rather than a number |
| `-# suffix modifier allowed` | 6 | 0 |  |  | it is a rule about the item rather than a number |
| `-#% to cold resistance` | 6 | 4 | resistance-cold | flat | 2 of them: it is a roll from a patch that has been replaced |
| `adds # to # fire damage to attacks` | 6 | 6 | damage-fire | flat |  |
| `archon recovery period expires #% faster` | 6 | 0 |  |  | no pattern claims this wording yet |
| `causes enemies to explode on critical kill for #% of their life as physical damage` | 6 | 0 |  |  | it changes what enemies have, not what the character has |
| `charms applied to you have #% increased effect` | 6 | 0 |  |  | no pattern claims this wording yet |
| `charms gain # charges per second` | 6 | 0 |  |  | it scales off another number the plan does not hold |
| `grants # passive skill point` | 6 | 0 |  |  | no pattern claims this wording yet |
| `grants skill level # chaos bolt` | 6 | 0 |  |  | it grants a skill rather than a number |
| `grants skill level # purity of ice` | 6 | 0 |  |  | it grants a skill rather than a number |
| `grants skill level # purity of lightning` | 6 | 0 |  |  | it grants a skill rather than a number |
| `has +# to evasion rating per player level has +# to maximum energy shield per player level` | 6 | 0 |  |  | it scales off another number the plan does not hold |
| `invocated spells deal #% increased damage` | 6 | 0 |  |  | no pattern claims this wording yet |
| `loads an additional bolt` | 6 | 0 |  |  | no pattern claims this wording yet |
| `minions have #% increased critical damage bonus` | 6 | 6 | minion-critical-damage | increased |  |
| `projectiles have #% increased critical hit chance against enemies further than #m` | 6 | 0 |  |  | it changes what enemies have, not what the character has |
| `recover #% of maximum life for each endurance charge consumed` | 6 | 0 |  |  | it scales off another number the plan does not hold |
| `#% chance for lightning skills to chain an additional time` | 5 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% faster start of energy shield recharge while shapeshifted` | 5 | 0 |  |  | it only applies while something is true |
| `#% increased accuracy rating with one handed melee weapons` | 5 | 0 |  |  | no pattern claims this wording yet |
| `#% increased armour from equipped body armour` | 5 | 0 |  |  | no pattern claims this wording yet |
| `#% increased armour if you ve consumed an endurance charge recently` | 5 | 0 |  |  | it only applies if something is true |
| `#% increased armour while bleeding` | 5 | 0 |  |  | it only applies while something is true |
| `#% increased armour while stationary` | 5 | 0 |  |  | it only applies while something is true |
| `#% increased armour while surrounded` | 5 | 0 |  |  | it only applies while something is true |
| `#% increased attack damage against rare or unique enemies` | 5 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased attack damage while on low life` | 5 | 0 |  |  | it only applies while something is true |
| `#% increased attack speed per # dexterity` | 5 | 0 |  |  | it scales off another number the plan does not hold |
| `#% increased attack speed while a rare or unique enemy is in your presence` | 5 | 0 |  |  | it only applies while something is true |
| `#% increased attack speed with axes` | 5 | 0 |  |  | no pattern claims this wording yet |
| `#% increased attack speed with one handed melee weapons` | 5 | 0 |  |  | no pattern claims this wording yet |
| `#% increased ballista damage` | 5 | 5 | ballista-damage | increased |  |
| `#% increased damage against immobilised enemies` | 5 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased duration` | 5 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% increased duration of ignite shock and chill on enemies` | 5 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased elemental damage while shapeshifted` | 5 | 0 |  |  | it only applies while something is true |
| `#% increased endurance charge duration` | 5 | 5 | endurance-charge-duration | increased |  |
| `#% increased energy shield from equipped body armour` | 5 | 0 |  |  | no pattern claims this wording yet |
| `#% increased evasion rating while surrounded` | 5 | 0 |  |  | it only applies while something is true |
| `#% increased flask mana recovery rate` | 5 | 5 | flask-mana-recovery | increased |  |
| `#% increased freeze buildup with quarterstaves` | 5 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% increased life recovery rate` | 5 | 0 |  |  | no pattern claims this wording yet |
| `#% increased life regeneration rate while stationary` | 5 | 0 |  |  | it only applies while something is true |
| `#% increased parry hit area of effect` | 5 | 0 |  |  | no pattern claims this wording yet |
| `#% increased pin duration` | 5 | 5 | pin-duration | increased |  |
| `#% increased projectile damage if you ve dealt a melee hit in the past eight seconds` | 5 | 0 |  |  | it only applies if something is true |
| `#% increased spell damage with spells that cost life` | 5 | 0 |  |  | no pattern claims this wording yet |
| `#% of damage taken bypasses energy shield` | 5 | 0 |  |  | no pattern claims this wording yet |
| `#% of elemental damage taken recouped as energy shield` | 5 | 0 |  |  | no pattern claims this wording yet |
| `#% of flask recovery applied instantly` | 5 | 0 |  |  | no pattern claims this wording yet |
| `#% of maximum life converted to energy shield` | 5 | 0 |  |  | it converts one number into another |
| `#% of physical damage prevented recouped as life` | 5 | 0 |  |  | no pattern claims this wording yet |
| `#% reduced cast speed` | 5 | 5 | speed-cast | increased |  |
| `#% reduced duration of curses on you` | 5 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% reduced flask charges used from mana flasks` | 5 | 0 |  |  | no pattern claims this wording yet |
| `#% reduced ignite duration on you` | 5 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% reduced maximum life` | 5 | 4 | life | increased | 1 of them: it is a roll from a patch that has been replaced |
| `#% reduced rarity of items found` | 5 | 2 | magic-find | increased | 3 of them: the item has several versions and the plan does not record which one |
| `+# intelligence requirement` | 5 | 0 |  |  | no pattern claims this wording yet |
| `+# to level of all melee skills` | 5 | 5 | skills-tab | flat |  |
| `+# to maximum number of elemental infusions` | 5 | 0 |  |  | no pattern claims this wording yet |
| `+# to strength and dexterity` | 5 | 5 | strength + dexterity | flat |  |
| `+#% of armour also applies to elemental damage while shapeshifted` | 5 | 0 |  |  | it only applies while something is true |
| `+#% surpassing chance to fire an additional projectile` | 5 | 0 |  |  | it is a chance of something happening, not an amount |
| `+#% to maximum quality` | 5 | 0 |  |  | no pattern claims this wording yet |
| `allies in your presence deal # to # added attack lightning damage` | 5 | 0 |  |  | it is somebody else's number, not the character's |
| `allies in your presence have #% increased critical hit chance` | 5 | 0 |  |  | it is somebody else's number, not the character's |
| `attack skills deal #% increased damage while holding a shield` | 5 | 0 |  |  | it only applies while something is true |
| `buffs on you expire #% slower` | 5 | 0 |  |  | no pattern claims this wording yet |
| `companions gain #% damage as extra chaos damage` | 5 | 0 |  |  | it is somebody else's number, not the character's |
| `companions have #% increased area of effect` | 5 | 5 | companion-area-of-effect | increased |  |
| `companions have +#% to all elemental resistances` | 5 | 0 |  |  | it is somebody else's number, not the character's |
| `culling strike` | 5 | 0 |  |  | no pattern claims this wording yet |
| `damage penetrates #% of enemy elemental resistances` | 5 | 5 | penetration-fire + penetration-cold + penetration-lightning | flat |  |
| `gain #% of damage as extra physical damage` | 5 | 5 | extra-physical-damage | flat |  |
| `grants skill level # firebolt` | 5 | 0 |  |  | it grants a skill rather than a number |
| `grenade skills fire an additional projectile` | 5 | 0 |  |  | no pattern claims this wording yet |
| `ignites you inflict deal damage #% faster` | 5 | 0 |  |  | no pattern claims this wording yet |
| `inherent rage loss starts # second later` | 5 | 0 |  |  | no pattern claims this wording yet |
| `leech #% of physical attack damage as life` | 5 | 5 | life-leech | flat |  |
| `leech life #% slower` | 5 | 0 |  |  | no pattern claims this wording yet |
| `mark skills have #% increased skill effect duration` | 5 | 0 |  |  | the vocabulary has no name for this number yet |
| `offering skills have #% increased buff effect` | 5 | 0 |  |  | it is somebody else's number, not the character's |
| `offering skills have #% increased duration` | 5 | 0 |  |  | it is somebody else's number, not the character's |
| `projectiles deal #% increased damage with hits against enemies within #m` | 5 | 0 |  |  | it changes what enemies have, not what the character has |
| `recover # life when you block` | 5 | 0 |  |  | it only applies if something is true |
| `sealed skills have #% increased seal gain frequency` | 5 | 0 |  |  | no pattern claims this wording yet |
| `skills which create fissures have a #% chance to create an additional fissure` | 5 | 0 |  |  | it is a chance of something happening, not an amount |
| `temporary minion skills have +# to limit of minions summoned` | 5 | 0 |  |  | it is somebody else's number, not the character's |
| `warcries empower an additional attack` | 5 | 0 |  |  | no pattern claims this wording yet |
| `warcry skills have #% increased area of effect` | 5 | 0 |  |  | no pattern claims this wording yet |
| `you can apply an additional curse` | 5 | 0 |  |  | it is a rule about the item rather than a number |
| `your other modifiers to rarity of items found do not apply` | 5 | 0 |  |  | the item has several versions and the plan does not record which one |
| `# mana gained when you block` | 4 | 0 |  |  | it only applies if something is true |
| `#% chance for flasks you use to not consume charges` | 4 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% chance for mace slam skills you use yourself to cause an additional aftershock` | 4 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% chance for slam skills you use yourself to cause an additional aftershock` | 4 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% chance that if you would gain endurance charges you instead gain up to maximum endurance charges` | 4 | 0 |  |  | it only applies if something is true |
| `#% chance that if you would gain frenzy charges you instead gain up to your maximum number of frenzy charges` | 4 | 0 |  |  | it only applies if something is true |
| `#% chance that if you would gain power charges you instead gain up to` | 4 | 0 |  |  | it only applies if something is true |
| `#% chance to create an additional remnant` | 4 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% chance to gain a charge when you kill an enemy` | 4 | 0 |  |  | it only applies if something is true |
| `#% chance to gain arcane surge when you deal a critical hit` | 4 | 0 |  |  | it only applies if something is true |
| `#% chance to not destroy corpses when consuming corpses` | 4 | 0 |  |  | it only applies if something is true |
| `#% chance to poison on hit with attacks` | 4 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% chance when a charm is used to use another charm without consuming charges` | 4 | 0 |  |  | it only applies if something is true |
| `#% increased accuracy rating with bows` | 4 | 0 |  |  | no pattern claims this wording yet |
| `#% increased area of effect of ancestrally boosted attacks` | 4 | 0 |  |  | no pattern claims this wording yet |
| `#% increased armour and evasion rating while leeching` | 4 | 0 |  |  | it only applies while something is true |
| `#% increased armour while shapeshifted` | 4 | 0 |  |  | it only applies while something is true |
| `#% increased attack and cast speed with elemental skills` | 4 | 0 |  |  | no pattern claims this wording yet |
| `#% increased attack cold damage` | 4 | 0 |  |  | no pattern claims this wording yet |
| `#% increased attack speed while dual wielding` | 4 | 0 |  |  | it only applies while something is true |
| `#% increased attack speed with swords` | 4 | 0 |  |  | no pattern claims this wording yet |
| `#% increased attribute requirements` | 4 | 4 | attribute-requirements | increased |  |
| `#% increased attributes` | 4 | 4 | strength + dexterity + intelligence | increased |  |
| `#% increased critical damage bonus if you ve consumed a power charge recently` | 4 | 0 |  |  | it only applies if something is true |
| `#% increased damage against immobilised enemies while shapeshifted` | 4 | 0 |  |  | it only applies while something is true |
| `#% increased damage if you have consumed a corpse recently` | 4 | 0 |  |  | it only applies if something is true |
| `#% increased damage with hits against burning enemies` | 4 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased endurance frenzy and power charge duration` | 4 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% increased evasion rating from equipped body armour` | 4 | 0 |  |  | no pattern claims this wording yet |
| `#% increased evasion rating if you have been hit recently` | 4 | 0 |  |  | it only applies if something is true |
| `#% increased evasion rating if you ve consumed a frenzy charge recently` | 4 | 0 |  |  | it only applies if something is true |
| `#% increased evasion rating while moving` | 4 | 0 |  |  | it only applies while something is true |
| `#% increased evasion rating while sprinting` | 4 | 0 |  |  | it only applies while something is true |
| `#% increased magnitude of bleeding you inflict against enemies affected by incision` | 4 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased magnitude of non-damaging ailments you inflict` | 4 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% increased mana cost of skills` | 4 | 4 | resource-cost-reduction | increased |  |
| `#% increased mana flask charges gained` | 4 | 4 | flask-charges-gained | increased |  |
| `#% increased reservation efficiency of companion skills` | 4 | 0 |  |  | it is somebody else's number, not the character's |
| `#% increased spell damage while wielding a melee weapon` | 4 | 0 |  |  | it only applies while something is true |
| `#% increased stun buildup with maces` | 4 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% increased stun threshold while channelling` | 4 | 0 |  |  | it only applies while something is true |
| `#% increased trap throwing speed` | 4 | 0 |  |  | no pattern claims this wording yet |
| `#% of damage from hits is taken from your damageable companion s life before you` | 4 | 0 |  |  | it is somebody else's number, not the character's |
| `#% of lightning damage converted to cold damage` | 4 | 0 |  |  | it converts one number into another |
| `#% of physical damage taken as fire damage` | 4 | 0 |  |  | it converts one number into another |
| `#% of physical damage taken recouped as life` | 4 | 0 |  |  | no pattern claims this wording yet |
| `#% of your base life regeneration is granted to allies in your presence` | 4 | 0 |  |  | it is somebody else's number, not the character's |
| `#% reduced charges per use` | 4 | 0 |  |  | it scales off another number the plan does not hold |
| `#% reduced damage` | 4 | 4 | damage | increased |  |
| `#% reduced duration of ailments on you` | 4 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% reduced freeze duration on you` | 4 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% reduced movement speed` | 4 | 4 | speed-movement | increased |  |
| `#% reduced projectile range` | 4 | 0 |  |  | no pattern claims this wording yet |
| `#% reduced skill speed` | 4 | 4 | speed-skill | increased |  |
| `#has +# to evasion rating per player level` | 4 | 0 |  |  | it scales off another number the plan does not hold |
| `+# metres to melee strike range` | 4 | 0 |  |  | no pattern claims this wording yet |
| `+# prefix modifier allowed` | 4 | 0 |  |  | it is a rule about the item rather than a number |
| `+# to dexterity and intelligence` | 4 | 4 | dexterity + intelligence | flat |  |
| `+# to level of all chaos spell skills` | 4 | 4 | skills-tab | flat |  |
| `+# to level of all fire spell skills` | 4 | 4 | skills-tab | flat |  |
| `+# to level of all lightning spell skills` | 4 | 4 | skills-tab | flat |  |
| `+# to level of all physical spell skills` | 4 | 4 | skills-tab | flat |  |
| `+# to level of all projectile skills` | 4 | 4 | skills-tab | flat |  |
| `+# to maximum number of summoned ballista totems` | 4 | 0 |  |  | it is somebody else's number, not the character's |
| `+# to maximum number of summoned totems` | 4 | 0 |  |  | it is somebody else's number, not the character's |
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
| `allies in your presence deal # to # added attack cold damage` | 4 | 0 |  |  | it is somebody else's number, not the character's |
| `allies in your presence deal # to # added attack fire damage` | 4 | 0 |  |  | it is somebody else's number, not the character's |
| `allies in your presence have #% increased critical damage bonus` | 4 | 0 |  |  | it is somebody else's number, not the character's |
| `always hits` | 4 | 0 |  |  | no pattern claims this wording yet |
| `attacks have added physical damage equal to #% of maximum life` | 4 | 0 |  |  | it scales off another number the plan does not hold |
| `break armour on critical hit with spells equal to #% of physical damage dealt` | 4 | 0 |  |  | it scales off another number the plan does not hold |
| `corrupting will always result in change` | 4 | 0 |  |  | no pattern claims this wording yet |
| `damage penetrates #% elemental resistances` | 4 | 4 | penetration-fire + penetration-cold + penetration-lightning | flat |  |
| `gain #% of maximum energy shield as additional freeze threshold` | 4 | 0 |  |  | the vocabulary has no name for this number yet |
| `gain #% of physical damage as extra chaos damage` | 4 | 4 | extra-chaos-damage | flat |  |
| `grants skill level # decompose` | 4 | 0 |  |  | it grants a skill rather than a number |
| `grants skill level # heart of ice` | 4 | 0 |  |  | it grants a skill rather than a number |
| `grants skill level # lightning bolt` | 4 | 0 |  |  | it grants a skill rather than a number |
| `grants skill level # sigil of power` | 4 | 0 |  |  | it grants a skill rather than a number |
| `inflict abyssal wasting on hit` | 4 | 0 |  |  | it happens on an event rather than standing |
| `inherent loss of rage is #% slower` | 4 | 0 |  |  | no pattern claims this wording yet |
| `minions gain #% of their maximum life as extra maximum energy shield` | 4 | 0 |  |  | it is somebody else's number, not the character's |
| `minions have #% increased cooldown recovery rate` | 4 | 0 |  |  | it is somebody else's number, not the character's |
| `other modifiers to movement speed except for sprinting do not apply` | 4 | 0 |  |  | it is a roll from a patch that has been replaced |
| `recover #% of maximum mana when you consume a power charge` | 4 | 0 |  |  | it only applies if something is true |
| `recover #% of missing life before being hit by an enemy` | 4 | 0 |  |  | it is a roll from a patch that has been replaced |
| `recover #% of your maximum life when an enemy dies in your presence` | 4 | 0 |  |  | the item has several versions and the plan does not record which one |
| `recover #% of your maximum mana when an enemy dies in your presence` | 4 | 0 |  |  | the item has several versions and the plan does not record which one |
| `spells gain #% of damage as extra chaos damage` | 4 | 4 | extra-chaos-damage | flat |  |
| `targets can be affected by +# of your poisons at the same time` | 4 | 0 |  |  | it is a rule about the item rather than a number |
| `totems gain +#% to all maximum elemental resistances` | 4 | 0 |  |  | it is somebody else's number, not the character's |
| `you and allies in your presence have #% increased attack speed` | 4 | 0 |  |  | the item has several versions and the plan does not record which one |
| `you and allies in your presence have #% increased cast speed` | 4 | 0 |  |  | the item has several versions and the plan does not record which one |
| `your maximum number of power charges` | 4 | 0 |  |  | no pattern claims this wording yet |
| `# life gained when you block` | 3 | 0 |  |  | it only applies if something is true |
| `# physical damage taken on minion death` | 3 | 0 |  |  | the item has several versions and the plan does not record which one |
| `#% additional physical damage reduction` | 3 | 3 | damage-reduction | flat |  |
| `#% chance for lightning damage with hits to be lucky` | 3 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% chance for projectiles to pierce enemies within #m distance of you` | 3 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% chance for spell damage with critical hits to be lucky` | 3 | 0 |  |  | the item has several versions and the plan does not record which one |
| `#% chance for trigger skills to refund half of energy spent` | 3 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% chance to aggravate bleeding on targets you hit with attacks` | 3 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% chance to deal your thorns damage to enemies you hit with melee attacks` | 3 | 0 |  |  | the item has several versions and the plan does not record which one |
| `#% chance to impale on spell hit` | 3 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% chance to intimidate enemies for # seconds on hit` | 3 | 0 |  |  | the item has several versions and the plan does not record which one |
| `#% chance when collecting an elemental infusion to gain an` | 3 | 0 |  |  | it only applies if something is true |
| `#% increased accuracy rating while shapeshifted` | 3 | 0 |  |  | it only applies while something is true |
| `#% increased amount of life leeched while shapeshifted` | 3 | 0 |  |  | it only applies while something is true |
| `#% increased amount recovered` | 3 | 0 |  |  | no pattern claims this wording yet |
| `#% increased area of effect for attacks per # intelligence` | 3 | 0 |  |  | it scales off another number the plan does not hold |
| `#% increased area of effect if you have stunned an enemy recently` | 3 | 0 |  |  | it only applies if something is true |
| `#% increased armour evasion and energy shield while channelling` | 3 | 0 |  |  | it only applies while something is true |
| `#% increased armour if you have been hit recently` | 3 | 0 |  |  | it only applies if something is true |
| `#% increased arrow speed` | 3 | 0 |  |  | no pattern claims this wording yet |
| `#% increased attack and cast speed if you ve summoned a totem recently` | 3 | 0 |  |  | it only applies if something is true |
| `#% increased attack damage if you have shapeshifted to an animal form recently` | 3 | 0 |  |  | it only applies if something is true |
| `#% increased attack damage while dual wielding` | 3 | 0 |  |  | it only applies while something is true |
| `#% increased ballista critical damage bonus` | 3 | 0 |  |  | no pattern claims this wording yet |
| `#% increased ballista critical hit chance` | 3 | 0 |  |  | no pattern claims this wording yet |
| `#% increased ballista immobilisation buildup` | 3 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% increased cast speed if you ve dealt a critical hit recently` | 3 | 0 |  |  | it only applies if something is true |
| `#% increased cast speed with cold skills` | 3 | 0 |  |  | no pattern claims this wording yet |
| `#% increased chance to inflict ailments against rare or unique enemies` | 3 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% increased chance to inflict ailments with projectiles` | 3 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% increased charges` | 3 | 0 |  |  | no pattern claims this wording yet |
| `#% increased charges gained` | 3 | 0 |  |  | no pattern claims this wording yet |
| `#% increased cost efficiency` | 3 | 0 |  |  | no pattern claims this wording yet |
| `#% increased cost efficiency of attacks` | 3 | 0 |  |  | no pattern claims this wording yet |
| `#% increased critical damage bonus against enemies that are on full life` | 3 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased critical damage bonus with daggers` | 3 | 0 |  |  | no pattern claims this wording yet |
| `#% increased critical damage bonus with quarterstaves` | 3 | 0 |  |  | no pattern claims this wording yet |
| `#% increased critical damage bonus with spears` | 3 | 0 |  |  | no pattern claims this wording yet |
| `#% increased critical hit chance against blinded enemies` | 3 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased critical hit chance against marked enemies` | 3 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased critical hit chance if you haven t dealt a critical hit recently` | 3 | 0 |  |  | it only applies if something is true |
| `#% increased critical hit chance while shapeshifted` | 3 | 0 |  |  | it only applies while something is true |
| `#% increased critical hit chance with crossbows` | 3 | 0 |  |  | no pattern claims this wording yet |
| `#% increased damage for each type of elemental ailment on enemy` | 3 | 0 |  |  | it scales off another number the plan does not hold |
| `#% increased damage while leeching` | 3 | 0 |  |  | it only applies while something is true |
| `#% increased damage while you have a totem` | 3 | 0 |  |  | it only applies while something is true |
| `#% increased damage while you have an active charm` | 3 | 0 |  |  | it only applies while something is true |
| `#% increased damage with axes` | 3 | 3 | damage-with-axes | increased |  |
| `#% increased damage with daggers` | 3 | 3 | damage-with-daggers | increased |  |
| `#% increased damage with hits against enemies that are on full life` | 3 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased damage with hits against ignited enemies` | 3 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased damage with hits against rare and unique enemies` | 3 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased effect of puppet master` | 3 | 0 |  |  | no pattern claims this wording yet |
| `#% increased effect of socketed augment items` | 3 | 0 |  |  | no pattern claims this wording yet |
| `#% increased effect of socketed soul cores` | 3 | 0 |  |  | it is a roll from a patch that has been replaced |
| `#% increased energy shield recharge rate while shapeshifted` | 3 | 0 |  |  | it only applies while something is true |
| `#% increased evasion rating if you have hit an enemy recently` | 3 | 0 |  |  | it only applies if something is true |
| `#% increased evasion rating when on full life` | 3 | 0 |  |  | it only applies if something is true |
| `#% increased fire damage per endurance charge consumed recently` | 3 | 0 |  |  | it only applies for a while after something happens |
| `#% increased flask and charm charges gained` | 3 | 0 |  |  | no pattern claims this wording yet |
| `#% increased global armour evasion and energy shield` | 3 | 3 | armour + evasion + energy-shield | increased |  |
| `#% increased global armour evasion and energy shield per socket filled` | 3 | 0 |  |  | the item has several versions and the plan does not record which one |
| `#% increased global physical damage` | 3 | 3 | damage-physical | increased |  |
| `#% increased hazard area of effect` | 3 | 0 |  |  | no pattern claims this wording yet |
| `#% increased hazard duration` | 3 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% increased ice crystal life` | 3 | 0 |  |  | no pattern claims this wording yet |
| `#% increased life recovery from flasks used when on low life` | 3 | 0 |  |  | it only applies if something is true |
| `#% increased life regeneration rate while on low life` | 3 | 0 |  |  | it only applies while something is true |
| `#% increased life regeneration rate while shapeshifted` | 3 | 0 |  |  | it only applies while something is true |
| `#% increased magnitude of bleeding you inflict with critical hits` | 3 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% increased magnitude of impales inflicted with spells` | 3 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% increased magnitude of jagged ground you create` | 3 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% increased maximum life for each corrupted item equipped` | 3 | 0 |  |  | it scales off another number the plan does not hold |
| `#% increased maximum runic ward` | 3 | 0 |  |  | no pattern claims this wording yet |
| `#% increased melee attack speed` | 3 | 0 |  |  | no pattern claims this wording yet |
| `#% increased melee damage against heavy stunned enemies` | 3 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased melee damage against immobilised enemies` | 3 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased melee damage with hits at close range` | 3 | 0 |  |  | no pattern claims this wording yet |
| `#% increased movement speed if you ve killed recently` | 3 | 0 |  |  | it only applies if something is true |
| `#% increased projectile stun buildup` | 3 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% increased skill speed with channelling skills` | 3 | 0 |  |  | no pattern claims this wording yet |
| `#% increased spell damage while on full energy shield` | 3 | 0 |  |  | it only applies while something is true |
| `#% increased spell damage while you have arcane surge` | 3 | 0 |  |  | it only applies while something is true |
| `#% increased spell physical damage` | 3 | 0 |  |  | no pattern claims this wording yet |
| `#% increased stun buildup with melee damage` | 3 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% increased stun buildup with quarterstaves` | 3 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% increased stun threshold while on full life` | 3 | 0 |  |  | it only applies while something is true |
| `#% increased weapon swap speed` | 3 | 0 |  |  | no pattern claims this wording yet |
| `#% less maximum life` | 3 | 2 | life | more | 1 of them: the item has several versions and the plan does not record which one |
| `#% life recovery from flasks also applies to runic ward` | 3 | 0 |  |  | it converts one number into another |
| `#% of damage taken recouped as life while channelling` | 3 | 0 |  |  | it only applies while something is true |
| `#% of leech is instant` | 3 | 0 |  |  | no pattern claims this wording yet |
| `#% of spell damage leeched as life` | 3 | 0 |  |  | no pattern claims this wording yet |
| `#% reduced area of effect` | 3 | 3 | area-of-effect | increased |  |
| `#% reduced armour break taken` | 3 | 0 |  |  | no pattern claims this wording yet |
| `#% reduced attribute requirements` | 3 | 1 | attribute-requirements | increased | 2 of them: it multiplies the item's own number, not the character's |
| `#% reduced critical hit chance` | 3 | 3 | critical-chance | increased |  |
| `#% reduced elemental ailment duration on you` | 3 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% reduced movement speed penalty while actively blocking` | 3 | 0 |  |  | it only applies while something is true |
| `#% reduced projectile speed` | 3 | 3 | projectile-speed | increased |  |
| `#% reduced shock duration on you` | 3 | 0 |  |  | the vocabulary has no name for this number yet |
| `#has +# to maximum energy shield per player level` | 3 | 0 |  |  | it scales off another number the plan does not hold |
| `+# maximum stacks of puppet master` | 3 | 0 |  |  | no pattern claims this wording yet |
| `+# metres to dodge roll distance` | 3 | 0 |  |  | no pattern claims this wording yet |
| `+# prefix modifiers allowed` | 3 | 0 |  |  | it is a rule about the item rather than a number |
| `+# strength requirement` | 3 | 0 |  |  | no pattern claims this wording yet |
| `+# suffix modifiers allowed` | 3 | 0 |  |  | it is a rule about the item rather than a number |
| `+# to level of all curse skills` | 3 | 3 | skills-tab | flat |  |
| `+# to level of all mark skills` | 3 | 3 | skills-tab | flat |  |
| `+# to level of all skills` | 3 | 3 | skills-all | flat |  |
| `+# to level of all trap skill gems` | 3 | 3 | skills-tab | flat |  |
| `+# to maximum rage while shapeshifted` | 3 | 0 |  |  | it only applies while something is true |
| `+# to maximum spirit per # maximum life` | 3 | 0 |  |  | it is a roll from a patch that has been replaced |
| `+# to spirit per socket filled` | 3 | 0 |  |  | the item has several versions and the plan does not record which one |
| `+# to spirit while you have at least # dexterity` | 3 | 0 |  |  | the item has several versions and the plan does not record which one |
| `+# to spirit while you have at least # intelligence` | 3 | 0 |  |  | the item has several versions and the plan does not record which one |
| `+# to spirit while you have at least # strength` | 3 | 0 |  |  | the item has several versions and the plan does not record which one |
| `+#% to all elemental resistances per socket filled` | 3 | 0 |  |  | the item has several versions and the plan does not record which one |
| `+#% to all maximum resistances` | 3 | 3 | resistance-fire-max + resistance-cold-max + resistance-lightning-max | flat |  |
| `+#% to cold and lightning resistances per equipped item with a fire resistance modifier` | 3 | 0 |  |  | the item has several versions and the plan does not record which one |
| `+#% to fire and cold resistances per equipped item with a lightning resistance modifier` | 3 | 0 |  |  | the item has several versions and the plan does not record which one |
| `+#% to fire and lightning resistances per equipped item with a cold resistance modifier` | 3 | 0 |  |  | the item has several versions and the plan does not record which one |
| `-# physical damage taken from attack hits` | 3 | 0 |  |  | no pattern claims this wording yet |
| `-# prefix modifiers allowed` | 3 | 0 |  |  | it is a rule about the item rather than a number |
| `-# suffix modifiers allowed` | 3 | 0 |  |  | it is a rule about the item rather than a number |
| `-#% to chaos resistance` | 3 | 3 | resistance-chaos | flat |  |
| `additional elemental infusion of the same type` | 3 | 0 |  |  | no pattern claims this wording yet |
| `allies in your presence deal # to # added attack chaos damage` | 3 | 0 |  |  | it is somebody else's number, not the character's |
| `allies in your presence gain #% of damage as extra chaos damage` | 3 | 0 |  |  | the item has several versions and the plan does not record which one |
| `allies in your presence have +#% to all elemental resistances` | 3 | 0 |  |  | it is somebody else's number, not the character's |
| `allies in your presence regenerate # life per second` | 3 | 0 |  |  | it scales off another number the plan does not hold |
| `allies in your presence regenerate #% of your maximum life per second` | 3 | 0 |  |  | it scales off another number the plan does not hold |
| `allocates # sinister jewel sockets` | 3 | 0 |  |  | the item has several versions and the plan does not record which one |
| `alternating every # seconds` | 3 | 0 |  |  | no pattern claims this wording yet |
| `attacks have #% chance to cause bleeding` | 3 | 0 |  |  | it is a chance of something happening, not an amount |
| `attacks with one-handed weapons have #% increased chance to inflict ailments` | 3 | 0 |  |  | it is a chance of something happening, not an amount |
| `banner skills have #% increased aura magnitudes` | 3 | 0 |  |  | no pattern claims this wording yet |
| `base critical hit chance for attacks with weapons is #%` | 3 | 0 |  |  | it is a chance of something happening, not an amount |
| `bifurcates critical hits` | 3 | 0 |  |  | no pattern claims this wording yet |
| `can have # additional crafted modifier` | 3 | 0 |  |  | it is a rule about the item rather than a number |
| `cannot be blinded` | 3 | 0 |  |  | no pattern claims this wording yet |
| `cannot load or fire ammunition` | 3 | 0 |  |  | no pattern claims this wording yet |
| `cannot use projectile attacks` | 3 | 0 |  |  | no pattern claims this wording yet |
| `companions gain #% damage as extra cold damage` | 3 | 0 |  |  | it is somebody else's number, not the character's |
| `companions have #% increased attack speed` | 3 | 0 |  |  | it is somebody else's number, not the character's |
| `companions have #% increased movement speed` | 3 | 0 |  |  | it is somebody else's number, not the character's |
| `corrupted blood cannot be inflicted on you` | 3 | 0 |  |  | no pattern claims this wording yet |
| `curses you inflict can affect hexproof enemies` | 3 | 0 |  |  | it changes what enemies have, not what the character has |
| `detonator skills have #% increased area of effect` | 3 | 0 |  |  | no pattern claims this wording yet |
| `enemies blinded by you have #% reduced critical hit chance` | 3 | 0 |  |  | it changes what enemies have, not what the character has |
| `enemies have an accuracy penalty against you based on distance` | 3 | 0 |  |  | it changes what enemies have, not what the character has |
| `enemies you curse have -#% to chaos resistance` | 3 | 0 |  |  | it changes what enemies have, not what the character has |
| `enemies you mark take #% increased damage` | 3 | 0 |  |  | it changes what enemies have, not what the character has |
| `every rage also grants #% increased armour` | 3 | 0 |  |  | no pattern claims this wording yet |
| `every rage also grants #% increased stun threshold` | 3 | 0 |  |  | the vocabulary has no name for this number yet |
| `gain # rage on melee axe hit` | 3 | 0 |  |  | no pattern claims this wording yet |
| `gain #% of damage as extra damage of all elements` | 3 | 0 |  |  | it converts one number into another |
| `gain #% of physical damage as extra fire damage` | 3 | 3 | extra-fire-damage | flat |  |
| `gain arcane surge when a minion dies` | 3 | 0 |  |  | the item has several versions and the plan does not record which one |
| `gain onslaught for # seconds when a minion dies` | 3 | 0 |  |  | the item has several versions and the plan does not record which one |
| `gain physical thorns damage equal to #% of item armour on equipped body armour` | 3 | 0 |  |  | it scales off another number the plan does not hold |
| `gains # charges per second` | 3 | 0 |  |  | it scales off another number the plan does not hold |
| `grants # additional skill slot` | 3 | 0 |  |  | no pattern claims this wording yet |
| `grants # life per enemy hit` | 3 | 0 |  |  | it scales off another number the plan does not hold |
| `grants # rage on hit` | 3 | 0 |  |  | it happens on an event rather than standing |
| `grants skill level # bone blast` | 3 | 0 |  |  | it grants a skill rather than a number |
| `grants skill level # coiling bolts` | 3 | 0 |  |  | it grants a skill rather than a number |
| `grants skill level # discipline` | 3 | 0 |  |  | it grants a skill rather than a number |
| `grants skill level # feast of flesh` | 3 | 0 |  |  | it grants a skill rather than a number |
| `grants skill level # freezing shards` | 3 | 0 |  |  | it grants a skill rather than a number |
| `grants skill level # malice` | 3 | 0 |  |  | it grants a skill rather than a number |
| `grants skill level # mana drain` | 3 | 0 |  |  | it grants a skill rather than a number |
| `grants skill level # mirror of refraction` | 3 | 0 |  |  | it grants a skill rather than a number |
| `grants skill level # power siphon` | 3 | 0 |  |  | it grants a skill rather than a number |
| `grants skill level # solar orb` | 3 | 0 |  |  | it grants a skill rather than a number |
| `grants skill level # spiraling conspiracy` | 3 | 0 |  |  | it grants a skill rather than a number |
| `grants skill level # volatile dead` | 3 | 0 |  |  | it grants a skill rather than a number |
| `grenades have #% chance to activate a second time` | 3 | 0 |  |  | it is a chance of something happening, not an amount |
| `hits break #% increased armour on targets with ailments` | 3 | 0 |  |  | no pattern claims this wording yet |
| `hits have #% reduced critical hit chance against you` | 3 | 0 |  |  | it changes what enemies have, not what the character has |
| `ignites you inflict spread to other enemies that stay within # metres for # second` | 3 | 0 |  |  | it changes what enemies have, not what the character has |
| `increases movement speed by #% plus #% per # evasion rating up to a maximum of #%` | 3 | 0 |  |  | it is a roll from a patch that has been replaced |
| `invocated skills have #% increased maximum energy` | 3 | 0 |  |  | no pattern claims this wording yet |
| `leech life #% faster` | 3 | 0 |  |  | no pattern claims this wording yet |
| `lose #% of maximum life per second` | 3 | 0 |  |  | it scales off another number the plan does not hold |
| `minions break armour equal to #% of physical damage dealt` | 3 | 0 |  |  | it scales off another number the plan does not hold |
| `minions deal #% increased damage if you ve hit recently` | 3 | 0 |  |  | it only applies if something is true |
| `minions have #% increased magnitude of damaging ailments` | 3 | 0 |  |  | it is somebody else's number, not the character's |
| `minions have #% increased movement speed` | 3 | 0 |  |  | it is somebody else's number, not the character's |
| `minions have +#% to cold resistance` | 3 | 0 |  |  | it is somebody else's number, not the character's |
| `minions have +#% to fire resistance` | 3 | 0 |  |  | it is somebody else's number, not the character's |
| `minions have +#% to lightning resistance` | 3 | 0 |  |  | it is somebody else's number, not the character's |
| `minions regenerate #% of maximum life per second` | 3 | 0 |  |  | it scales off another number the plan does not hold |
| `on hitting an enemy gains maximum added cold damage equal to the enemy s power for # seconds up to a total of #` | 3 | 0 |  |  | it scales off another number the plan does not hold |
| `projectile attacks have a #% chance to fire two additional projectiles while moving` | 3 | 0 |  |  | it only applies while something is true |
| `projectiles have #% increased critical damage bonus against enemies within #m` | 3 | 0 |  |  | it changes what enemies have, not what the character has |
| `recover # runic ward when you block` | 3 | 0 |  |  | it only applies if something is true |
| `recover #% of maximum life on killing a poisoned enemy` | 3 | 0 |  |  | it changes what enemies have, not what the character has |
| `recover #% of maximum mana when a charm is used` | 3 | 0 |  |  | it only applies if something is true |
| `regenerate #% of maximum life per second if you ve used a life flask in the past # seconds` | 3 | 0 |  |  | it only applies if something is true |
| `reserves #% of life` | 3 | 0 |  |  | no pattern claims this wording yet |
| `skills gain #% of mana cost as extra life cost` | 3 | 0 |  |  | it converts one number into another |
| `skills have #% chance to not remove charges but still count as consuming them` | 3 | 0 |  |  | it is a chance of something happening, not an amount |
| `skills have #% chance to not remove elemental infusions but still count as consuming them` | 3 | 0 |  |  | it is a chance of something happening, not an amount |
| `take #% less damage from hits` | 3 | 0 |  |  | no pattern claims this wording yet |
| `take #% less damage over time` | 3 | 0 |  |  | no pattern claims this wording yet |
| `this item gains bonuses from socketed items as though it was a helmet` | 3 | 0 |  |  | no pattern claims this wording yet |
| `this item gains bonuses from socketed items as though it was boots` | 3 | 0 |  |  | no pattern claims this wording yet |
| `this item gains bonuses from socketed items as though it was gloves` | 3 | 0 |  |  | no pattern claims this wording yet |
| `thorns damage has #% chance to ignore enemy armour` | 3 | 0 |  |  | it is a chance of something happening, not an amount |
| `upgrades a socketed rune` | 3 | 0 |  |  | no pattern claims this wording yet |
| `used when you are affected by a slow` | 3 | 0 |  |  | it only applies if something is true |
| `used when you become frozen` | 3 | 0 |  |  | it only applies if something is true |
| `used when you become ignited` | 3 | 0 |  |  | it only applies if something is true |
| `used when you become poisoned` | 3 | 0 |  |  | it only applies if something is true |
| `used when you become shocked` | 3 | 0 |  |  | it only applies if something is true |
| `used when you become stunned` | 3 | 0 |  |  | it only applies if something is true |
| `used when you kill a rare or unique enemy` | 3 | 0 |  |  | it only applies if something is true |
| `used when you start bleeding` | 3 | 0 |  |  | it only applies if something is true |
| `used when you take chaos damage from a hit` | 3 | 0 |  |  | it only applies if something is true |
| `used when you take cold damage from a hit` | 3 | 0 |  |  | it only applies if something is true |
| `used when you take fire damage from a hit` | 3 | 0 |  |  | it only applies if something is true |
| `used when you take lightning damage from a hit` | 3 | 0 |  |  | it only applies if something is true |
| `using a mana flask grants guard equal to #% of flask s recovery amount for # seconds` | 3 | 0 |  |  | the item has several versions and the plan does not record which one |
| `warcries explode corpses dealing #% of their life as physical damage` | 3 | 0 |  |  | no pattern claims this wording yet |
| `when socketed into a unique kalguuran or ezomyte item destroys the item to create a rune imbued with that item s power` | 3 | 0 |  |  | it only applies if something is true |
| `you and allies in your presence have #% increased accuracy rating` | 3 | 0 |  |  | the item has several versions and the plan does not record which one |
| `you and allies in your presence have #% increased cooldown recovery rate` | 3 | 0 |  |  | the item has several versions and the plan does not record which one |
| `you and allies in your presence have +#% to chaos resistance` | 3 | 0 |  |  | the item has several versions and the plan does not record which one |
| `your speed is unaffected by slows` | 3 | 0 |  |  | no pattern claims this wording yet |
| `# life regeneration per second per socket filled` | 2 | 0 |  |  | the item has several versions and the plan does not record which one |
| `# to # added cold damage per frenzy charge` | 2 | 0 |  |  | it scales off another number the plan does not hold |
| `#% chance for charms you use to not consume charges` | 2 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% chance for remnants you pick up to count as picking up an additional remnant` | 2 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% chance for shapeshift slam skills you use yourself to cause an additional aftershock` | 2 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% chance for skills to retain #% of glory on use` | 2 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% chance to avoid being ignited` | 2 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% chance to avoid being shocked` | 2 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% chance to avoid being stunned` | 2 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% chance to avoid chaos damage from hits` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `#% chance to avoid death from hits` | 2 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% chance to avoid elemental ailments` | 2 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% chance to avoid physical damage from hits` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `#% chance to gain a power charge on critical hit` | 2 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% chance to gain volatility when you are stunned` | 2 | 0 |  |  | it only applies if something is true |
| `#% chance to hinder enemies on hit with spells` | 2 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% chance to inflict bleeding on critical hit with attacks` | 2 | 0 |  |  | it is a chance of something happening, not an amount |
| `#% chance when you reload a crossbow to be immediate` | 2 | 0 |  |  | it only applies if something is true |
| `#% faster start of energy shield recharge when not on full life` | 2 | 0 |  |  | it only applies if something is true |
| `#% increased accuracy rating against rare or unique enemies` | 2 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased accuracy rating at close range` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased accuracy rating while dual wielding` | 2 | 0 |  |  | it only applies while something is true |
| `#% increased accuracy rating with spears` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased accuracy rating with two handed melee weapons` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased area of effect for skills used by totems` | 2 | 0 |  |  | it is somebody else's number, not the character's |
| `#% increased armour +# to maximum mana` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased armour and energy shield +# to maximum mana` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased armour and evasion +# to maximum mana` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased armour if you haven t been hit recently` | 2 | 0 |  |  | it only applies if something is true |
| `#% increased attack and cast speed` | 2 | 2 | speed-attack + speed-cast | increased |  |
| `#% increased attack damage against bleeding enemies` | 2 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased attack damage if you have been heavy stunned recently` | 2 | 0 |  |  | it only applies if something is true |
| `#% increased attack damage per # item armour and evasion on equipped shield` | 2 | 0 |  |  | it scales off another number the plan does not hold |
| `#% increased attack damage while you have no life flask uses left` | 2 | 0 |  |  | it only applies while something is true |
| `#% increased attack physical damage` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased attack speed during any flask effect` | 2 | 0 |  |  | it only applies while something is true |
| `#% increased attack speed if you ve been hit recently` | 2 | 0 |  |  | it only applies if something is true |
| `#% increased attack speed while leeching` | 2 | 0 |  |  | it only applies while something is true |
| `#% increased attack speed while your companion is in your presence` | 2 | 0 |  |  | it only applies while something is true |
| `#% increased attack speed with crossbows` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased attack speed with one handed weapons` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased block recovery` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased cast speed for each different spell you ve cast in the last eight seconds` | 2 | 0 |  |  | it scales off another number the plan does not hold |
| `#% increased cast speed gain #% of elemental damage as extra cold damage` | 2 | 0 |  |  | it converts one number into another |
| `#% increased cast speed when on full life` | 2 | 0 |  |  | it only applies if something is true |
| `#% increased cast speed when on low life` | 2 | 0 |  |  | it only applies if something is true |
| `#% increased cast speed while on full mana` | 2 | 0 |  |  | it only applies while something is true |
| `#% increased chaos damage for each corrupted item equipped` | 2 | 0 |  |  | it scales off another number the plan does not hold |
| `#% increased cold damage if you ve collected a cold infusion in the last # seconds` | 2 | 0 |  |  | it only applies if something is true |
| `#% increased cooldown recovery rate for throwing traps` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased cost of skills for each # total mana spent recently` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `#% increased critical damage bonus if you haven t dealt a critical hit recently` | 2 | 0 |  |  | it only applies if something is true |
| `#% increased critical damage bonus per power charge` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `#% increased critical damage bonus with bows` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased critical hit chance against dazed enemies` | 2 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased critical hit chance against enemies that are on full life` | 2 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased critical hit chance against enemies that have entered your presence recently` | 2 | 0 |  |  | it only applies for a while after something happens |
| `#% increased critical hit chance against humanoids` | 2 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased critical hit chance if you have killed recently` | 2 | 0 |  |  | it only applies if something is true |
| `#% increased critical hit chance if you have shapeshifted to an animal form recently` | 2 | 0 |  |  | it only applies if something is true |
| `#% increased critical hit chance with one handed melee weapons` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased critical hit chance with quarterstaves` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased critical hit chance with spears` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased damage against dazed enemies` | 2 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased damage against demons` | 2 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased damage if you ve dealt a critical hit in the past # seconds` | 2 | 0 |  |  | it only applies if something is true |
| `#% increased damage if you ve triggered a skill recently` | 2 | 0 |  |  | it only applies if something is true |
| `#% increased damage taken` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased damage while affected by a herald` | 2 | 0 |  |  | it only applies while something is true |
| `#% increased damage with hits against enemies affected by ailments` | 2 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased damage with hits against hindered enemies` | 2 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased damage with quarterstaves` | 2 | 2 | damage-with-quarterstaves | increased |  |
| `#% increased damage with unarmed attacks` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased deflection rating while moving` | 2 | 0 |  |  | it only applies while something is true |
| `#% increased duration of ailments on beasts` | 2 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% increased duration of elemental ailments on enemies` | 2 | 0 |  |  | the item has several versions and the plan does not record which one |
| `#% increased effect of jewel socket passive skills` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `#% increased effect of small passive skills in radius` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased effect of socketed runes` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased elemental ailment application if you have shapeshifted to an animal form recently` | 2 | 0 |  |  | it only applies if something is true |
| `#% increased energy shield +# to maximum mana` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased evasion and energy shield +# to maximum mana` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased evasion rating +# to maximum mana` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased evasion rating if you haven t been hit recently` | 2 | 0 |  |  | it only applies if something is true |
| `#% increased evasion rating if you ve dodge rolled recently` | 2 | 0 |  |  | it only applies if something is true |
| `#% increased evasion rating while you have energy shield` | 2 | 0 |  |  | it only applies while something is true |
| `#% increased experience gain` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased fire damage if you ve collected a fire infusion in the last # seconds` | 2 | 0 |  |  | it only applies if something is true |
| `#% increased freeze buildup with empowered attacks` | 2 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% increased freeze duration on enemies` | 2 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased global evasion rating when on low life` | 2 | 0 |  |  | it only applies if something is true |
| `#% increased grenade area of effect` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased hazard immobilisation buildup` | 2 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% increased hinder duration` | 2 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% increased immobilisation buildup against constructs` | 2 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased life cost efficiency` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased life regeneration rate during effect of any life flask` | 2 | 0 |  |  | it only applies while something is true |
| `#% increased life regeneration rate while moving` | 2 | 0 |  |  | it only applies while something is true |
| `#% increased lightning damage if you ve collected a lightning infusion in the last # seconds` | 2 | 0 |  |  | it only applies if something is true |
| `#% increased magnitude of abyssal wasting you inflict` | 2 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% increased magnitude of daze` | 2 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% increased magnitude of elemental ailments you inflict with spells` | 2 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% increased magnitude of non-damaging ailments you inflict with critical hits` | 2 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% increased magnitude of poison you inflict on targets that are not poisoned` | 2 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% increased mana regeneration rate while not on low mana` | 2 | 0 |  |  | it only applies while something is true |
| `#% increased mana regeneration rate while shapeshifted` | 2 | 0 |  |  | it only applies while something is true |
| `#% increased mana regeneration rate while shocked` | 2 | 0 |  |  | it only applies while something is true |
| `#% increased mana reservation efficiency of skills` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased maximum darkness` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased melee critical hit chance` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased minion accuracy rating` | 2 | 0 |  |  | it is somebody else's number, not the character's |
| `#% increased minion damage per different command skill used in the past # seconds` | 2 | 0 |  |  | it scales off another number the plan does not hold |
| `#% increased movement speed when on full life` | 2 | 0 |  |  | it only applies if something is true |
| `#% increased movement speed while affected by an ailment` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `#% increased parry range` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased physical damage while shapeshifted` | 2 | 0 |  |  | it only applies while something is true |
| `#% increased projectile speed for spell skills` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased reload speed` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased runic ward` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased shock chance against electrocuted enemies` | 2 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased skill speed if you ve consumed a frenzy charge recently` | 2 | 0 |  |  | it only applies if something is true |
| `#% increased spell damage +# to maximum mana` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased spell damage for each # total mana you have spent recently` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `#% increased spell damage if you have shapeshifted to human form recently` | 2 | 0 |  |  | it only applies if something is true |
| `#% increased spell damage per # intelligence` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `#% increased spell damage per # maximum mana` | 2 | 0 |  |  | it scales off another number the plan does not hold |
| `#% increased stun buildup against enemies within # metres` | 2 | 0 |  |  | it changes what enemies have, not what the character has |
| `#% increased stun buildup if you have shapeshifted to an animal form recently` | 2 | 0 |  |  | it only applies if something is true |
| `#% increased stun duration` | 2 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% increased thorns critical damage bonus` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased totem placement range` | 2 | 0 |  |  | it is somebody else's number, not the character's |
| `#% increased unarmed attack speed` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased volatility explosion delay` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% increased warcry buff effect` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% less attack damage` | 2 | 2 | damage-attack | more |  |
| `#% less maximum mana` | 2 | 1 | mana | more | 1 of them: the item has several versions and the plan does not record which one |
| `#% less spirit` | 2 | 1 | spirit | more | 1 of them: the item has several versions and the plan does not record which one |
| `#% of cold damage converted to lightning damage` | 2 | 0 |  |  | it converts one number into another |
| `#% of damage from hits is taken from your spectres life before you` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% of damage taken from deflected hits recouped as life` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% of damage taken from hits bypasses energy shield if energy shield is below half` | 2 | 0 |  |  | it only applies if something is true |
| `#% of elemental damage converted to chaos damage` | 2 | 0 |  |  | it converts one number into another |
| `#% of melee physical damage taken reflected to attacker` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% of physical damage from hits taken as lightning damage` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `#% reduced chill duration on you` | 2 | 0 |  |  | the vocabulary has no name for this number yet |
| `#% reduced duration of ignite shock and chill on enemies` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `#% reduced effect of non-damaging ailments on you` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% reduced energy shield recharge rate` | 2 | 2 | energy-shield-recharge | increased |  |
| `#% reduced flask life recovery rate` | 2 | 2 | flask-life-recovery | increased |  |
| `#% reduced grenade detonation time` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% reduced life recovery rate` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% reduced life regeneration rate` | 2 | 2 | life-regeneration | increased |  |
| `#% reduced poison duration` | 2 | 2 | poison-duration | increased |  |
| `#% reduced projectile speed for spell skills` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% reduced recovery rate` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% reduced reload speed` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% reduced spirit` | 2 | 2 | spirit | increased |  |
| `#% reduced volatility explosion delay` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% slower start of energy shield recharge` | 2 | 0 |  |  | no pattern claims this wording yet |
| `#% to gain archon of undeath when you create an offering` | 2 | 0 |  |  | it only applies if something is true |
| `#grants skill level # alchemist s boon` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # archmage` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # arctic armour` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # attrition` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # barkskin` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # barrier invocation` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # berserk` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # blink` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # briarpatch` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # cast on critical` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # cast on dodge` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # cast on elemental ailment` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # cast on minion death` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # charge regulation` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # combat frenzy` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # convalescence` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # defiance banner` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # dread banner` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # elemental conflux` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # elemental invocation` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # eternal rage` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # feral invocation` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # ghost dance` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # herald of ash` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # herald of blood` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # herald of ice` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # herald of plague` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # herald of thunder` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # iron ward` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # lingering illusion` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # magma barrier` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # mana remnants` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # mirage archer` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # overwhelming presence` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # plague bearer` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # raging spirits` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # ravenous swarm` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # reaper s invocation` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # rhoa mount` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # sacrifice` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # savage fury` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # scavenged plating` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # shard scavenger` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # siphon elements` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # time of need` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # trail of caltrops` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # trinity` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # war banner` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # wind dancer` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # withering presence` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#grants skill level # wolf pack` | 2 | 0 |  |  | it grants a skill rather than a number |
| `#has +# to maximum runic ward per player level` | 2 | 0 |  |  | it scales off another number the plan does not hold |
| `+# charm slots` | 2 | 2 | charm-slots | flat |  |
| `+# to accuracy rating #% increased light radius` | 2 | 0 |  |  | no pattern claims this wording yet |
| `+# to ailment threshold` | 2 | 2 | ailment-threshold | flat |  |
| `+# to all attributes per socket filled` | 2 | 0 |  |  | the item has several versions and the plan does not record which one |
| `+# to armour per strength` | 2 | 0 |  |  | it scales off another number the plan does not hold |
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
| `+# to limit for elemental skills` | 2 | 0 |  |  | no pattern claims this wording yet |
| `+# to maximum life per socket filled` | 2 | 0 |  |  | the item has several versions and the plan does not record which one |
| `+# to maximum mana per socket filled` | 2 | 0 |  |  | the item has several versions and the plan does not record which one |
| `+# to stun threshold per # maximum runic ward` | 2 | 0 |  |  | it scales off another number the plan does not hold |
| `+# to stun threshold per dexterity` | 2 | 0 |  |  | it scales off another number the plan does not hold |
| `+# to stun threshold per socket filled` | 2 | 0 |  |  | the item has several versions and the plan does not record which one |
| `+# to weapon range` | 2 | 0 |  |  | no pattern claims this wording yet |
| `+#% to all elemental resistances per socketed grand spectrum` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `+#% to all resistances for each corrupted item equipped` | 2 | 0 |  |  | it scales off another number the plan does not hold |
| `+#% to chaos resistance per socket filled` | 2 | 0 |  |  | the item has several versions and the plan does not record which one |
| `+#% to cold and chaos resistances` | 2 | 2 | resistance-cold + resistance-chaos | flat |  |
| `+#% to fire and chaos resistances` | 2 | 2 | resistance-fire + resistance-chaos | flat |  |
| `+#% to fire spell critical hit chance` | 2 | 0 |  |  | no pattern claims this wording yet |
| `+#% to lightning and chaos resistances` | 2 | 2 | resistance-lightning + resistance-chaos | flat |  |
| `-# to maximum rage` | 2 | 2 | maximum-rage | flat |  |
| `-#% to all maximum elemental resistances` | 2 | 2 | resistance-fire-max + resistance-cold-max + resistance-lightning-max | flat |  |
| `-#% to amount of damage prevented by deflection` | 2 | 0 |  |  | no pattern claims this wording yet |
| `accuracy rating is doubled` | 2 | 0 |  |  | no pattern claims this wording yet |
| `aggravate bleeding on targets you critically hit with attacks` | 2 | 0 |  |  | no pattern claims this wording yet |
| `all damage from hits against bleeding targets contributes to chill magnitude` | 2 | 0 |  |  | it changes what enemies have, not what the character has |
| `all damage from hits against poisoned targets contributes to chill magnitude` | 2 | 0 |  |  | it changes what enemies have, not what the character has |
| `all damage taken from hits while bleeding contributes to magnitude of chill on you` | 2 | 0 |  |  | it only applies while something is true |
| `all damage taken from hits while poisoned contributes to magnitude of chill on you` | 2 | 0 |  |  | it only applies while something is true |
| `all damage with this weapon causes electrocution buildup` | 2 | 0 |  |  | the vocabulary has no name for this number yet |
| `allies in your presence deal # to # added attack physical damage` | 2 | 0 |  |  | it is somebody else's number, not the character's |
| `allies in your presence have +# to accuracy rating` | 2 | 0 |  |  | it is somebody else's number, not the character's |
| `apply to energy shield recharge rate` | 2 | 0 |  |  | no pattern claims this wording yet |
| `as being boosted by chilled ground` | 2 | 0 |  |  | no pattern claims this wording yet |
| `as being boosted by ignited ground` | 2 | 0 |  |  | no pattern claims this wording yet |
| `as being boosted by ignited shocked and chilled ground` | 2 | 0 |  |  | no pattern claims this wording yet |
| `as being boosted by shocked ground` | 2 | 0 |  |  | no pattern claims this wording yet |
| `attack hits aggravate any bleeding on targets which is older than # seconds` | 2 | 0 |  |  | no pattern claims this wording yet |
| `attacks chain # additional times` | 2 | 0 |  |  | no pattern claims this wording yet |
| `attacks chain an additional time` | 2 | 0 |  |  | no pattern claims this wording yet |
| `attacks gain #% of damage as extra cold damage` | 2 | 0 |  |  | it converts one number into another |
| `attacks gain #% of damage as extra fire damage` | 2 | 0 |  |  | it converts one number into another |
| `attacks have #% chance to maim on hit` | 2 | 0 |  |  | it is a chance of something happening, not an amount |
| `attacks used by ballistas have #% increased attack speed` | 2 | 0 |  |  | no pattern claims this wording yet |
| `attacks used by totems have #% increased attack speed per summoned totem` | 2 | 0 |  |  | it scales off another number the plan does not hold |
| `attacks with this weapon gain #% of physical damage as extra damage of each element` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `attacks with this weapon have added cold damage equal to #% to #% of maximum mana` | 2 | 0 |  |  | it scales off another number the plan does not hold |
| `bears the mark of the abyssal lord` | 2 | 0 |  |  | no pattern claims this wording yet |
| `bleeding you inflict deals fire damage instead of physical damage` | 2 | 0 |  |  | no pattern claims this wording yet |
| `bleeding you inflict is aggravated` | 2 | 0 |  |  | no pattern claims this wording yet |
| `blocking damage poisons the enemy as though dealing # base chaos damage` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `bolts fired by crossbow attacks have #% chance to not` | 2 | 0 |  |  | it is a chance of something happening, not an amount |
| `bow attacks consume #% of your maximum life flask charges if possible to deal added physical damage equal to #% of flask s life recovery amount` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `bow attacks fire # additional arrows` | 2 | 0 |  |  | no pattern claims this wording yet |
| `bow attacks fire an additional arrow` | 2 | 0 |  |  | no pattern claims this wording yet |
| `break armour equal to #% of physical damage dealt` | 2 | 0 |  |  | it scales off another number the plan does not hold |
| `breaks # armour on critical hit` | 2 | 0 |  |  | it happens on an event rather than standing |
| `can allocate passive skills from the sorceress s starting point` | 2 | 0 |  |  | the item has several versions and the plan does not record which one |
| `can allocate passive skills from the warrior s starting point` | 2 | 0 |  |  | the item has several versions and the plan does not record which one |
| `can have # additional instilled modifiers` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `can roll destruction modifiers` | 2 | 0 |  |  | it is a rule about the item rather than a number |
| `cannot be ignited` | 2 | 0 |  |  | no pattern claims this wording yet |
| `cannot be light stunned` | 2 | 0 |  |  | no pattern claims this wording yet |
| `cannot be poisoned` | 2 | 0 |  |  | no pattern claims this wording yet |
| `cannot have energy shield` | 2 | 0 |  |  | no pattern claims this wording yet |
| `causes bleeding on hit` | 2 | 0 |  |  | it happens on an event rather than standing |
| `causes double stun buildup` | 2 | 0 |  |  | the vocabulary has no name for this number yet |
| `chance to block damage is lucky` | 2 | 0 |  |  | it is a chance of something happening, not an amount |
| `chaos resistance is zero` | 2 | 0 |  |  | no pattern claims this wording yet |
| `charms gain # charge per second` | 2 | 0 |  |  | it scales off another number the plan does not hold |
| `containing corrupted magic jewels` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `convert #% of requirements to dexterity` | 2 | 0 |  |  | no pattern claims this wording yet |
| `convert #% of requirements to intelligence` | 2 | 0 |  |  | no pattern claims this wording yet |
| `convert #% of requirements to strength` | 2 | 0 |  |  | no pattern claims this wording yet |
| `critical hits poison the enemy` | 2 | 0 |  |  | it changes what enemies have, not what the character has |
| `curse enemies with enfeeble on block` | 2 | 0 |  |  | it changes what enemies have, not what the character has |
| `curses you inflict have infinite duration` | 2 | 0 |  |  | the vocabulary has no name for this number yet |
| `curses you inflict spread to enemies within # metres when cursed enemy dies` | 2 | 0 |  |  | it only applies if something is true |
| `damage penetrates #% of enemy elemental resistances while shapeshifted` | 2 | 0 |  |  | it only applies while something is true |
| `dazes on hit` | 2 | 0 |  |  | it happens on an event rather than standing |
| `deal #% increased damage with hits to rare or unique enemies for each second they ve ever been in your presence up to a maximum of #%` | 2 | 0 |  |  | it scales off another number the plan does not hold |
| `deal #% of overkill damage to enemies within # metres of the enemy killed` | 2 | 0 |  |  | it changes what enemies have, not what the character has |
| `decimating strike` | 2 | 0 |  |  | no pattern claims this wording yet |
| `defend with #% of armour` | 2 | 0 |  |  | no pattern claims this wording yet |
| `double stun threshold while shield is raised` | 2 | 0 |  |  | it only applies while something is true |
| `effect is not removed when unreserved life is filled` | 2 | 0 |  |  | it only applies if something is true |
| `enemies chilled by your hits can be shattered as though frozen` | 2 | 0 |  |  | it changes what enemies have, not what the character has |
| `enemies frozen by you have -#% to cold resistance` | 2 | 0 |  |  | it changes what enemies have, not what the character has |
| `enemies frozen by you take #% increased damage` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `enemies in your presence are blinded` | 2 | 0 |  |  | it changes what enemies have, not what the character has |
| `enemies in your presence are ignited as though dealt # base fire damage` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `enemies in your presence have -#% to fire resistance` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `enemies in your presence have exposure` | 2 | 0 |  |  | it changes what enemies have, not what the character has |
| `enemies take #% increased damage for each elemental ailment type among` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `enemies you kill have a #% chance to explode dealing a quarter of their maximum life as chaos damage` | 2 | 0 |  |  | it is a chance of something happening, not an amount |
| `enemy affected by abyssal wasting` | 2 | 0 |  |  | the item has several versions and the plan does not record which one |
| `energy shield does not recharge` | 2 | 0 |  |  | no pattern claims this wording yet |
| `every # rage also grants #% of damage taken recouped as life` | 2 | 0 |  |  | no pattern claims this wording yet |
| `every # seconds during effect deal #% of mana spent in those seconds as chaos damage to enemies within # metres` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `every # seconds gain a verisium infusion` | 2 | 0 |  |  | no pattern claims this wording yet |
| `every second inflicts critical weakness on enemies in your presence for # seconds` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `excess life recovery added as guard for # seconds` | 2 | 0 |  |  | no pattern claims this wording yet |
| `expend ammunition if you ve reloaded recently` | 2 | 0 |  |  | it only applies if something is true |
| `fire damage also contributes to bleeding magnitude` | 2 | 0 |  |  | the vocabulary has no name for this number yet |
| `flammability magnitude is doubled` | 2 | 0 |  |  | the vocabulary has no name for this number yet |
| `flasks do not recover life` | 2 | 0 |  |  | no pattern claims this wording yet |
| `gain # dark whisper every second there is a cursed enemy in your presence` | 2 | 0 |  |  | it changes what enemies have, not what the character has |
| `gain # druidic prowess for every # total rage spent` | 2 | 0 |  |  | it scales off another number the plan does not hold |
| `gain # guard for # seconds per combo expended when using skills` | 2 | 0 |  |  | it only applies if something is true |
| `gain # life per enemy hit with attacks if you have dealt a critical hit recently` | 2 | 0 |  |  | it only applies if something is true |
| `gain # mana per enemy hit with attacks` | 2 | 0 |  |  | it scales off another number the plan does not hold |
| `gain # rage when critically hit by an enemy` | 2 | 0 |  |  | it only applies if something is true |
| `gain # rage when your hit ignites a target` | 2 | 0 |  |  | it only applies if something is true |
| `gain #% of damage as chaos damage per undead minion` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `gain #% of damage as extra chaos damage while you are missing runic ward` | 2 | 0 |  |  | it only applies while something is true |
| `gain #% of damage as extra cold damage while you are missing runic ward` | 2 | 0 |  |  | it only applies while something is true |
| `gain #% of damage as extra cold damage with spells` | 2 | 0 |  |  | it converts one number into another |
| `gain #% of damage as extra damage of a random element` | 2 | 0 |  |  | it converts one number into another |
| `gain #% of damage as extra fire damage while you are missing runic ward` | 2 | 0 |  |  | it only applies while something is true |
| `gain #% of damage as extra fire damage with spells` | 2 | 0 |  |  | it converts one number into another |
| `gain #% of damage as extra lightning damage while you are missing runic ward` | 2 | 0 |  |  | it only applies while something is true |
| `gain #% of damage as extra lightning damage with spells` | 2 | 0 |  |  | it converts one number into another |
| `gain #% of damage as fire damage per #% chance to block` | 2 | 0 |  |  | it scales off another number the plan does not hold |
| `gain #% of elemental damage as extra cold damage` | 2 | 0 |  |  | it converts one number into another |
| `gain #% of elemental damage as extra fire damage` | 2 | 0 |  |  | it converts one number into another |
| `gain #% of elemental damage as extra lightning damage` | 2 | 0 |  |  | it converts one number into another |
| `gain #% of evasion rating as extra armour` | 2 | 0 |  |  | it converts one number into another |
| `gain #% of lightning damage as extra cold damage` | 2 | 0 |  |  | it converts one number into another |
| `gain #% of maximum life as extra maximum energy shield` | 2 | 0 |  |  | the item has several versions and the plan does not record which one |
| `gain #% of maximum life as extra maximum runic ward` | 2 | 0 |  |  | it converts one number into another |
| `gain #% of maximum mana as armour` | 2 | 0 |  |  | no pattern claims this wording yet |
| `gain #% of maximum mana as extra maximum energy shield` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `gain #% of physical damage as extra cold damage` | 2 | 2 | extra-cold-damage | flat |  |
| `gain #% of physical damage as extra cold damage against dazed enemies` | 2 | 0 |  |  | it changes what enemies have, not what the character has |
| `gain accuracy rating equal to your intelligence` | 2 | 0 |  |  | it scales off another number the plan does not hold |
| `gain deflection rating equal to #% of armour` | 2 | 0 |  |  | it scales off another number the plan does not hold |
| `grants skill level # consecrate` | 2 | 0 |  |  | it grants a skill rather than a number |
| `grants skill level # dark pact` | 2 | 0 |  |  | it grants a skill rather than a number |
| `grants skill level # enervating nova` | 2 | 0 |  |  | it grants a skill rather than a number |
| `grants skill level # exsanguinate` | 2 | 0 |  |  | it grants a skill rather than a number |
| `grants skill level # fulmination` | 2 | 0 |  |  | it grants a skill rather than a number |
| `grants skill level # galvanic field` | 2 | 0 |  |  | it grants a skill rather than a number |
| `grants skill level # reap` | 2 | 0 |  |  | it grants a skill rather than a number |
| `grants skill level # soulrend` | 2 | 0 |  |  | it grants a skill rather than a number |
| `grants skill level # spellslinger` | 2 | 0 |  |  | it grants a skill rather than a number |
| `grants skill level # unleash` | 2 | 0 |  |  | it grants a skill rather than a number |
| `grants skill level # wither` | 2 | 0 |  |  | it grants a skill rather than a number |
| `grenade skills have +# cooldown use` | 2 | 0 |  |  | no pattern claims this wording yet |
| `has # augment sockets` | 2 | 0 |  |  | no pattern claims this wording yet |
| `has no accuracy penalty from range` | 2 | 0 |  |  | no pattern claims this wording yet |
| `has no attribute requirements` | 2 | 0 |  |  | no pattern claims this wording yet |
| `hazards have #% chance to rearm after they are triggered` | 2 | 0 |  |  | it is a chance of something happening, not an amount |
| `historic` | 2 | 0 |  |  | no pattern claims this wording yet |
| `hits against you have #% reduced critical damage bonus per socket filled` | 2 | 0 |  |  | the item has several versions and the plan does not record which one |
| `hits with this weapon have # to # added physical damage per #% block chance` | 2 | 0 |  |  | it scales off another number the plan does not hold |
| `hits with this weapon have no critical damage bonus` | 2 | 0 |  |  | no pattern claims this wording yet |
| `ignite you inflict deals chaos damage instead of fire damage` | 2 | 0 |  |  | no pattern claims this wording yet |
| `immune to maim` | 2 | 0 |  |  | no pattern claims this wording yet |
| `increases and reductions to minion attack speed also affect you` | 2 | 0 |  |  | it is somebody else's number, not the character's |
| `increases and reductions to projectile speed also apply to damage with bows` | 2 | 0 |  |  | no pattern claims this wording yet |
| `inflict anaemia on hit anaemia allows +# corrupted blood debuffs to be inflicted on enemies` | 2 | 0 |  |  | it changes what enemies have, not what the character has |
| `inflict elemental exposure on hit lowering total elemental resistances by #%` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `intimidate enemies on block for # seconds` | 2 | 0 |  |  | it changes what enemies have, not what the character has |
| `invocated spells have #% chance to consume half as much energy` | 2 | 0 |  |  | it is a chance of something happening, not an amount |
| `invocated spells have #% increased critical hit chance` | 2 | 0 |  |  | no pattern claims this wording yet |
| `invocation spells have #% increased critical damage bonus` | 2 | 0 |  |  | no pattern claims this wording yet |
| `iron reflexes` | 2 | 0 |  |  | no pattern claims this wording yet |
| `leech #% of physical attack damage as life leech life #% slower` | 2 | 0 |  |  | no pattern claims this wording yet |
| `leech #% of physical attack damage as mana` | 2 | 2 | mana-leech | flat |  |
| `life leech can overflow maximum life` | 2 | 0 |  |  | no pattern claims this wording yet |
| `life leech effects are not removed when unreserved life is filled` | 2 | 0 |  |  | it only applies if something is true |
| `life that would be lost by taking damage is instead reserved` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `lightning damage of enemies hitting you is unlucky` | 2 | 0 |  |  | it changes what enemies have, not what the character has |
| `lightning skills chain +# times` | 2 | 0 |  |  | no pattern claims this wording yet |
| `lose #% of maximum life on kill` | 2 | 0 |  |  | it happens on an event rather than standing |
| `lose all tailwind when hit` | 2 | 0 |  |  | it only applies if something is true |
| `maim on critical hit` | 2 | 0 |  |  | it happens on an event rather than standing |
| `maximum chance to evade is #%` | 2 | 0 |  |  | it is a chance of something happening, not an amount |
| `maximum physical damage reduction is #%` | 2 | 0 |  |  | no pattern claims this wording yet |
| `maximum quality is #%` | 2 | 0 |  |  | no pattern claims this wording yet |
| `melee attack skills have +# to maximum number of summoned totems` | 2 | 0 |  |  | it is somebody else's number, not the character's |
| `meta skills have #% increased reservation efficiency` | 2 | 0 |  |  | no pattern claims this wording yet |
| `minions cause #% increased stun buildup` | 2 | 0 |  |  | it is somebody else's number, not the character's |
| `minions deal #% increased damage with command skills for each different type of persistent minion in your presence` | 2 | 0 |  |  | it scales off another number the plan does not hold |
| `minions have #% increased attack speed` | 2 | 0 |  |  | it is somebody else's number, not the character's |
| `minions have #% increased evasion rating` | 2 | 0 |  |  | it is somebody else's number, not the character's |
| `minions have #% increased skill speed with command skills` | 2 | 0 |  |  | it is somebody else's number, not the character's |
| `minions have +#% surpassing chance to fire an additional projectile` | 2 | 0 |  |  | it is a chance of something happening, not an amount |
| `minions have +#% to all maximum elemental resistances` | 2 | 0 |  |  | it is somebody else's number, not the character's |
| `minions have +#% to maximum cold resistances` | 2 | 0 |  |  | it is somebody else's number, not the character's |
| `minions have +#% to maximum fire resistances` | 2 | 0 |  |  | it is somebody else's number, not the character's |
| `minions have +#% to maximum lightning resistances` | 2 | 0 |  |  | it is somebody else's number, not the character's |
| `minions recoup #% of damage taken as life` | 2 | 0 |  |  | it is somebody else's number, not the character's |
| `minions strikes have melee splash` | 2 | 0 |  |  | it is somebody else's number, not the character's |
| `no inherent loss of rage` | 2 | 0 |  |  | no pattern claims this wording yet |
| `no physical damage` | 2 | 0 |  |  | no pattern claims this wording yet |
| `non-channelling spells deal #% increased damage per # maximum life` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `non-channelling spells have #% increased critical hit chance per # maximum life` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `off-hand hits inflict runefather s challenge` | 2 | 0 |  |  | no pattern claims this wording yet |
| `offering skills have #% increased area of effect` | 2 | 0 |  |  | it is somebody else's number, not the character's |
| `on hitting an enemy gains maximum added lightning damage equal to` | 2 | 0 |  |  | it scales off another number the plan does not hold |
| `pain attunement` | 2 | 0 |  |  | no pattern claims this wording yet |
| `parry has #% increased stun buildup` | 2 | 0 |  |  | the vocabulary has no name for this number yet |
| `physical damage is pinning` | 2 | 0 |  |  | no pattern claims this wording yet |
| `projectiles from spells cannot pierce` | 2 | 0 |  |  | no pattern claims this wording yet |
| `projectiles have #% chance to fork` | 2 | 0 |  |  | it is a chance of something happening, not an amount |
| `projectiles have #% chance to fork if you ve dealt a melee hit in the past eight seconds` | 2 | 0 |  |  | it only applies if something is true |
| `regenerate #% of maximum life over # second when stunned` | 2 | 0 |  |  | it only applies if something is true |
| `regenerate #% of maximum life per second if you have been hit recently` | 2 | 0 |  |  | it only applies if something is true |
| `regenerate #% of maximum life per second while on low life` | 2 | 0 |  |  | it only applies while something is true |
| `regenerate #% of maximum life per second while surrounded` | 2 | 0 |  |  | it only applies while something is true |
| `remnants you create have #% reduced effect` | 2 | 0 |  |  | no pattern claims this wording yet |
| `rolls only the minimum or maximum damage value for physical damage` | 2 | 0 |  |  | no pattern claims this wording yet |
| `runic ward recovery can overflow maximum runic ward` | 2 | 0 |  |  | no pattern claims this wording yet |
| `sealed skills have +# to maximum seals` | 2 | 0 |  |  | no pattern claims this wording yet |
| `shapeshift skills have #% increased skill effect duration` | 2 | 0 |  |  | the vocabulary has no name for this number yet |
| `skill mana costs converted to life costs` | 2 | 0 |  |  | it converts one number into another |
| `skills gain #% of damage as extra lightning damage per # runic ward cost` | 2 | 0 |  |  | it scales off another number the plan does not hold |
| `skills have #% chance to not remove elemental infusions but still count as consuming them if you ve lost an archon buff in the past # seconds` | 2 | 0 |  |  | it only applies if something is true |
| `skills have -# seconds to cooldown` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `slam skills have #% increased area of effect` | 2 | 0 |  |  | no pattern claims this wording yet |
| `socketed gems have #% more attack and cast speed` | 2 | 0 |  |  | no pattern claims this wording yet |
| `spell damage penetrates #% of enemy elemental resistances while on low runic ward` | 2 | 0 |  |  | it only applies while something is true |
| `targets cursed by you have #% reduced life regeneration rate` | 2 | 0 |  |  | no pattern claims this wording yet |
| `the enemy s power for # seconds up to a total of #` | 2 | 0 |  |  | it changes what enemies have, not what the character has |
| `this item gains bonuses from socketed items as though it was a body armour` | 2 | 0 |  |  | the item has several versions and the plan does not record which one |
| `totems gain +#% to all elemental resistances` | 2 | 0 |  |  | it is somebody else's number, not the character's |
| `totems have #% additional physical damage reduction` | 2 | 0 |  |  | it is somebody else's number, not the character's |
| `transforms all cold and lightning modifiers on the item into equivalent fire modifiers` | 2 | 0 |  |  | it is a rule about the item rather than a number |
| `transforms all fire and cold modifiers on the item into equivalent lightning modifiers` | 2 | 0 |  |  | it is a rule about the item rather than a number |
| `transforms all fire cold and lightning modifiers on the item into equivalent chaos modifiers` | 2 | 0 |  |  | it is a rule about the item rather than a number |
| `unblockable` | 2 | 0 |  |  | no pattern claims this wording yet |
| `until you take no damage to life for # seconds` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `unwavering stance` | 2 | 0 |  |  | no pattern claims this wording yet |
| `used when you become cursed` | 2 | 0 |  |  | it only applies if something is true |
| `when socketed transforms all fire and lightning modifiers to equivalent cold modifiers` | 2 | 0 |  |  | it only applies if something is true |
| `wind skills which can be boosted by elemental ground surfaces can be boosted by multiple elemental ground surfaces` | 2 | 0 |  |  | it is a rule about the item rather than a number |
| `withered does not expire on enemies ignited by you` | 2 | 0 |  |  | it changes what enemies have, not what the character has |
| `withered you inflict also increases fire damage taken` | 2 | 0 |  |  | no pattern claims this wording yet |
| `you can have two companions of different types` | 2 | 0 |  |  | it is somebody else's number, not the character's |
| `you can wield two-handed axes maces and swords in one hand` | 2 | 0 |  |  | no pattern claims this wording yet |
| `you cannot be chilled or frozen` | 2 | 0 |  |  | no pattern claims this wording yet |
| `you gain onslaught for # seconds on kill` | 2 | 0 |  |  | it happens on an event rather than standing |
| `you have consecrated ground around you while stationary` | 2 | 0 |  |  | it only applies while something is true |
| `you have no critical damage bonus` | 2 | 0 |  |  | no pattern claims this wording yet |
| `you have no spirit` | 2 | 0 |  |  | no pattern claims this wording yet |
| `you take fire damage instead of physical damage from bleeding` | 2 | 0 |  |  | no pattern claims this wording yet |
| `your ailments on them` | 2 | 0 |  |  | it is a roll from a patch that has been replaced |
| `your heavy stun buildup empties #% faster` | 2 | 0 |  |  | the vocabulary has no name for this number yet |
| `your minions are gigantic if they have revived recently` | 2 | 0 |  |  | it only applies if something is true |
| `your speed is unaffected by slows while sprinting` | 2 | 0 |  |  | it only applies while something is true |
| `#% increased chance to poison` | 1 | 1 | poison-chance | increased |  |
| `#% increased charm charges used` | 1 | 0 | charm-charges-used | increased | it is a roll from a patch that has been replaced |
| `#% increased flask charges used` | 1 | 1 | flask-charges-used | increased |  |
| `#% less armour and evasion rating` | 1 | 1 | armour + evasion | more |  |
| `#% less armour evasion and energy shield` | 1 | 0 | armour + evasion + energy-shield | more | the item has several versions and the plan does not record which one |
| `#% less attributes` | 1 | 1 | strength + dexterity + intelligence | more |  |
| `#% less damage` | 1 | 0 | damage | more | the item has several versions and the plan does not record which one |
| `#% less evasion rating` | 1 | 1 | evasion | more |  |
| `#% less flask charges used` | 1 | 0 | flask-charges-used | more | the item has several versions and the plan does not record which one |
| `#% less life recovery from flasks` | 1 | 1 | flask-life-recovery | more |  |
| `#% less magnitude of chill you inflict` | 1 | 1 | chill-magnitude | more |  |
| `#% less magnitude of shock you inflict` | 1 | 1 | shock-magnitude | more |  |
| `#% less mana regeneration rate` | 1 | 1 | mana-regeneration | more |  |
| `#% less movement speed` | 1 | 0 | speed-movement | more | the item has several versions and the plan does not record which one |
| `#% less poison duration` | 1 | 1 | poison-duration | more |  |
| `#% more amount of life leeched` | 1 | 1 | life-leech | more |  |
| `#% more charm charges gained` | 1 | 1 | charm-charges-gained | more |  |
| `#% more critical damage bonus` | 1 | 1 | critical-damage | more |  |
| `#% more immobilisation buildup` | 1 | 1 | immobilisation-buildup | more |  |
| `#% more magnitude of bleeding you inflict` | 1 | 1 | bleeding-magnitude | more |  |
| `#% more maximum life` | 1 | 1 | life | more |  |
| `#% reduced accuracy rating` | 1 | 1 | attack-rating | increased |  |
| `#% reduced armour` | 1 | 1 | armour | increased |  |
| `#% reduced armour evasion and energy shield` | 1 | 1 | armour + evasion + energy-shield | increased |  |
| `#% reduced attack and cast speed` | 1 | 1 | speed-attack + speed-cast | increased |  |
| `#% reduced charm charges gained` | 1 | 1 | charm-charges-gained | increased |  |
| `#% reduced cold damage` | 1 | 1 | damage-cold | increased |  |
| `#% reduced cooldown recovery rate` | 1 | 1 | cooldown-reduction | increased |  |
| `#% reduced critical damage bonus` | 1 | 1 | critical-damage | increased |  |
| `#% reduced curse duration` | 1 | 1 | curse-duration | increased |  |
| `#% reduced dexterity` | 1 | 1 | dexterity | increased |  |
| `#% reduced effect of archon buffs on you` | 1 | 1 | archon-buffs-effect-on-you | increased |  |
| `#% reduced endurance charge duration` | 1 | 1 | endurance-charge-duration | increased |  |
| `#% reduced evasion rating` | 1 | 1 | evasion | increased |  |
| `#% reduced flask effect duration` | 1 | 1 | flask-effect-duration | increased |  |
| `#% reduced flask mana recovery rate` | 1 | 1 | flask-mana-recovery | increased |  |
| `#% reduced global armour evasion and energy shield` | 1 | 1 | armour + evasion + energy-shield | increased |  |
| `#% reduced grenade damage` | 1 | 1 | grenade-damage | increased |  |
| `#% reduced hazard damage` | 1 | 1 | hazard-damage | increased |  |
| `#% reduced intelligence` | 1 | 1 | intelligence | increased |  |
| `#% reduced magnitude of bleeding on you` | 1 | 1 | bleeding-magnitude-on-you | increased |  |
| `#% reduced magnitude of poison you inflict` | 1 | 1 | poison-magnitude | increased |  |
| `#% reduced mana cost of skills` | 1 | 0 | resource-cost-reduction | increased | it is a roll from a patch that has been replaced |
| `#% reduced mana regeneration rate` | 1 | 1 | mana-regeneration | increased |  |
| `#% reduced maximum energy shield` | 1 | 1 | energy-shield | increased |  |
| `#% reduced quantity of gold dropped by slain enemies` | 1 | 0 | gold-find | increased | the item has several versions and the plan does not record which one |
| `#% reduced spell area damage` | 1 | 1 | spell-area-damage | increased |  |
| `#% reduced spell damage` | 1 | 1 | damage-spell | increased |  |
| `#% reduced stun threshold` | 1 | 1 | stun-threshold | increased |  |
| `#% reduced totem life` | 1 | 0 | totem-life | increased | it is a roll from a patch that has been replaced |
| `+# to level of all chaos skills` | 1 | 1 | skills-tab | flat |  |
| `+# to level of all corrupted spell skill gems` | 1 | 1 | skills-tab | flat |  |
| `+# to level of all elemental skills` | 1 | 1 | skills-tab | flat |  |
| `+# to level of despair skills` | 1 | 0 | skills-single | flat | the item has several versions and the plan does not record which one |
| `+# to level of elemental weakness skills` | 1 | 0 | skills-single | flat | the item has several versions and the plan does not record which one |
| `+# to level of enfeeble skills` | 1 | 0 | skills-single | flat | the item has several versions and the plan does not record which one |
| `+# to level of temporal chains skills` | 1 | 0 | skills-single | flat | the item has several versions and the plan does not record which one |
| `+# to level of vulnerability skills` | 1 | 0 | skills-single | flat | the item has several versions and the plan does not record which one |
| `-# to accuracy rating` | 1 | 1 | attack-rating | flat |  |
| `-# to strength` | 1 | 1 | strength | flat |  |
| `-#% to lightning resistance` | 1 | 1 | resistance-lightning | flat |  |
| `-#% to maximum block chance` | 1 | 0 | block | flat | it is a roll from a patch that has been replaced |
| `equipment and skill gems have #% increased attribute requirements` | 1 | 1 | attribute-requirements | increased |  |
| `gain #% of physical damage as extra lightning damage` | 1 | 1 | extra-lightning-damage | flat |  |
| `meta skills gain #% more energy` | 1 | 1 | meta-skill-energy | more |  |
| `minions have #% reduced maximum life` | 1 | 1 | life-minion | increased |  |
| `spell skills have #% reduced area of effect` | 1 | 1 | spell-area-of-effect | increased |  |

## The tail we did not map

**1,831 templates, 1,831 lines (14.6% of everything)** — each seen exactly
once, and none of them claimed by a pattern. They are kept, filed against the stat they talk
about, and left out of the arithmetic. Why, counted up:

| why it is not counted | templates |
| --- | ---: |
| no pattern claims this wording yet | 595 |
| it only applies if something is true | 212 |
| it only applies while something is true | 186 |
| it scales off another number the plan does not hold | 181 |
| it changes what enemies have, not what the character has | 143 |
| the item has several versions and the plan does not record which one | 125 |
| it grants a skill rather than a number | 96 |
| it is a chance of something happening, not an amount | 72 |
| it is somebody else's number, not the character's | 70 |
| the vocabulary has no name for this number yet | 51 |
| it converts one number into another | 39 |
| it is a roll from a patch that has been replaced | 17 |
| it is a rule about the item rather than a number | 17 |
| it only applies for a while after something happens | 16 |
| it happens on an event rather than standing | 11 |

A sample of twenty, so the shape of the tail is visible:

- `#`
- `#% increased armour and evasion +# to stun threshold`
- `#% increased culling strike threshold against rare or unique enemies`
- `#% increased life and mana regeneration rate for each minion in your presence up to a maximum of #%`
- `#% increased skill effect duration with plant skills`
- `#% of elemental damage taken recouped as life`
- `+# to level of all # skills`
- `additional rune-only sockets`
- `bear skills convert #% of physical damage to fire damage`
- `cold damage from hits contributes to flammability and ignite magnitudes instead of chill magnitude or freeze buildup`
- `deals #% of current mana as chaos damage to you when effect ends`
- `enemies you kill while they are affected by abyssal wasting`
- `gain #% of physical damage as extra lightning damage against dazed enemies`
- `grants skill hollow focus`
- `grenade skills have +# cooldown uses`
- `legacy of quicksilver`
- `no movement speed penalty while shield is raised`
- `recover # mana when used`
- `slam skills you use yourself cause an additional aftershock`
- `trigger lightning bolt skill on critical hit`

## The biggest single thing we could not map

`+# to any attribute` — **293 lines**, every one of them a passive tree node. The game
lets a person choose which of the three attributes the node gives, and a plan records that it
was allocated but not what was chosen, so there is no attribute to add it to. Splitting it
three ways would state three times the truth. It is held against the row it belongs to and
counted nowhere.

## What the vocabulary grew

Seven names, because an unnamed stat lands under `other` and these are not other:
`spirit` and `stun-threshold` (pools a person reads beside life and mana), `damage-spell` and
`damage-attack` (two brackets this game never adds together, so neither can be `damage`),
`damage-minion` and `life-minion` (a summoner's whole build has no other row), and
`speed-skill`. Everything else this game says that the other two do not is carried under its
own id — `freeze-buildup`, `presence-area-of-effect`, `charm-slots` — written noun first so
the name a person reads under `other` is the name the game uses.

## A known consequence, stated plainly

A stat that only ever receives increases and has no base — movement speed, spell damage,
minion damage — totals **zero**, because the pool multiplies a base it does not have. The
working still shows the bracket, so `Movement speed 0.00, increased −7` reads as what it is:
we know the modifiers and not the number they modify. The alternative was to write in a
baseline of 100 for every percentage stat, and that would be a number nobody recorded.
