# SPDX-License-Identifier: AGPL-3.0-only
"""
Swara Studio v2: the course import, the reader's rules, progress, practice,
the Listening room, community rooms and the Studio admin.

The course text is Sophia's and never committed here: every lesson and
exercise below is written for these tests. Pure rules run everywhere; the
database tests run from scripts/test-erase.sh against a migrated Postgres
and SKIP (saying so) without SHRUTI_ERASE_DATABASE_URL.
"""
from __future__ import annotations

import asyncio
import inspect
import os
import uuid

import pytest

from shruti.api.routes import carnatic_community as community
from shruti.api.routes import carnatic_course as routes
from shruti.api.routes import carnatic_studio as studio
from shruti.core import carnatic_checks as checks
from shruti.core import carnatic_course as course
from shruti.core import carnatic_drills as drills

URL = os.environ.get("SHRUTI_ERASE_DATABASE_URL", "")
needs_db = pytest.mark.skipif(not URL, reason=(
    "SHRUTI_ERASE_DATABASE_URL is not set — the school was NOT checked against Postgres. Run scripts/test-erase.sh"))

BODY = """{{drone}}

Press play[^a]. A second mention[^b] and the first again[^a].

<!-- Sophia: a note for later -->

> [!listen]
> Hum along.

{{quiz id=T01.L01.Q1}}
"""
FRONT = {"format": 2, "id": "T01.L01", "slug": "test-sa", "lang": "en", "revision": 1, "status": "draft", "unit": 1,
         "order": 1, "title": "Test Sa", "summary": "A test.", "level": "beginner", "minutes": 5,
         "goals": ["one"], "sources": [{"key": "a", "cite": "A", "confidence": "high"},
                                        {"key": "b", "cite": "B", "confidence": "medium"}],
         "exercises": ["T01.L01.Q1"], "recordings": [{"id": "test-rec-01", "why": "listen"}]}


# ── pure rules ──────────────────────────────────────────────────────────────

def test_footnotes_are_numbered_by_first_use_and_notes_never_leave() -> None:
    assert course.footnote_order(BODY) == ["a", "b"]
    assert "Sophia" not in course.strip_notes(BODY)
    assert course.editor_notes(BODY) == ["Sophia: a note for later"]
    kinds = [e["kind"] for e in course.embeds(BODY)]
    assert kinds == ["drone", "quiz"]


def test_the_checks_speak_in_words_and_only_three_things_block_publishing() -> None:
    ok = course.check_lesson(FRONT, BODY, {"T01.L01.Q1"})
    assert not ok["publishable"] and any("editor note" in p["text"] for p in ok["problems"])
    clean = course.check_lesson(FRONT, course.strip_notes(BODY), {"T01.L01.Q1"})
    assert clean["publishable"]
    unknown = course.check_lesson(FRONT, course.strip_notes(BODY) + "\n[^zz]\n", {"T01.L01.Q1"})
    assert unknown["publishable"] and any("zz has no source" in p["text"] for p in unknown["problems"])
    missing = course.check_lesson({**FRONT, "title": ""}, course.strip_notes(BODY), set())
    texts = [p["text"] for p in missing["problems"] if p["blocksPublishing"]]
    assert any("title" in t for t in texts) and any("T01.L01.Q1" in t for t in texts)


def test_format_2_is_the_only_format_and_tags_follow_the_exercise_kind() -> None:
    body = course.strip_notes(BODY)
    old = course.check_lesson({**FRONT, "format": 1}, body, {"T01.L01.Q1"})
    assert not old["publishable"] and any("format 2" in p["text"] for p in old["problems"])
    # {{quiz}} on a tap task: the tag follows the kind, said in words (not blocking)
    tagged = course.check_lesson(FRONT, body, {"T01.L01.Q1"}, None, {"T01.L01.Q1": "tap"})
    assert tagged["publishable"] and any("its tag is {{tap}}" in p["text"] for p in tagged["problems"])
    # a key a tag doesn't know, and the format-2 tags
    extra = course.check_lesson(FRONT, body + "\n{{recording id=x hide_raga=true}}\n{{checkpoint unit=4}}\n{{selftest id=K.04}}\n",
                                {"T01.L01.Q1"})
    texts = [p["text"] for p in extra["problems"]]
    assert any("doesn't take hide_raga" in t for t in texts)
    assert not any("checkpoint" in t and "isn't a tag" in t for t in texts)
    assert not any("selftest" in t and "isn't a tag" in t for t in texts)
    # tools must match the embeds
    tools = course.check_lesson({**FRONT, "tools": ["drone", "tuner"]}, body, {"T01.L01.Q1"})
    assert any("listed but not used: tuner" in p["text"] and "used but not listed: quiz" in p["text"] for p in tools["problems"])


