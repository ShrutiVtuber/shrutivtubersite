# SPDX-License-Identifier: AGPL-3.0-only
"""
Swara Studio when an account is deleted, and Listen's reports, against
Postgres (the owner's rules of 26 Sep 2026).

- Listen posts, comments, likes, reports and the practice log are kept
  without a name; settings, progress and app sign-ins go.
- Songs are the person's choice: `anonymise` keeps published sheets up,
  credited to nobody (unpublished drafts go); `delete` deletes them all.
  Somebody with songs who has not chosen is asked (409) and nothing goes.
- Three reports from different accounts hide a post until she reviews it;
  restoring it spends those reports.

Needs a database migrated to head: run `scripts/test-erase.sh`. Without
`SHRUTI_ERASE_DATABASE_URL` these SKIP, and say so.
"""
from __future__ import annotations

import asyncio
import os
import uuid

import pytest

URL = os.environ.get("SHRUTI_ERASE_DATABASE_URL", "")
needs_db = pytest.mark.skipif(not URL, reason=(
    "SHRUTI_ERASE_DATABASE_URL is not set — Swara Studio's deletion was NOT checked. Run scripts/test-erase.sh"))


def _run(coro):
    return asyncio.run(coro)


async def _people_with_one_of_everything(s):
    from shruti.models.accounts import User
    from shruti.models.carnatic import (
        CarnaticComment, CarnaticDeviceLink, CarnaticLike, CarnaticPost, CarnaticPracticeDay,
        CarnaticProfile, CarnaticProgress, CarnaticReport, CarnaticSong,
    )
    from datetime import datetime, timedelta, timezone

    tag = uuid.uuid4().hex[:8]
    a = User(email=f"ada-{tag}@example.com", display_name="Ada")
    b = User(email=f"bo-{tag}@example.com", display_name="Bo")
    s.add_all([a, b]); await s.flush()
    sheet = CarnaticSong(user_id=a.id, slug=f"kaalai-{tag}", title="Kaalai", raga="mohanam", tala="adi",
                         body={"title": "Kaalai"}, published=True, published_at=datetime.now(timezone.utc))
    draft = CarnaticSong(user_id=a.id, slug=f"draft-{tag}", title="Draft", raga="mohanam", tala="adi",
                         body={"title": "Draft"})
    s.add_all([sheet, draft]); await s.flush()
    post = CarnaticPost(user_id=a.id, song_id=sheet.id, title="Kaalai, live", player="youtube",
                        url="https://youtu.be/x")
    bos = CarnaticPost(user_id=b.id, title="Bo's sketch", player="youtube", url="https://youtu.be/y")
    s.add_all([post, bos]); await s.flush()
    s.add_all([
        CarnaticComment(post_id=bos.id, user_id=a.id, body="Lovely"),
        CarnaticLike(post_id=bos.id, user_id=a.id),
        CarnaticReport(user_id=a.id, post_id=bos.id, reason="test"),
        CarnaticPracticeDay(user_id=a.id, day="2026-09-26", seconds=600, sessions=1),
        CarnaticProfile(user_id=a.id, settings={"lang": "ta"}),
        CarnaticProgress(user_id=a.id, item_id="sarali_01", speeds=[1]),
        CarnaticDeviceLink(user_id=a.id, token_hash="t" + tag, code_hash="c" + tag,
                           expires_at=datetime.now(timezone.utc) + timedelta(minutes=5)),
    ])
    await s.commit()
    return a, b, sheet, draft, post, bos


