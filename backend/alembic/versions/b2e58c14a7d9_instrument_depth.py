"""The instruments get an explanation and a set of real questions.

Revision ID: b2e58c14a7d9
Revises: a1c74e9d3b52

The nine instrument pages were a form, a result and a paragraph — between 278
and 438 words each, with no subheadings on five of them. They are the only part
of this site a stranger might reach without having heard of Shruti, and at that
length they will not be reached at all.

The answer is not padding. It is the one thing this site can say that a
calculator farm cannot: which rule was followed, and why another source gives a
different answer. Every `faq_md` below leads with a disagreement question for
exactly that reason — "why does another site say something else" is both the
most common real question and the one nobody else answers honestly.

Seeded here so the pages are not empty, and editable from the admin from the
moment they exist, because this is her writing and not mine to own.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "b2e58c14a7d9"
down_revision = "a1c74e9d3b52"
branch_labels = None
depends_on = None


CONTENT: dict[str, dict[str, str]] = {}

CONTENT["planetary-hours"] = {"body": """
An hour here is not sixty minutes. It is a twelfth of the daylight, and in
winter that is a good deal less than sixty — and a twelfth of the night, which
in winter is a good deal more. The two only meet at the equinoxes.

This is the older sense of the word, and it is the one the whole scheme of
planetary rulership was built on. The day is divided at sunrise and sunset
rather than at midnight, so a planetary day begins when the Sun comes up and
runs to the next sunrise.

The first hour of the day belongs to the ruler of the weekday — the Sun on
Sunday, the Moon on Monday, and so on. From there the hours run in Chaldean
order: **Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon**, which is the seven
in descending order of how long they appear to take to go round.

There is a small piece of arithmetic worth knowing, because it explains
something otherwise arbitrary. Twenty-four hours through a cycle of seven
leaves a remainder of three. So each day begins three places further along the
Chaldean order than the last — and stepping three at a time through Saturn,
Jupiter, Mars, Sun, Venus, Mercury, Moon produces Sun, Moon, Mars, Mercury,
Jupiter, Venus, Saturn. **That is the order of the days of the week.** The
names of our weekdays are a fossil of this table.
""".strip(), "faq": """
### Why does another site give me a different hour?

Almost always the definition of sunrise. Some sources use the moment the upper
limb of the Sun touches the horizon, some the centre of the disc; some correct
for atmospheric refraction and some do not; and altitude moves it again. Those
differences are minutes, and a minute either side of an hour boundary changes
which hour you are in.

The other common cause is a source that divides the day at **midnight** rather
than at sunrise. That is a different system wearing the same name, and it will
disagree with this one by hours rather than minutes.

### What happens near the poles?

The scheme stops working, and the page says so rather than inventing a number.
Above the Arctic and below the Antarctic circles there are stretches of the
year with no sunrise or no sunset at all, and a twelfth of a day that never
ends is not a quantity.

### Which hour should I use?

That is not a question this instrument answers. It computes the hours and names
their rulers; what a given hour is *good for* belongs to whichever tradition
you are working in, and those traditions disagree with each other.
""".strip()}

CONTENT["solar-stations"] = {"body": """
Four moments a day, and only one of them is where you would expect.

**Rise** and **set** are the Sun crossing the horizon. **Culmination** is the
Sun at its highest — due south from the northern temperate latitudes, due north
from the southern. **Nadir** is the opposite point, the Sun at its lowest,
below the horizon and directly behind the earth from you.

Culmination is local apparent noon, and it is almost never at twelve o'clock.
Two things move it. The first is where you sit inside your timezone: a timezone
is an hour wide at the equator and everyone in it keeps the same clock, so if
you are at the western edge your noon is later than the clock's. The second is
the equation of time — the Sun runs a little fast or a little slow against
clock time through the year, by up to about sixteen minutes either way, because
the earth's orbit is an ellipse and its axis is tilted. Add summer time and
local noon can sit well after one in the afternoon.
""".strip(), "faq": """
### Why isn't culmination at 12:00?

Three reasons stacked: your longitude within the timezone, the equation of time
(up to roughly sixteen minutes either way across the year), and daylight saving
where it applies. Clock noon is an administrative convenience; culmination is
an astronomical event.

### Why does the table say a station does not occur?

