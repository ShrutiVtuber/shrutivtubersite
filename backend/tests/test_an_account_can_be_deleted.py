# SPDX-License-Identifier: AGPL-3.0-only
"""
An account can be deleted — all the way — and what its owner made public
stays up, without their name.

⚠ **Deletion could not finish, and nobody knew.** Nine tables pointed at
`site_user` with no ON DELETE and `erase()` never cleared them, so the final
DELETE raised, the transaction rolled back, and the person had been told
nothing went wrong. No test ran it; every guard in this suite reads source.

So two kinds of check here:

- **Guards on the source**, which run everywhere: every foreign key to
  `site_user` is answered for, every endpoint that makes something public asks
  for the agreement first, and a public name is never an email address.
- **The deletion itself, against Postgres**, which is the only way to know a
  foreign key will not refuse it. It needs a database migrated to head and
  runs from `scripts/test-erase.sh`; without `SHRUTI_ERASE_DATABASE_URL` it
  SKIPS, and says so, rather than passing on nothing.
"""
from __future__ import annotations

import asyncio
import importlib.util
import inspect
import os
import re
from datetime import datetime, timezone

import pytest

from conftest import BACKEND, ROOT   # noqa: E402  (see conftest for why)

URL = os.environ.get("SHRUTI_ERASE_DATABASE_URL", "")
NOW = datetime.now(timezone.utc)

# Foreign keys to site_user answered before migration k9i6f2g7h854, by their
# own ON DELETE — and the one `erase()` clears by hand.
ANSWERED_EARLIER = {
    ("standing_test", "user_id"), ("collab_group", "user_id"), ("app_device", "user_id"),
    ("practice_vote", "user_id"), ("practice_strike", "user_id"), ("practice_report", "user_id"),
}
CLEARED_BY_ERASE = {("guide_run", "user_id")}


def code_of(function) -> str:
    source = inspect.getsource(function)
    source = re.sub(r'"""..*?"""', " ", source, flags=re.S)
    return re.sub(r"(?m)#.*$", " ", source)