def test_items_waiting_for_an_annotation_are_hidden() -> None:
    from shruti.api.routes import carnatic_course as routes
    ex = {"id": "U04.L10.A1", "kind": "listening", "auto": [
        {"type": "timestamp", "recording": "r", "answer": None, "text": "When?"},
        {"type": "text", "recording": "r", "answer_from": "raga", "answer": None},
        {"type": "choice", "answer": "a", "options": [{"id": "a", "text": "A"}], "explain": "x"}]}
    out = routes._ready(ex)
    assert len(out["auto"]) == 2 and out["waiting"] == 1


def test_a_typo_is_not_a_change_of_meaning() -> None:
    assert not course.is_meaning_change("The drone holds Sa.", "The drone hold Sa.")
    assert course.is_meaning_change("The drone holds Sa.", "The drone holds Pa, and the tanpura sounds Ma.")


def test_the_raga_normaliser_matches_spellings() -> None:
    k = routes.raga_key
    assert k("Sankarabharanam") == k("Dheerasankarabharanam") == k("dhira sankarabharanam")
    assert k("Thodi") == k("Todi") and k("Mohanam") == k("Mohana") and k("Kalyani") == k("kalyaani")


def test_three_words_are_the_only_scale() -> None:
    assert [routes.word_for(r, 10) for r in (4, 5, 7, 8, 10)] == \
        ["new", "getting there", "getting there", "comfortable", "comfortable"]


def test_review_boxes_follow_the_leitner_ladder() -> None:
    assert routes.BOX_DAYS == [0, 1, 3, 7, 16, 35, 75]


def test_prechecks_are_friendly_notes_about_units_and_swaras() -> None:
    assert checks.fits_tala("S R G M | P D | N S' ||", "adi", 1) == []
    note = checks.fits_tala("S R G M P D N", "adi", 1)[0]
    assert "7 units" in note and "needs 8" in note and "1 units before samam" in note
    assert checks.three_equal("ta ka di mi , ta ka di mi , ta ka di mi") == []
    assert checks.three_equal("ta ka di , ta ka , ta ka di")
    assert checks.total_matras("S , , R", 4) == [] and checks.total_matras("S ;", 4)
    assert checks.seconds("2:14") == 134 and checks.seconds("1:02:03") == 3723


def test_scales_are_labelled_and_gamaka_ragas_come_from_recordings() -> None:
    ms = [l for l in drills.LEVELS if l["family"] == "MS"]
    assert ms and all(l["note"] == "a scale, not a raga" for l in ms)
    assert {k["id"] for k in drills.TALA_KEEPING} == {f"K.{i:02d}" for i in range(1, 17)}
    c7 = next(c for c in drills.CONFUSABLE if c["set"] == "C7")
    assert c7["mode"] == "recordings"


def test_nothing_here_keeps_a_streak_or_a_grade() -> None:
    import re
    for mod in (routes, community, studio, course):
        code = re.sub(r'""".*?"""', "", inspect.getsource(mod), flags=re.S)
        code = re.sub(r"(?m)#.*$", "", code)
        assert "streak" not in code.lower(), mod.__name__
        assert "grade" not in code.lower(), mod.__name__


def test_the_horoscope_room_never_lists_school_pieces() -> None:
    from shruti.api.routes import practice
    src = inspect.getsource(practice)
    assert src.count("PracticeWork.room == HOROSCOPE") >= 5
    assert "work.room != HOROSCOPE" in inspect.getsource(practice.one)


# ── against Postgres ────────────────────────────────────────────────────────

