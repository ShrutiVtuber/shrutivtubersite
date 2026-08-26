# SPDX-License-Identifier: AGPL-3.0-only
"""
Sponsors, polls, the Discord count and being told when a stream starts.

The properties here are the ones that are quiet when broken: a poll that counts
somebody twice still renders, a Discord panel that leaks every reader to
Discord still shows a number, and a notification key that changes still shows a
working button.
"""
from __future__ import annotations

import inspect
from pathlib import Path

from shruti.api.routes import community, content
from shruti.core import push


def _src() -> Path:
    here = Path(__file__).resolve()
    for base in (here.parents[1], here.parents[2]):
        if (base / "frontend" / "site" / "src").is_dir():
            return base / "frontend" / "site" / "src"
    return here.parents[1] / "frontend" / "site" / "src"


SRC = _src()


# ── sponsors ────────────────────────────────────────────────────────────────

def test_the_home_page_shows_at_most_three_sponsors():
    """A fourth card turns a thank-you into an ad break."""
    assert content.FEATURED_SPONSORS == 3
    assert "FEATURED_SPONSORS" in inspect.getsource(content.get_featured_sponsors)


def test_a_finished_sponsorship_is_not_featured():
    """
    The home page is the loudest place on the site and should not be thanking
    somebody who stopped six months ago.
    """
    source = inspect.getsource(content.get_featured_sponsors)
    assert "s.until" in source and "continue" in source


def test_a_colour_that_is_not_a_colour_is_dropped():
    """
    These go into a style attribute. A typo should produce a plain card, not a
    broken one.
    """
    assert content._HEX.match("#2B1B3D")
    assert not content._HEX.match("red")
    assert not content._HEX.match("#2B1B3")
    assert not content._HEX.match("#2B1B3D; position:fixed")


def test_sponsor_links_declare_what_they_are():
    row = (SRC / "components" / "brand" / "SponsorRow.astro").read_text()
    partners = (SRC / "pages" / "partners.astro").read_text()
    assert 'rel="sponsored noopener"' in row
    assert 'rel="sponsored noopener"' in partners


def test_the_partners_page_discloses_the_arrangement():
    partners = (SRC / "pages" / "partners.astro").read_text()
    assert "money changes" in partners
    assert "no sponsor has" in partners.lower() or "never seen" in partners.lower()


# ── polls ───────────────────────────────────────────────────────────────────

def test_changing_a_vote_moves_it_rather_than_adding_one():
    """A poll that counts somebody twice because they reconsidered is a poll
    nobody should read."""
    source = inspect.getsource(community.vote)
    assert "existing.option_id = option.id" in source


def test_the_answers_cannot_be_edited_after_people_have_voted():
    """
    Editing a label silently changes what a vote meant: the count stays on a
    row that now says something else, and nobody can tell.
    """
    # The BODY, not the docstring — which necessarily says "label" while
    # explaining why the code must not touch one.
    source = inspect.getsource(community.update_poll)
    body = source.split('"""')[2]
    assert "PollOption" not in body
    assert "label" not in body


def test_a_signed_out_voter_is_the_visit_counter_s_hash_not_an_address():
    source = inspect.getsource(community._voter)
    assert "_visitor" in source
    assert "address" not in source


def test_one_vote_each_is_enforced_by_the_database():
    """
    Not only by the route remembering to look. Two requests racing would both
    find no existing vote.
    """
    # /app in the container, the backend directory in a checkout. `community`
    # lives at <root>/shruti/api/routes/, so the root is three parents up from
    # the package rather than from the module.
    import shruti

    root = Path(shruti.__file__).resolve().parent.parent
    path = root / "alembic" / "versions" / "f3c72d9a1e58_polls.py"
    assert path.is_file(), f"{path} is not readable — this check would prove nothing"
    migration = path.read_text()
    assert 'ix_poll_vote_one_each' in migration
    assert "unique=True" in migration.split("ix_poll_vote_one_each")[1][:120]


