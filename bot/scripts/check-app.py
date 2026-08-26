#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""
Ask Discord what this application is actually configured as.

Reading the settings back beats reading them off a screen: the portal moves its
controls around, "Save" is easy to miss, and a toggle that looks on can be
un-saved. This asks the source.

The token is read from .env and never printed, never logged, and never included
in an error — the failure messages below deliberately say what is wrong without
quoting the credential.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Application flags that matter. The *_LIMITED variants mean "switched on in
# the portal but not yet reviewed", which is the normal state under the review
# threshold — so seeing LIMITED is not a problem in itself, it just means the
# toggle is ON.
FLAGS = {
    1 << 12: ("Presence intent", "approved"),
    1 << 13: ("Presence intent", "ON, pending review"),
    1 << 14: ("Server Members intent", "approved"),
    1 << 15: ("Server Members intent", "ON, pending review"),
    1 << 18: ("Message Content intent", "approved"),
    1 << 19: ("Message Content intent", "ON, pending review"),
    1 << 16: ("Below the verification guild limit", "informational"),
}

# What this bot should look like. Every one of these is a decision recorded in
# docs/BOT_PLAN.md, so a mismatch is a drift from a decision rather than taste.
WANT = {
    "bot_public": (True, "others must be able to add it — that is the product"),
    "bot_require_code_grant": (False, "turning this on breaks ordinary invites"),
}
UNWANTED_INTENTS = {
    "Server Members intent":
        "not needed: role assignment is a REST call governed by permissions, "
        "and Discord rejects intent requests where an alternative would work",
    "Message Content intent":
        "not needed: slash commands carry their own data, and this is the "
        "hardest intent to get approved",
    "Presence intent": "not needed by anything planned",
}


def token() -> str:
    env = Path(__file__).resolve().parents[2] / ".env"
    if not env.is_file():
        sys.exit("No .env found. Run scripts/set-secret.sh SHRUTI_DISCORD_BOT_TOKEN first.")
    for line in env.read_text().splitlines():
        if line.startswith("SHRUTI_DISCORD_BOT_TOKEN="):
            value = line.split("=", 1)[1].strip()
            if value:
                return value
    sys.exit("SHRUTI_DISCORD_BOT_TOKEN is not set in .env.")


def main() -> int:
    req = urllib.request.Request(
        "https://discord.com/api/v10/applications/@me",
        headers={"Authorization": f"Bot {token()}", "User-Agent": "vcordbot-config-check/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            app = json.load(r)
    except urllib.error.HTTPError as exc:
        if exc.code == 401:
            print("REFUSED by Discord: the token is not valid.")
            print("If it was reset in the portal, the old one stopped working the moment")
            print("the new one was shown. Run scripts/set-secret.sh again.")
            return 1
        print(f"Discord returned {exc.code}.")
        return 1
    except Exception as exc:                            # noqa: BLE001
        print(f"Could not reach Discord: {type(exc).__name__}")
        return 1

    print(f"  name            {app.get('name')}")
    print(f"  application id  {app.get('id')}")
    print(f"  bot username    {(app.get('bot') or {}).get('username', '—')}")
    print(f"  in guilds       {app.get('approximate_guild_count', 0)}")
    print(f"  terms / privacy {'set' if app.get('terms_of_service_url') else 'MISSING'}"
          f" / {'set' if app.get('privacy_policy_url') else 'MISSING'}")
    if app.get("interactions_endpoint_url"):
        print(f"  interactions    {app['interactions_endpoint_url']}  <- set!")
    else:
        print("  interactions    not set (correct for a gateway bot)")
    if app.get("role_connections_verification_url"):
        print(f"  linked roles    {app['role_connections_verification_url']}")

    print()
    problems: list[str] = []

    for key, (want, why) in WANT.items():
        got = app.get(key)
        ok = got == want
        print(f"  {'ok  ' if ok else 'FIX '} {key} = {got}")
        if not ok:
            problems.append(f"{key} should be {want} — {why}")

    flags = app.get("flags", 0)
    on = {}
    for bit, (name, state) in FLAGS.items():
        if flags & bit:
            on[name] = state
    print()
    if not on:
        print("  ok   no privileged intents are enabled")
    for name, state in sorted(on.items()):
        if name in UNWANTED_INTENTS:
            print(f"  FIX  {name}: {state}")
            problems.append(f"turn OFF {name} — {UNWANTED_INTENTS[name]}")
        else:
            print(f"  --   {name}: {state}")

    print()
    if problems:
        print("To change:")
        for p in problems:
            print(f"  · {p}")
        return 2
    print("Configured as the plan says.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
