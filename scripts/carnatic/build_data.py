#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""
Build Swara Studio's data files from the private research repository.

    python3 scripts/carnatic/build_data.py <research dir> <out dir>

The research (ragas, talas, lessons, instruments, with their sources and
confidence levels) is a compilation kept in a private repository and is All
Rights Reserved; see its LICENSE-DATA.md. This script is the only bridge: it
reads that folder and writes the handful of JSON files the site serves at
runtime from a volume. Nothing it reads or writes is committed here.

Standard library only, so it runs anywhere `scripts/sync-carnatic-data.sh`
does. It fails loudly (exit 1) rather than publishing something half-built.

What it fixes on the way through, because the handoff's copies of the data
carried these slips and the site must not:

- a melakarta whose two schools use the same name has no Dikshitar-school
  name at all (null, shown as nothing), never "None";
- the Wikipedia disambiguation a script name was filed under ("(இராகம்)",
  "రాగం", "(ರಾಗ)", "(ಕರ್ನಾಟಕ)") is not part of the name;
- the source markers ᵃ and ˡN from the research tables are stripped;
- Tamil names keep BOTH spellings where both are sourced: the grantha style
  (ஸ, ஸ்ரீ; the default) and the pure-Tamil style (ச, சிறீ), as two fields,
  never joined with a slash.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import sys
import unicodedata
from pathlib import Path

FORMAT = 1

# ── owner decisions that shape the data (DECISIONS.md) ─────────────────────

# ragas §5: tagged "Hindustani-derived, often heard in tukkadas".
HINDUSTANI = {"behag", "desh", "sindhubhairavi", "shivaranjani", "brindavana-saranga",
              "hamir-kalyani", "yamunakalyani"}
# ragas §4: Mayamalavagowla, then Malahari and Mohanam (geethams) first.
FIRST = ["malahari", "mohanam"]

TALA_OF_LESSON = {
    # lesson file id -> the practical tala the trainer and player keep
    "adi": "adi",
    "chaturasra_jati_triputa": "adi",
    "chaturasra_jati_rupaka": "rupaka_chaturasra",
    "misra_jati_jhampa": "misra_jhampa",
    "tisra_jati_triputa": "tisra_triputa",
    "khanda_jati_ata": "khanda_ata",
    "chaturasra_jati_eka": "chaturasra_eka",
}

SPEEDS = {1: 1, 2: 2, 3: 4}          # speed level -> swaras per count
ALLOWED_REPEATS = (1, 2, 4)

JATI_WORD = {5: "audava", 6: "shadava", 7: "sampurna"}

GRANTHA = re.compile(r"[ஸஷஜஹ]|ஸ்ரீ|க்ஷ")


class BuildError(Exception):
    pass


def load(root: Path, rel: str):
    path = root / rel
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise BuildError(f"missing {rel}")
    except json.JSONDecodeError as e:
        raise BuildError(f"{rel} is not valid JSON: {e}")


def drop_history(value):
    """Research files keep every pass's old values under `history`; the site needs none of it."""
    if isinstance(value, dict):
        return {k: drop_history(v) for k, v in value.items() if k not in ("history", "_batch")}
    if isinstance(value, list):
        return [drop_history(v) for v in value]
    return value


def slug(name: str) -> str:
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


# ── script names ────────────────────────────────────────────────────────────

DISAMBIGUATORS = [
    r"\s*\((?:இ)?ராகம்\)", r"\s*\(ரா?கம்\)", r"\s*\(రాగం\)", r"\s+రాగం$", r"\s*\(ರಾಗ\)",
    r"\s*\(ಕರ್ನಾಟಕ\)", r"\s*\(alt\. name\)",
]


def clean_script(text: str | None) -> str | None:
    """A script name as a name: no source markers, no Wikipedia disambiguation."""
    if not text:
        return None
    t = unicodedata.normalize("NFC", text)
    t = re.sub(r"[ᵃˡ]+\d*", "", t)
    t = t.replace("†", "")
    t = re.sub(r"\((?:Hindustani[^)]*)\)", "", t)
    t = re.sub(r"\s+", " ", t).strip(" ;/")
    for pattern in DISAMBIGUATORS:
        t = re.sub(pattern, "", t).strip()
    t = re.sub(r"\s+", " ", t).strip(" ;/")
    return t or None


