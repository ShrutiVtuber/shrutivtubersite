# SPDX-License-Identifier: AGPL-3.0-only
"""
Swara Studio's rules, kept apart from its routes so they can be tested on
their own: where the data lives, what a setting may be, what a song may hold,
who has no part limit, and the one-time codes that sign the app in.

The musical facts are NOT here. They are files built from the private
research (scripts/sync-carnatic-data.sh) and read from `DATA_DIR`. The few
numbers below (how many counts a tala has, which tokens are notes) are the
grammar the composer is checked against, not a compilation of anything.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import secrets
import time
import unicodedata
from collections import defaultdict, deque
from pathlib import Path
from urllib.parse import urlparse

DATA_DIR = Path(os.environ.get("SHRUTI_CARNATIC_DIR", "/app/carnatic"))

#: The files a manifest may name. Anything else is refused by name, so a
#: request can never walk out of the directory.
DATA_FILE = re.compile(r"^[a-z][a-z0-9-]{0,40}\.json$")


def manifest() -> dict | None:
    """The published manifest, or None when nothing has been synced (a working state)."""
    try:
        return json.loads((DATA_DIR / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def data_path(name: str) -> Path | None:
    """The path of a published data file, only if the manifest names it."""
    if not DATA_FILE.match(name) or name == "manifest.json":
        return None
    m = manifest()
    if not m or name not in {f.get("name") for f in m.get("files", [])}:
        return None
    path = DATA_DIR / name
    return path if path.is_file() else None


def digest_of(name: str) -> str | None:
    m = manifest() or {}
    return next((f.get("digest") for f in m.get("files", []) if f.get("name") == name), None)


_cache: dict[str, tuple[str, dict]] = {}


def data(name: str) -> dict | None:
    """A data file, parsed, cached until its digest changes."""
    path = data_path(name)
    if path is None:
        return None
    digest = digest_of(name) or ""
    hit = _cache.get(name)
    if hit and hit[0] == digest:
        return hit[1]
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    _cache[name] = (digest, parsed)
    return parsed


# ── settings ────────────────────────────────────────────────────────────────

INSTRUMENTS = ("voice", "venu", "veena", "violin", "mridangam")

#: DECISIONS.md (26 Sep 2026): voice C, flute the learner's flute with E5
#: suggested, veena E3, violin E. The mridangam follows the singer; C3 here.
DEFAULT_SA = {"voice": "C3", "venu": "E5", "veena": "E3", "violin": "E4", "mridangam": "C3"}

DEFAULTS = {
    "lang": "en", "swaraLetters": "interface", "tamilStyle": "grantha", "theme": "system",
    "instrument": "voice", "hand": "right", "sa": DEFAULT_SA["voice"], "flute": "E",
    "droneTuning": "pa", "playbackTuning": "just", "subscripts": "info", "otherScripts": "show",
    "tempo": 60, "fourthSpeed": False, "eighthAlankaram": False,
}

CHOICES = {
    "lang": ("en", "ta", "te", "kn"),
    "swaraLetters": ("latin", "interface"),
    "tamilStyle": ("grantha", "pure"),
    "theme": ("dawn", "dusk", "system"),
    "instrument": INSTRUMENTS,
    "hand": ("right", "left"),
    "droneTuning": ("pa", "ma", "ni", "mute"),
    "playbackTuning": ("just", "equal"),
    "subscripts": ("info", "always"),
    "otherScripts": ("show", "hide"),
}
PITCH = re.compile(r"^[A-G]#?[1-6]$")
FLUTE = re.compile(r"^[A-G]#?( bass)?$")


class Invalid(ValueError):
    """A value a person sent that cannot be kept, with a sentence saying why."""


def clean_settings(given: dict) -> dict:
    """
    The settings to keep: known keys checked, unknown keys kept as they came
    (a newer app must not lose an older one's fields), nothing else.
    """
    if not isinstance(given, dict):
        raise Invalid("Settings are an object.")
    if len(json.dumps(given)) > 8000:
        raise Invalid("Those settings are too large to keep.")
    out = dict(given)
    for key, allowed in CHOICES.items():
        if key in out and out[key] not in allowed:
            raise Invalid(f"{key} must be one of {', '.join(allowed)}.")
    if "sa" in out and not (isinstance(out["sa"], str) and PITCH.match(out["sa"])):
        raise Invalid("Sa is a pitch such as C3 or E5.")
    if "flute" in out and not (isinstance(out["flute"], str) and FLUTE.match(out["flute"])):
        raise Invalid("A flute is named by its Sa, such as E or E bass.")
    if "tempo" in out:
        if not isinstance(out["tempo"], int) or isinstance(out["tempo"], bool) or not 40 <= out["tempo"] <= 70:
            raise Invalid("Speed 1 is between 40 and 70 counts a minute.")
    for key in ("fourthSpeed", "eighthAlankaram"):
        if key in out and not isinstance(out[key], bool):
            raise Invalid(f"{key} is true or false.")
    return out


def with_defaults(settings: dict | None) -> dict:
    return {**DEFAULTS, **(settings or {})}


# ── the part limit ──────────────────────────────────────────────────────────

#: Two parts a song for everybody; Swaras supporters have no limit (the
#: owner's rule: a Swaras supporter gets every gated tool, this included).
FREE_PARTS = 2


def part_limit(supporter: bool) -> int | None:
    return None if supporter else FREE_PARTS


# ── songs ───────────────────────────────────────────────────────────────────

#: Counts per avartanam of every tala the composer offers.
TALA_COUNTS = {
    "adi": 8, "adi_2_kalai": 16, "rupaka_3count": 3, "misra_chapu": 7, "khanda_chapu": 5,
    "tisra_triputa": 7, "khanda_ata": 14, "misra_jhampa": 10, "rupaka_chaturasra": 6,
    "chaturasra_eka": 4, "tisra_eka": 3, "deshadi": 8,
}
GAMAKAS = ("kampita", "jaru-up", "jaru-down", "nokku", "sphurita", "pratyahata", "ravai",
           "khandippu", "odukkal", "orikkai")
NOTE = re.compile(r"^(?:(?P<g>[a-z-]+):)?(?P<low>\.{0,2})(?P<s>[SRGMPDN])(?P<v>[123])?(?P<high>'{0,2})$")
STROKES = ("tha", "dhi", "thom", "nam", "ki", "ta", "mi", "chapu", "arai-chapu", "dheem", "tham",
           "dhom", "gumki", "-")
SONG_BYTES = 64 * 1024
SONGS_PER_PERSON = 200


def parse_note(token: str) -> dict | None:
    """A note token, or None for a hold. Raises Invalid for anything else."""
    if token in (",", ";"):
        return None
    m = NOTE.match(token)
    if not m:
        raise Invalid(f"“{token}” is not a note.")
    g = m.group("g")
    if g and g not in GAMAKAS:
        raise Invalid(f"The sheet has no sign for a gamaka called “{g}”.")
    s, v = m.group("s"), m.group("v")
    if v and s in "SP":
        raise Invalid(f"{s} has no variants.")
    if v == "3" and s == "M":
        raise Invalid("Ma is M1 or M2.")
    octave = len(m.group("high")) - len(m.group("low"))
    return {"gamaka": g, "swara": s, "variant": int(v) if v else None, "octave": octave}


def check_song(body: dict) -> dict:
    """
    Check a song body against format 1 (docs/carnatic/API.md §5). Returns it
    unchanged when it is sound; raises Invalid with the first problem.

    A note outside the raga is NOT a problem: it stays where the composer put
    it and the sheet marks it for them to decide.
    """
    if not isinstance(body, dict):
        raise Invalid("A song is an object.")
    if len(json.dumps(body, ensure_ascii=False).encode()) > SONG_BYTES:
        raise Invalid("That song is too long to keep here (64 KB).")
    if body.get("format") != 1:
        raise Invalid("Songs are format 1.")
    title = body.get("title")
    if not isinstance(title, str) or not title.strip() or len(title) > 120:
        raise Invalid("A song needs a title of up to 120 characters.")
    tala = body.get("tala")
    if tala not in TALA_COUNTS:
        raise Invalid("Choose one of the composer's talas.")
    counts = TALA_COUNTS[tala]
    parts = body.get("parts") or []
    if not isinstance(parts, list) or not parts:
        raise Invalid("A song has at least its melody.")
    ids = []
    for p in parts:
        if not isinstance(p, dict) or not isinstance(p.get("id"), str) or p.get("kind") not in ("melody", "strokes"):
            raise Invalid("Each part has an id and is a melody or strokes.")
        ids.append(p["id"])
    if len(set(ids)) != len(ids):
        raise Invalid("Two parts share an id.")
    if "melody" not in ids:
        raise Invalid("The melody is one of the parts.")
    sections = body.get("sections")
    if not isinstance(sections, list) or len(sections) > 24:
        raise Invalid("A song has up to 24 sections.")
    for sec in sections:
        if not isinstance(sec, dict) or not isinstance(sec.get("lines"), list):
            raise Invalid("Each section has lines.")
        per = sec.get("notesPerCount", 1)
        if per not in (1, 2, 4):
            raise Invalid("A count holds one, two or four notes.")
        for line in sec["lines"]:
            cs = line.get("counts") if isinstance(line, dict) else None
            if not isinstance(cs, list) or len(cs) != counts:
                raise Invalid(f"Every line in {tala.replace('_', ' ')} has {counts} counts.")
            for c in cs:
                notes = c.get("notes") if isinstance(c, dict) else None
                if not isinstance(notes, list) or len(notes) != per:
                    raise Invalid(f"Each count in this section holds {per} note{'s' if per > 1 else ''}.")
                for n in notes:
                    if not isinstance(n, str):
                        raise Invalid("A note is written as text.")
                    parse_note(n)
                if len(str(c.get("sahitya", ""))) > 40:
                    raise Invalid("A count's sahitya is up to 40 characters.")
                for pid, strokes in (c.get("parts") or {}).items():
                    if pid not in ids or not isinstance(strokes, list):
                        raise Invalid("A count names a part the song does not have.")
                    for s in strokes:
                        if s not in STROKES:
                            raise Invalid(f"The sheet has no mridangam stroke called “{s}”.")
    return body


def parts_in(body: dict) -> int:
    return len(body.get("parts") or [])


def song_slug(title: str) -> str:
    """A readable address with a random tail, so two “Untitled” songs never collide."""
    base = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode().lower()
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")[:48] or "song"
    return f"{base}-{secrets.token_hex(2)}"


def out_of_raga(body: dict, raga: dict | None) -> list[str]:
    """The notes a composer used that the raga does not have (for the sheet's quiet flag)."""
    if not raga:
        return []
    allowed = set()
    for scale in (raga.get("arohana", ""), raga.get("avarohana", "")):
        for tok in scale.split():
            m = NOTE.match(tok.replace("!a", "").replace("!v", ""))
            if m:
                allowed.add(m.group("s") + (m.group("v") or ""))
    letters = {a[0] for a in allowed} | {"S", "P"}
    found = []
    for sec in body.get("sections", []):
        for line in sec.get("lines", []):
            for c in line.get("counts", []):
                for n in c.get("notes", []):
                    p = parse_note(n)
                    if p is None:
                        continue
                    name = p["swara"] + (str(p["variant"]) if p["variant"] else "")
                    ok = p["swara"] in letters if p["variant"] is None else (name in allowed or p["swara"] in "SP")
                    if not ok and name not in found:
                        found.append(name)
    return found


# ── Listen ──────────────────────────────────────────────────────────────────

PLAYERS = {
    "youtube": ("youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be", "music.youtube.com"),
    "soundcloud": ("soundcloud.com", "www.soundcloud.com", "on.soundcloud.com"),
    "vimeo": ("vimeo.com", "www.vimeo.com", "player.vimeo.com"),
    "bandcamp": None,           # any *.bandcamp.com
}


def player_of(url: str) -> str | None:
    """Which player a link opens in, or None when it is not one the room embeds."""
    try:
        u = urlparse(url.strip())
    except ValueError:
        return None
    if u.scheme != "https" or not u.netloc:
        return None
    host = u.netloc.lower().split(":")[0]
    for name, hosts in PLAYERS.items():
        if hosts is None:
            if host.endswith(".bandcamp.com"):
                return name
        elif host in hosts:
            return name
    return None


# ── signing in on the app ───────────────────────────────────────────────────

CODE_ALPHABET = "23456789ABCDEFGHJKMNPQRSTVWXYZ"
LINK_SECONDS = 300
LIVE_LINKS = 3


def new_code() -> str:
    raw = "".join(secrets.choice(CODE_ALPHABET) for _ in range(8))
    return f"{raw[:4]}-{raw[4:]}"


def normalise_code(typed: str) -> str | None:
    """What was typed, as the eight symbols it must be, or None."""
    s = re.sub(r"[\s\-_.]", "", typed or "").upper()
    if len(s) != 8 or any(ch not in CODE_ALPHABET for ch in s):
        return None
    return s


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def code_hash(code: str, secret: str) -> str:
    return hmac.new(secret.encode(), ("carnatic-link:" + code).encode(), hashlib.sha256).hexdigest()


class Window:
    """Failures in a sliding window, per key, in memory (one backend process)."""

    def __init__(self, limit: int, seconds: int = 600):
        self.limit, self.seconds = limit, seconds
        self._seen: dict[str, deque] = defaultdict(deque)

    def _trim(self, key: str, now: float) -> deque:
        q = self._seen[key]
        while q and now - q[0] > self.seconds:
            q.popleft()
        return q

    def full(self, key: str) -> bool:
        return len(self._trim(key, time.monotonic())) >= self.limit

    def add(self, key: str) -> None:
        now = time.monotonic()
        self._trim(key, now).append(now)
