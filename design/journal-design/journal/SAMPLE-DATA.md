# Sample data — every invented figure, and where it lives

Nothing in the reference pages is computed. The values below were authored to be
realistic and **internally consistent** so the layouts could be judged; they are
the only content that must change before a reader sees this section. Swapping
them is mechanical — each row names the file and the block.

The consistency is deliberate and worth preserving when you replace them: the
sidereal figures are the tropical ones minus the stated ayanāṁśa, so a
half-replaced block will look wrong to anyone who checks.

## The sky at publication — `.j-record`

`article.html`, `article-cover.html` (identical block; in production it is
stored per entry at publish time and never recomputed).

| Field | Value used | Note |
|---|---|---|
| Sun · tropical | 2°14′ ♍ | Plausible for 2026-08-25 |
| Sun · sidereal, Lahiri | 8°23′ ♌ | = tropical − 23°51′ |
| Moon · tropical | 19°41′ ♓ | |
| Moon · sidereal, Lahiri | 25°50′ ♒ | = tropical − 23°51′ |
| Tithi | Kṛṣṇa Ekādaśī · ends 03:41 | |
| Nakṣatra | Mṛgaśīrṣa · ends 21:07 | |
| Attic | δωδεκάτη Μεταγειτνιῶνος | Observed crescent, Athens |
| Thelemic | Anno IVxxxiv ☉ in ♍ | |
| Footer | Swiss Ephemeris 2.10.03 · Lahiri · amānta · observed crescent | The rule line |

The ayanāṁśa is stated as **23°51′** on `docs-page.html`. If you change it,
change both sidereal figures and that cell together.

## Ephemeris response table — `docs-page.html`

Sun 14°02′ ♉ / 20°11′ ♈ · Moon 02°47′ ♑ / 08°56′ ♐ · `moon.speed` 13.42°/day ·
Asc 28°19′ ♌ / 04°28′ ♌ · Attic ἑβδόμη Μουνιχιῶνος. Same −23°51′ relationship.
The refusal JSON (`no_sunrise` at 78.22°N on 2026-12-21) is a real condition and
a real latitude, but the payload shape is proposed, not implemented.

## Flag comparison table — `article.html`

Relative costs 1.0× / 1.4× / 0.6× are illustrative. Measure before publishing —
this is the one table a reader might act on.

## Attic festival corpus — `wiki-article.html`

Five rows shown of a claimed 51. Noumenia and the Deipnon carry real citations
(Plut. *Mor.* 828a; Ar. *Plut.* 594); the Metageitnia range, the Mysteries
14-or-15 dispute and the Skira refusal are shaped to demonstrate the four
grades. **Replace from the real corpus before publication** — a graded table is
a claim about evidence, and inventing the evidence is the one failure this
design cannot survive. Rail counts (51 / 33 / 9 / 4 / 5) must be recomputed from
whatever the corpus actually holds.

## Changelog — `changelog.html`, `changelog-entry.html`

Versions 0.9.1–0.9.4, dates, commit `4f1c9ae`, tag `v0.9.4`, and the six group
lists are written to look like real release notes. In production these are
pulled from the repository at tag time, so they will be replaced wholesale by
the sync rather than edited by hand. The "4 of 31 releases" count is invented.

## Counts and titles everywhere else

48 entries · Writing 21 · Documentation 14 · Wiki 9 · Changelog 4 · Calendars 7
· category counts in the tag rows · "page 2 of 4" · "14 sources". All invented,
all cheap to replace, none of them load-bearing for the layout.

## Art

`cover-metageitnion.png`, `cover-stream.png` and `attic-two-authorities.png` are
generated stand-ins: the dawn sky gradient with a label saying so. They exist so
no page 404s and so the cover-present state can be judged. Commission the first
two (see the design system's `guidelines/art-shot-list.md`); the third is a
screenshot of `/tools/attic-calendar` in its two-authorities state.

Every image slot falls back to the sky plate, so deleting a stand-in without
replacing it degrades to a designed state rather than a broken image.