def tamil_pair(candidates: list[tuple[str, str]]) -> dict:
    """
    Two Tamil spellings, where both are sourced: the grantha style and the
    pure-Tamil style. `candidates` is [(kind, text)] with kind "a" (the
    Wikipedia article title, which follows Tamil Wikipedia's pure-Tamil
    style) or "l" (the janya list, which prints grantha letters).

    The one with more grantha letters is the grantha form; when they differ
    in something other than grantha letters (a different spelling, not a
    different style) the article's form stands alone.
    """
    forms = []
    for kind, text in candidates:
        t = clean_script(text)
        if t and t not in [f for _k, f in forms]:
            forms.append((kind, t))
    if not forms:
        return {"grantha": None, "pure": None}
    if len(forms) == 1:
        return {"grantha": forms[0][1], "pure": None}
    score = lambda s: len(GRANTHA.findall(s))
    a = next((f for k, f in forms if k == "a"), forms[0][1])
    best = max(forms, key=lambda kf: score(kf[1]))[1]
    least = min(forms, key=lambda kf: score(kf[1]))[1]
    if score(best) > score(least):
        return {"grantha": best, "pure": least}
    # Different spellings in the same style: the article's stands alone.
    return {"grantha": a, "pure": None}


def parse_janya_scripts(gaps: str) -> dict[str, dict]:
    """GAPS_PASS_3.md §6, the table of janya names in Tamil, Telugu and Kannada."""
    start = gaps.index("## 6. Script names for the 62 janya ragas")
    end = gaps.index("## 7.", start)
    out: dict[str, dict] = {}
    for line in gaps[start:end].splitlines():
        if not line.startswith("| ") or line.startswith("| id ") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        rid, ta, te, kn = cells[:4]
        out[rid] = {"ta": _cell(ta), "te": _cell(te), "kn": _cell(kn)}
    return out


def _cell(cell: str) -> list[tuple[str, str]]:
    """Each '; '-separated spelling in a cell, with where it came from."""
    found = []
    for piece in cell.split(";"):
        piece = piece.strip()
        if not piece:
            continue
        if "→" in piece:                      # "ஸிந்தோளம் [sic] → இந்தோளம் ˡ249": the arrow's target
            piece = piece.split("→", 1)[1]
        kind = "a" if "ᵃ" in piece else "l"
        # A Hindustani article standing in for a different raga ("Jaijaivanti
        # article" for Dwijavanti) is not this raga's name.
        if "Jaijaivanti" in piece:
            continue
        piece = piece.replace("[sic]", "")
        for part in piece.split("/"):
            found.append((kind, part))
    return found


# Where the research table says, in its own flags, which form is the name.
SCRIPT_OVERRIDES = {
    # GAPS §6 flags: "sri" — the article title is ஸ்ரீ, Tamil Wikipedia's
    # pure-Tamil category spells it சிறீ(ராகம்); DECISIONS 26 Sep: grantha
    # ஸ்ரீ is the default, சிறீ the pure-Tamil setting. Never both joined.
    ("sri", "ta"): {"grantha": "ஸ்ரீ", "pure": "சிறீ"},
    # "shuddha-dhanyasi": the article is the alternative name
    # (Udayaravichandrika); the list row gives the raga's own name second.
    ("shuddha-dhanyasi", "ta"): {"grantha": "சுத்த தன்யாசி", "pure": None},
    # kn gives only the alternative name; show nothing rather than another raga's name.
    ("shuddha-dhanyasi", "kn"): None,
    # GAPS §6 flag: the list's பெளளி is a different Unicode sequence; use the article's.
    ("bowli", "ta"): {"grantha": "பௌளி", "pure": None},
}


