# SPDX-License-Identifier: AGPL-3.0-only
"""
The Ledger on stream shows chat what the person wrote for chat, and nothing
else (design_handoff_ledger_overlays README §3–§8, A1–A6; docs/LEDGER.md).

Two kinds of check, as in `test_a_ledger_is_one_company_in_one_game`:

- **Guards on the source**, which run everywhere: the routes, who they ask,
  the fair use, the frame's arithmetic, the fourth theme and its hooks, the
  strip and the path strip, the gallery's starting layout.
- **Against Postgres**: a frame built from a ledger holding cash, notes, an
  unopened plan and a stranger's ledger carries none of them; a token reads
  only its own ledger; revoking works; the live plan goes on DELETE; erasing
  the account takes the ledger's overlays. It needs a database migrated to
  head and runs from `scripts/test-erase.sh`; without
  `SHRUTI_ERASE_DATABASE_URL` it SKIPS, and says so.
"""
from __future__ import annotations

import asyncio
import inspect
import json
import os
import re

import pytest
from fastapi import HTTPException

from conftest import ROOT   # noqa: E402  (see conftest for why)
from shruti.api.routes import ledger, ledger_stream, overlay_guides
from shruti.models.ledger import LedgerWeek

URL = os.environ.get("SHRUTI_ERASE_DATABASE_URL", "")

ROUTES = {
    ("GET", "/api/ledger/ledgers/{ledger_id}/overlays"),
    ("POST", "/api/ledger/ledgers/{ledger_id}/overlays"),
    ("DELETE", "/api/ledger/ledgers/{ledger_id}/overlays/{token_id}"),
    ("POST", "/api/ledger/ledgers/{ledger_id}/layouts"),
    ("PUT", "/api/ledger/ledgers/{ledger_id}/on-screen"),
    ("PUT", "/api/ledger/ledgers/{ledger_id}/live"),
    ("DELETE", "/api/ledger/ledgers/{ledger_id}/live"),
}


def code_of(thing) -> str:
    source = inspect.getsource(thing)
    source = re.sub(r'"""..*?"""', " ", source, flags=re.S)
    return re.sub(r"(?m)#.*$", " ", source)


def _file(*parts: str) -> str:
    for base in (ROOT, ROOT / "backend"):
        path = base.joinpath(*parts)
        if path.exists():
            return path.read_text()
    raise AssertionError(f"missing: {'/'.join(parts)}")


def _site(*parts: str) -> str:
    return _file("frontend", "site", "src", *parts)


# ── the routes ──────────────────────────────────────────────────────────────

def test_the_routes_are_the_ones_the_controls_call() -> None:
    assert {(m, r.path) for r in ledger_stream.router.routes for m in r.methods} == ROUTES


def test_the_ledger_on_stream_is_served() -> None:
    from shruti.api import app as app_module
    assert "app.include_router(ledger_stream.router)" in inspect.getsource(app_module)


def test_every_route_answers_only_for_the_readers_own_ledger() -> None:
    for route in ledger_stream.router.routes:
        assert "_my_ledger(" in code_of(route.endpoint), f"{route.path} does not ask whose ledger it is"


def test_minting_follows_every_overlays_fair_use_and_never_charges() -> None:
    code = code_of(ledger_stream.mint_ledger_token)
    assert "refuse_if_out_of_allowance(" in code and "_refuse_if_suspended(" in code
    assert "secrets.token_urlsafe" in code
    for word in ("stripe", "Checkout", "Hosting(", "charge", "price"):
        assert word not in code, f"minting reaches for {word}"
    assert "OverlayToken.ledger_id" in code_of(overlay_guides.my_tokens) or "LEDGER_KINDS" in code_of(overlay_guides.my_tokens)
    assert set(ledger_stream.ALL_KINDS) <= set(overlay_guides.SITE_KINDS), "the allowance does not count ledger overlays"


def test_a_ledgers_layout_is_minted_like_every_overlay_and_draws_only_that_ledger() -> None:
    code = code_of(ledger_stream.mint_ledger_layout)
    for call in ("_my_ledger(", "refuse_if_out_of_allowance(", "_refuse_if_suspended(", "refuse_a_collision(",
                 "secrets.token_urlsafe", '"ledger_id": g.id', "ledger_id=g.id"):
        assert call in code, f"a ledger's layout is minted without {call}"
    for word in ("stripe", "Checkout", "Hosting(", "charge", "price"):
        assert word not in code, f"minting a layout reaches for {word}"
    host = code_of(overlay_guides.guide)
    assert "_ledger_layout_frame(" in host, "a layout with no run never draws its ledger"
    frame = code_of(overlay_guides._ledger_layout_frame)
    assert "g.user_id != token.user_id" in frame, "a layout draws a ledger its minter no longer keeps"
    assert frame.index('base["unchanged"] = True') < frame.index("_fill_goals("), "the unchanged answer computes the frame"
    assert "o.ledger_id and not o.run_id" in code_of(overlay_guides.my_tokens), "the account page cannot name a ledger's layout"
    gallery = _site("pages", "guides", "overlays.astro")
    assert "/layouts`" in gallery and "data-ledger" in gallery, "the gallery's Ledger card still mints a run's layout"