def _bundle(tag: str, body: str = BODY, title: str = "Test Sa", rec_title: str = "A recording") -> dict:
    lesson_id = f"T{tag}.L01"
    body = body.replace("T01.L01.Q1", f"{lesson_id}.Q1")
    front = {**FRONT, "id": lesson_id, "slug": f"test-sa-{tag}", "title": title, "exercises": [f"{lesson_id}.Q1"],
             "unit": 1}
    return {
        "format": 2, "units": [],
        "lessons": [{"hash": course.digest(front, body), "front": front, "body": body}],
        "exercises": [{"id": f"{lesson_id}.Q1", "unit": 1, "lesson": lesson_id, "kind": "quiz", "hash": "h1",
                       "data": {"id": f"{lesson_id}.Q1", "kind": "quiz", "items": [
                           {"type": "choice", "text": "Which?", "options": [{"id": "a", "text": "A"}],
                            "answer": "a", "explain": "Because."}]}},
                      {"id": f"{lesson_id}.P1", "unit": 1, "lesson": lesson_id, "kind": "practice", "hash": "h2",
                       "data": {"id": f"{lesson_id}.P1", "kind": "practice", "prompt": "Write.",
                                "submission": {"text": {"required": True, "words": [3, 20]},
                                               "sargam": {"required": False, "raga": "mohanam", "tala": "adi", "speed": 1}},
                                "prechecks": ["fits_tala"],
                                "rubric": [{"id": "clear", "ask": "Clear?", "scale": ["no", "partly", "yes"]},
                                           {"id": "tip", "ask": "A tip", "answer": "free"}]}},
                      {"id": f"CP.T{tag}", "unit": 1, "lesson": lesson_id, "kind": "checkpoint", "hash": "h3",
                       "data": {"id": f"CP.T{tag}", "kind": "checkpoint", "skills": [{"id": "s", "name": "Sa"}],
                                "parts": [{"quiz": f"{lesson_id}.Q1", "count": 1, "skill": "s"}], "items": []}}],
        "glossary": [{"slug": f"vakra-{tag}", "term": "vakra", "definition": "zigzag", "lesson": lesson_id,
                      "aliases": ["vakra", "vakra raga"], "iso": "vakra", "source": "a", "hash": "g1"}],
        "recordings": [{"id": f"rec-{tag}-01", "provider": "youtube", "url": "https://youtu.be/x", "title": rec_title,
                        "channel": "C", "uploader_kind": "label", "artists": ["A"], "composition": "", "composer": "",
                        "form": "kriti", "raga": "mohanam", "tala": "", "page_says": {}, "listen_for": "the G",
                        "flags": [], "duration": "", "raw": {}, "hash": course.digest(rec_title)}],
    }


async def _session():
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    engine = create_async_engine(URL)
    return engine, AsyncSession(engine, expire_on_commit=False)


async def _import_never_overwrites_her_edits():
    from shruti.models.carnatic_course import CarnaticLesson, CarnaticRecording
    tag = uuid.uuid4().hex[:6]
    engine, s = await _session()
    async with s:
        first = await course.import_bundle(s, _bundle(tag))
        assert first["lessons"]["created"] == 1 and first["recordings"]["created"] == 1
        lid = f"T{tag}.L01"
        # Unedited: a changed file replaces it.
        await course.import_bundle(s, _bundle(tag, title="Test Sa, again"))
        row = await s.get(CarnaticLesson, (lid, "en"))
        await s.refresh(row)
        assert row.front["title"] == "Test Sa, again" and not row.admin_edited
        # She edits it in the admin.
        req = type("R", (), {"headers": {}, "cookies": {}})()
        saved = await studio.save(lid, studio.LessonSave(front={**row.front, "title": "Her title"}, body=row.body,
                                                         status="draft"), "en", "op", s)
        assert saved["edited"]
        # The file changes again: her copy stays, the newer file is kept beside it.
        third = await course.import_bundle(s, _bundle(tag, title="Writer's title"))
        await s.refresh(row)
        assert row.front["title"] == "Her title" and row.file_hash and third["lessons"]["newerFile"] == 1
        # She takes the file version: in step again.
        await studio.take_file(lid, "en", "op", s)
        await s.refresh(row)
        assert row.front["title"] == "Writer's title" and not row.admin_edited and not row.file_hash
        # A decided recording is never touched by an import.
        await studio.decide(f"rec-{tag}-01", studio.Decision(action="approve"), s)
        await course.import_bundle(s, _bundle(tag, rec_title="Changed title"))
        rec = await s.get(CarnaticRecording, f"rec-{tag}-01")
        await s.refresh(rec)
        assert rec.status == "approved" and rec.title == "A recording"
    await engine.dispose()