def janya_scripts(rid: str, table: dict) -> dict:
    row = table.get(rid, {"ta": [], "te": [], "kn": []})
    out = {}
    if (rid, "ta") in SCRIPT_OVERRIDES:
        out["ta"] = SCRIPT_OVERRIDES[(rid, "ta")]
    else:
        out["ta"] = tamil_pair(row["ta"])
    for lang in ("te", "kn"):
        if (rid, lang) in SCRIPT_OVERRIDES:
            out[lang] = SCRIPT_OVERRIDES[(rid, lang)]
            continue
        forms = [clean_script(t) for k, t in sorted(row[lang], key=lambda kt: kt[0] != "a")]
        forms = [f for f in forms if f]
        out[lang] = forms[0] if forms else None
    return out


def mela_scripts(m: dict) -> dict:
    s = m.get("scripts") or {}
    ta = (s.get("ta") or {}).get("text")
    return {
        "ta": {"grantha": clean_script(ta), "pure": None},
        "te": clean_script((s.get("te") or {}).get("text")),
        "kn": clean_script((s.get("kn") or {}).get("text")),
    }


def check_scripts(where: str, scripts: dict) -> None:
    """The slips that must never reach a page."""
    values = [scripts["ta"]["grantha"], scripts["ta"]["pure"], scripts["te"], scripts["kn"]]
    for v in values:
        if v is None:
            continue
        if re.search(r"[ᵃˡ†]|\(|\)|/|రాగం|ராகம்$|\bNone\b", v):
            raise BuildError(f"{where}: script name still carries a marker or disambiguation: {v!r}")


# ── katapayadi ──────────────────────────────────────────────────────────────

KATA = {}
for series in ("k kh g gh ṅ c ch j jh ñ", "ṭ ṭh ḍ ḍh ṇ t th d dh n", "p ph b bh m", "y r l v ś ṣ s h"):
    for i, c in enumerate(series.split()):
        KATA[c] = (i + 1) % 10
VOWELS = set("aāiīuūeēoōṛṝ")


def _consonants(akshara: str) -> list[str]:
    ak = unicodedata.normalize("NFC", akshara.lower()).replace("ṃ", "m")
    out, i = [], 0
    while i < len(ak) and ak[i] not in VOWELS:
        for size in (2, 1):
            if ak[i:i + size] in KATA:
                out.append(ak[i:i + size])
                i += size
                break
        else:
            i += 1
    return out


def katapayadi(m: dict) -> dict:
    k = m["katapayadi"]
    aks = k.get("aksharas_that_yield_number") or k["aksharas"]
    first = "first" in (k.get("rule_applied") or "")
    digits = []
    for a in aks[:2]:
        cs = _consonants(a)
        digits.append(0 if not cs else KATA[cs[0] if first else cs[-1]])
    number = digits[1] * 10 + digits[0]
    if number != m["number"]:
        raise BuildError(f"mela {m['number']}: katapayadi gives {number}")
    return {"aksharas": k["aksharas"], "used": aks, "digits": digits,
            "rule": "first consonant of a conjunct" if first else "last consonant of each akshara",
            "note": k.get("note")}


# ── ragas ───────────────────────────────────────────────────────────────────

def tier(e: dict) -> int:
    """Learning tier, editorial, derived from each raga's researched composition list."""
    if e["id"] in HINDUSTANI:
        return 4
    forms = {c["form"].lower() for c in e.get("compositions", [])}
    if e["id"] in FIRST or "geetham" in forms or e["id"] == "bilahari":
        return 1
    if any("varnam" in f for f in forms):
        return 2
    return 3