Because it does not. Inside the polar circles there are days with no sunrise
and days with no sunset, and this says so rather than printing a blank cell or
guessing. A missing station is information.
""".strip()}

CONTENT["lunar-stations"] = {"body": """
The same four stations as the Sun — rise, culmination, set and nadir — for a
body that keeps much worse time.

The Moon moves eastward against the stars by roughly thirteen degrees a day,
which means the earth has to turn about fifty minutes further to bring it back
to your horizon. So moonrise slips later day after day, and the slippage is not
even: it varies through the month and with your latitude, from about twenty
minutes to well over an hour.

Because the slip is close to an hour, a moonrise occasionally falls just past
midnight and a civil day ends up with none at all. That happens roughly once a
month. It is not an error, and this table names it rather than leaving a gap.
""".strip(), "faq": """
### Why is there no moonrise today?

Moonrise comes about fifty minutes later each day, so roughly once a month one
slips past midnight and a calendar day contains no moonrise at all. The same
happens to moonset. Where a station does not occur, the table says so.

### Why doesn't the phase match my calendar?

Phase is continuous — the Moon is always some fraction lit. A calendar that
prints one of four named phases has rounded, and the instant of new or full is
a *moment*, not a day. A calendar that shows the full moon on the 14th and one
that shows it on the 15th can both be right if the moment falls near midnight
in one of the two timezones.
""".strip()}

CONTENT["pancanga"] = {"body": """
Five limbs, and each one ends at a moment rather than at midnight. That is the
part that surprises people coming from a Gregorian calendar: a tithi does not
last a day, it lasts until it is finished, and the moment it ends is the number
worth having.

**Tithi** is the Moon gaining twelve degrees on the Sun. Thirty of them make a
lunation. Because both bodies move at varying speeds, a tithi runs anywhere
from about nineteen to about twenty-six hours.

**Vāra** is the weekday, and it is the only limb tied to the horizon — it
begins at sunrise, which is why the sunrise convention in force above moves the
whole day rather than one figure.

**Nakṣatra** is one of twenty-seven equal divisions of the sidereal circle,
each 13°20′, measured by where the Moon is.

**Yoga** is the summed longitudes of Sun and Moon, divided into the same
twenty-seven parts. It is a computed quantity rather than a thing in the sky.

**Karaṇa** is half a tithi, so two of them usually fall within one.
""".strip(), "faq": """
### Why does another pañcāṅga give me a different tithi?

Three causes, in order of how much they move things.

**The ayanāṁśa** — the offset between the tropical and sidereal zodiacs. Lahiri,
Raman, Krishnamurti and the rest disagree by a degree or more, which is enough
to move a nakṣatra boundary by hours. The rule this page used is named in the
bar at the top.

**The sunrise convention**, which decides where the day starts and therefore
which tithi is "today's".

**Your location.** These are local quantities. A pañcāṅga computed for Ujjain
and one computed for where you are will differ, and neither is wrong.

### What is an adhika or kṣaya tithi?

A tithi can be longer than the interval between two sunrises, in which case the
same tithi is current at both and it is counted twice — *adhika*, also called
*vṛddhi*. The opposite also happens: a short tithi can begin and end entirely
between two sunrises, so it is never current at a sunrise and is skipped —
*kṣaya*. Both are ordinary consequences of the definition, not corrections.

### Why is the vāra different from my weekday?

Because it starts at sunrise, not at midnight. Between midnight and sunrise the
pañcāṅga is still on the previous vāra.
""".strip()}

CONTENT["hindu-calendar"] = {"body": """
A lunisolar year: months measured by the Moon, kept in step with the Sun by
inserting a whole month when they drift too far apart.

Twelve lunar months come to about 354 days, roughly eleven short of the solar
year. Left alone the months would walk backwards through the seasons, as they
do in the Islamic calendar. They are held in place instead by a rule about
solar ingresses: when a lunar month contains **no** entry of the Sun into a new
sign, that month is doubled — **adhika māsa**, an extra month, and the year runs
to thirteen. The rarer opposite, where one lunar month contains **two** such
ingresses, deletes a month — **kṣaya māsa**.

The other thing to know is that the same stretch of time has two names. Under
the **amānta** convention a month ends at the new moon; under **pūrṇimānta** it
ends at the full moon. The two are offset by a fortnight, so the same day can
be in Śrāvaṇa by one reckoning and Bhādrapada by the other. Neither is a
mistake — they are regional conventions, broadly southern and northern.
""".strip(), "faq": """
### Why does my month have a different name here?

