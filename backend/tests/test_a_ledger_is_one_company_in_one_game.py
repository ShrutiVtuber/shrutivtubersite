# SPDX-License-Identifier: AGPL-3.0-only
"""
A ledger is one company in one game: its businesses, and the weeks they ran
(docs/LEDGER.md, Contract 3).

Two kinds of check, as in `test_an_account_can_be_deleted`:

- **Guards on the source**, which run everywhere: every route asks who is
  reading, the data route asks nobody, nothing is gated or paid for, a null
  line stays null, and the routes are the contract's.
- **The ledger against Postgres**: kept, written, exported and erased with the
  account. It needs a database migrated to head and runs from
  `scripts/test-erase.sh`; without `SHRUTI_ERASE_DATABASE_URL` it SKIPS, and
  says so, rather than passing on nothing.
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
from shruti.api.routes import gamedata, ledger
from shruti.models.ledger import LedgerWeek

URL = os.environ.get("SHRUTI_ERASE_DATABASE_URL", "")

CONTRACT = {
    ("GET", "/api/ledger/data"),
    ("GET", "/api/ledger/ledgers"), ("POST", "/api/ledger/ledgers"),
    ("GET", "/api/ledger/ledgers/{ledger_id}"), ("PUT", "/api/ledger/ledgers/{ledger_id}"),
    ("DELETE", "/api/ledger/ledgers/{ledger_id}"),
    ("POST", "/api/ledger/ledgers/{ledger_id}/businesses"),
    ("GET", "/api/ledger/businesses/{business_id}"), ("PUT", "/api/ledger/businesses/{business_id}"),
    ("DELETE", "/api/ledger/businesses/{business_id}"),
    ("PUT", "/api/ledger/businesses/{business_id}/weeks/{n}"),
    ("DELETE", "/api/ledger/businesses/{business_id}/weeks/{n}"),
    ("POST", "/api/ledger/ledgers/{ledger_id}/weeks/{n}"),
}


def code_of(thing) -> str:
    source = inspect.getsource(thing)
    source = re.sub(r'"""..*?"""', " ", source, flags=re.S)
    return re.sub(r"(?m)#.*$", " ", source)


def _routes():
    return [(m, r.path, r.endpoint) for r in ledger.router.routes for m in r.methods]


def _migration_text() -> str:
    for base in (ROOT / "backend", ROOT):
        found = list((base / "alembic" / "versions").glob("l0j7g3h8i965_*.py"))
        if found:
            return found[0].read_text()
    raise AssertionError("the Ledger's migration is missing")


# ── the contract ────────────────────────────────────────────────────────────

def test_the_routes_are_the_contracts() -> None:
    assert {(m, p) for m, p, _ in _routes()} == CONTRACT


def test_the_ledger_is_served() -> None:
    from shruti.api import app as app_module
    assert "app.include_router(ledger.router)" in inspect.getsource(app_module)


def test_every_route_but_the_data_asks_who_is_reading() -> None:
    """Every route but the pack answers only to a signed-in reader, through `_reader`."""
    for helper in (ledger._my_ledger, ledger._my_business):
        assert "_reader(" in code_of(helper)
        assert "404" in code_of(helper), "somebody else's ledger is 404, never 403"
    for method, path, endpoint in _routes():
        if path == "/api/ledger/data":
            continue
        code = code_of(endpoint)
        assert any(c in code for c in ("_reader(", "_my_ledger(", "_my_business(")), (
            f"{method} {path} answers without asking who is reading")


def test_the_data_route_reads_no_session() -> None:
    """Planning works signed out: the pack is facts about a game, nothing about a person."""
    assert not inspect.signature(ledger.data).parameters, "the data route takes a request or a session"
    code = code_of(ledger.data) + code_of(ledger._pack)
    for word in ("_reader", "current_user", "session", "Request", "cookie"):
        assert word not in code, f"the data route reads {word}"


def test_nothing_in_the_ledger_is_gated_or_paid_for() -> None:
    code = code_of(ledger)
    for word in ("require_publish_agreement", "require_admin", "refuse_if_out_of_allowance",
                 "Entitlement", "has_access", "Tier", "Supporter", "shruti.core.access"):
        assert word not in code, f"the ledger reaches for {word}"


def test_a_null_line_stays_null() -> None:
    """Not written is not zero: in, stored and out, a line left out is null."""
    lines = ledger.WeekLines(money_in=100)
    assert all(getattr(lines, line) is None for line in ledger.LINES if line != "money_in")
    view = ledger._week_view(LedgerWeek(business_id=1, n=3, money_in=100.0, goods=None, wages=0.0))
    assert view["goods"] is None and view["units"] is None and view["customers"] is None
    assert view["wages"] == 0.0, "a zero that was written is a zero"
    assert all(LedgerWeek.model_fields[line].default is None for line in ledger.LINES)
    code = code_of(ledger)
    assert not re.search(r"\bor 0(\.0)?\b|\?\? 0", code), "something reads a null line as zero"
    lines = _migration_text().split('op.create_table(\n        "ledger_week"')[1].split('"note"')[0]
    assert "MONEY_LINES" in lines and "server_default" not in lines, (
        "a week line has a default, so an unwritten line would read as 0")


def test_a_week_is_numbers_or_nothing() -> None:
    for bad in (float("nan"), float("inf"), True, "12", 1e14):
        with pytest.raises(Exception):
            ledger.WeekLines(money_in=bad)
    for bad in (1.5, -1, True):
        with pytest.raises(Exception):
            ledger.WeekLines(money_in=1, units=bad)
    week = ledger.WeekLines.model_validate({"moneyIn": 12.5, "goods": -3, "units": 4.0})
    assert week.money_in == 12.5 and week.goods == -3.0 and week.units == 4


def test_a_plan_is_checked_for_shape_and_size_not_sense() -> None:
    assert ledger._plan({"typeId": "whatever-this-is", "hours": [[0] * 24] * 7}) is not None
    for bad in ([], {"hours": [[0] * 24] * 6}, {"hours": [[10] * 24] * 7}, {"hours": [[True] * 24] * 7},
                {"x": "y" * (64 * 1024)}, {"x": float("nan")}):
        with pytest.raises(HTTPException):
            ledger._plan(bad)


def test_names_are_there_and_short() -> None:
    assert ledger._name("  Acorn Gifts ", "business") == "Acorn Gifts"
    for bad in ("", "   ", None, "x" * 81):
        with pytest.raises(HTTPException):
            ledger._name(bad, "ledger")


def test_week_numbers_are_bounded() -> None:
    src = inspect.getsource(ledger)
    assert "WeekN = Annotated[int, Path(ge=1, le=MAX_WEEK)]" in src and ledger.MAX_WEEK == 9999
    for fn in (ledger.write_week, ledger.remove_week, ledger.entry_grid):
        assert inspect.signature(fn).parameters["n"].annotation in ("WeekN", ledger.WeekN)


def test_the_entry_grid_skips_rows_without_money_in_and_says_so() -> None:
    code = code_of(ledger.entry_grid)
    assert "money_in is None" in code and "skipped" in code and "written" in code
    assert code.index("strangers") < code.index("_write_week("), "a stranger's row is refused before anything is written"


# ── the data pack ───────────────────────────────────────────────────────────

def test_a_missing_pack_is_a_working_state(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(gamedata, "GAMEDATA_DIR", tmp_path)
    with pytest.raises(HTTPException) as refused:
        ledger.data()
    assert refused.value.status_code == 404 and refused.value.detail == "the game's data is not loaded yet"
    (tmp_path / "ledger-big-ambitions.json").write_text(json.dumps({"game": {"id": "big-ambitions", "version": "1.0"}}))
    served = ledger.data()
    assert json.loads(served.body)["game"]["version"] == "1.0"
    assert served.media_type == "application/json"


# ── privacy ─────────────────────────────────────────────────────────────────

def test_a_ledger_goes_with_its_account_and_is_in_the_export() -> None:
    migration = _migration_text()
    assert 'down_revision = "k9i6f2g7h854"' in migration
    assert 'sa.ForeignKey("site_user.id", ondelete="CASCADE")' in migration
    assert 'sa.ForeignKey("ledger.id", ondelete="CASCADE")' in migration
    assert 'sa.ForeignKey("ledger_business.id", ondelete="CASCADE")' in migration
    assert 'NOBODYS_BUT_THEIRS = [("ledger", "user_id")]' in migration
    assert "def downgrade" in migration and 'op.drop_table("ledger")' in migration
    from shruti.api.routes import accounts
    code = code_of(accounts._everything_else)
    for name in ("Ledger,", "LedgerBusiness", "LedgerWeek", '"ledgers"'):
        assert name in code, f"the export leaves out {name}"


def test_the_ledger_hides_with_the_guides() -> None:
    from shruti.core import settings_store
    assert "/ledger" in settings_store.SECTION_PATHS["guides"]
    middleware = (ROOT / "frontend" / "site" / "src" / "middleware.ts").read_text()
    assert '"/ledger": "guides"' in middleware


# ── against Postgres ────────────────────────────────────────────────────────

@pytest.mark.skipif(not URL, reason=(
    "SHRUTI_ERASE_DATABASE_URL is not set — the ledger was NOT checked against a database. "
    "Run scripts/test-erase.sh"))
def test_a_ledger_is_kept_exported_and_erased(monkeypatch) -> None:
    asyncio.run(_keep_a_ledger_and_leave(monkeypatch))


async def _keep_a_ledger_and_leave(monkeypatch):
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlmodel import func, select

    from shruti.api.routes.accounts import erase, export_for
    from shruti.models.accounts import User
    from shruti.models.ledger import Ledger, LedgerBusiness

    engine = create_async_engine(URL)
    reader = {}

    async def as_reader(_request, _session):
        return reader["user"]

    monkeypatch.setattr(ledger, "_reader", as_reader)
    hours = [[0] * 9 + [1] * 12 + [0] * 3 for _ in range(7)]

    async with AsyncSession(engine, expire_on_commit=False) as s:
        cy = User(email="cy.ledger@example.com", display_name="Cy")
        di = User(email="di.ledger@example.com", display_name="Di")
        s.add_all([cy, di]); await s.flush(); await s.commit()

        reader["user"] = cy
        book = await ledger.start_ledger(ledger.LedgerIn.model_validate(
            {"name": " Acorn Holdings ", "difficulty": "Normal", "courses": ["headquarters"], "inGameDay": 12}), None, s)
        assert book["name"] == "Acorn Holdings" and book["difficulty"] == "normal" and book["inGameDay"] == 12
        gifts = await ledger.keep_plan(book["id"], ledger.BusinessIn(name="Acorn Gifts", plan={"typeId": "gift-shop", "hours": hours}), None, s)
        cafe = await ledger.keep_plan(book["id"], ledger.BusinessIn(name="Acorn Coffee", plan={}), None, s)
        assert gifts["keptPlan"] == gifts["plan"] and gifts["opened"] is False and cafe["position"] == 1

        week = await ledger.write_week(gifts["id"], 1, ledger.WeekLines.model_validate(
            {"moneyIn": 73171, "goods": 20000.5}), None, s)
        assert week["wages"] is None and week["goods"] == 20000.5, "an unwritten line came back as something"
        try:
            await ledger.write_week(gifts["id"], 2, ledger.WeekLines(goods=5), None, s)
            raise AssertionError("a week with no money in was written")
        except HTTPException as refused:
            assert refused.status_code == 422

        grid = await ledger.entry_grid(book["id"], 2, ledger.EntryGridIn.model_validate(
            {"rows": [{"businessId": gifts["id"], "moneyIn": 70000, "wages": 0},
                      {"businessId": cafe["id"], "goods": 12}]}), None, s)
        assert grid["written"] == [gifts["id"]] and grid["skipped"] == [cafe["id"]]
        weeks = grid["ledger"]["businesses"][0]["weeks"]
        assert [w["n"] for w in weeks] == [1, 2] and weeks[1]["wages"] == 0 and weeks[1]["goods"] is None

        opened = await ledger.change_business(gifts["id"], ledger.BusinessPatch.model_validate(
            {"opened": True, "plan": {"typeId": "gift-shop"}}), None, s)
        assert opened["opened"] and opened["keptPlan"]["hours"] == hours, "changing the plan left the kept one alone"
        await ledger.remove_week(gifts["id"], 1, None, s)

        # Somebody else's ledger is not there at all.
        reader["user"] = di
        theirs = await ledger.start_ledger(ledger.LedgerIn(name="Di's"), None, s)
        for attempt in (ledger.one_ledger(book["id"], None, s), ledger.one_business(gifts["id"], None, s),
                        ledger.write_week(gifts["id"], 3, ledger.WeekLines(money_in=1), None, s),
                        ledger.entry_grid(theirs["id"], 1, ledger.EntryGridIn.model_validate(
                            {"rows": [{"businessId": gifts["id"], "moneyIn": 1}]}), None, s)):
            try:
                await attempt
                raise AssertionError("somebody else's ledger answered")
            except HTTPException as refused:
                assert refused.status_code == 404
        assert [g["id"] for g in await ledger.my_ledgers(None, s)] == [theirs["id"]]

        reader["user"] = cy
        mine = await ledger.my_ledgers(None, s)
        assert [(g["id"], g["businesses"]) for g in mine] == [(book["id"], 2)]

        exported = await export_for(cy, s)
        assert len(exported["ledgers"]) == 1, "the export has no ledger"
        kept = exported["ledgers"][0]
        assert kept["name"] == "Acorn Holdings" and len(kept["businesses"]) == 2
        written = kept["businesses"][0]["weeks"]
        assert [w["n"] for w in written] == [2] and written[0]["goods"] is None and written[0]["money_in"] == 70000
        ids = dict(cy=cy.id, di=di.id, book=book["id"], theirs=theirs["id"])

    async with AsyncSession(engine, expire_on_commit=False) as s:
        await erase(await s.get(User, ids["cy"]), s)

    async with AsyncSession(engine, expire_on_commit=False) as s:
        assert await s.get(Ledger, ids["book"]) is None, "the ledger outlived its account"
        left = (await s.execute(select(func.count()).select_from(LedgerBusiness)
                                .where(LedgerBusiness.ledger_id == ids["book"]))).scalar_one()
        assert left == 0, "a business outlived its ledger"
        weeks_left = (await s.execute(select(func.count()).select_from(LedgerWeek))).scalar_one()
        assert weeks_left == 0, "a week outlived its business"
        assert await s.get(Ledger, ids["theirs"]) is not None, "somebody else's ledger went too"
    await engine.dispose()


def test_the_server_totals_a_week_and_never_counts_a_blank() -> None:
    """The app shows the week the server reads; it adds nothing up itself."""
    from shruti.api.routes.ledger import _week_total
    from shruti.models.ledger import LedgerWeek

    assert _week_total(LedgerWeek(business_id=1, n=1, money_in=100.0, goods=30.0, wages=None, rent=10.0)) == 60.0
    assert _week_total(LedgerWeek(business_id=1, n=1, money_in=None, goods=30.0)) is None
    assert _week_total(LedgerWeek(business_id=1, n=1, money_in=50.0)) == 50.0