def raga_record(e: dict, kind: str, scripts: dict) -> dict:
    c = e["classification"]
    return drop_history({
        "id": e["id"],
        "kind": kind,
        "name": e["name"],
        "iso": e.get("name_iso15919"),
        "aliases": e.get("alternate_names", []),
        "parent": e["parent_melakarta"],
        "parentAlternatives": e.get("parent_alternatives", []),
        "arohana": e["arohana"],
        "avarohana": e["avarohana"],
        "variants": e.get("lakshana_variants", []),
        "anya": e.get("anya_swaras", []),
        "classification": {
            "aro": c["aro_count"], "ava": c["ava_count"],
            "jati": "–".join(JATI_WORD.get(n, str(n)) for n in (c["aro_count"], c["ava_count"])),
            "vakra": bool(c.get("vakra")), "bhashanga": c.get("upanga_bhashanga") == "bhashanga",
            "varja": bool(c.get("varja")),
        },
        "jiva": e.get("jiva_swaras"),
        "nyasa": e.get("nyasa_swaras"),
        "graha": e.get("graha_swaras"),
        "prayogas": e.get("prayogas", []),
        "gamakaCharacter": e.get("gamaka_character", []),
        "timeRasa": e.get("time_rasa"),
        "compositions": [
            {k: v for k, v in comp.items() if k != "verified_at"} | {"verified": comp.get("verified_at") not in (None, "UNVERIFIED")}
            for comp in e.get("compositions", [])
        ],
        "disagreements": e.get("disagreements", []),
        "hindustaniComparison": e.get("hindustani_comparison"),
        "editorialNotes": e.get("editorial_notes"),
        "pedagogy": e.get("pedagogical_importance"),
        "confidence": e.get("confidence", "medium"),
        "confidenceReason": e.get("confidence_reason"),
        "sources": e.get("sources", []),
        "tier": tier(e) if kind == "janya" else None,
        "hindustani": e["id"] in HINDUSTANI,
        "scripts": scripts,
    })


def build_ragas(root: Path, gaps: str) -> dict:
    mela_doc = load(root, "ragas/melakarta.json")
    janya_doc = load(root, "ragas/janya.json")
    table = parse_janya_scripts(gaps)

    melas = []
    for m in mela_doc["melakartas"]:
        dik = m.get("dikshitar_school_name")
        if isinstance(dik, str) and dik.strip().lower() in ("", "none", "null"):
            dik = None
        scripts = mela_scripts(m)
        check_scripts(f"mela {m['number']}", scripts)
        sw = m["swarasthanas"]
        melas.append({
            "number": m["number"],
            "id": slug(m["name"]),
            "name": m["name"],
            "iso": m.get("name_iso15919"),
            "aliases": m.get("alternate_names", []),
            "chakra": {"number": m["chakra"]["number"], "name": m["chakra"]["name"],
                       "iso": m["chakra"].get("name_iso15919"), "mnemonic": m["chakra"].get("mnemonic"),
                       "position": m["chakra"]["position_in_chakra"]},
            "madhyama": m["madhyama"],
            "swaras": ["S", sw["R"], sw["G"], sw["M"], "P", sw["D"], sw["N"]],
            "swarasthanaNames": m.get("swarasthana_names", {}),
            "semitones": m["semitones_from_sa"],
            "arohana": m["arohana"],
            "avarohana": m["avarohana"],
            "vivadi": m.get("vivadi", []),
            "katapayadi": katapayadi(m),
            # ⚠ Same name in both schools (12 Rupavati, 36 Chalanata, …): null,
            # which the page shows as nothing at all.
            "dikshitar": dik,
            "scripts": scripts,
            "scriptsFlags": m.get("scripts_flags", []),
            "notes": m.get("notes") if m.get("notes") != "Same name in both schools." else None,
            "confidence": m.get("confidence", {}),
            "confidenceReason": m.get("confidence_reason"),
            "janyas": [],
            "performed": None,
        })
    if len(melas) != 72:
        raise BuildError(f"expected 72 melakartas, found {len(melas)}")
    by_number = {m["number"]: m for m in melas}

    janyas = []
    for e in janya_doc["janya_ragas"]:
        scripts = janya_scripts(e["id"], table)
        check_scripts(f"janya {e['id']}", scripts)
        rec = raga_record(e, "janya", scripts)
        janyas.append(rec)
        parent = by_number.get(e["parent_melakarta"]["number"])
        if parent is None:
            raise BuildError(f"{e['id']}: parent mela {e['parent_melakarta']} does not exist")
        parent["janyas"].append(e["id"])

    performed = []
    for e in janya_doc.get("melakarta_ragas_as_performed", []):
        number = e["parent_melakarta"]["number"]
        mela = by_number[number]
        rec = raga_record(e, "melakarta", mela["scripts"])
        rec["number"] = number
        performed.append(rec)
        mela["performed"] = e["id"]

    order = {rid: i for i, rid in enumerate(FIRST)}
    janyas.sort(key=lambda r: (r["tier"], order.get(r["id"], 99), r["parent"]["number"], r["name"]))
    for i, r in enumerate(janyas, 1):
        r["order"] = i

    aliases = {}
    for m in melas:
        for a in [m["name"], *m["aliases"]]:
            aliases.setdefault(a, f"mela:{m['number']}")
    for r in janyas + performed:
        for a in [r["name"], *r["aliases"]]:
            a = re.sub(r"\s*\(.*\)$", "", a)
            aliases.setdefault(a, r["id"])

    return {"format": FORMAT, "melakartas": melas, "janyas": janyas, "performed": performed,
            "aliases": aliases, "meta": {
                "melakartaScheme": mela_doc["meta"].get("scheme"),
                "katapayadiRule": mela_doc["meta"].get("katapayadi_rule"),
                "dikshitarCaveat": mela_doc["meta"].get("dikshitar_names_caveat"),
                "scriptsPolicy": "Every Tamil, Telugu and Kannada name is an unverified candidate until a native reader clears it.",
                "researchLimits": janya_doc["meta"].get("research_limits"),
            }}


