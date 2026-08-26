# SPDX-License-Identifier: AGPL-3.0-only
"""
The ephemeris client, and the promises it makes to the layer above.

Every error it raises is shown to a person in a Discord channel, so the
messages are part of the contract rather than debug output.
"""
from __future__ import annotations

import inspect
import re

import pytest

from vcordbot.astro import Astro, AstroError


def test_it_never_imports_discord() -> None:
    """
    The reason the tests above need no token. If this module ever reaches for
    the gateway, the split that makes any of this testable has gone.
    """
    import ast
    import vcordbot.astro as m

    # Strip docstrings and comments before looking. This module's own prose
    # explains why it must not import the gateway, and the word appears there
    # — which is exactly how this test failed the first time it was run. It is
    # the third time in this project that a comment has tripped its own check.
    tree = ast.parse(inspect.getsource(m))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)) and ast.get_docstring(node):
            node.body = node.body[1:]
    code = ast.unparse(tree)
    assert "discord" not in code.lower()


def test_empty_parameters_are_dropped_not_sent_blank() -> None:
    """
    `place=` reads as "a place called nothing" to some endpoints rather than
    "no place given", and the difference is a wrong answer instead of a
    default one.
    """
    src = inspect.getsource(Astro._get)
    assert 'v not in (None, "")' in src


def test_every_failure_message_is_safe_to_show_a_stranger() -> None:
    """
    No URLs, no status codes, no stack. Somebody in another person's Discord
    should not learn our internal hostnames because the ephemeris hiccupped.
    """
    src = inspect.getsource(Astro._get)
    for message in re.findall(r'AstroError\("([^"]+)"\)', src):
        assert "http" not in message.lower()
        assert not re.search(r"\b\d{3}\b", message)
        assert message[0].isupper() and message.endswith(".")


def test_the_timeout_leaves_room_for_discords_deadline() -> None:
    """Discord wants an interaction acknowledged within three seconds; anything
    slower than that has to be deferred, so the client must not sit for 30."""
    from vcordbot.astro import TIMEOUT
    assert TIMEOUT <= 10


def test_error_is_a_runtime_error() -> None:
    assert issubclass(AstroError, RuntimeError)
