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
CHANNEL = 7
ROLE = 8

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
})

NAMES = {c["name"] for c in COMMANDS}