# ── talas ───────────────────────────────────────────────────────────────────

ACTION = {"beat": "clap", "finger": "finger", "wave": "wave", "silent": "silent", "rest": "silent"}


def counts_of(kriya: list[dict]) -> list[dict]:
    out = []
    for k in kriya:
        action = ACTION.get(k.get("type"), k.get("type"))
        out.append({k2: v for k2, v in {
            "n": k.get("count"),
            "action": action,
            "finger": k.get("finger"),
            "anga": k.get("anga_index", 0),
            "angaName": k.get("anga"),
            "samam": bool(k.get("samam")),
        }.items() if v is not None})
    return out


def compact_counts(compact: str) -> list[dict]:
    """'B . . B . B .' (chapu talas) as counts: claps and silent counts."""
    fingers = {"l": "little", "r": "ring", "m": "middle", "i": "index", "t": "thumb"}
    out = []
    for i, tok in enumerate(compact.split(), 1):
        if tok == "B":
            out.append({"n": i, "action": "clap"})
        elif tok == "W":
            out.append({"n": i, "action": "wave"})
        elif tok == ".":
            out.append({"n": i, "action": "silent"})
        elif tok in fingers:
            out.append({"n": i, "action": "finger", "finger": fingers[tok]})
    if out:
        out[0]["samam"] = True
    return out


NICE = {
    "adi": ("Adi", "I₄ O O"),
    "adi_2_kalai": ("Adi, 2-kalai", "every action twice"),
    "rupaka_3count": ("Rupaka", "clap, clap, wave"),
    "misra_chapu": ("Misra chapu", "3 + 2 + 2"),
    "khanda_chapu": ("Khanda chapu", "2 + 3"),
    "tisra_triputa": ("Tisra triputa", "I₃ O O"),
    "khanda_ata": ("Khanda ata", "I₅ I₅ O O"),
    "misra_jhampa": ("Misra jhampa", "I₇ U O"),
    "rupaka_chaturasra": ("Rupaka, 6-count", "O I₄"),
    "chaturasra_eka": ("Chatusra eka", "I₄"),
    "tisra_eka": ("Tisra eka", "I₃"),
}
ORDER = ["adi", "adi_2_kalai", "rupaka_3count", "misra_chapu", "khanda_chapu", "tisra_triputa",
         "khanda_ata", "misra_jhampa", "rupaka_chaturasra", "chaturasra_eka", "tisra_eka"]