async def _format_2_import():
    from shruti.models.carnatic_course import CarnaticExercise, CarnaticGlossary
    tag = uuid.uuid4().hex[:6]
    engine, s = await _session()
    async with s:
        await course.import_bundle(s, _bundle(tag))
        await s.commit()
        g = await s.get(CarnaticGlossary, f"vakra-{tag}")
        assert g.aliases == ["vakra", "vakra raga"] and g.iso == "vakra" and g.source == "a"
        cp = await s.get(CarnaticExercise, f"CP.T{tag}")
        assert cp.kind == "checkpoint" and cp.data["parts"][0]["skill"] == "s"
        with pytest.raises(ValueError):
            await course.import_bundle(s, {**_bundle(tag), "format": 1})
    await engine.dispose()


@needs_db
def test_the_import_reads_format_2_and_refuses_format_1() -> None:
    asyncio.run(_format_2_import())


@needs_db
def test_an_import_creates_then_never_overwrites_her_edits() -> None:
    asyncio.run(_import_never_overwrites_her_edits())


async def _publishing_rules():
    from fastapi import HTTPException
    from shruti.models.carnatic_course import CarnaticLesson
    tag = uuid.uuid4().hex[:6]
    engine, s = await _session()
    async with s:
        await course.import_bundle(s, _bundle(tag))
        lid = f"T{tag}.L01"
        row = await s.get(CarnaticLesson, (lid, "en"))
        # Not public while a draft.
        req = type("R", (), {"headers": {}, "cookies": {}})()
        with pytest.raises(HTTPException):
            await routes.course_lesson(lid, req, "en", False, s)
        # Publishing is blocked by the open editor note, and says so.
        blocked = await studio.save(lid, studio.LessonSave(front=row.front, body=row.body, status="published"),
                                    "en", "op", s)
        assert blocked.status_code == 422
        # A change of more than a typo asks about meaning, once.
        new_body = course.strip_notes(row.body) + "\nA whole new paragraph that changes what the lesson says.\n"
        asked = await studio.save(lid, studio.LessonSave(front=row.front, body=new_body, status="published"),
                                  "en", "op", s)
        assert asked.status_code == 409
        done = await studio.save(lid, studio.LessonSave(front=row.front, body=new_body, status="published",
                                                        meaningChange=True), "en", "op", s)
        assert done["status"] == "published" and done["revision"] == 2
        public = await routes.course_lesson(f"test-sa-{tag}", req, "en", False, s)
        assert public["revision"] == 2 and [x["key"] for x in public["sources"]] == ["a", "b"]
        assert public["sources"][0]["n"] == 1 and "Sophia" not in public["body"]
        revs = await studio.revisions(lid, "en", s)
        assert len(revs["items"]) == 2, "the import and the one save that went through"
    await engine.dispose()


@needs_db
def test_publishing_is_blocked_only_by_what_the_format_says() -> None:
    asyncio.run(_publishing_rules())