def test_a_closed_poll_refuses_votes():
    source = inspect.getsource(community.vote)
    assert "poll.closed" in source and "409" in source


# ── discord ─────────────────────────────────────────────────────────────────

def test_discord_is_called_by_the_server_not_the_reader():
    """
    An embedded widget is an iframe, and an iframe means every reader's browser
    talks to Discord whether or not they have an account there. The site makes
    zero third-party requests on every page and that is easy to lose by
    accident.
    """
    source = inspect.getsource(community.discord)
    assert "httpx" in source
    for page in ("pages/community.astro",):
        text = (SRC / page).read_text()
        assert "discord.com/widget" not in text
        assert "<iframe" not in text


def test_the_widget_s_member_list_is_not_shown():
    """
    Discord returns usernames and avatars of everyone online. Putting a hundred
    handles on a public page because they were in a voice channel is a thing
    done to them, not for them.
    """
    source = inspect.getsource(community.discord)
    assert '"members"' not in source or "NOT body" in source
    assert "presence_count" in source


def test_a_discord_outage_does_not_break_the_page():
    source = inspect.getsource(community.discord)
    assert "except Exception" in source


# ── push ────────────────────────────────────────────────────────────────────

def test_the_push_carries_no_payload():
    """
    Nothing readable transits Mozilla's or Google's servers, and there is no
    aes128gcm to get subtly wrong.
    """
    source = inspect.getsource(push.push_one)
    assert '"Content-Length": "0"' in source
    assert "aes128gcm" not in source


def test_a_dead_subscription_is_deleted_rather_than_retried():
    """A push service that keeps being handed a gone endpoint rate-limits the
    sender."""
    source = inspect.getsource(community.push_send)
    assert "(404, 410)" in source
    assert "session.delete(row)" in source


def test_notifying_never_requires_an_account():
    """Asking for an account before telling somebody a stream started is a toll
    booth on a favour."""
    source = inspect.getsource(community.push_subscribe)
    assert "require_admin" not in source
    assert "user is not None" in source, "an account is recorded, never required"


def test_a_stale_notice_shows_nothing():
    """A browser waking an hour after a stream ended must not announce it."""
    assert community.NOTICE_LIFE <= 12 * 60 * 60
    assert "NOTICE_LIFE" in inspect.getsource(community.push_notice)


def _worker() -> str:
    path = SRC.parent / "public" / "sw.js"
    assert path.is_file(), (
        f"{path} is not readable — the checks below would pass on nothing"
    )
    return path.read_text()


def test_the_service_worker_is_not_an_offline_cache():
    """
    Caching a server-rendered site whose content changes without a deploy means
    serving yesterday's sky from disk.
    """
    sw = _worker()
    assert "caches.open" not in sw
    assert "addEventListener(\"fetch\"" not in sw


def test_the_worker_shows_nothing_when_there_is_nothing_to_say():
    sw = _worker()
    assert "!notice.title" in sw and "return" in sw


# ── the game ────────────────────────────────────────────────────────────────

def test_the_game_does_not_pretend_to_divine_anything():
    """
    Every instrument here says what it cannot compute, and /terms says nothing
    on the site is predictive. A fortune-telling toy would contradict all of it
    for engagement.
    """
    text = (SRC / "components" / "community" / "GlyphGame.astro").read_text()
    # Below the frontmatter: the comment above it necessarily uses these words
    # to say why the game does not.
    game = text.split("---", 2)[-1].lower()
    for forbidden in ("fortune", "your future", "predict", "destiny", "reading for you"):
        assert forbidden not in game


def test_the_game_asks_for_the_text_glyphs():
    """Same reason as the chart wheel: the zodiac defaults to emoji
    presentation, and a learner needs the glyph."""
    game = (SRC / "components" / "community" / "GlyphGame.astro").read_text()
    assert "︎" in game
