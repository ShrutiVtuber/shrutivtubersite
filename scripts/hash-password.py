#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""
Print an Argon2 hash for SHRUTI_ADMIN_PASSWORD_HASH.

    docker compose run --rm backend python /app/../scripts/hash-password.py
    # or, with argon2-cffi available locally:
    python scripts/hash-password.py

Reads the password from a prompt, never from an argument — an argument lands in
shell history and in the process list, where anyone on the box can read it.
"""
import getpass
import sys

try:
    from argon2 import PasswordHasher
except ImportError:
    sys.exit("argon2-cffi is not installed. Run this inside the backend image.")

a = getpass.getpass("password: ")
b = getpass.getpass("again: ")
if a != b:
    sys.exit("they did not match")
if len(a) < 12:
    sys.exit("use at least 12 characters — this is the only thing guarding the admin")
print(PasswordHasher().hash(a))