def test_the_overlay_reads_a_ledger_through_its_token_and_polls_it_cheaply() -> None:
    code = code_of(overlay_guides.guide)
    assert "ledger_stream.token_frame(" in code
    cheap = code_of(ledger_stream.token_frame)
    assert cheap.index('"unchanged": True') < cheap.index("await frame("), "the unchanged answer computes the frame"


def test_the_frame_never_reaches_for_cash_notes_unopened_plans_or_a_weeks_source() -> None:
    code = code_of(ledger_stream.frame)
    assert "opened_at.is_not(None)" in code, "a plan that was never opened reaches the frame"
    for word in (".note", "cash", "source", "custom_note", "kept_plan"):
        assert word not in code, f"the frame reads {word}"
    assert "engine_plan(" in code, "a plan reaches the stream with more than the engine reads"
    assert ledger_stream.engine_plan({"typeId": "gift-shop", "note": "mine", "cash": 5}) == {"typeId": "gift-shop"}


def test_a_weeks_total_leaves_an_unwritten_line_out_and_never_reads_it_as_zero() -> None:
    w = LedgerWeek(business_id=1, n=6, money_in=100.0, goods=30.0, wages=None, rent=0.0)
    assert ledger_stream.week_total(w) == 70.0
    assert ledger_stream.week_total(LedgerWeek(business_id=1, n=6, money_in=None, goods=5.0)) is None
    assert not re.search(r"\bor 0(\.0)?\b", code_of(ledger_stream)), "something reads a null line as zero"


def test_the_companys_week_is_the_latest_any_open_business_wrote() -> None:
    rows = [{"week": 6, "total": 72880.0}, {"week": 6, "total": -1820.0}, {"week": 5, "total": 9480.0}, {"week": None, "total": None}]
    assert ledger_stream.company_week(rows) == {"n": 6, "total": 71060.0}
    assert ledger_stream.company_week([{"week": None, "total": None}]) is None


def test_a_company_strip_and_a_path_strip_never_share_an_edge() -> None:
    bottom = overlay_guides.clean_layout([{"kind": "ledger-strip"}, {"kind": "guide-path"}])
    assert [e["kind"] for e in bottom] == ["ledger-strip", "guide-path"], "the site's layout dropped a Ledger element"
    assert ledger_stream.strip_collision(bottom)
    with pytest.raises(HTTPException) as refused:
        overlay_guides.refuse_a_collision(bottom)
    assert refused.value.status_code == 422
    apart = overlay_guides.clean_layout([{"kind": "ledger-strip", "y": 72}, {"kind": "guide-path"}])
    assert ledger_stream.strip_collision(apart) is None
    for place in ("mint_token", "set_layout"):
        assert "refuse_a_collision(" in code_of(getattr(overlay_guides, place)), f"{place} saves a collision"


def test_a_layout_draws_a_ledger_only_for_the_person_who_keeps_it() -> None:
    code = code_of(ledger_stream.fill_element)
    assert "g.user_id != owner_id" in code
    assert "run.user_id" in code_of(overlay_guides.guide)
    assert "ledger_id" in overlay_guides.PRIVATE_FIELDS, "the gallery would show which ledger a layout names"


# ── the fourth theme ────────────────────────────────────────────────────────

