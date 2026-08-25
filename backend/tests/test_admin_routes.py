# SPDX-License-Identifier: AGPL-3.0-only
"""
Route ordering in the admin router.

FastAPI matches in declaration order, so a catch-all like `/{kind}` swallows
every specific path declared after it. This has bitten three times in this
codebase — POST /media, then GET /claim, then GET /media and GET /settings
together — and each time the symptom was silence rather than an error: the
media library rendered as an empty library, and the imprint form rendered as
blank fields. Both are exactly what an unused feature looks like, which is why
they survived so long.

Twice the fix was to move one route up, and twice that left the trap armed for
the next person. This test is the fix that does not depend on anybody
remembering.
"""
from __future__ import annotations

from shruti.api.routes.admin import router


def _routes():
    out = []
    for route in router.routes:
        for method in sorted(getattr(route, "methods", []) or []):
            if method in {"HEAD", "OPTIONS"}:
                continue
            out.append((method, route.path))
    return out


def test_no_specific_route_is_declared_after_its_catch_all() -> None:
    """
    The real rule, checked directly: for every route, no EARLIER route with the
    same method may shadow it.

    A path shadows another when it has the same number of segments and each of
    its segments either matches exactly or is a parameter.
    """
    def segments(path: str) -> list[str]:
        return [p for p in path.strip("/").split("/") if p]

    def shadows(earlier: str, later: str) -> bool:
        a, b = segments(earlier), segments(later)
        if len(a) != len(b):
            return False
        for x, y in zip(a, b):
            if x.startswith("{"):
                continue              # a parameter eats a literal
            if x != y:
                return False
        return True

    routes = _routes()
    for i, (method, path) in enumerate(routes):
        for earlier_method, earlier_path in routes[:i]:
            if earlier_method != method or earlier_path == path:
                continue
            assert not shadows(earlier_path, path), (
                f"{method} {path} is unreachable: {earlier_method} {earlier_path} "
                f"is declared first and matches it. Move it above the catch-alls."
            )


def test_the_routes_that_have_actually_been_shadowed_are_reachable() -> None:
    """Named explicitly, because these three are the ones that broke."""
    routes = _routes()
    for method, path in (("GET", "/api/admin/media"), ("POST", "/api/admin/media"),
                         ("GET", "/api/admin/settings"), ("GET", "/api/admin/claim")):
        assert (method, path) in routes, f"{method} {path} is missing entirely"

    generic = [i for i, (_m, p) in enumerate(routes) if "{kind}" in p]
    specific = [i for i, (_m, p) in enumerate(routes) if "{kind}" not in p]
    assert min(generic) > max(specific), (
        "a specific route is declared after a /{kind} catch-all and is unreachable"
    )