async def _leave(songs: str):
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlmodel import func, select
    from shruti.api.routes.accounts import delete_account
    from shruti.models.carnatic import (
        CarnaticComment, CarnaticDeviceLink, CarnaticLike, CarnaticPost, CarnaticPracticeDay,
        CarnaticProfile, CarnaticProgress, CarnaticReport, CarnaticSong,
    )
    from fastapi import Response

    engine = create_async_engine(URL)
    async with AsyncSession(engine, expire_on_commit=False) as s:
        a, b, sheet, draft, post, bos = await _people_with_one_of_everything(s)
        uid = a.id

        # Not chosen yet: asked, and nothing goes.
        asked = await delete_account(Response(), a, s, songs=None)
        assert asked.status_code == 409 and b'"SONGS_CHOICE_NEEDED"' in asked.body
        assert b'"songs":2' in asked.body and b'"published":1' in asked.body
        assert await s.get(CarnaticSong, sheet.id) is not None

        result = await delete_account(Response(), a, s, songs=songs)
        assert result["ok"]

    async with AsyncSession(engine, expire_on_commit=False) as s:
        count = lambda model, *where: s.execute(select(func.count()).select_from(model).where(*where))
        # Kept without a name.
        p = await s.get(CarnaticPost, post.id)
        assert p is not None and p.user_id is None and p.author_deleted_at is not None
        c = (await s.execute(select(CarnaticComment).where(CarnaticComment.post_id == bos.id))).scalar_one()
        assert c.user_id is None and c.author_deleted_at is not None
        assert (await count(CarnaticLike, CarnaticLike.post_id == bos.id)).scalar_one() == 1
        assert (await count(CarnaticReport, CarnaticReport.post_id == bos.id)).scalar_one() == 1
        day = (await s.execute(select(CarnaticPracticeDay).where(CarnaticPracticeDay.day == "2026-09-26",
                                                                  CarnaticPracticeDay.seconds == 600))).scalars().all()
        assert day and all(d.user_id is None for d in day)
        # Theirs alone: gone.
        for model in (CarnaticProfile, CarnaticProgress, CarnaticDeviceLink):
            assert (await count(model, model.user_id == uid)).scalar_one() == 0
        # Nothing anywhere still points at them.
        for model in (CarnaticSong, CarnaticPost, CarnaticComment, CarnaticLike, CarnaticReport, CarnaticPracticeDay):
            assert (await count(model, model.user_id == uid)).scalar_one() == 0, model.__name__
        # Bo is untouched.
        assert (await s.get(CarnaticPost, bos.id)).user_id == b.id
        # Songs, as chosen. The draft goes either way.
        assert await s.get(CarnaticSong, draft.id) is None
        kept = await s.get(CarnaticSong, sheet.id)
        if songs == "anonymise":
            assert kept is not None and kept.published and kept.user_id is None and kept.author_deleted_at is not None
            assert p.song_id == sheet.id
        else:
            assert kept is None and p.song_id is None
    await engine.dispose()


@needs_db
def test_anonymise_keeps_the_published_sheet_credited_to_nobody() -> None:
    _run(_leave("anonymise"))


@needs_db
def test_delete_takes_every_song_and_keeps_the_rest_without_a_name() -> None:
    _run(_leave("delete"))


async def _three_reports():
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from shruti.api.routes import carnatic as routes
    from shruti.models.accounts import User
    from shruti.models.carnatic import CarnaticPost

    routes.REPORTED_BY_USER._seen.clear()
    engine = create_async_engine(URL)
    async with AsyncSession(engine, expire_on_commit=False) as s:
        tag = uuid.uuid4().hex[:8]
        people = [User(email=f"r{i}-{tag}@example.com", display_name=f"R{i}") for i in range(6)]
        s.add_all(people); await s.flush()
        post = CarnaticPost(user_id=people[0].id, title="Reported", player="youtube", url="https://youtu.be/z")
        s.add(post); await s.commit()

        # The same person reporting twice is one report.
        await routes._report(people[1], "spam", s, post, post_id=post.id)
        await routes._report(people[1], "spam", s, post, post_id=post.id)
        await routes._report(people[2], "", s, post, post_id=post.id)
        await s.refresh(post)
        assert not post.hidden, "two reporters must not hide anything"
        await routes._report(people[3], "rude", s, post, post_id=post.id)
        await s.refresh(post)
        assert post.hidden and post.hidden_by == "reports"

        # Waiting for her, first in the queue; reporters are never named.
        mod = await routes.admin_moderation("op", s)
        first = mod["posts"][0]
        assert first["id"] == post.id and first["hiddenBy"] == "reports" and first["reports"] == 3
        assert mod["awaitingReview"] >= 1
        assert not any(k in first for k in ("reporters", "userIds", "by"))

        # She restores it: the reports she weighed are spent.
        await routes.admin_hide_post(post.id, routes.HideIn(hidden=False), "op", s)
        await s.refresh(post)
        assert not post.hidden and post.reviewed_at is not None
        await routes._report(people[4], "", s, post, post_id=post.id)
        await s.refresh(post)
        assert not post.hidden, "reports made before she restored it must not count again"

        # She removes it: gone, with its reports.
        await routes.admin_remove_post(post.id, "op", s)
        assert await s.get(CarnaticPost, post.id) is None
    await engine.dispose()


@needs_db
def test_three_reporters_hide_a_post_until_she_reviews_it() -> None:
    _run(_three_reports())