def test_ledger_is_the_fourth_theme_with_the_designs_values_and_its_hooks() -> None:
    assert overlay_guides.THEMES[-1] == "ledger" and len(overlay_guides.THEMES) == 4
    css = _site("styles", "overlay-guides.css")
    block = css.split('.gov[data-theme="ledger"] {', 1)[1].split("}", 1)[0]
    for value in ("rgba(20, 26, 38, .95)", "#34425F", "#F1EDE4", "#C3C0B6", "#9C998F", "#C7849F", "#4A5C82",
                  "--gt-radius: 2px", "--ov-sigil-cap: butt", "rgba(143, 190, 232, .08)"):
        assert value in block, f"the Ledger theme lacks {value}"
    hooks = css.split(".gov {\n  --ov-margin: none;", 1)
    assert len(hooks) == 2, "the other themes do not leave the margin off"
    for hook in ("--ov-rule-row: transparent", "--ov-total-rule: transparent"):
        assert hook in hooks[1].split("}", 1)[0]
    for token in ("margin", "rule-row", "total-rule", "sigil-cap"):
        assert token in overlay_guides.EDITABLE and overlay_guides.css_var(token).startswith("--ov-")
    assert overlay_guides.css_value("margin", "none") == "none"
    assert overlay_guides.css_value("sigil-cap", "round") == "round"
    assert overlay_guides.css_value("sigil-cap", "url(x)") == ""
    assert "--ov-margin:#C7849F;" in overlay_guides.theme_css({"ledger": {"margin": "#C7849F"}})
    assert "THEMES" in code_of(overlay_guides.mint_token)


def test_the_state_colours_stay_outside_every_theme() -> None:
    css = _site("styles", "overlay-guides.css")
    block = css.split('.gov[data-theme="ledger"] {', 1)[1].split("}", 1)[0]
    assert "--st-" not in block, "the Ledger theme repaints a state colour"


def test_big_ambitions_wears_the_ledger_by_default() -> None:
    assert ledger_stream.GAME_THEMES["big-ambitions"] == "ledger"
    assert "GAME_THEMES.get(g.game" in code_of(ledger_stream.mint_ledger_token)
    track = _site("pages", "guides", "[game]", "[slug]", "track.astro")
    assert '"big-ambitions": "ledger"' in track
    for page in (("pages", "builds", "[id].astro"), ("pages", "groups", "[code].astro")):
        assert 'value: "ledger"' in _site(*page), f"{page[-1]} cannot mint in the Ledger theme"
    from shruti.api.routes import builds, groups
    for mint in (builds.mint_build_token, groups):
        assert "overlay_guides import MOTIONS, THEMES" in inspect.getsource(mint)


def test_the_gallery_starts_with_big_ambitions_ledger() -> None:
    starter = next(s for s in overlay_guides.STARTER_LAYOUTS if s["id"] == "big-ambitions-ledger")
    assert starter["label"] == "Big Ambitions · Ledger" and starter["theme"] == "ledger"
    assert [e["kind"] for e in overlay_guides.clean_layout(starter["layout"])] == ["ledger-plate", "guide-goal"]
    code = code_of(overlay_guides.gallery)
    assert "STARTER_LAYOUTS" in code and "PRIVATE_FIELDS" in code


# ── the migration ───────────────────────────────────────────────────────────

def test_the_ledgers_overlays_go_with_the_ledger_and_the_ledger_with_the_account() -> None:
    migration = _file("alembic", "versions", "m1k7h4i0j076_the_ledger_on_stream.py")
    assert 'down_revision = "l0j7g3h8i965"' in migration
    assert 'sa.ForeignKey("ledger.id", ondelete="CASCADE"' in migration
    assert 'sa.ForeignKey("ledger_business.id", ondelete="SET NULL"' in migration
    for column in ('"live_plan"', '"live_updated_at"', '"live_change"', '"on_screen_business_id"', '"ledger_id"'):
        assert column in migration
    assert "def downgrade" in migration


def test_the_overlay_pages_draw_the_seven_and_poll_within_a_second() -> None:
    page = _site("pages", "overlay", "ledger.astro")
    for kind in ledger_stream.ALL_KINDS:
        assert f'"{kind}"' in page
    assert "setInterval(tick, 1000)" in page
    assert 'r.status === 404' in page, "a revoked overlay keeps drawing"
    assert "t=" not in page.split("<body>", 1)[1].split("</body>", 1)[0].replace("data-token", ""), "the token is rendered"
    elements = _site("lib", "overlay-elements.ts")
    assert "drawLedger(" in elements


# ── against Postgres ────────────────────────────────────────────────────────

@pytest.mark.skipif(not URL, reason=(
    "SHRUTI_ERASE_DATABASE_URL is not set — the Ledger on stream was NOT checked against a database. "
    "Run scripts/test-erase.sh"))
def test_a_ledger_on_stream_shows_only_what_was_written_for_chat(monkeypatch) -> None:
    asyncio.run(_stream_a_ledger(monkeypatch))


