#!/usr/bin/env python3
"""
Make the VAPID pair, once.

**Run this once and keep the output.** Every browser that subscribes binds its
subscription to the public key it saw, so regenerating these unsubscribes
everybody silently — they keep the notification permission and simply stop
receiving anything, which is the worst version of broken.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shruti.core.push import generate_keys        # noqa: E402

private, public = generate_keys()
print("SHRUTI_VAPID_PRIVATE_KEY=" + private)
print("SHRUTI_VAPID_PUBLIC_KEY=" + public)
print("SHRUTI_VAPID_SUBJECT=mailto:business@shrutivtuber.com")
print()
print("Put these in .env. Keep the private key out of the repository, and do")
print("not regenerate them — every existing subscriber would stop receiving")
print("notifications without being told.")