async def _learner():
    from shruti.models.accounts import User
    tag = uuid.uuid4().hex[:6]
    engine, s = await _session()
    async with s:
        u = User(email=f"learner-{tag}@example.com", display_name="Learner")
        s.add(u)
        await s.commit()

        class Req:
            async def json(self):
                return {"completedAt": "2026-09-26T10:00:00+00:00", "updatedAt": "2026-09-26T10:00:00+00:00"}
        st = await routes.put_my_lesson("U01.L01", routes.LessonStateIn(
            completedAt="2026-09-26T10:00:00+00:00", updatedAt="2026-09-26T10:00:00+00:00",
            openedAt="2026-09-26T09:00:00+00:00"), Req(), u, s)
        assert st["completedAt"] and st["openedAt"].startswith("2026-09-26T09")

        class Older:
            async def json(self):
                return {"completedAt": None, "updatedAt": "2026-09-25T10:00:00+00:00"}
        st = await routes.put_my_lesson("U01.L01", routes.LessonStateIn(
            completedAt=None, updatedAt="2026-09-25T10:00:00+00:00", openedAt="2026-09-20T09:00:00+00:00"),
            Older(), u, s)
        assert st["completedAt"], "an older change must not undo a newer one"
        assert st["openedAt"].startswith("2026-09-20"), "opened keeps the earliest"

        a1 = routes.AttemptIn(id="a1", itemId="CP.U09", kind="checkpoint", startedAt="2026-09-26T10:00:00+00:00",
                              result={"right": 3, "of": 5, "skills": {"melakarta": {"right": 3, "of": 5}}})
        r1 = await routes.post_attempts(routes.AttemptsIn(attempts=[a1, a1]), u, s)
        assert r1["stored"] == 1
        a2 = routes.AttemptIn(id="a2", itemId="CP.U09", kind="checkpoint", startedAt="2026-09-27T10:00:00+00:00",
                              result={"right": 5, "of": 5, "skills": {"melakarta": {"right": 5, "of": 5}}})
        r2 = await routes.post_attempts(routes.AttemptsIn(attempts=[a2]), u, s)
        mel = next(b for b in r2["bests"] if b["skill"] == "melakarta")
        assert mel["best"]["word"] == "comfortable" and mel["previous"]["word"] == "getting there"

        c = routes.CardIn(key="SW.04:G2-G3", box=2, lastSeen="2026-09-01T10:00:00+00:00", recent=[True])
        await routes.put_cards(routes.CardsIn(cards=[c]), u, s)
        stale = routes.CardIn(key="SW.04:G2-G3", box=0, lastSeen="2026-08-20T10:00:00+00:00", recent=[False])
        out = await routes.put_cards(routes.CardsIn(cards=[stale]), u, s)
        assert out["items"][0]["box"] == 2, "the most recent review wins"
        assert out["due"] >= 1
    await engine.dispose()


@needs_db
def test_progress_merges_and_bests_use_three_words() -> None:
    asyncio.run(_learner())


async def _community():
    from fastapi import HTTPException
    from shruti.core.consents import PUBLISH
    from shruti.models.accounts import ConsentRecord, User
    tag = uuid.uuid4().hex[:6]
    engine, s = await _session()
    async with s:
        await course.import_bundle(s, _bundle(tag))
        people = [User(email=f"c{i}-{tag}@example.com", display_name=f"C{i}") for i in range(5)]
        s.add_all(people)
        await s.flush()
        author = people[0]
        s.add(ConsentRecord(user_id=author.id, email=author.email, kind=PUBLISH.kind, granted=True,
                            version="test", wording=PUBLISH.wording, lawful_basis=PUBLISH.lawful_basis,
                            source="test"))
        await s.commit()
        ex = f"exercise:T{tag}.L01.P1"
        draft = await community.create(community.WorkIn(room="carnatic-practice", subject=ex, title="Mine", parts=[
            community.PartIn(key="text", body="Two words"),
            community.PartIn(key="sargam", body="S R G M P D N", data={"raga": "mohanam"})]), author, s)
        # A stranger can't see a draft.
        with pytest.raises(HTTPException):
            await community.work(draft["id"], people[1], s)
        sent = await community.submit(draft["id"], author, s)
        hints = " ".join(sent["hints"])
        assert "2 words" in hints and "7 units" in hints, "prechecks are notes, never blocks"
        # One vote each; rubric as totals.
        await community.vote(draft["id"], people[1], s)
        await community.vote(draft["id"], people[1], s)
        r = await community.rubric(draft["id"], community.RubricIn(answers={"clear": "yes", "tip": "Nice"}),
                                   people[1], s)
        assert r["totals"]["clear"]["yes"] == 1 and r["freeAnswers"]["tip"] == 1
        view = await community.work(draft["id"], people[2], s)
        assert view["votes"] == 1 and "user" not in str(view["rubric"]).lower()
        # A reply on one part.
        c = await community.comment(draft["id"], community.CommentIn(body="On the notation", part="sargam"),
                                    people[2], s)
        listed = await community.comments(draft["id"], None, s)
        assert listed["items"][0]["partLabel"] == "the notation"
        # A block works both ways, silently.
        await community.block(community.BlockIn(userId=people[3].id), author, s)
        with pytest.raises(HTTPException):
            await community.comment(draft["id"], community.CommentIn(body="hi"), people[3], s)
        # Three distinct reporters hide it until she reviews; the author sees why.
        for p in people[1:4]:
            await community.report_work(draft["id"], community.ReportIn(reason="spam"), p, s)
        with pytest.raises(HTTPException):
            await community.work(draft["id"], people[4], s)
        own = await community.work(draft["id"], author, s)
        assert own["hidden"] and own["hiddenBy"] == "reports"
        mod = await studio.moderation(s)
        entry = next(e for e in mod["items"] if e["kind"] == "work" and e["id"] == draft["id"])
        assert entry["hiddenBy"] == "reports" and entry["reports"] == 3 and "reporters" not in entry
        await studio.verdict("work", draft["id"], studio.Verdict(outcome="restore"), s)
        back = await community.work(draft["id"], people[4], s)
        assert not back["hidden"]
    await engine.dispose()