def build_talas(root: Path) -> dict:
    doc = load(root, "tala/talas.json")
    konn = load(root, "tala/konnakol.json")
    practical = {t["id"]: t for t in doc["practical_talas"]}
    missing = [i for i in ORDER if i not in practical]
    if missing:
        raise BuildError(f"practical talas missing: {missing}")

    def angas_of(counts):
        groups, cur, last = [], [], None
        for c in counts:
            a = c.get("anga", 0)
            if cur and a != last:
                groups.append(len(cur))
                cur = []
            cur.append(c)
            last = a
        if cur:
            groups.append(len(cur))
        return groups

    out = []
    for tid in ORDER:
        t = practical[tid]
        counts = counts_of(t["kriya"]) if t.get("kriya") else compact_counts(t["kriya_compact"])
        if "chapu" in tid:
            # The default claps (DECISIONS tala §2), one group per clap.
            groups = [3, 2, 2] if tid == "misra_chapu" else [2, 3]
            n = 0
            for gi, size in enumerate(groups):
                for _ in range(size):
                    counts[n]["anga"] = gi
                    n += 1
        name, shape = NICE[tid]
        out.append(drop_history({
            "id": tid,
            "slug": tid.replace("_", "-").replace("rupaka-3count", "rupaka").replace("rupaka-chaturasra", "rupaka-6"),
            "name": name,
            "fullName": t.get("name"),
            "angaNotation": t.get("anga_notation") or t.get("structure"),
            "shape": shape,
            "counts": counts,
            "angas": angas_of(counts),
            "grid": t.get("grid"),
            "gridNote": t.get("grid_note"),
            "compact": t.get("kriya_compact"),
            "speech": t.get("count_speech"),
            "notes": t.get("notes"),
            "variants": t.get("kriya_variants", []),
            "discrepancy": t.get("discrepancy"),
            "konnakol": t.get("konnakol"),
            "confidence": t.get("confidence"),
            "sources": t.get("sources", []),
        }))
    adi = next(t for t in out if t["id"] == "adi")
    out.append({
        **{k: v for k, v in adi.items() if k not in ("variants", "discrepancy")},
        "id": "deshadi", "slug": "deshadi", "name": "Deshadi", "fullName": "Deshadi (Adi, starts 1½ beats in)",
        "shape": "enters 1½ beats after samam", "eduppu": 1.5, "asTala": "adi",
        "notes": "Performed today as Adi tala with the song entering 1½ beats after samam (Sambamoorthy, South Indian Music Book III pp. 56-57; karnatik.com glossary). The historical form is a 4-count tala shown as a wave and three beats.",
        "confidence": "high (Adi with a 1½-beat eduppu); medium that Nadopasana is in Deshadi (karnatik.com only)",
        "variants": [],
    })

    suladi = []
    for t in doc["talas_35"]:
        suladi.append({"id": t["id"], "family": t["family"], "jati": t["jati"], "name": t.get("sanskrit_name"),
                       "angaNotation": t["anga_notation"],
                       "angas": [a["aksharas"] for a in t["angas"]], "aksharas": t["aksharas"],
                       "counts": counts_of(t["kriya"])})

    return drop_history({
        "format": FORMAT,
        "practical": out,
        "suladi": suladi,
        "jatis": doc.get("jatis"),
        "angas": doc.get("angas"),
        "fingerOrder": doc.get("finger_order"),
        "nadai": doc.get("gati_nadai"),
        "kalai": doc.get("kalai"),
        "konnakol": {"bySubdivision": konn.get("syllables_by_subdivision"), "gati": konn.get("gati_syllables"),
                     "examples": konn.get("worked_examples")},
        "alankaramTalas": [
            {"n": 1, "tala": "chaturasra_jati_dhruva"}, {"n": 2, "tala": "chaturasra_jati_matya"},
            {"n": 3, "tala": "chaturasra_jati_rupaka"}, {"n": 4, "tala": "misra_jati_jhampa"},
            {"n": 5, "tala": "tisra_jati_triputa"}, {"n": 6, "tala": "khanda_jati_ata"},
            {"n": 7, "tala": "chaturasra_jati_eka"}, {"n": 8, "tala": "sankeerna_jati_eka", "optional": True},
        ],
    })


# ── lessons ─────────────────────────────────────────────────────────────────

TOKEN = re.compile(r"^(\.?[SRGMPDN]|[SRGMPDN]'?|,)$")
RAGA_SWARAS = {"Mayamalavagowla": set("SRGMPDN"), "Malahari": set("SRGMPD")}


