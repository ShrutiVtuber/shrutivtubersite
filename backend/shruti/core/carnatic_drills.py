# SPDX-License-Identifier: AGPL-3.0-only
"""
The ear-training ladders (EAR_TRAINING.md §4), the tala-keeping tasks
K.01-K.16 (SELF_TEST.md §3) and the confusable sets, as data.

These are the drill *definitions*: ids, what each level asks, how it is
answered, which lesson opens it. The items themselves are generated at
play time from the research data (the swaras, the melakartas, the
prayogas), so a drill can never contradict the raga pages. When the course
repository gains `exercises/drills.yaml` (EAR_TRAINING.md §7), the import
carries it and it replaces these defaults.

`unlocked_by` is advice: a level whose lesson isn't complete is drawn dashed
with the lesson named, and opens anyway.
"""
from __future__ import annotations

FAMILIES = [
    {"id": "SW", "title": "Swaras against the drone", "answerBy": "swara buttons", "words": "swaras"},
    {"id": "PD", "title": "Phrase dictation", "answerBy": "sargam input, partial credit", "words": "phrases"},
    {"id": "PR", "title": "Raga phrases", "answerBy": "choice, yes/no, text", "words": "raga phrases"},
    {"id": "RR", "title": "Raga from recordings", "answerBy": "choice, text", "words": "ragas from recordings"},
    {"id": "GM", "title": "Gamakas", "answerBy": "choice, multi-select", "words": "gamakas"},
    {"id": "TL", "title": "Tala and laya", "answerBy": "choice, tap", "words": "tala and laya"},
    {"id": "MS", "title": "Melakarta scales", "answerBy": "choice, number", "words": "melakarta scales",
     "note": "a scale, not a raga"},
    {"id": "FM", "title": "Forms", "answerBy": "choice", "words": "forms"},
]


def _l(id, title, unlocked_by, answer="choice", audio="synth", fluent=3000, note=None, ladder=None):
    return {"id": id, "family": id.split(".")[0], "title": title, "unlockedBy": unlocked_by, "answer": answer,
            "audio": {"kind": audio}, "fluentMs": fluent, "note": note, "ladder": ladder or []}


SW_LADDER = ["3 choices, 2 s notes", "5 choices, 1 s", "all, 0.5 s", "drone for one second, then silence"]
PD_LADDER = ["3 notes", "5 notes", "8 notes", "12 notes", "16 notes"]
RR_LADDER = ["60 s clips", "30 s clips", "15 s clips"]
GM_LADDER = ["wide and slow", "narrower and faster", "inside a phrase"]
TL_LADDER = ["40-70 a minute", "40-100", "40-140"]