async def _stream_a_ledger(monkeypatch):
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlmodel import func, select

    from shruti.api.routes.accounts import erase
    from shruti.models import OverlayToken
    from shruti.models.accounts import User
    from shruti.models.ledger import Ledger

    engine = create_async_engine(URL)
    reader = {}

    async def as_reader(_request, _session):
        return reader["user"]

    monkeypatch.setattr(ledger, "_reader", as_reader)
    hours = [[0] * 9 + [1] * 12 + [0] * 3 for _ in range(7)]
    SECRET_NOTE = "the bank loan is due friday"
    SECRET_PLAN = "Acorn Casino (never opened)"

    async with AsyncSession(engine, expire_on_commit=False) as s:
        ev = User(email="ev.stream@example.com", display_name="Ev")
        fy = User(email="fy.stream@example.com", display_name="Fy")
        s.add_all([ev, fy]); await s.flush(); await s.commit()

        reader["user"] = ev
        book = await ledger.start_ledger(ledger.LedgerIn(name="Acorn Holdings"), None, s)
        plan = {"typeId": "gift-shop", "buildingId": "12-2nd-avenue", "hours": hours,
                "note": SECRET_NOTE, "cashOnHand": 987654}
        gifts = await ledger.keep_plan(book["id"], ledger.BusinessIn(name="Acorn Gifts", plan=plan), None, s)
        cafe = await ledger.keep_plan(book["id"], ledger.BusinessIn(name="Acorn Coffee", plan={}), None, s)
        await ledger.keep_plan(book["id"], ledger.BusinessIn(name=SECRET_PLAN, plan={}), None, s)
        for b in (gifts, cafe):
            await ledger.change_business(b["id"], ledger.BusinessPatch(opened=True), None, s)
        await ledger.write_week(gifts["id"], 6, ledger.WeekLines.model_validate(
            {"moneyIn": 93561, "goods": 15363, "wages": 2268, "note": SECRET_NOTE}), None, s)
        await ledger.write_week(cafe["id"], 5, ledger.WeekLines.model_validate({"moneyIn": 1000, "goods": 2820}), None, s)

        # A ledger of somebody else's, for the token that must not read it.
        reader["user"] = fy
        theirs = await ledger.start_ledger(ledger.LedgerIn(name="Fy's Holdings"), None, s)

        reader["user"] = ev
        minted = await ledger_stream.mint_ledger_token(
            book["id"], ledger_stream.LedgerTokenIn(kind="ledger-plate"), None, s)
        assert minted["theme"] == "ledger", "Big Ambitions did not default to the Ledger theme"
        assert minted["path"].startswith("/overlay/ledger?t=")
        plan_token = await ledger_stream.mint_ledger_token(
            book["id"], ledger_stream.LedgerTokenIn(kind="ledger-plan-panel", theme="plain", motion="still"), None, s)
        listed = await ledger_stream.ledger_tokens(book["id"], None, s)
        assert [t["kind"] for t in listed] == ["ledger-plate", "ledger-plan-panel"]
        assert all("token" not in t for t in listed), "a listed overlay carries its address"
        try:
            await ledger_stream.mint_ledger_token(theirs["id"], ledger_stream.LedgerTokenIn(kind="ledger-plate"), None, s)
            raise AssertionError("an overlay was minted on somebody else's ledger")
        except HTTPException as refused:
            assert refused.status_code == 404

        # The frame: only what was written for chat.
        shown = await overlay_guides.guide(minted["token"], "", s)
        el = shown["element"]
        assert el["company"] == "Acorn Holdings"
        assert [b["name"] for b in el["businesses"]] == ["Acorn Gifts", "Acorn Coffee"]
        assert el["businesses"][0]["week"] == 6 and round(el["businesses"][0]["total"]) == 75930
        assert el["businesses"][1]["total"] == -1820
        assert el["week"] == {"n": 6, "total": 75930.0}
        assert el["onScreen"] == gifts["id"] and el["onScreenPlan"]["typeId"] == "gift-shop"
        said = json.dumps(shown)
        for secret in (SECRET_NOTE, SECRET_PLAN, "987654", "cashOnHand", "note", "source", "Fy's Holdings"):
            assert secret not in said, f"the stream carries {secret!r}"
        assert "live" not in el, "a business element carries the plan on stream"

        again = await overlay_guides.guide(minted["token"], shown["version"], s)
        assert again.get("unchanged") is True, "an unchanged ledger was recomputed"

        # The business on screen: an open business of this ledger only.
        try:
            await ledger_stream.set_on_screen(book["id"], ledger_stream.OnScreenIn(business_id=10**8), None, s)
            raise AssertionError("a business outside the ledger went on screen")
        except HTTPException as refused:
            assert refused.status_code == 404
        unopened = [b for b in (await ledger.one_ledger(book["id"], None, s))["businesses"] if not b["opened"]][0]
        try:
            await ledger_stream.set_on_screen(book["id"], ledger_stream.OnScreenIn(business_id=unopened["id"]), None, s)
            raise AssertionError("a plan that was never opened went on screen")
        except HTTPException as refused:
            assert refused.status_code == 422
        await ledger_stream.set_on_screen(book["id"], ledger_stream.OnScreenIn.model_validate({"businessId": cafe["id"]}), None, s)
        moved = await overlay_guides.guide(minted["token"], shown["version"], s)
        assert not moved.get("unchanged") and moved["element"]["onScreen"] == cafe["id"]

        # The plan on stream: empty until the switch, the plan while on, gone on DELETE.
        empty = await overlay_guides.guide(plan_token["token"], "", s)
        assert empty["element"]["live"] is None
        await ledger_stream.put_live(book["id"], ledger_stream.LiveIn.model_validate(
            {"plan": {"typeId": "gift-shop", "note": SECRET_NOTE}, "name": "Acorn Gifts",
             "change": {"label": "A second register", "delta": 12845}}), None, s)
        live = await overlay_guides.guide(plan_token["token"], empty["version"], s)
        assert live["element"]["live"]["plan"] == {"typeId": "gift-shop"}
        assert live["element"]["live"]["change"] == {"label": "A second register", "delta": 12845}
        assert "businesses" not in live["element"] and SECRET_NOTE not in json.dumps(live)
        await ledger_stream.drop_live(book["id"], None, s)
        off = await overlay_guides.guide(plan_token["token"], live["version"], s)
        assert off["element"]["live"] is None, "the plan stayed on stream after the switch went off"
        assert (await s.get(Ledger, book["id"])).live_plan is None

        # The gallery's layout: bound to this ledger with no run, drawing only it.
        laid = await ledger_stream.mint_ledger_layout(book["id"], ledger_stream.LedgerLayoutIn.model_validate(
            {"layout": [{"kind": "ledger-plate", "x": 1112, "y": 48, "w": 760, "ledger_id": theirs["id"]},
                        {"kind": "guide-goal", "x": 72, "y": 800, "w": 860}],
             "theme": "ledger", "motion": "reduced", "label": "Big Ambitions · Ledger"}), None, s)
        assert laid["kind"] == "guide-layout" and laid["path"].startswith("/overlay/guide-layout?t=")
        drawn = await overlay_guides.guide(laid["token"], "", s)
        assert [e["kind"] for e in drawn["elements"]] == ["ledger-plate", "guide-goal"]
        plate_el = drawn["elements"][0]["element"]
        assert plate_el["company"] == "Acorn Holdings", "the layout drew the ledger it was sent, not its own"
        assert drawn["elements"][1]["element"] == {}
        said = json.dumps(drawn)
        for secret in (SECRET_NOTE, SECRET_PLAN, "987654", "Fy's Holdings"):
            assert secret not in said, f"the layout carries {secret!r}"
        assert (await overlay_guides.guide(laid["token"], drawn["version"], s)).get("unchanged") is True
        assert "guide-layout" in [t["kind"] for t in await ledger_stream.ledger_tokens(book["id"], None, s)]
        try:
            await ledger_stream.mint_ledger_layout(theirs["id"], ledger_stream.LedgerLayoutIn.model_validate(
                {"layout": [{"kind": "ledger-plate"}]}), None, s)
            raise AssertionError("a layout was minted on somebody else's ledger")
        except HTTPException as refused:
            assert refused.status_code == 404
        try:
            await ledger_stream.mint_ledger_layout(book["id"], ledger_stream.LedgerLayoutIn.model_validate(
                {"layout": [{"kind": "guide-goal"}]}), None, s)
            raise AssertionError("a ledger's layout was minted with nothing of the ledger in it")
        except HTTPException as refused:
            assert refused.status_code == 422
        await ledger_stream.revoke_ledger_token(book["id"], laid["id"], None, s)

        # Revoked is gone.
        await ledger_stream.revoke_ledger_token(book["id"], plan_token["id"], None, s)
        try:
            await overlay_guides.guide(plan_token["token"], "", s)
            raise AssertionError("a revoked overlay still answers")
        except HTTPException as refused:
            assert refused.status_code == 404
        ids = dict(ev=ev.id, book=book["id"])

    async with AsyncSession(engine, expire_on_commit=False) as s:
        await erase(await s.get(User, ids["ev"]), s)

    async with AsyncSession(engine, expire_on_commit=False) as s:
        left = (await s.execute(select(func.count()).select_from(OverlayToken)
                                .where(OverlayToken.ledger_id == ids["book"]))).scalar_one()
        assert left == 0, "a ledger's overlay outlived the account"
        assert await s.get(Ledger, ids["book"]) is None
    await engine.dispose()