def anga_sizes(root: Path) -> dict:
    doc = load(root, "tala/talas.json")
    out = {t["id"]: [a["aksharas"] for a in t["angas"]] for t in doc["talas_35"]}
    out["adi"] = out["chaturasra_jati_triputa"]
    return out


def repeats_for(total: int, aksharas: int) -> dict:
    """
    How many times an exercise is sung at each speed so it ends on samam: the
    fewest repetitions that fill whole avartanams (validate_varisai.py's rule).
    """
    out = {}
    for level, per_count in SPEEDS.items():
        per_av = aksharas * per_count
        rep = per_av // math.gcd(total, per_av)
        if rep not in ALLOWED_REPEATS:
            raise BuildError(f"needs {rep} repetitions at speed {level}")
        out[str(level)] = rep
    return out


def build_lessons(root: Path) -> dict:
    doc = load(root, "lessons/abhyasa_gana.json")
    sizes = anga_sizes(root)
    sets, path = [], []
    for s in doc["sets"]:
        items = s.get("exercises") or s.get("items") or []
        out_items = []
        for it in items:
            tala = it["tala"]
            if tala not in sizes:
                raise BuildError(f"{it['id']}: unknown tala {tala}")
            raga = it.get("raga", "Mayamalavagowla")
            allowed = RAGA_SWARAS.get(raga)
            if allowed is None:
                raise BuildError(f"{it['id']}: unknown raga {raga}")
            if "lines" in it:
                sections = [{"section": None, "lines": it["lines"]}]
            else:
                sections = [{"section": sec.get("section"), "lines": sec.get("lines", [])} for sec in it["sections"]]
            total = 0
            for sec in sections:
                for n, line in enumerate(sec["lines"], 1):
                    toks = [t for seg in line["segments"] for t in seg]
                    for t in toks:
                        if not TOKEN.match(t) or (t != "," and t.strip(".'") not in allowed):
                            raise BuildError(f"{it['id']} line {n}: bad token {t!r}")
                    if [len(seg) for seg in line["segments"]] != sizes[tala] * (len(toks) // sum(sizes[tala])):
                        raise BuildError(f"{it['id']} line {n}: segments do not match the tala")
                    total += len(toks)
            optional = it["id"].startswith("alankaram_8")
            rec = {
                "id": it["id"],
                "title": it.get("title"),
                "tala": tala,
                "practicalTala": TALA_OF_LESSON.get(tala),
                "angas": sizes[tala],
                "raga": raga,
                "units": total,
                "repeats": repeats_for(total, sum(sizes[tala])),
                "sections": [{"section": sec["section"],
                              "lines": [{"segments": l["segments"], "sahitya": l.get("sahitya_source")}
                                        for l in sec["lines"]]} for sec in sections],
                "optional": optional,
            }
            for key in ("type", "composer", "language", "raga_scale", "tala_note", "technique"):
                if it.get(key):
                    rec[key] = it[key]
            out_items.append(rec)
            if not optional:
                path.append(it["id"])
        sets.append(drop_history({"id": s["id"], "name": s["name"], "countNote": s.get("count_note"),
                                  "definition": s.get("definition"), "technique": s.get("technique"),
                                  "confidence": s.get("confidence"), "items": out_items,
                                  "refs": s.get("exercise_refs")}))
    if len(path) != 50:
        raise BuildError(f"the default path should have 50 items, it has {len(path)}")
    meta = doc["meta"]
    return drop_history({
        "format": FORMAT,
        "defaultRaga": meta.get("default_raga"),
        "attribution": meta.get("attribution"),
        "speeds": meta.get("speed_levels"),
        "speedNote": meta.get("speed_note"),
        "path": path,
        "sets": sets,
        "varnamsComing": [
            {"title": "Ninnukori", "raga": "mohanam", "tala": "Adi"},
            {"title": "Evvari bodhana", "raga": "abhogi"},
            {"title": "Inta chalamu", "raga": "begada", "tala": "Adi"},
            {"title": "Jalajakshi", "raga": "hamsadhwani"},
        ],
    })


# ── instruments ─────────────────────────────────────────────────────────────

def parse_mridangam_scripts(gaps: str) -> dict:
    start = gaps.index("## 5. Mridangam stroke names")
    end = gaps.index("## 6.", start)
    out = {}
    for line in gaps[start:end].splitlines():
        if not line.startswith("| ") or line.startswith("| stroke") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        stroke, ta, te, kn = cells[:4]

        def first(cell):
            sourced = "**" in cell
            m = re.search(r"\*\*(.+?)\*\*", cell)
            text = m.group(1) if m else re.split(r"\s*\(", cell)[0]
            return {"text": text.strip(), "sourced": sourced}
        out[stroke] = {"ta": first(ta), "te": first(te), "kn": first(kn)}
    return out


def build_instruments(root: Path, gaps: str) -> dict:
    venu = drop_history(load(root, "instruments/venu.json"))
    veena = drop_history(load(root, "instruments/veena.json"))
    violin = drop_history(load(root, "instruments/violin.json"))
    mridangam = drop_history(load(root, "instruments/mridangam.json"))
    voice = drop_history(load(root, "instruments/voice.json"))
    tanpura = drop_history(load(root, "instruments/tanpura.json"))
    if len(venu["fingerings"]) != 40:
        raise BuildError(f"venu.json should have 40 fingerings, has {len(venu['fingerings'])}")
    scripts = parse_mridangam_scripts(gaps)
    for s in mridangam.get("strokes", []):
        key = s["id"].replace("_", " ")
        s["scripts"] = scripts.get(key) or scripts.get(s["id"])
    for c in mridangam.get("combinations", []):
        name = c.get("name") or c["id"]
        c["scripts"] = scripts.get(name)
    for inst in (venu, veena, violin, mridangam):
        inst.pop("sourceKeys", None)
    return {"format": FORMAT, "venu": venu, "veena": veena, "violin": violin,
            "mridangam": mridangam, "voice": voice, "tanpura": tanpura}


# ── the web overlays (research/web/) ────────────────────────────────────────

def build_featured(root: Path, ragas: dict) -> dict:
    doc = load(root, "web/featured.json")
    ids = {r["id"] for r in ragas["janyas"] + ragas["performed"]}
    for rid, page in doc["ragas"].items():
        if rid not in ids:
            raise BuildError(f"featured page for unknown raga {rid}")
        for rel in page.get("related", []):
            if rel not in ids:
                raise BuildError(f"{rid}: related raga {rel} has no page")
    return {"format": FORMAT, **drop_history(doc)}


def build_gamakas(root: Path) -> dict:
    doc = load(root, "web/gamakas.json")
    if len(doc["gamakas"]) < 9:
        raise BuildError("the gamaka library should list nine gamakas")
    return {"format": FORMAT, **doc}


# ── main ────────────────────────────────────────────────────────────────────

def build(root: Path, out: Path) -> dict:
    if not (root / "LICENSE-DATA.md").is_file():
        raise BuildError("LICENSE-DATA.md is missing; the research is not published without it")
    gaps = (root / "GAPS_PASS_3.md").read_text(encoding="utf-8")
    ragas = build_ragas(root, gaps)
    files = {
        "ragas.json": ragas,
        "talas.json": build_talas(root),
        "lessons.json": build_lessons(root),
        "instruments.json": build_instruments(root, gaps),
        "featured.json": build_featured(root, ragas),
        "gamakas.json": build_gamakas(root),
    }
    out.mkdir(parents=True, exist_ok=True)
    listed = []
    for name, data in files.items():
        raw = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        (out / name).write_bytes(raw)
        listed.append({"name": name, "digest": hashlib.sha256(raw).hexdigest()[:16], "bytes": len(raw)})
    digest = hashlib.sha256("".join(f["digest"] for f in listed).encode()).hexdigest()[:16]
    return {"format": FORMAT, "digest": digest, "files": listed,
            "counts": {"melakartas": len(ragas["melakartas"]), "janyas": len(ragas["janyas"]),
                       "performed": len(ragas["performed"])}}


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    try:
        summary = build(Path(argv[1]), Path(argv[2]))
    except BuildError as e:
        print(f"carnatic data: {e}", file=sys.stderr)
        return 1
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