LEVELS = [
    _l("SW.01", "Sa, Pa, or neither?", "U01.L03", ladder=SW_LADDER),
    _l("SW.02", "Which octave: mandra, madhya or tara", "U01.L04", ladder=SW_LADDER),
    _l("SW.03", "The seven swaras of Mayamalavagowla", "U02.L02", answer="swara", ladder=SW_LADDER),
    _l("SW.04", "The pairs that matter", "U02.L05", ladder=SW_LADDER),
    _l("SW.05", "All twelve swarasthanas", "U02.L05", answer="swara", ladder=SW_LADDER),
    _l("SW.06", "Any swara, in any octave", "U02.L05", answer="swara", ladder=SW_LADDER),
    _l("SW.07", "Two swaras: which is higher, and name both", "U02.L04", answer="swara", ladder=SW_LADDER),
    _l("PD.01", "3 notes, stepwise", "U03.L01", answer="sargam", fluent=8000, ladder=PD_LADDER),
    _l("PD.02", "4-6 notes with holds", "U03.L03", answer="sargam", fluent=10000, ladder=PD_LADDER),
    _l("PD.03", "Janta patterns", "U05.L04", answer="sargam", fluent=10000, ladder=PD_LADDER),
    _l("PD.04", "Leaps of a third to a sixth", "U05.L05", answer="sargam", fluent=10000, ladder=PD_LADDER),
    _l("PD.05", "Phrases into tara or mandra", "U05.L07", answer="sargam", fluent=10000, ladder=PD_LADDER),
    _l("PD.06", "Speed 2, one avartanam of Adi", "U05.L10", answer="sargam", fluent=15000, ladder=PD_LADDER),
    _l("PD.07", "Varisai lines in another raga", "U07.L02", answer="sargam", fluent=15000, ladder=PD_LADDER),
    _l("PD.08", "Prayogas, raga named", "U10.L03", answer="sargam", fluent=15000, ladder=PD_LADDER),
    _l("PD.09", "A phrase from a recording", "U21.L04", answer="sargam", audio="recording", fluent=30000),
    _l("PR.01", "Which raga does this phrase belong to?", "U12.L01", fluent=6000),
    _l("PR.02", "Is this phrase idiomatic in raga X?", "U10.L08", answer="yesno", fluent=6000),
    _l("PR.03", "Four choices across everything studied", "U12.L08", fluent=8000),
    _l("PR.04", "Name the raga", "U15.L12", answer="text", fluent=10000),
    _l("RR.01", "Two choices", "U07.L09", audio="recording", fluent=30000, ladder=RR_LADDER),
    _l("RR.02", "Four choices, among studied ragas", "U12.L08", audio="recording", fluent=30000, ladder=RR_LADDER),
    _l("RR.03", "Name the raga", "U15.L12", answer="text", audio="recording", fluent=30000, ladder=RR_LADDER),
    _l("RR.04", "Raga, form and tala of a clip", "U17.L06", answer="fields", audio="recording", fluent=45000),
    _l("RR.05", "Shruti's flute recordings", "U12.L08", audio="recording", fluent=30000),
    _l("GM.01", "Plain note or kampita?", "U11.L02", ladder=GM_LADDER),
    _l("GM.02", "Jaru up, jaru down, or a plain step?", "U11.L03", ladder=GM_LADDER),
    _l("GM.03", "Nokku, odukkal or orikkai?", "U11.L04", ladder=GM_LADDER),
    _l("GM.04", "On a repeated note: plain, sphurita or pratyahata?", "U11.L05", ladder=GM_LADDER),
    _l("GM.05", "Ravai or khandippu?", "U11.L05", ladder=GM_LADDER),
    _l("GM.06", "Which gamaka is on the marked note?", "U11.L08", ladder=GM_LADDER),
    _l("GM.07", "Gamakas in a recording clip", "U11.L10", answer="multi", audio="recording", fluent=20000),
    _l("TL.01", "Which tala?", "U04.L08", audio="kriya", fluent=15000, ladder=TL_LADDER),
    _l("TL.02", "Which tala, from claps only?", "U04.L08", audio="kriya", fluent=15000, ladder=TL_LADDER),
    _l("TL.03", "Which speed: 1, 2 or 3?", "U04.L09", fluent=10000, ladder=TL_LADDER),
    _l("TL.04", "How many aksharas? Count it", "U08.L03", answer="number", audio="kriya", fluent=20000),
    _l("TL.05", "Which nadai?", "U08.L05", audio="konnakol", fluent=10000, ladder=TL_LADDER),
    _l("TL.06", "1 kalai or 2 kalai?", "U08.L07", fluent=15000),
    _l("TL.07", "Where does the song start?", "U08.L08", answer="tap", fluent=15000),
    _l("TL.08", "Which tala, from a recording clip", "U04.L10", audio="recording", fluent=30000),
    _l("TL.09", "Where does this mora land? Tap it", "U16.L04", answer="tap", audio="konnakol", fluent=20000),
    _l("TL.10", "Tap when the nadai changes", "U16.L02", answer="tap", audio="konnakol", fluent=20000),
    _l("TL.11", "Korvai landing in a recording", "U16.L11", answer="tap", audio="recording", fluent=30000),
    _l("MS.01", "Which R and G?", "U09.L03", note="a scale, not a raga"),
    _l("MS.02", "Which D and N?", "U09.L03", note="a scale, not a raga"),
    _l("MS.03", "M1 or M2?", "U09.L03", note="a scale, not a raga"),
    _l("MS.04", "The mela number", "U09.L03", answer="number", fluent=12000, note="a scale, not a raga"),
    _l("FM.01", "Pallavi, anupallavi or charanam?", "U14.L02", audio="recording", fluent=20000),
    _l("FM.02", "Composed or improvised?", "U19.L01", audio="recording", fluent=20000),
    _l("FM.03", "Which item of a main piece?", "U20.L03", audio="recording", fluent=20000),
]

# EAR_TRAINING.md §4 PR: confusable sets. `mode` is Sophia's to change.
CONFUSABLE = [
    {"set": "C1", "ragas": ["mohanam", "shivaranjani"], "mode": "synth", "unlockedBy": "U12.L03",
     "differ": "G3 against G2"},
    {"set": "C2", "ragas": ["abhogi", "sriranjani"], "mode": "synth", "unlockedBy": "U12.L06",
     "differ": "Sriranjani adds N2"},
    {"set": "C3", "ragas": ["mohanam", "hamsadhwani"], "mode": "synth", "unlockedBy": "U12.L05",
     "differ": "D2 against N3"},
    {"set": "C4", "ragas": ["kalyani", "saranga"], "mode": "synth", "unlockedBy": "U15.L01",
     "differ": "Saranga uses both madhyamas"},
    {"set": "C5", "ragas": ["kalyani", "mohana-kalyani"], "mode": "synth", "unlockedBy": "U15.L01", "differ": ""},
    {"set": "C6", "ragas": ["sankarabharanam", "bilahari"], "mode": "synth", "unlockedBy": "U15.L02", "differ": ""},
    {"set": "C7", "ragas": ["sankarabharanam", "begada", "bilahari"], "mode": "recordings", "unlockedBy": "U15.L07",
     "differ": "Begada's nishada sits between N2 and N3"},
    {"set": "C8", "ragas": ["todi", "dhanyasi", "bhairavi"], "mode": "recordings", "unlockedBy": "U15.L04",
     "differ": ""},
    {"set": "C9", "ragas": ["kharaharapriya", "bhairavi"], "mode": "recordings", "unlockedBy": "U15.L05",
     "differ": "the emphasised Ma in R G M P"},
    {"set": "C10", "ragas": ["mayamalavagowla", "saveri"], "mode": "recordings", "unlockedBy": "U12.L01",
     "differ": ""},
    {"set": "C11", "ragas": ["pantuvarali", "poorvikalyani"], "mode": "recordings", "unlockedBy": "U15.L10",
     "differ": ""},
    {"set": "C12", "ragas": ["keeravani", "kalyana-vasantam"], "mode": "synth", "unlockedBy": "U10.L08",
     "differ": ""},
    {"set": "C13", "ragas": ["kambhoji", "harikambhoji", "yadukula-kambhoji"], "mode": "recordings",
     "unlockedBy": "U15.L06", "differ": ""},
]

