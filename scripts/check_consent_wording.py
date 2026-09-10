#!/usr/bin/env python3
"""
The consent wording shown to a person must be the wording that gets stored.

The site renders from `frontend/site/src/lib/consents.ts` and the backend files
what `backend/shruti/core/consents.py` says. If those drift, the record says one
thing and the person read another — which is worse than having no record,
because it looks like evidence and is not.

Run in CI. Exits non-zero on any difference.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _find(*candidates: str) -> Path:
    """
    The file, wherever this happens to be running.

    ⚠ On a laptop the tree is `backend/shruti/...`; in the test container
    `shruti` is mounted at `/app/shruti` and there is no `backend/`. Assuming
    one layout made this script exit 2 on a missing file, and the test that
    runs it reported "the consent wording has drifted" — which is a different
    and much more alarming sentence than "I could not find the file".
    """
    for candidate in candidates:
        path = ROOT / candidate
        if path.is_file():
            return path
    return ROOT / candidates[0]


BACKEND = _find("backend/shruti/core/consents.py", "shruti/core/consents.py")
SITE = _find("frontend/site/src/lib/consents.ts")


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def backend_wording(src: str) -> dict[str, str]:
    out = {}
    for m in re.finditer(r'kind="(\w+)".*?wording=\(\s*((?:"[^"]*"\s*)+)\)', src, re.S):
        out[m.group(1)] = norm("".join(re.findall(r'"([^"]*)"', m.group(2))))
    return out


def site_wording(src: str) -> dict[str, str]:
    out = {}
    for m in re.finditer(r'kind:\s*"(\w+)".*?wording:\s*((?:"[^"]*"\s*\+?\s*)+),', src, re.S):
        out[m.group(1)] = norm("".join(re.findall(r'"([^"]*)"', m.group(2))))
    return out


def main() -> int:
    be_src, fe_src = BACKEND.read_text(), SITE.read_text()
    be, fe = backend_wording(be_src), site_wording(fe_src)

    problems = []
    if not be or not fe:
        problems.append("could not parse one of the files — the shapes have changed")

    for kind in sorted(set(be) | set(fe)):
        if be.get(kind) != fe.get(kind):
            problems.append(
                f"{kind}: the wording differs\n"
                f"    backend: {be.get(kind)!r}\n"
                f"    site   : {fe.get(kind)!r}"
            )

    be_v = re.search(r'CONSENT_VERSION = "([^"]+)"', be_src)
    fe_v = re.search(r'CONSENT_VERSION = "([^"]+)"', fe_src)
    if not be_v or not fe_v or be_v.group(1) != fe_v.group(1):
        problems.append(
            f"CONSENT_VERSION differs: backend "
            f"{be_v.group(1) if be_v else '?'} vs site {fe_v.group(1) if fe_v else '?'}"
        )

    if problems:
        print("consent wording has drifted:\n")
        for p in problems:
            print(f"  - {p}")
        print(
            "\nThe record must say what the person actually read. Change both, "
            "and bump CONSENT_VERSION in both."
        )
        return 1

    print(f"consent wording matches across {len(be)} decisions, version {be_v.group(1)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