async def _a_reported_sheet():
    from datetime import datetime, timezone
    from fastapi import HTTPException
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from shruti.api.routes import carnatic as routes
    from shruti.models.accounts import User
    from shruti.models.carnatic import CarnaticPost, CarnaticReport, CarnaticSong
    from sqlmodel import func, select

    routes.REPORTED_BY_USER._seen.clear()
    engine = create_async_engine(URL)
    async with AsyncSession(engine, expire_on_commit=False) as s:
        tag = uuid.uuid4().hex[:8]
        people = [User(email=f"s{i}-{tag}@example.com", display_name=f"S{i}") for i in range(5)]
        s.add_all(people); await s.flush()
        # An anonymised sheet: its author chose to keep it when they left.
        sheet = CarnaticSong(user_id=None, slug=f"kept-{tag}", title="Kept", raga="mohanam", tala="adi",
                             body={"title": "Kept"}, published=True, published_at=datetime.now(timezone.utc),
                             author_deleted_at=datetime.now(timezone.utc))
        s.add(sheet); await s.flush()
        post = CarnaticPost(user_id=people[0].id, song_id=sheet.id, title="Linked", player="youtube",
                            url="https://youtu.be/k")
        s.add(post); await s.commit()

        for who in (people[1], people[1], people[2]):
            await routes.report_sheet(sheet.slug, routes.ReportIn(reason="wrong"), who, s)
        await s.refresh(sheet)
        assert not sheet.hidden, "two reporters must not hide a sheet"
        await routes.report_sheet(sheet.slug, routes.ReportIn(reason=""), people[3], s)
        await s.refresh(sheet)
        assert sheet.hidden and sheet.hidden_by == "reports"

        # Hidden: not found for anyone, and no longer linked from Listen.
        with pytest.raises(HTTPException) as e:
            await routes.sheet(sheet.slug, people[4], s)
        assert e.value.status_code == 404
        assert (await routes.listen_post(post.id, None, s))["sheetSlug"] is None

        mod = await routes.admin_moderation("op", s)
        first = mod["sheets"][0]
        assert first["id"] == sheet.id and first["hiddenBy"] == "reports" and first["reports"] == 3
        assert first["anonymised"] and not any(k in first for k in ("reporters", "userIds", "by"))

        # Restored: shown again, and only new reports count.
        await routes.admin_hide_sheet(sheet.id, routes.HideIn(hidden=False), "op", s)
        await s.refresh(sheet)
        assert not sheet.hidden and sheet.reviewed_at is not None
        assert (await routes.sheet(sheet.slug, people[4], s))["author"] is None
        await routes.report_sheet(sheet.slug, routes.ReportIn(reason=""), people[4], s)
        await s.refresh(sheet)
        assert not sheet.hidden

        # Removed for good, although its author chose to keep it.
        await routes.admin_remove_sheet(sheet.id, "op", s)
        assert await s.get(CarnaticSong, sheet.id) is None
        assert (await s.execute(select(func.count()).select_from(CarnaticReport)
                                .where(CarnaticReport.song_id == sheet.id))).scalar_one() == 0
        await s.refresh(post)
        assert post.song_id is None
    await engine.dispose()


@needs_db
def test_a_sheet_is_hidden_by_three_reporters_and_she_can_remove_it() -> None:
    _run(_a_reported_sheet())


async def _banned(monkeypatch):
    from datetime import datetime, timezone
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from shruti.api.routes import admin
    from shruti.core import mail
    from shruti.models.accounts import User
    from shruti.models.carnatic import CarnaticComment, CarnaticPost, CarnaticSong

    class Sent:
        sent, error = True, None

    async def send(**_kw):
        return Sent()

    monkeypatch.setattr(mail, "send", send)
    engine = create_async_engine(URL)
    async with AsyncSession(engine, expire_on_commit=False) as s:
        tag = uuid.uuid4().hex[:8]
        u = User(email=f"banned-{tag}@example.com", display_name="Banned")
        s.add(u); await s.flush()
        sheet = CarnaticSong(user_id=u.id, slug=f"ban-sheet-{tag}", title="Sheet", raga="mohanam", tala="adi",
                             body={"title": "Sheet"}, published=True, published_at=datetime.now(timezone.utc))
        draft = CarnaticSong(user_id=u.id, slug=f"ban-draft-{tag}", title="Draft", raga="mohanam", tala="adi",
                             body={"title": "Draft"})
        s.add_all([sheet, draft]); await s.flush()
        post = CarnaticPost(user_id=u.id, song_id=sheet.id, title="Theirs", player="youtube", url="https://youtu.be/b")
        s.add(post); await s.flush()
        s.add(CarnaticComment(post_id=post.id, user_id=u.id, body="hello"))
        await s.commit()

        await admin.ban_user(u.id, admin.BanIn(reason="test"), s, "op")

        # Songs and sheets: removed, not kept credited to nobody.
        assert await s.get(CarnaticSong, sheet.id) is None and await s.get(CarnaticSong, draft.id) is None
        # Everything else keeps the rule for any deleted account: kept without a name.
        kept = await s.get(CarnaticPost, post.id)
        await s.refresh(kept)
        assert kept is not None and kept.user_id is None and kept.song_id is None
    await engine.dispose()


@needs_db
def test_a_ban_removes_their_songs_and_keeps_the_rest_without_a_name(monkeypatch) -> None:
    _run(_banned(monkeypatch))
