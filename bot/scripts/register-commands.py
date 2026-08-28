#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""
Tell Discord which commands exist.

A PUT of the whole list rather than one POST per command: PUT is a replace, so
a command deleted from `commands.py` disappears from the picker instead of
lingering and answering "I do not have that command".

    register-commands.py                 globally, and clears guild overrides
    register-commands.py <guild id>      to one server — instant, for testing

Use the guild form while developing. The global form is for when it is real.

**A GUILD REGISTRATION SHADOWS THE GLOBAL ONE, SILENTLY.** They are two
separate lists, and where a name appears in both, the guild copy is what that
server's picker shows. That is what makes the guild form useful for testing —
it appears at once, where a global change takes up to an hour — and it is also
a trap with a long fuse: register globally afterwards and the server you tested
in keeps serving whatever it was left holding, for as long as nobody looks.

This bot got caught by exactly that. Three commands were registered to one
server during development, the global list read empty, and the two disagreed
for a fortnight without anything appearing to be wrong.

So the global form CLEARS the guild lists as it goes. Not tidiness: it is what
makes "registered globally" mean the same thing in every server, which is the
only way the sentence is worth printing.
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from vcordbot.commands import for_discord                   # noqa: E402


def env(name: str) -> str:
    root = Path(__file__).resolve().parents[2] / ".env"
    if root.is_file():
        for line in root.read_text().splitlines():
            if line.startswith(f"{name}="):
                return line.split("=", 1)[1].strip()
    return ""


API = "https://discord.com/api/v10"


def call(url: str, token: str, *, method: str = "GET", body=None):
    """One Discord call. The token is never printed, including on failure."""
    req = urllib.request.Request(
        url, method=method,
        data=None if body is None else json.dumps(body).encode(),
        headers={"Authorization": f"Bot {token}",
                 "Content-Type": "application/json",
                 "User-Agent": "vcordbot-register/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r) if r.status != 204 else None


def clear_guild_overrides(app_id: str, token: str) -> None:
    """
    Remove every guild-scoped list, so the global one is what servers see.

    An empty PUT is the removal — the same replace-semantics the whole script
    relies on. A server the bot cannot read is skipped rather than fatal: a
    partial clear still leaves fewer places for the two lists to disagree, and
    refusing to register at all because one server is unreachable would be a
    worse trade.
    """
    try:
        guilds = call(f"{API}/users/@me/guilds", token)
    except urllib.error.HTTPError as exc:
        print(f"  (could not list servers — {exc.code}; guild overrides left alone)")
        return

    for g in guilds:
        gid, name = g["id"], g.get("name", gid)
        try:
            existing = call(f"{API}/applications/{app_id}/guilds/{gid}/commands", token)
            if not existing:
                continue
            call(f"{API}/applications/{app_id}/guilds/{gid}/commands", token,
                 method="PUT", body=[])
            names = ", ".join(f"/{c['name']}" for c in existing)
            print(f"  cleared {len(existing)} shadowing command(s) in {name}: {names}")
        except urllib.error.HTTPError as exc:
            print(f"  (could not clear {name} — {exc.code}; it may still shadow)")


def main() -> int:
    app_id, token = env("SHRUTI_DISCORD_APP_ID"), env("SHRUTI_DISCORD_BOT_TOKEN")
    if not app_id or not token:
        print("SHRUTI_DISCORD_APP_ID or SHRUTI_DISCORD_BOT_TOKEN is missing from .env")
        return 1

    guild = sys.argv[1] if len(sys.argv) > 1 else ""
    url = (f"https://discord.com/api/v10/applications/{app_id}/guilds/{guild}/commands"
           if guild else
           f"https://discord.com/api/v10/applications/{app_id}/commands")

    req = urllib.request.Request(
        url, data=json.dumps(for_discord()).encode(), method="PUT",
        headers={"Authorization": f"Bot {token}", "Content-Type": "application/json",
                 "User-Agent": "vcordbot-register/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            got = json.load(r)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:400]
        print(f"Discord refused with {exc.code}:\n{detail}")
        return 1

    where = f"guild {guild}" if guild else "globally (up to an hour to appear)"
    print(f"Registered {len(got)} command(s) {where}:")
    for c in got:
        print(f"  /{c['name']} — {c['description']}")

    if guild:
        # Said every time, because the shadow is invisible from Discord's own
        # UI and the person who registers here is rarely the one who wonders,
        # weeks later, why one server is answering differently.
        print("\nThis list SHADOWS the global one in that server until it is "
              "cleared.\nRun this with no argument when you are done testing.")
    else:
        print("\nClearing guild lists, so every server sees this one:")
        clear_guild_overrides(app_id, token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
