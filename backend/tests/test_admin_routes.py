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


def _routes(which=router):
    out = []
    for route in which.routes:
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


def test_no_router_anywhere_shadows_one_of_its_own_routes():
    """
    The same rule, applied to every router rather than only to the admin one.

    It has bitten three times in this file's history and each time the fix was
    local. `/api/classes` was where it would have bitten next: a reader route
    of `/{slug}/lessons/{id}` matches `/admin/lessons/{id}` exactly, and only
    the accident that one was GET and the other PATCH kept them apart. The
    reader routes are declared last there now, so it does not depend on that.
    """
    # ⚠ EVERY router with a catch-all, not a list somebody remembered to add
    # to. The practice room grew `/admin/reports` under an existing
    # `/{work_id}` while this list did not name it, and a guard that only
    # covers the routers it was written for is a guard that stops covering the
    # code as the code grows.
    import importlib
    import pkgutil

    import shruti.api.routes as routes_pkg

    modules = []
    for info in pkgutil.iter_modules(routes_pkg.__path__):
        module = importlib.import_module(f"shruti.api.routes.{info.name}")
        if hasattr(module, "router"):
            modules.append(module)
    assert len(modules) >= 8, "the router sweep found almost nothing"

    def segments(path: str) -> list[str]:
        return [p for p in path.strip("/").split("/") if p]

    def shadows(earlier: str, later: str) -> bool:
        a, b = segments(earlier), segments(later)
        if len(a) != len(b):
            return False
        return all(x.startswith("{") or x == y for x, y in zip(a, b))

    for module in modules:
        routes = _routes(module.router)
        for i, (method, path) in enumerate(routes):
            for earlier_method, earlier_path in routes[:i]:
                if earlier_method != method or earlier_path == path:
                    continue
                assert not shadows(earlier_path, path), (
                    f"in {module.__name__}: {method} {path} is unreachable — "
                    f"{earlier_method} {earlier_path} is declared first and "
                    f"matches it."
                )


def test_the_class_admin_is_declared_before_the_slug_that_would_eat_it():
    """
    Named separately from the general rule, because the general rule only
    catches it once somebody adds the method that collides — by which point
    the endpoint is written and appears to do nothing.
    """
    from shruti.api.routes import classes

    paths = [route.path for route in classes.router.routes if getattr(route, "methods", None)]
    last_admin = max(i for i, p in enumerate(paths) if "/admin/" in p)
    first_slug = min(i for i, p in enumerate(paths) if "{slug}" in p)
    assert last_admin < first_slug, (
        "a /{slug} route is declared before the admin routes, so "
        "/api/classes/admin/... will be read as a course called 'admin'"
    )
