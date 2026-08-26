# SPDX-License-Identifier: AGPL-3.0-only
"""
What the bot can be asked, as data.

A list rather than decorators, because the same definitions are needed in three
places — registered with Discord, dispatched at runtime, and asserted in tests
— and three sources for one list is how a command ends up registered and
unimplemented.
"""
from __future__ import annotations

# Discord application command option types.
STRING = 3

# Every instrument the ephemeris can answer without storing anything. The
# chart commands are deliberately absent for now: a chart is birth data, and
# birth data does not belong in somebody else's Discord channel without the
# ephemeral handling designed for it.
COMMANDS: list[dict] = [
    {
        "name": "hour",
        "description": "The planetary hour right now, and when it turns over.",
        "options": [
            {"type": STRING, "name": "place", "required": False,
             "description": "A city. Defaults to the server's place, or Athens."},
        ],
    },
    {
        "name": "isopsephy",
        "description": "Add up a word by its letters, in six scripts.",
        "options": [
            {"type": STRING, "name": "text", "required": True,
             "description": "The word or phrase to reckon."},
            # The VALUES are the daemon's cipher slugs, so nothing has to be
            # translated at dispatch time and there is no mapping to drift.
            # Hebrew defaults to hechrachi — finals take their ordinary values,
            # which is what the website's own page says it uses. Gadol, where
            # finals run 500–900, is a different answer and a separate choice.
            {"type": STRING, "name": "script", "required": False,
             "description": "Which table to reckon by. Greek unless you say otherwise.",
             "choices": [
                 {"name": "Greek", "value": "greek-iso"},
                 {"name": "Hebrew (ordinary values)", "value": "heb-hechrachi"},
                 {"name": "Hebrew (finals 500–900)", "value": "heb-gadol"},
                 {"name": "English (simple)", "value": "eng-simple"},
                 {"name": "Coptic", "value": "copt-iso"},
                 {"name": "Arabic (abjad)", "value": "ar-abjad"},
                 {"name": "Sanskrit (kaṭapayādi)", "value": "skt-katapayadi"},
             ]},
        ],
    },
]

NAMES = {c["name"] for c in COMMANDS}
