# SPDX-License-Identifier: AGPL-3.0-only
"""
`/horoscope` — the material, not the horoscope.

The cheap half of her Discord bridge: somebody in `#horoscope-practise` asks for
the sky and gets what the writing desk on the site would put beside the box.
The expensive half — reading what they then write — needs a gateway this bot
does not have, so this stands alone until it does.

⚠ **It must not interpret.** The command hands over ingresses, stations,
lunations and eclipses with the house each falls in. What any of it MEANS is the
writer's work, which is the entire point of a practice room; a bot that offered
a reading would be doing the exercise for them.
"""
from __future__ import annotations

from tests.test_dispatch import FakeAstro, cmd, run     # the shared harness


def _text(reply: dict) -> str:
    embeds = (reply.get("data") or {}).get("embeds") or []
    return "\n".join(e.get("description", "") for e in embeds)


def test_it_hands_back_what_happens_in_the_period() -> None:
    astro = FakeAstro()
    reply = run(cmd("horoscope", sign="leo", period="weekly"), astro=astro)
    body = _text(reply)
    assert "Venus enters Scorpio" in body
    assert "new moon in Virgo" in body
    assert "Uranus turns retrograde" in body


def test_the_aspects_are_left_out() -> None:
    """
    A week holds about a hundred. Listing them would bury the four events the
    desk actually shows, and Discord would cut the message off anyway.
    """
    astro = FakeAstro()
    body = _text(run(cmd("horoscope"), astro=astro))
    assert "opposition" not in body.lower()


def test_houses_are_counted_from_the_rising_sign() -> None:
    """
    Whole sign, and the whole reason a sign is asked for. Venus entering Scorpio
    is the 4th from Leo rising and the 8th from Aries.
    """
    leo = _text(run(cmd("horoscope", sign="leo"), astro=FakeAstro()))
    aries = _text(run(cmd("horoscope", sign="aries"), astro=FakeAstro()))
    assert "**4th**" in leo, "Scorpio is the 4th from Leo"
    assert "**8th**" in aries, "Scorpio is the 8th from Aries"


def test_it_says_nothing_about_what_any_of_it_means() -> None:
    """
    The line this command must not cross. A bot that offered an interpretation
    would be doing the exercise the practice room exists for.
    """
    body = _text(run(cmd("horoscope"), astro=FakeAstro())).lower()
    for word in ("you will", "expect ", "this means", "suggests", "brings you"):
        assert word not in body, f"the command is interpreting: {word!r}"


def test_an_unknown_period_falls_back_rather_than_failing() -> None:
    astro = FakeAstro()
    run(cmd("horoscope", period="fortnightly"), astro=astro)
    kind, start, end = astro.calls[-1]
    assert kind == "events"
    # A week, not a crash and not a year.
    assert start[:10] != end[:10]


def test_a_quiet_period_is_an_answer_rather_than_an_error() -> None:
    class Quiet(FakeAstro):
        async def events(self, start, end):
            self.calls.append(("events", start, end))
            return {"events": []}

    body = _text(run(cmd("horoscope"), astro=Quiet()))
    assert "Nothing ingresses" in body
    assert "quiet week reads differently" in body