FADE_ALL = ["all", "claps", "samam", "none"]


def _k(id, title, tala, tempo, targets, unlocked_by, **extra):
    return {"id": id, "kind": "tap", "title": title, "tala": tala, "tempoRange": list(tempo), "tempo": tempo[0] + 10,
            "targets": targets, "unlockedBy": unlocked_by, "avartanams": extra.pop("avartanams", 4),
            "countIn": 1, "speed": extra.pop("speed", 1), "nadai": extra.pop("nadai", 4),
            "report": ["perfect", "on_time", "early", "late", "missed"], **extra}


TALA_KEEPING = [
    _k("K.01", "Keep Adi for 4 avartanams with the app", "adi", (50, 70), "claps", "U04.L02"),
    _k("K.02", "Keep Adi while the audio fades", "adi", (50, 80), "claps", "U04.L02", fade=FADE_ALL),
    _k("K.03", "Rupaka (3) for 8 avartanams", "rupaka", (50, 90), "claps", "U04.L05", avartanams=8),
    _k("K.04", "Misra chapu", "misra_chapu", (50, 100), "claps", "U04.L07", avartanams=8),
    _k("K.05", "Khanda chapu", "khanda_chapu", (50, 100), "claps", "U04.L08", avartanams=8),
    _k("K.06", "Keep Adi while a sarali varisai plays in speeds 1, 2 and 3", "adi", (50, 80), "claps", "U04.L09",
       speed=[1, 2, 3], plays="sarali_01", avartanams=6),
    _k("K.07", "Up and down: speeds 1, 2, 3, 2, 1", "adi", (50, 80), "claps", "U05.L10",
       speed=[1, 2, 3, 2, 1], plays="sarali_01", avartanams=10),
    _k("K.08", "Find samam after a gap", "adi", (50, 90), "samam-after-gap", "U04.L10", gap=[1, 3], avartanams=6),
    _k("K.09", "Keep the alankaram talas while the alankaram plays", "chaturasra_jati_dhruva", (50, 80), "claps",
       "U05.L09", plays="alankaram_1"),
    _k("K.10", "2-kalai Adi, every action twice", "adi_2_kalai", (40, 70), "claps", "U08.L07", avartanams=2),
    _k("K.11", "Enter on the eduppu", "adi", (50, 80), "entry", "U08.L08", eduppu=[0.5, 1.5]),
    _k("K.12", "Keep Adi through nadai changes (4, 3, 5)", "adi", (50, 80), "claps", "U08.L05", nadai=[4, 3, 5],
       avartanams=3),
    _k("K.13", "Tap the konnakol syllable onsets", "adi", (40, 70), "syllables", "U16.L01"),
    _k("K.14", "Keep tala while a korvai plays, then tap its landing", "adi", (50, 90), "claps-and-landing",
       "U16.L06"),
    _k("K.15", "Chapu talas under swara rounds", "misra_chapu", (60, 110), "claps", "U19.L05", avartanams=8),
    _k("K.16", "Tap along with a real recording", "adi", (40, 140), "claps", "U04.L10", recording=True),
]

# SELF_TEST.md §2: topic review strands, by the units that carry them.
TOPICS = {
    "pitch": [1, 2], "notation": [3, 21], "tala": [4, 8], "raga": [7, 10, 12, 15], "melakarta": [9],
    "gamaka": [11], "forms": [6, 13, 14, 17], "laya": [16], "manodharma": [19], "history": [18, 20],
}


def definitions(flags: dict[str, bool]) -> dict:
    return {"families": FAMILIES, "levels": LEVELS, "confusable": CONFUSABLE,
            "ragaFlags": {r: {"synthOk": ok} for r, ok in sorted(flags.items())},
            "talaKeeping": TALA_KEEPING, "topics": TOPICS}