Almost certainly amānta versus pūrṇimānta. The two conventions end the month at
opposite points of the lunation, so for half of every month they disagree about
the name while agreeing about everything else. The convention in force is named
at the top of the page.

### Why is there a thirteenth month this year?

An adhika māsa. A lunar month passed without the Sun entering a new sign, so it
was doubled to keep the calendar in step with the seasons. It happens roughly
seven times in nineteen years.

### Do festivals fall in the extra month?

No. Festivals wait for the *nija* — the true month that follows. The adhika
month is treated as an insertion rather than as the month it shares a name
with, and that rule is authentic rather than a simplification made here.
""".strip()}

CONTENT["attic-calendar"] = {"body": """
The civil calendar of Athens, which is lunisolar and counted in a way no modern
calendar is.

A month opens at the **noumenia**, the first day after the new moon, and runs
either **full** (thirty days) or **hollow** (twenty-nine). Which one it is
emerges from where the next conjunction falls, not from a fixed table — so
there is no rule of thumb like "thirty days hath September".

The days are counted in three groups of ten. The first ten count forward, *of
the waxing month*. The middle ten count forward again. The **last ten count
backwards** — the twenty-first day of a full month is "tenth of the waning",
and the count runs down toward the end. The final day is **ἕνη καὶ νέα**, "old
and new", and belongs to both the month ending and the month beginning.

Twelve lunar months fall about eleven days short of the solar year, so a
thirteenth is inserted seven times in nineteen — a second Poseideon, dropped in
after the first.
""".strip(), "faq": """
### Why do sources disagree about today's Attic date?

Because there is no single right answer, and this is the most important thing
to understand about this instrument.

The Athenian civil calendar was **administered, not calculated**. Archons
inserted and removed days for political and religious convenience, and ancient
sources complain about it: the civil calendar and the moon are recorded drifting
apart by days. There was also a separate conciliar calendar running alongside it
on a different cycle entirely.

So any modern Attic date is a **reconstruction** from a rule, not a record of
what an Athenian would have called today. Different reconstructions choose
different rules and get different answers. This page states the rule it used at
the top; that is the honest form of the claim, and a source that presents its
Attic date as simply correct is overstating what can be known.

### Why is the last third of the month counted backwards?

It is how the Athenians counted, and it follows the Moon: the last decad is the
waning, and the numbers count down toward the dark. It also means a hollow month
is shortened cleanly — you drop a day from the middle of the backward count
rather than renumbering the end.

### What is ἕνη καὶ νέα?

"Old and new" — the last day of the month, understood as belonging to the
month that is ending and the one that is beginning at once. The conjunction
falls in it.
""".strip()}

CONTENT["natal-chart"] = {"body": """
A figure for one moment and one place: where the bodies were, as seen from
there, then.

The positions themselves are not controversial. They come from an ephemeris and
they are the same numbers an observatory would give you. Everything that people
argue about happens after that — which zodiac you read them against, how you
divide the sky into places, and what any of it means.

**Tropical or sidereal.** The tropical zodiac is tied to the equinox; the
sidereal to the stars. They coincided about seventeen centuries ago and have
been separating since, at roughly a degree every seventy-two years. They now sit
about twenty-four degrees apart — enough to move the Sun a whole sign for the
same birth. Neither is a mistake and neither is a correction of the other; they
are two different things to measure from.

**Houses.** Whole-sign places make each sign one house, which is the older
Hellenistic practice and the one this defaults to under that tradition. Quadrant
systems divide differently and put the same planet in a different house. The
system in force is named at the top.

The tables are the reading. The wheel is drawn from the same numbers and adds
nothing the tables do not already say — it is there because a picture is easier
to hold in the head.
""".strip(), "faq": """
### Why is my Sun in a different sign here than on another site?

You have almost certainly compared a tropical chart with a sidereal one. They
are about twenty-four degrees apart, so anyone born within roughly the last
three weeks of a sign in one system falls into the previous sign in the other.
Both charts are correct within their own tradition. The choice is yours and it
is shown at the top of the page.

### I don't know my birth time. Is the chart useless?