def _migration():
    versions = ROOT / "backend" / "alembic" / "versions"
    if not versions.is_dir():
        versions = ROOT / "alembic" / "versions"
    path = next(versions.glob("k9i6f2g7h854_*.py"))
    spec = importlib.util.spec_from_file_location("k9i6f2g7h854", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _foreign_keys_to_users() -> set[tuple[str, str]]:
    """(table, column) for every model field pointing at site_user."""
    found = set()
    for path in (BACKEND / "models").glob("*.py"):
        table = None
        lines = path.read_text().splitlines()
        for i, line in enumerate(lines):
            m = re.search(r'__tablename__\s*=\s*"(\w+)"', line)
            if m:
                table = m.group(1)
            if 'foreign_key="site_user.id"' in line:
                # The field name is on this line or the one that opened the Field(.
                for back in range(i, max(i - 3, -1), -1):
                    f = re.match(r"\s+(\w+):", lines[back])
                    if f:
                        found.add((table, f.group(1)))
                        break
    return found


def test_every_foreign_key_to_a_user_is_answered_for() -> None:
    """
    A table added later that points at users, and says nothing about what
    happens to its rows when one is deleted, would make deletion fail again —
    silently, for everybody who has a row in it. This is where it gets caught.
    """
    m = _migration()
    answered = (
        {(t, c) for t, c, *_rest in m.KEPT_WITHOUT_A_NAME}
        | set(m.NOBODYS_BUT_THEIRS) | ANSWERED_EARLIER | CLEARED_BY_ERASE
    )
    keys = _foreign_keys_to_users()
    assert len(keys) > 25, "found too few foreign keys — the parse has broken, not the schema"
    missing = sorted(keys - answered)
    assert not missing, (
        "these point at site_user and nothing says what happens to them when an "
        f"account is deleted: {missing}. Give them an ON DELETE in a migration, "
        "or clear them in accounts.erase, and name them here."
    )


def _classes_of_tables() -> dict[str, str]:
    out = {}
    for path in (BACKEND / "models").glob("*.py"):
        cls = None
        for line in path.read_text().splitlines():
            m = re.match(r"class (\w+)\(", line)
            if m:
                cls = m.group(1)
            t = re.search(r'__tablename__\s*=\s*"(\w+)"', line)
            if t and cls:
                out[t.group(1)] = cls
    return out


def test_the_export_reaches_every_table_that_holds_a_person() -> None:
    """
    The right of access is "everything held about you". A table that points
    at people and is missing from the export leaves the download short, and
    nobody reading a JSON file would notice what is not in it.
    """
    from shruti.api.routes import accounts

    code = code_of(accounts.export_for) + code_of(accounts._everything_else)
    classes = _classes_of_tables()
    tables = {t for t, _c in _foreign_keys_to_users()}
    missing = sorted(t for t in tables if classes.get(t) and classes[t] + "." not in code
                     and classes[t] + ")" not in code and classes[t] + "," not in code)
    assert not missing, f"the export never reads these tables: {missing}"


def test_the_export_never_carries_a_key() -> None:
    from shruti.api.routes.accounts import _NEVER_EXPORTED, _plain
    from shruti.models.accounts import SavedChart

    row = _plain(SavedChart(user_id=1, owner_token="secret-owner", share_token="secret-share",
                            birth_date="1990-01-01"))
    assert "owner_token" not in row and "share_token" not in row
    assert "password_hash" in _NEVER_EXPORTED and "public_key" in _NEVER_EXPORTED


def test_the_app_is_served_the_words_it_files() -> None:
    from shruti.api.routes.accounts import CONSENT_SOURCES, consent_wording
    from shruti.core.consents import ALL, PUBLISH

    served = asyncio.run(consent_wording())
    assert served["publish"]["wording"] == PUBLISH.wording
    assert {c["kind"] for c in served["consents"]} == {c.kind for c in ALL}, (
        "the publish agreement must not join the signup list")
    assert "app" in CONSENT_SOURCES and "publish-dialog" in CONSENT_SOURCES


def test_what_is_nobodys_but_theirs_goes_with_them() -> None:
    m = _migration()
    for table in ("passkey", "push_subscription", "saved_chart", "comparison", "entitlement",
                  "enrolment", "lesson_progress", "nativity"):
        assert (table, "user_id") in m.NOBODYS_BUT_THEIRS, f"{table} must cascade"
    assert ("practice_block", "blocked_id") in m.NOBODYS_BUT_THEIRS


def test_what_they_published_is_kept_and_marked() -> None:
    m = _migration()
    kept = {(t, c): ondelete for t, c, _target, ondelete, _null in m.KEPT_WITHOUT_A_NAME}
    for key in (("guide", "created_by"), ("guide_version", "created_by"),
                ("practice_work", "user_id"), ("practice_comment", "user_id"),
                ("guide_group", "created_by"), ("guide_group_contribution", "user_id"),
                ("build", "user_id")):
        assert kept.get(key) == "SET NULL", f"{key} must outlive its author"
        assert key[0] in m.ANONYMISED, f"{key[0]} must say when its author left"


def test_every_way_of_going_public_asks_first() -> None:
    from shruti.api.routes import builds, groups, guides, practice

    for fn in (guides.submit, practice.submit, practice.comment, groups.create,
               groups.contribute, builds.share_build):
        assert "require_publish_agreement(" in code_of(fn), (
            f"{fn.__module__}.{fn.__name__} makes something public without the agreement")


def test_the_agreement_is_asked_on_publishing_and_never_at_signup() -> None:
    from shruti.core.consents import ALL, BY_KIND, PUBLISH

    assert PUBLISH not in ALL, "signup and the app's consent screen render ALL"
    assert BY_KIND["publish"] is PUBLISH, "the account page must be able to give and withdraw it"
    assert PUBLISH.lawful_basis == "contract"
    assert "name taken off" in PUBLISH.wording and "Discord" in PUBLISH.wording


def test_a_reply_to_somebody_who_left_wakes_nobody() -> None:
    """
    `tell(to_user=None)` means every device that wants replies. A notification
    addressed to an anonymised author would go to all of them, so every call
    that addresses one checks there is somebody there first.
    """
    from shruti.api.routes import practice

    source = inspect.getsource(practice)
    for m in re.finditer(r"to_user=work\.user_id", source):
        before = source[max(0, m.start() - 1500):m.start()]
        guard = before.rfind("if work.user_id")
        assert guard != -1, "a reply notification is sent without checking the author is there"
        line = before[guard:before.find("\n", guard)]
        assert "is not None" in line or line.strip().rstrip(":") == "if work.user_id", line


def test_a_public_name_is_never_an_email_address() -> None:
    from shruti.api.routes.practice import _name
    from shruti.models.accounts import User

    assert _name(User(email="someone.private@example.com", display_name="")) == "somebody"
    assert _name(User(email="x@example.com", display_name="  Ada ")) == "Ada"
    assert _name(None) == "somebody"


def test_the_website_asks_before_it_publishes() -> None:
    site = ROOT / "frontend" / "site" / "src"
    for page in ("pages/guides/write/[version].astro", "pages/practice/[id].astro",
                 "pages/groups/index.astro", "pages/groups/[code].astro"):
        text = (site / page).read_text()
        assert "<PublishConsent />" in text, f"{page} can publish but has no dialog to ask with"
    assert "publishing(" in (site / "lib/groups.ts").read_text()
    assert "publishing(" in (site / "pages/practice/[id].astro").read_text()
    assert "publishing(" in (site / "pages/guides/write/[version].astro").read_text()


@pytest.mark.skipif(not URL, reason=(
    "SHRUTI_ERASE_DATABASE_URL is not set — the deletion itself was NOT checked. "
    "Run scripts/test-erase.sh"))
def test_an_account_can_be_deleted() -> None:
    asyncio.run(_delete_somebody_with_one_of_everything())


def body(authors):
    return {"guide": {"id": "x", "title": "T", "authors": authors, "licence": "CC-BY-SA-4.0"}, "phases": []}


async def _delete_somebody_with_one_of_everything():
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlmodel import func, select

    from shruti.api.routes.accounts import erase
    from shruti.core.consents import PUBLISH
    from shruti.core.publishing import has_agreed_to_publish
    from shruti.models import OverlayToken, PushSubscription
    from shruti.models.accounts import (
        Comparison, ConsentRecord, Nativity, Passkey, SavedChart, Subscriber, User,
    )
    from shruti.models.guides import (
        Build, Game, Group, GroupContribution, GroupMember, Guide, GuideRun, GuideVersion, GuideVote,
    )
    from shruti.models.practice import PracticeBlock, PracticeComment, PracticeReading, PracticeWork

    engine = create_async_engine(URL)
    async with AsyncSession(engine, expire_on_commit=False) as s:
        a = User(email="ada@example.com", display_name="Ada")
        b = User(email="bo@example.com", display_name="Bo")
        s.add_all([a, b]); await s.flush()
        game = Game(slug="big-ambitions", name="Big Ambitions"); s.add(game); await s.flush()

        s.add(ConsentRecord(user_id=a.id, email=a.email, kind="account", granted=True, version="v",
                            wording="w", lawful_basis="contract", source="signup"))
        s.add(Subscriber(email=a.email, user_id=a.id, confirm_token="c1", unsubscribe_token="u1"))
        s.add(Nativity(user_id=a.id, birth_date="1990-01-01"))
        s.add(Passkey(user_id=a.id, credential_id="cred-a", public_key="k", sign_count=0))
        s.add(PushSubscription(user_id=a.id, endpoint="https://push/a", p256dh="p", auth="x"))
        ca = SavedChart(user_id=a.id, owner_token="oa", share_token="sa", birth_date="1990-01-01")
        cb = SavedChart(user_id=b.id, owner_token="ob", share_token="sb", birth_date="1991-01-01")
        s.add_all([ca, cb]); await s.flush()
        s.add(Comparison(user_id=b.id, owner_token="cmp-b", left_id=cb.id, right_id=ca.id))

        # Guides: G1 published (with a private draft update), G2 draft only,
        # G3 Bo's fork of G1, G4 Bo's guide with Ada's accepted change and a pending proposal.
        g1 = Guide(game_id=game.id, slug="g1", title="First million", created_by=a.id)
        g2 = Guide(game_id=game.id, slug="g2", title="Draft", created_by=a.id)
        g4 = Guide(game_id=game.id, slug="g4", title="Bo's", created_by=b.id)
        s.add_all([g1, g2, g4]); await s.flush()
        v1 = GuideVersion(guide_id=g1.id, number=1, body=body(["Ada"]), created_by=a.id, state="published")
        v1d = GuideVersion(guide_id=g1.id, number=2, body=body(["Ada"]), created_by=a.id, state="draft")
        v2 = GuideVersion(guide_id=g2.id, number=1, body=body(["Ada"]), created_by=a.id, state="draft")
        v4 = GuideVersion(guide_id=g4.id, number=1, body=body(["Bo"]), created_by=a.id, contributed_by=a.id,
                          state="published", accepted_at=NOW)
        v4p = GuideVersion(guide_id=g4.id, number=2, body=body(["Bo"]), created_by=a.id, contributed_by=a.id,
                           state="proposed")
        s.add_all([v1, v1d, v2, v4, v4p]); await s.flush()
        g1.published_version_id = v1.id; g4.published_version_id = v4.id
        g3 = Guide(game_id=game.id, slug="g3", title="Fork", created_by=b.id, forked_from_id=g1.id)
        s.add(g3); await s.flush()
        v3 = GuideVersion(guide_id=g3.id, number=1, body=body(["Ada", "Bo"]), created_by=b.id, state="published")
        s.add(v3); await s.flush(); g3.published_version_id = v3.id
        run_b = GuideRun(guide_id=g1.id, user_id=b.id)
        run_a = GuideRun(guide_id=g4.id, user_id=a.id)
        run_b2 = GuideRun(guide_id=g2.id, user_id=b.id)
        s.add_all([run_b, run_a, run_b2]); await s.flush()
        s.add(GuideVote(guide_id=g4.id, user_id=a.id))
        s.add(OverlayToken(token="tok-a", kind="guide-now", user_id=a.id, run_id=run_a.id))

        # Groups: one Bo joined, one only Ada is in.
        gr1 = Group(code="AAAAAA", name="Tier push", created_by=a.id)
        gr2 = Group(code="BBBBBB", name="Alone", created_by=a.id)
        s.add_all([gr1, gr2]); await s.flush()
        s.add_all([GroupMember(group_id=gr1.id, user_id=a.id), GroupMember(group_id=gr1.id, user_id=b.id),
                   GroupMember(group_id=gr2.id, user_id=a.id),
                   GroupContribution(group_id=gr1.id, user_id=a.id, amount=30),
                   GroupContribution(group_id=gr1.id, user_id=b.id, amount=12)])

        # Practice: a submitted reading, a draft, comments both ways, blocks both ways.
        w1 = PracticeWork(user_id=a.id, period="2026-09", submitted_at=NOW)
        w2 = PracticeWork(user_id=a.id, period="2026-10")
        w3 = PracticeWork(user_id=b.id, period="2026-09", submitted_at=NOW)
        s.add_all([w1, w2, w3]); await s.flush()
        s.add_all([PracticeReading(work_id=w1.id, sign="aries", body_md="text"),
                   PracticeComment(work_id=w1.id, user_id=b.id, body_md="lovely"),
                   PracticeComment(work_id=w3.id, user_id=a.id, body_md="thank you"),
                   PracticeBlock(user_id=a.id, blocked_id=b.id), PracticeBlock(user_id=b.id, blocked_id=a.id)])

        # Builds: shared (with notes), unshared, and one beside Ada's run.
        shared = Build(user_id=a.id, game_id=game.id, name="Shared", share_code="SHARE1", shared_at=NOW,
                       goals={"helm": {"target": "Crown", "note": "private!", "met": True}},
                       plan={"notes": "secret plan", "sections": [{"note": "x", "id": "gear"}]})
        mine = Build(user_id=a.id, game_id=game.id, name="Mine", run_id=run_a.id)
        s.add_all([shared, mine]); await s.flush()
        s.add(OverlayToken(token="tok-build", kind="build", user_id=a.id, build_id=mine.id))
        s.add(ConsentRecord(user_id=a.id, email=a.email, kind=PUBLISH.kind, granted=True, version="v",
                            wording=PUBLISH.wording, lawful_basis="contract", source="publish-modal"))
        await s.commit()
        ids = dict(a=a.id, b=b.id, g1=g1.id, g2=g2.id, g3=g3.id, g4=g4.id, v1=v1.id, v1d=v1d.id, v4=v4.id,
                   v4p=v4p.id, gr1=gr1.id, gr2=gr2.id, w1=w1.id, w2=w2.id, w3=w3.id, shared=shared.id,
                   mine=mine.id, run_b=run_b.id, run_b2=run_b2.id, ca=ca.id, cb=cb.id)
        assert await has_agreed_to_publish(s, a), "the agreement on file should count"
        assert not await has_agreed_to_publish(s, b), "no agreement on file should not count"

        # The gate, as an endpoint meets it: 428 until agreed, then through.
        from fastapi import HTTPException
        from shruti.api.routes.accounts import ConsentChangeIn, change_consent, export_for
        from shruti.core.publishing import require_publish_agreement
        try:
            await require_publish_agreement(s, b)
            raise AssertionError("publishing went through with no agreement on file")
        except HTTPException as refused:
            assert refused.status_code == 428 and "account page" in refused.detail
        await change_consent(ConsentChangeIn(kind="publish", granted=True, source="app"), b, s)
        await require_publish_agreement(s, b)
        # An old yes to other words is not a yes to these.
        s.add(ConsentRecord(user_id=b.id, email=b.email, kind=PUBLISH.kind, granted=True, version="old",
                            wording="words nobody reads any more", lawful_basis="contract", source="app"))
        await s.commit()
        assert not await has_agreed_to_publish(s, b)

        # The export, before anything goes: every kind of thing Ada made is in it.
        exported = await export_for(a, s)
        for key in ("guides", "guideVersions", "groupsStarted", "groupContributions", "builds",
                    "practiceWorks", "practiceReadings", "practiceComments", "practiceBlocks",
                    "savedCharts", "passkeys", "pushSubscriptions", "overlays"):
            assert exported[key], f"the export has no {key}"
        text = str(exported)
        assert "oa" not in [c.get("owner_token") for c in exported["savedCharts"]]
        assert "cred-a" in text and "public_key" not in text and "https://push/a" not in text

    async with AsyncSession(engine, expire_on_commit=False) as s:
        a = await s.get(User, ids["a"])
        result = await erase(a, s)

    async with AsyncSession(engine, expire_on_commit=False) as s:
        checks = []

        def check(label, ok):
            checks.append((label, ok))

        async def count(model, *where):
            return (await s.execute(select(func.count()).select_from(model).where(*where))).scalar_one()

        check("the account is gone", await s.get(User, ids["a"]) is None)
        check("the other person is untouched", await s.get(User, ids["b"]) is not None)
        g1 = await s.get(Guide, ids["g1"])
        check("published guide kept", g1 is not None and not g1.hidden)
        check("published guide has no author", g1 is not None and g1.created_by is None)
        check("its private draft update is gone", await s.get(GuideVersion, ids["v1d"]) is None)
        v1 = await s.get(GuideVersion, ids["v1"])
        check("published version kept, credit reads somebody",
              v1 is not None and v1.created_by is None and v1.body["guide"]["authors"] == ["somebody"])
        check("Bo's run of the published guide survives", await s.get(GuideRun, ids["run_b"]) is not None)
        check("draft-only guide is gone", await s.get(Guide, ids["g2"]) is None)
        check("the run of the draft-only guide went with it", await s.get(GuideRun, ids["run_b2"]) is None)
        v3 = (await s.execute(select(GuideVersion).where(GuideVersion.guide_id == ids["g3"]))).scalars().first()
        check("Bo's fork kept, Ada's name out of its credits",
              v3 is not None and v3.body["guide"]["authors"] == ["somebody", "Bo"])
        v4 = await s.get(GuideVersion, ids["v4"])
        check("accepted change kept without a name",
              v4 is not None and v4.contributed_by is None and v4.created_by is None)
        check("pending proposal is gone", await s.get(GuideVersion, ids["v4p"]) is None)
        check("Ada's vote is gone", await count(GuideVote, GuideVote.user_id == ids["a"]) == 0)
        gr1 = await s.get(Group, ids["gr1"])
        check("group Bo joined is kept, ownerless", gr1 is not None and gr1.created_by is None)
        total = (await s.execute(select(func.sum(GroupContribution.amount))
                                 .where(GroupContribution.group_id == ids["gr1"]))).scalar_one()
        check("its total still counts Ada's 30", total == 42)
        check("group only Ada was in is gone", await s.get(Group, ids["gr2"]) is None)
        w1 = await s.get(PracticeWork, ids["w1"])
        check("submitted reading kept without a name", w1 is not None and w1.user_id is None)
        check("its readings and Bo's comment kept",
              await count(PracticeReading, PracticeReading.work_id == ids["w1"]) == 1
              and await count(PracticeComment, PracticeComment.work_id == ids["w1"]) == 1)
        check("draft reading is gone", await s.get(PracticeWork, ids["w2"]) is None)
        c = (await s.execute(select(PracticeComment).where(PracticeComment.work_id == ids["w3"]))).scalars().first()
        check("Ada's comment on Bo's reading kept without a name", c is not None and c.user_id is None)
        check("blocks both ways are gone", await count(PracticeBlock) == 0)
        sh = await s.get(Build, ids["shared"])
        check("shared build kept, ownerless, notes stripped",
              sh is not None and sh.user_id is None and "note" not in sh.goals["helm"]
              and "notes" not in sh.plan and "note" not in sh.plan["sections"][0])
        check("unshared build is gone", await s.get(Build, ids["mine"]) is None)
        check("overlay tokens are gone", await count(OverlayToken) == 0)
        check("passkey, push, nativity gone",
              await count(Passkey) == 0 and await count(PushSubscription) == 0 and await count(Nativity) == 0)
        check("Ada's chart and Bo's comparison with it are gone",
              await s.get(SavedChart, ids["ca"]) is None and await count(Comparison) == 0)
        check("Bo's own chart is untouched", await s.get(SavedChart, ids["cb"]) is not None)
        check("newsletter subscription is gone", await count(Subscriber) == 0)
        cr = (await s.execute(select(ConsentRecord))).scalars().all()
        hers = [r for r in cr if r.user_id != ids["b"]]
        check("consent trail kept, anonymised",
              len(hers) == 2 and all(r.user_id is None and r.email == f"deleted-account-{ids['a']}" for r in hers))
        check("the other person's consents are untouched",
              sum(1 for r in cr if r.user_id == ids["b"] and r.email == "bo@example.com") == 2)

        failed = [l for l, ok in checks if not ok]
        assert not failed, "after deleting an account, these do not hold:\n  " + "\n  ".join(failed)
    await engine.dispose()

