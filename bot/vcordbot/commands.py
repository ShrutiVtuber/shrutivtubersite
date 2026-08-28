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
SUB_COMMAND = 1
STRING = 3
BOOLEAN = 5
CHANNEL = 7
ROLE = 8

# Keys below that Discord has never heard of. They are the help text, kept
# beside the command they document so that adding a command adds its own
# entry in `/help` and cannot forget to — and stripped by `for_discord()`
# before the list is registered.
OURS = ("usage", "example", "summary")

# Every instrument the ephemeris can answer without storing anything.
#
# `/chart` was held back until there was somewhere safe to put the answer,
# because a chart IS birth data and birth data does not belong in somebody
# else's Discord channel by default. It is here now with that handling: the
# reply is ephemeral unless the person casting it asks for otherwise, and
# nothing about it is written down anywhere.
COMMANDS: list[dict] = [
    {
        "name": "hour",
        "description": "The planetary hour right now, and when it turns over.",
        "usage": "/hour [place:<city>]",
        "example": "/hour place:Athens",
        "options": [
            {"type": STRING, "name": "place", "required": False,
             "description": "A city. Defaults to the server's place, or Athens."},
        ],
    },
    {
        "name": "isopsephy",
        "description": "Add up a word by its letters, in six scripts.",
        "usage": "/isopsephy text:<word> [script:<table>]",
        "example": "/isopsephy text:Ἀγάπη script:Greek",
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

COMMANDS.append({
    "name": "chart",
    "description": "Cast a natal chart from a birth date, time and place.",
    "usage": ("/chart date:<YYYY-MM-DD> time:<HH:MM|unknown> city:<name> "
              "country:<name>\n       [state:<US only>] [tradition:<hellenic|vedic>] "
              "[share:<true|false>]"),
    "example": "/chart date:1996-05-14 time:09:30 city:Athens country:Greece",
    "summary": ("The reply is yours alone unless you pass share:true. Nothing is "
                "stored, here or anywhere."),
    "options": [
        {"type": STRING, "name": "date", "required": True,
         "description": "Birth date, YYYY-MM-DD. e.g. 1996-05-14"},
        # Required, and `unknown` is one of the things it takes. The site's own
        # tool is built around this state: with no time the ascendant is not
        # merely imprecise, it is undefined, and a tool that quietly used noon
        # would hand back a fabricated one. Making it a value rather than a
        # separate flag means nobody types 12:00 to get past a required field.
        {"type": STRING, "name": "time", "required": True,
         "description": "Birth time, 24-hour. e.g. 09:30 — or 'unknown'"},
        {"type": STRING, "name": "city", "required": True,
         "description": "Town or city of birth. e.g. Athens"},
        {"type": STRING, "name": "country", "required": True,
         "description": "Country of birth. e.g. Greece"},
        {"type": STRING, "name": "state", "required": False,
         "description": "For the USA, where a city name repeats. e.g. CA or California"},
        # The VALUES are the daemon's own slugs, so nothing is translated at
        # dispatch time and there is no mapping to drift — the same rule the
        # isopsephy ciphers follow. The NAME is hers: she says Hellenic.
        {"type": STRING, "name": "tradition", "required": False,
         "description": "Which sky, whose houses. Hellenic unless you say otherwise.",
         "choices": [
             {"name": "Hellenic", "value": "hellenistic"},
             {"name": "Vedic", "value": "vedic"},
         ]},
        {"type": BOOLEAN, "name": "share", "required": False,
         "description": "Post it in the channel. Off by default — it is your birth data."},
    ],
})

COMMANDS.append({
    "name": "help",
    "description": "What this bot can do, and the syntax for each.",
    "usage": "/help [command:<name>]",
    "example": "/help command:chart",
    "options": [
        {"type": STRING, "name": "command", "required": False,
         "description": "One command in full. Omit for all of them."},
    ],
})

COMMANDS.append({
    "name": "announce",
    "description": "Say something in this server when a channel goes live.",
    # Manage Server. Discord hides the command from anybody else, which is the
    # good half — the handler checks it too, because a default_member_permissions
    # is a UI hint and not an authorisation.
    "default_member_permissions": str(1 << 5),
    # Announcements belong to a server, not to a person's DMs.
    "dm_permission": False,
    "options": [
        {"type": SUB_COMMAND, "name": "here",
         "description": "Post announcements in this channel.",
         "options": [
             {"type": ROLE, "name": "mention", "required": False,
              "description": "A role to ping. Only this role can ever be pinged."},
         ]},
        {"type": SUB_COMMAND, "name": "watch",
         "description": "Watch a channel and announce when it goes live.",
         "options": [
             {"type": STRING, "name": "platform", "required": True,
              "description": "Where to watch.",
              "choices": [{"name": "Twitch", "value": "twitch"},
                          {"name": "YouTube", "value": "youtube"}]},
             {"type": STRING, "name": "handle", "required": True,
              "description": "A Twitch login, or a YouTube channel id starting UC."},
         ]},
        {"type": SUB_COMMAND, "name": "unwatch",
         "description": "Stop watching one.",
         "options": [
             {"type": STRING, "name": "platform", "required": True,
              "description": "Where it was watched.",
              "choices": [{"name": "Twitch", "value": "twitch"},
                          {"name": "YouTube", "value": "youtube"}]},
             {"type": STRING, "name": "handle", "required": True,
              "description": "The same handle you added."},
         ]},
        {"type": SUB_COMMAND, "name": "message",
         "description": "What the announcement says. {handle} {title} {game} {url}",
         "options": [
             {"type": STRING, "name": "template", "required": True,
              "description": "e.g. {handle} is live — {title} {url}"},
         ]},
        {"type": SUB_COMMAND, "name": "status",
         "description": "What this server is set up to announce."},
    ],
    "usage": ["/announce here [mention:<role>]",
              "/announce watch platform:<twitch|youtube> handle:<name>",
              "/announce unwatch platform:<twitch|youtube> handle:<name>",
              "/announce message template:<text>",
              "/announce status"],
    "example": "/announce watch platform:twitch handle:shruti",
    "summary": "Needs Manage Server.",
})

NAMES = {c["name"] for c in COMMANDS}

# Commands that go and ask something slow before they can answer. Discord gives
# three seconds to say ANYTHING, and a geocoder plus an ephemeris is not
# reliably inside that, so these are acknowledged first and filled in after.
# Getting this list wrong is visible either way: too few and the interaction
# times out, too many and a fast answer arrives as an edit.
DEFERRED = {"chart"}

# `/help command:` offers the same names that exist, rather than a hand-kept
# copy of them that can fall behind.
for _c in COMMANDS:
    if _c["name"] == "help":
        _c["options"][0]["choices"] = [
            {"name": n, "value": n} for n in sorted(NAMES)
        ]


def for_discord() -> list[dict]:
    """
    The list as Discord will take it, with our own keys removed.

    The help text lives inside the command definitions so that the two cannot
    drift, which means it also has to be taken back out before registration —
    Discord validates this payload strictly and an unknown key is a rejected
    PUT, not a warning.
    """
    def strip(node):
        if isinstance(node, dict):
            return {k: strip(v) for k, v in node.items() if k not in OURS}
        if isinstance(node, list):
            return [strip(v) for v in node]
        return node

    return [strip(c) for c in COMMANDS]
