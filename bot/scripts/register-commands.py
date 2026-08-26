#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""
Tell Discord which commands exist.

A PUT of the whole list rather than one POST per command: PUT is a replace, so
a command deleted from `commands.py` disappears from the picker instead of
lingering and answering "I do not have that command".

    register-commands.py                 globally — up to an hour to propagate
    register-commands.py <guild id>      to one server — instant, for testing

Use the guild form while developing. The global form is for when it is real.
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from vcordbot.commands import COMMANDS                      # noqa: E402


def env(name: str) -> str:
    root = Path(__file__).resolve().parents[2] / ".env"
    if root.is_file():
        for line in root.read_text().splitlines():
            if line.startswith(f"{name}="):
                return line.split("=", 1)[1].strip()
    return ""


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
        url, data=json.dumps(COMMANDS).encode(), method="PUT",
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