@needs_db
def test_the_practice_room_rules_hold_for_school_pieces() -> None:
    asyncio.run(_community())


async def _everything_waiting_for_her():
    from shruti.models.carnatic_course import CarnaticQuestion
    tag = uuid.uuid4().hex[:6]
    lid = f"T{tag}.L01"
    b = _bundle(tag)
    b["questions"] = [{"id": f"q{tag}", "group": "By ear", "text": "The test recording's tala.", "lessons": [lid], "position": 0}]
    b["exercises"].append({"id": f"{lid}.A1", "unit": 1, "lesson": lid, "kind": "listening", "hash": "h9",
                           "data": {"id": f"{lid}.A1", "kind": "listening", "recordings": [{"id": f"rec-{tag}-01"}],
                                    "auto": [{"type": "timestamp", "text": "When does the anupallavi begin?", "answer": None,
                                              "tolerance": 6}]}})
    engine, s = await _session()
    async with s:
        await course.import_bundle(s, b)
        await s.commit()
        # Her notes, each with its line, so the editor can open on it.
        notes = [n for n in (await studio.notes(s))["items"] if n["lesson"] == lid]
        assert notes and notes[0]["who"] == "Sophia" and notes[0]["line"] > 1 and "a note for later" in notes[0]["text"]
        # The question: answered, then the file rewords it; her answer stays.
        await studio.answer_question(f"q{tag}", studio.QuestionIn(answer="Adi, 2 kalai", done=True), s)
        b["questions"][0]["text"] = "The test recording's tala, by ear."
        await course.import_bundle(s, b)
        await s.commit()
        q = await s.get(CarnaticQuestion, f"q{tag}")
        await s.refresh(q)
        assert q.text.endswith("by ear.") and q.answer == "Adi, 2 kalai" and q.done
        csv = await studio.export_questions("csv", s)
        assert "Adi, 2 kalai" in csv.body.decode()
        # The item waiting for her time: listed with its recording, hidden from learners until she sets it.
        waiting = [w for w in (await studio.waiting(s))["items"] if w["exercise"] == f"{lid}.A1"]
        assert waiting and waiting[0]["recording"] == f"rec-{tag}-01"
        assert routes._ready({"auto": [{"answer": None}], "id": "x"})["auto"] == []
        await studio.fill_waiting(f"{lid}.A1", studio.WaitingAnswer(part="auto", index=0, answer="1:32"), s)
        assert not [w for w in (await studio.waiting(s))["items"] if w["exercise"] == f"{lid}.A1"]
    await engine.dispose()


@needs_db
def test_the_studio_brings_everything_waiting_for_her_into_one_place() -> None:
    asyncio.run(_everything_waiting_for_her())


def test_a_close_guess_is_named_as_its_pair() -> None:
    pair = next(c for c in drills.CONFUSABLE if set(c["ragas"]) == {"kharaharapriya", "bhairavi"})
    assert pair["set"] == "C9"
    src = inspect.getsource(routes.guess)
    assert '"close"' in src and "CONFUSABLE" in src