No, but be clear about which parts are unsafe. The **Ascendant and Midheaven**
move roughly a degree every four minutes, so without a time they are unusable —
and so is every house placement that depends on them. The **Moon** travels
about thirteen degrees a day, so it can be uncertain by half a sign. Everything
slower than the Moon is fine.

This page marks what it cannot know rather than quietly defaulting to noon,
because a chart that looks complete and is not is worse than one that admits a
gap.

### Are the positions rounded or interpreted?

Neither. They are shown as computed. Where a convention had to be chosen, it is
named rather than assumed.
""".strip()}

CONTENT["isopsephy"] = {"body": """
Before there were separate digits, the letters were the numbers. Greek, Hebrew,
Arabic and several other scripts each assigned a value to every letter, so any
word already had a sum whether anyone intended it or not. Reckoning with those
sums is **isopsephy** in Greek and **gematria** in Hebrew.

Each script is summed under **its own table**, and nothing is converted between
them. This matters more than it sounds: a Greek word and a Hebrew word that
come to the same number have not met. The tables are historically unrelated, and
a coincidence between them is arithmetic rather than meaning. Matches here are
therefore only ever found inside one system.

The Greek table keeps three letters that dropped out of the alphabet but kept
their places in the count: **digamma** (also written stigma) at 6, **koppa** at
90, and **sampi** at 900. They are easy to omit and omitting them silently
produces wrong sums for a great many words, because everything above them
shifts.
""".strip(), "faq": """
### Why is my Hebrew sum different somewhere else?

Most often the final forms. This uses *mispar hechrachi*, where the five finals
take the same values as their ordinary letters — kaf is 20 whether or not it
ends the word. A widespread alternative, *mispar gadol*, gives the finals
500 through 900 instead. Both are real conventions with long histories, and
they simply give different numbers.

### Why don't matches cross between scripts?

Because the tables have no common ancestor in the sense that would make such a
match mean anything. Greek assigns values in alphabet order; the Arabic abjad
runs in a different order from the modern alphabet; Hebrew has its own. Two
words from different systems landing on the same total is what you would expect
from arithmetic on a few hundred possibilities.

### What are digamma, koppa and sampi?

Letters Greek stopped writing but never removed from the count. Digamma sat
sixth, koppa between pi and rho, sampi at the end. Their numeric slots stayed
occupied, so any table that leaves them out gives the wrong value to every
letter above them.
""".strip()}

CONTENT["sigil-generator"] = {"body": """
Write a statement of intent, strike out the letters that repeat, and bind what
is left into a single figure. The method is straightforward and this shows every
step of it, so nothing about the result has to be taken on trust.

The letter-reduction method is one approach among several — it is the one
associated with Austin Osman Spare and it became the common form in twentieth
century practice. It is not the only way and it is not a canonical one. What it
has going for it is that it is checkable: you can follow the reduction yourself
and see how the figure was arrived at.

The same letters always produce the same figure. That is deliberate. A
generator that returned something different each time would make a sigil
unrepeatable, and being able to draw the same figure again — from memory, on
paper, a year later — is most of what a sigil is for.

Nothing typed here leaves your machine. The reduction and the drawing both
happen in the browser.
""".strip(), "faq": """
### Is this the correct way to make a sigil?

There is no correct way. Letter reduction is one method with a hundred-odd
years behind it; there are others — planetary squares, wax and thread, purely
intuitive drawing — and traditions that would not recognise any of them. This
implements one method transparently rather than presenting it as the method.

### Why do I get the same figure every time?

By design. A sigil you cannot reproduce is of limited use, so the same input
always gives the same output. If you want a different figure, change the
statement — which is a real choice rather than a reroll.

### Does anything I type get sent anywhere?

No. Both the reduction and the drawing run on your own machine, and the text
never reaches the server. That is why this page keeps working with the network
off.
""".strip()}


def upgrade() -> None:
    op.add_column("tool", sa.Column("faq_md", sa.Text(), nullable=False, server_default=""))

    tool = sa.table(
        "tool",
        sa.column("slug", sa.String),
        sa.column("body_md", sa.String),
        sa.column("faq_md", sa.Text),
    )
    conn = op.get_bind()
    for slug, parts in CONTENT.items():
        conn.execute(
            tool.update()
            .where(tool.c.slug == slug)
            .values(body_md=parts["body"], faq_md=parts["faq"])
        )


def downgrade() -> None:
    op.drop_column("tool", "faq_md")
