# SPDX-License-Identifier: AGPL-3.0-only
"""
Editable strings, and the one rule that makes them safe.

Page blocks cover sections. Most of the words on this site are not sections —
they are the line under a form, the label on a button, the sentence explaining
why a field is optional. About six thousand of them lived in templates, on a
site whose whole premise is that she edits it herself.
"""
from __future__ import annotations

import re
from pathlib import Path


def _src() -> Path:
    here = Path(__file__).resolve()
    for base in (here.parents[1], here.parents[2]):
        if (base / "frontend" / "site" / "src").is_dir():
            return base / "frontend" / "site" / "src"
    return here.parents[1] / "frontend" / "site" / "src"


SRC = _src()
BACKEND = Path(__file__).resolve().parents[1]
ROOT_SCRIPTS = (Path('/app/scripts') if Path('/app/scripts/convert-to-copy.py').exists()
                else Path(__file__).resolve().parents[2] / 'scripts')


def code_of(path: Path) -> str:
    """
    A file's source with its prose removed.

    Same helper as test_overlays, same reason: this test asserts the component
    never uses set:html, and the comment explaining WHY it never uses set:html
    tripped it. Rewording the comment to dodge the grep would delete the
    explanation to protect the test, which is precisely backwards.
    """
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"\{/\*.*?\*/\}", "", text, flags=re.S)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"(?<![:/])//[^\n]*", "", text)


def test_the_default_lives_in_the_template_and_always_renders() -> None:
    """
    The rule the whole design rests on. A row only ever OVERRIDES the words the
    page was written with, so an empty table renders a complete site, a page
    nobody has seeded reads exactly as written, and a string she has never
    touched cannot vanish because a query failed.
    """
    lib = (SRC / "lib" / "copy.ts").read_text(encoding="utf-8")
    assert "key in overrides ? overrides[key] : fallback" in lib

    # And the fetch failing must leave the written words standing, not throw.
    assert "catch" in lib
    assert "let overrides" in lib


def test_a_cleared_string_stays_cleared() -> None:
    """
    `in` rather than truthiness. A row set to an empty string is a deliberate
    blank — she deleted the sentence — and falling back to the default there
    would make a line impossible to remove. Deleting the ROW is how you go
    back, and the admin offers exactly that.
    """
    lib = (SRC / "lib" / "copy.ts").read_text(encoding="utf-8")
    assert "key in overrides" in lib
    assert "overrides[key] ||" not in lib, "an empty override falls back"


def test_seeding_never_overwrites_her_words() -> None:
    """
    The seeder reads the templates; the templates are never told what to say.
    It records the label, the default and the position — and for a row that
    already exists it updates only those.
    """
    import inspect

    from shruti.api.routes.admin import seed_copy

    src = inspect.getsource(seed_copy)
    body = src.split("row.label = ")[1]
    assert "row.value" not in body, "seeding writes over a value she has edited"


def test_the_copy_routes_sit_above_the_generic_collection_routes() -> None:
    """
    `/{kind}` matches any single segment, so registered after it "copy" is read
    as a collection name and answered with "unknown collection" — which is
    exactly what happened, and looked like the routes not existing at all.
    """
    admin = (BACKEND / "shruti" / "api" / "routes" / "admin.py").read_text(encoding="utf-8")
    assert admin.index('@router.post("/copy/seed")') < admin.index('@router.get("/{kind}")')
    assert admin.index('@router.get("/copy")') < admin.index('@router.get("/{kind}")')


def test_every_seeded_key_is_unique_per_page() -> None:
    """
    Without the constraint a double seed gives a page two answers for one key,
    and the winner is whichever the query happens to return first.
    """
    mig = next((BACKEND / "alembic" / "versions").glob("*_copy.py"))
    assert "uq_copy_page_key" in mig.read_text(encoding="utf-8")


def test_the_admin_groups_words_by_page() -> None:
    """
    Her words: "page blocks are not usable as they are just all thrown on the
    page blocks page with no way to see to which page they actually belong."
    Both screens group by page now, and both offer a filter.
    """
    for name in ("copy.astro", "blocks.astro"):
        page = (SRC / "pages" / "admin" / name).read_text(encoding="utf-8")
        assert "page-filter" in page, f"{name} has no page filter"
        assert "page-name" in page, f"{name} does not head its groups with the page"


def test_a_retrofitted_page_declares_its_own_page_name() -> None:
    """
    `copy("support")` on /support. A page reading another page's strings would
    silently show the wrong words, and nothing would look broken.
    """
    pages = SRC / "pages"
    for f in pages.rglob("*.astro"):
        text = f.read_text(encoding="utf-8")
        m = re.search(r'copy\(\s*["\']([^"\']+)["\']\s*\)', text)
        if not m:
            continue
        declared = m.group(1)
        rel = str(f.relative_to(pages)).removesuffix(".astro")
        if rel.endswith("/index"):
            rel = rel.removesuffix("/index")
        expected = "home" if rel == "index" else rel
        assert declared == expected, (
            f"{f.name} asks for copy(\"{declared}\") but is /{expected}")


def test_inline_copy_renders_only_four_tags() -> None:
    """
    A sentence with a link in it is one string she edits, not two fragments —
    but the component that renders it must not become a hole. It builds the
    nodes itself rather than setting HTML, so the only tags that can come out
    are the four it knows.
    """
    comp = code_of(SRC / "components" / "content" / "Copy.astro")
    assert "set:html" not in comp, "arbitrary markup can reach the page"
    # Text nodes are escaped, not interpolated raw.
    assert "set:text" in comp


def test_bold_is_not_read_as_two_italics() -> None:
    comp = code_of(SRC / "components" / "content" / "Copy.astro")
    tok = comp[comp.index("const TOKEN"):comp.index("function parse")]
    assert tok.index(r"\*\*") < tok.index(r"|\*(["), (
        "the italic pattern is tried before the bold one")


def test_an_untouched_string_follows_the_template() -> None:
    """
    If she has never edited a string, its value is still exactly the default it
    was seeded with — so when the template's words change, the value follows.

    Without this, rewriting a line in a template silently does nothing: the row
    seeded with the old words wins, the page shows the old words, and nothing
    says why. Found exactly that way, on /press.

    The moment she edits it the two diverge and seeding stops touching it.
    """
    import inspect

    from shruti.api.routes.admin import seed_copy

    src = inspect.getsource(seed_copy)
    assert "row.value == row.default_value and row.value != item.default" in src
    # And it must still never overwrite a value she HAS changed.
    guarded = src.split("if row.value == row.default_value")[1].split("\n\n")[0]
    assert "row.value = item.default" in guarded


def test_the_helper_is_not_called_t() -> None:
    """
    `t` is the likeliest identifier in the codebase to be a map or filter
    callback parameter, and a shadowed helper fails at RUNTIME —
    "t2 is not a function", on one page, in production, long after the change
    looked fine everywhere else.

    It happened: /support has `TIERS.map((t) => ...)` and a converted string
    landed inside it. The whole page 500'd while every other page was fine.

    So the helper is `say`, which nothing shadows.
    """
    pages = SRC / "pages"
    for f in list(pages.rglob("*.astro")) + list((SRC / "components").rglob("*.astro")):
        if "admin" in str(f) or "overlay" in str(f):
            continue
        text = f.read_text(encoding="utf-8")
        assert "const t = await copy(" not in text, f"{f.name} names the helper `t`"
        assert not re.search(r'\bt\(\s*["\'`][\w.]+["\'`]\s*,', text), (
            f"{f.name} still calls t(...) — it will break if `t` is shadowed")


def test_a_component_declares_a_shared_namespace() -> None:
    """
    A component does not know what page it is on, and its words are shared by
    every page that shows it — so it gets a namespace of its own, and the admin
    says out loud that editing one changes it everywhere.
    """
    comps = [f for f in (SRC / "components").rglob("*.astro")
             if "await copy(" in f.read_text(encoding="utf-8")]
    assert comps, "no component uses the copy helper"
    for f in comps:
        m = re.search(r'copy\(\s*["\']([^"\']+)["\']', f.read_text(encoding="utf-8"))
        assert m and m.group(1).startswith("component:"), (
            f"{f.name} asks for a page namespace, not a component one")

    admin = (SRC / "pages" / "admin" / "copy.astro").read_text(encoding="utf-8")
    assert "shared — changing this changes it on every page" in admin


def test_the_preview_reads_the_page_rather_than_marking_it() -> None:
    """
    The preview matches on the text the site already renders, and adds nothing
    to it. Marking every string with a data attribute would make the preview
    structurally different from what a reader gets — which is the one thing a
    preview must never be.

    The iframe is same-origin, so the admin can read its DOM directly.
    """
    prev = code_of(SRC / "pages" / "admin" / "preview.astro")
    assert "contentDocument" in prev, "the preview cannot read the page"
    assert "data-copy" not in prev, "the site is being instrumented for preview"
    # Both directions: field -> page, and page -> field.
    assert "markInPage" in prev
    assert "wireFrame" in prev


def test_the_preview_collapses_whitespace_before_matching() -> None:
    """
    The source wraps its lines; the browser does not. An exact match would fail
    on almost every paragraph on the site.
    """
    prev = code_of(SRC / "pages" / "admin" / "preview.astro")
    assert 'replace(/\\s+/g, " ")' in prev


def test_the_preview_keeps_its_place_across_a_save() -> None:
    """
    Reloading the iframe to the top on every edit is what makes a preview
    useless for anything below the fold.
    """
    prev = code_of(SRC / "pages" / "admin" / "preview.astro")
    assert "scrollY" in prev and "scrollTo" in prev


def test_components_are_not_offered_for_page_preview() -> None:
    """
    A component has no page of its own. Its words are shared by every page that
    shows it, so it stays on the Words screen where that is said out loud.
    """
    prev = code_of(SRC / "pages" / "admin" / "preview.astro")
    assert "isComponent" in prev
    assert ".filter((p) => !isComponent(p))" in prev


def test_the_preview_shows_page_blocks_not_only_strings() -> None:
    """
    The bug she found: on /about the visible prose is three blocks totalling
    1,500 characters, and the panel showed nine strings — of which the first
    two were the <title> and the meta description, neither on the page at all.
    "The areas to edit don't actually match up to what is on the page." They
    did not, because most of the page was not in the panel.
    """
    prev = code_of(SRC / "pages" / "admin" / "preview.astro")
    assert "/api/admin/sections" in prev, "the preview cannot see page blocks"
    assert "BLOCK_FIELDS" in prev
    # And a block field saves to its own route, not the copy one.
    assert "sections/${blockId}" in prev


def test_the_panel_is_ordered_by_the_page_not_the_source() -> None:
    """
    The stored position is SOURCE order, which is not screen order: a page's
    title and meta description are declared first and rendered nowhere. The
    panel asks the rendered document instead, and anything it cannot find is
    moved to the end under a heading saying so — rather than sitting at the top
    pretending to be the first thing a reader sees.
    """
    prev = code_of(SRC / "pages" / "admin" / "preview.astro")
    assert "reorderByPage" in prev
    assert "getBoundingClientRect" in prev
    assert "not visible on this page" in prev


def test_reordering_keeps_a_block_together() -> None:
    """
    `:scope >` matters. Without it the selector also matches the fields INSIDE
    a block and hoists them out, scattering its eyebrow, heading and body down
    the panel as loose strings — worse than the ordering it was fixing.
    """
    prev = code_of(SRC / "pages" / "admin" / "preview.astro")
    assert ":scope > .str, :scope > .blk" in prev


def test_partial_matching_is_one_directional() -> None:
    """
    A page node must CONTAIN the whole string. The reverse — a short node
    inside a longer string — matches almost anything, and put the page <title>
    halfway down the page.
    """
    prev = code_of(SRC / "pages" / "admin" / "preview.astro")
    assert "have.includes(want)" in prev
    assert "want.includes(have)" not in prev


def test_prose_attributes_were_found_by_scanning_not_guessing() -> None:
    """
    The first list was imagined, and the omission cost a real bug: `subtitle`
    was missing, so the home page's hero line stayed hardcoded while an
    IDENTICAL meta description sat editable in the panel beside it. Editing the
    field changed the meta tag, the page kept showing the hardcoded line
    ("changing back to what it was before"), and the field then vanished into
    "not visible" because its new text matched nothing on the page ("the box is
    gone"). Both symptoms, one missing attribute name.
    """
    conv = (ROOT_SCRIPTS / "convert-to-copy.py").read_text(encoding="utf-8")
    for attr in ("subtitle", "greeting", "why", "legend", "explanation", "byline"):
        assert f'"{attr}"' in conv, f"{attr}= holds prose and is not converted"


def test_greek_capitals_are_told_they_are_greek() -> None:
    """
    Greek in capitals does not take the tonos. Browsers get that right on their
    own — but only when the run is marked as Greek, and this document is
    lang="en". Measured before and after:

        no lang     ΚΑΛΏΣ ΉΡΘΑΤΕ     wrong
        lang="el"   ΚΑΛΩΣ ΗΡΘΑΤΕ     right, and the dialytika survives

    Stripping the accents in the copy itself would be the wrong fix: it loses
    the dialytika rule, and the words could no longer be edited in their
    proper form.
    """
    comp = code_of(SRC / "components" / "content" / "Scripts.astro")
    assert '"el"' in comp and '"hi"' in comp
    assert "lang={r.lang}" in comp

    hero = code_of(SRC / "components" / "brand" / "Hero.astro")
    assert "<Scripts text={greeting}" in hero, "the greeting is not tagged"


def test_a_block_is_placed_by_its_most_distinctive_field() -> None:
    """
    Not by the minimum across all of them. The home page's support block has a
    link label of "Support the work", which is also a header nav item at the
    very top — so taking the minimum put a block that lives halfway down the
    page first in the panel.

    Order of preference: an exact heading match, then the body's first
    paragraph, then the title, then the eyebrow, and the link label last
    because it is the likeliest to also be navigation.
    """
    prev = code_of(SRC / "pages" / "admin" / "preview.astro")
    assert "findHeadingIn" in prev
    body = prev[prev.index("const tries"):prev.index("offsets.set(item, top)")]
    assert body.index("findHeadingIn") < body.index("link_label"), (
        "a link label is preferred over a heading")


def test_a_short_heading_can_still_be_found() -> None:
    """
    The general matcher refuses anything under eight characters, rightly —
    six characters of body text collide with everything. But /about's first
    block is titled "Shruti", and as an <h2> that is unambiguous. Raising the
    general minimum without this pushed every block on that page into
    "not visible".
    """
    prev = code_of(SRC / "pages" / "admin" / "preview.astro")
    head = prev[prev.index("function findHeadingIn"):]
    assert "want.length < 3" in head[:400], "headings inherit the long minimum"
    assert 'querySelectorAll<HTMLElement>("h1,h2,h3,h4,h5,h6")' in prev


def test_a_block_body_is_matched_by_its_first_paragraph() -> None:
    """
    A body is markdown and renders as several paragraphs, so no single text
    node holds all of it — matching the whole thing always fails.
    """
    prev = code_of(SRC / "pages" / "admin" / "preview.astro")
    assert "firstPara" in prev


def test_markdown_is_normalised_on_both_sides_before_matching() -> None:
    """
    The page shows rendered markdown; a block stores the source. Comparing
    "**Shruti** — Shruti Swara" against "Shruti — Shruti Swara" fails on the
    asterisks alone.

    Whitespace collapsing is not enough on its own. A string routed through
    <Copy> is stored as markdown and RENDERED as several nodes — a <strong>
    and the text either side of it — so the markers have to come off the
    stored value before it is compared, and the comparison has to be able to
    look at a whole element rather than a single text node. Nineteen
    paragraphs were made editable and became invisible to the panel in the
    same commit for want of exactly this.
    """
    prev = code_of(SRC / "pages" / "admin" / "preview.astro")
    assert "const plain" in prev
    assert "plain(t.data)" in prev
    assert "const spoken" in prev, "markdown markers must come off the value"
    assert "plain(spoken(value))" in prev
    assert "el.textContent" in prev, (
        "a <Copy> sentence spans children, so whole elements have to be tried"
    )


def test_the_copy_helper_never_appears_inside_a_client_script() -> None:
    """
    `say()` is server-side. Inside a <script> it is not called — it is TEXT.

    Three pages were shipping `{say("text.3", "No place of that name found…")}`
    verbatim into the place-search dropdown, because a page's client script
    builds markup in a JS string and a text-node rewrite matched happily inside
    it. Nothing catches that: it builds, it typechecks, the page returns 200,
    and the wrong thing only appears when a visitor searches for a place that
    does not exist.

    Only the BRACED form is a fault. A bare `say(a, b)` inside a script is a
    local helper — NotifyButton, WheelStepper and MediaField each define one —
    and rewriting those produced invalid JavaScript the first time this was
    cleaned up.
    """
    import re as _re

    # The WHOLE interpolation, closing brace included. Matching only the
    # opening `{` catches a JavaScript block brace sitting above a local call —
    #
    #     if (blocked) {
    #       say("Notifications are blocked for this site.", "…");
    #
    # — which is not a fault at all. This checker made exactly that mistake
    # first, and so did the tool that cleaned the real ones up, which rewrote
    # those local calls into invalid JavaScript.
    braced = _re.compile(r'\{\s*say\([^()]*\)\s*\}')
    offenders = []
    for f in sorted(SRC.rglob("*.astro")):
        text = f.read_text(encoding="utf-8")
        for block in _re.finditer(r"<script[\s>].*?</script>", text, _re.S | _re.I):
            if braced.search(block.group(0)):
                offenders.append(f.relative_to(SRC))
                break
    assert not offenders, (
        "the copy helper is inside client code and will render literally: "
        f"{offenders}"
    )


def test_no_prose_is_stranded_around_inline_markup() -> None:
    """
    A sentence with a bold run or a link in it must be ONE editable string.

    The failure she found: on /contact the bold half was editable and the two
    runs of prose around it were not. The sentence looks editable, mostly is
    not, and the panel offers a fragment — "Nothing appears until she has
    approved it" — with no way to reach the words on either side of it.

    Splitting is not the fix either. Three boxes for one sentence is a worse
    editing experience than none: she cannot read the sentence, and moving the
    bold means retyping both halves. `Copy` renders inline markdown from a
    single string, which is what these are converted to.

    Checks the TEMPLATE, not the rendered page, because the rendered page looks
    completely normal either way.
    """
    import re as _re

    inline = r"(?:strong|em|b|i|code|a|abbr)"
    prose = _re.compile(r"^[A-Za-z][A-Za-z0-9 ,.;:'’—–\-()!?]{11,}$")

    def outside_braces(text: str) -> str:
        out, depth = [], 0
        for ch in text:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth = max(0, depth - 1)
            elif depth == 0:
                out.append(ch)
        return "".join(out)

    offenders: list[str] = []
    for f in sorted(SRC.rglob("*.astro")):
        if "/admin/" in str(f) or "/overlay/" in str(f):
            continue
        text = f.read_text(encoding="utf-8")
        if text.startswith("---"):
            end = text.find("---", 3)
            if end > 0:
                text = text[end + 3:]
        text = _re.sub(r"<script[\s>].*?</script>", " ", text, flags=_re.S | _re.I)
        text = _re.sub(r"<style[\s>].*?</style>", " ", text, flags=_re.S | _re.I)

        for block in _re.finditer(r"<(p|li|h[1-6])\b[^>]*>(.*?)</\1>", text, _re.S):
            inner = block.group(2)
            if not _re.search(rf"<{inline}\b", inner):
                continue
            bare = _re.sub(r"<[^>]*>", "\x00", outside_braces(inner))
            for run in bare.split("\x00"):
                cleaned = _re.sub(r"\s+", " ", run).strip()
                if prose.match(cleaned) and " " in cleaned:
                    offenders.append(f"{f.relative_to(SRC)}: {cleaned[:56]!r}")

    assert not offenders, (
        "prose stranded beside inline markup — wrap the whole sentence in "
        "<Copy text={say(...)} /> with the emphasis as markdown:\n  "
        + "\n  ".join(offenders[:8])
    )


def test_every_visible_string_is_editable() -> None:
    """
    The sweep that should have existed three rounds ago.

    Each earlier check named the element types it looked at — first leaf
    elements only, then p/li/h*. Naming them is guessing, and the guess was
    wrong every time: an <option> label, a legend inside a <span>, a sentence
    in a <blockquote>. She found each of those, one screenshot at a time.

    So this names nothing. It removes the frontmatter, the client scripts, the
    styles, the comments and every JSX expression — `say(...)` calls included,
    since those ARE editable — and whatever text survives is text a reader sees
    and nobody can change.

    ⚠ The frontmatter fence is `---` AT THE START OF A LINE. Searching for the
    bare string cuts at the first horizontal rule inside a doc comment and then
    reports that comment's prose as visible, which sent this hunting three
    strings no reader will ever see.
    """
    import re as _re

    def strip_expressions(text: str) -> str:
        """
        Remove JSX expressions, ignoring braces inside string literals.

        A `say("…", "… {sign} …")` default carries braces of its own, and
        counting those as expression delimiters unbalances everything after
        them — which reported five fragments of perfectly editable sentences
        as uneditable text.
        """
        out, depth, quote = [], 0, ""
        prev = ""
        for ch in text:
            if quote:
                if ch == quote and prev != "\\":
                    quote = ""
            # Quotes only delimit a string INSIDE an expression. At depth zero
            # an apostrophe is prose — "don't" — and treating it as an opening
            # quote swallows everything up to the next one, braces included,
            # which desynchronises the rest of the file and reports fragments
            # of perfectly editable sentences as uneditable.
            elif depth > 0 and ch in "\"'`":
                quote = ch
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth = max(0, depth - 1)
            elif depth == 0:
                out.append(ch)
            prev = ch
        return "".join(out)

    prose = _re.compile(r"[a-z]{3}")
    junk = _re.compile(r"^(&[a-z]+;|[\s·—–|/,.:;()\[\]{}<>+\-*&%$#@!?\"'`~^=]*)$")

    offenders: list[str] = []
    for f in sorted(SRC.rglob("*.astro")):
        # The admin is hers to read, not her audience's.
        if "/admin/" in str(f) or "/overlay/" in str(f) or f.name == "AdminLayout.astro":
            continue
        text = f.read_text(encoding="utf-8")
        if text.startswith("---"):
            fence = _re.search(r"^---\s*$", text[3:], _re.M)
            if fence:
                text = text[3 + fence.end():]
        text = _re.sub(r"<script[\s>].*?</script>", " ", text, flags=_re.S | _re.I)
        text = _re.sub(r"<style[\s>].*?</style>", " ", text, flags=_re.S | _re.I)
        text = _re.sub(r"\{/\*.*?\*/\}", " ", text, flags=_re.S)
        text = strip_expressions(text)
        text = _re.sub(r"<[^>]*>", "\x00", text)
        for run in text.split("\x00"):
            run = _re.sub(r"\s+", " ", run).strip()
            if len(run) < 3 or junk.match(run) or not prose.search(run):
                continue
            offenders.append(f"{f.relative_to(SRC)}: {run[:60]!r}")

    assert not offenders, (
        f"{len(offenders)} strings a reader sees and nobody can edit — route "
        "each through say(), or through <Copy> if it sits beside inline "
        "markup:\n  " + "\n  ".join(offenders[:12])
    )


def test_the_helper_is_never_inside_a_template_literal() -> None:
    """
    `{say(...)}` inside a JavaScript template literal is four characters and a
    function name, not a call.

    Two pages were shipping it verbatim: /tools built a paragraph as a string
    for `<Prose html=...>`, and /tools/events showed an embed snippet in a
    textarea. Both rendered the literal text of the call to a reader, and
    neither the build nor a typecheck says a word.

    ⚠ Backticks are NOT paired off globally. A regex character class holding a
    backtick, or a say() default quoting one, leaves an odd count — and the
    first version of this test skipped any such file rather than guess. That
    was worse than guessing: /tools/index.astro is one of those files, so the
    check was inert on the very page the bug was found. It went green against
    a deliberately reintroduced fault.

    Instead: find each place an expression OPENS with a template literal —
    `={`` or `>{`` — and scan forward to that literal's own closing backtick.
    Starting from a known opening needs no pairing at all.
    """
    import re as _re

    offenders: list[str] = []
    for f in sorted(SRC.rglob("*.astro")):
        text = _re.sub(r"\{/\*.*?\*/\}", " ",
                       f.read_text(encoding="utf-8"), flags=_re.S)
        text = _re.sub(r"/\*.*?\*/", " ", text, flags=_re.S)
        text = _re.sub(r"(?m)^\s*//.*$", " ", text)

        for opening in _re.finditer(r"[=>]\s*\{\s*`", text):
            i = opening.end()
            # Forward to this literal's closing backtick, honouring escapes.
            j = i
            while j < len(text):
                if text[j] == "\\":
                    j += 2
                    continue
                if text[j] == "`":
                    break
                j += 1
            body = text[i:j]
            if _re.search(r"(?<!\$)\{\s*say\(", body):
                offenders.append(f"{f.relative_to(SRC)}: {body[:70]!r}")

    assert not offenders, (
        "the copy helper is inside a template literal and will render as its "
        "own source; use ${say(...)}:\n  " + "\n  ".join(offenders[:6])
    )


def test_the_seeder_reads_a_call_with_a_trailing_comma() -> None:
    """
    A dangling comma must not make a string vanish.

    `say(\n  "key",\n  "a long default",\n)` is what a formatter produces when
    it wraps a long call across lines, and the seeder's pattern originally
    required the closing paren to follow the default directly. Without the
    comma allowed, the call simply does not match: the string is never
    registered, the page renders its default perfectly, and the admin has no
    row for it. No error anywhere.

    Found when a paragraph on /tools stayed truncated after its template had
    already been fixed — the fix could not reach the database because the
    database had never heard of the key.
    """
    import re as _re

    seeder = (ROOT_SCRIPTS / "seed-copy.mjs").read_text(encoding="utf-8")
    line = next(
        l for l in seeder.splitlines() if l.startswith("const CALL")
    )
    assert ",?" in line, "a trailing comma must be tolerated"

    # And prove it against the shape itself rather than trusting the read.
    pattern = _re.compile(
        r"""\bsay\(\s*(["'`])([^"'`]+?)\1\s*,\s*(["'`])([\s\S]*?)\3\s*"""
        r"""(?:,\s*(["'`])([^"'`]*?)\5\s*)?,?\s*\)"""
    )
    wrapped = 'say(\n  "text.9",\n  "A default long enough to wrap.",\n)'
    match = pattern.search(wrapped)
    assert match is not None, "the wrapped form must match"
    assert match.group(4) == "A default long enough to wrap."


def test_no_astro_comment_opens_an_expression_that_returns_an_element() -> None:
    """
    `{/* … */}` is not a comment everywhere it looks like one.

    Inside an arrow body that returns an element —

        {LIST.map((x) => (
          {/* why */}
          <a …>{x}</a>
        ))}

    — it is not in a position that allows a comment, and Astro does not fail.
    In unsubscribed.astro it broke the page outright; on the horoscope desk it
    silently dropped the element's ATTRIBUTES, so twelve links rendered
    perfectly and none of them counted. `astro check` reported nothing either
    time.

    Made twice by me, ten commits apart, which is what makes it worth a test
    rather than a resolution to be careful.
    """
    import re as _re

    # An opening `(` that begins a returned element, then a comment before any
    # element starts. `=> (` and `&& (` are the two forms that carry one.
    opener = _re.compile(r"(?:=>|&&|\?|:)\s*\(\s*\{\s*/\*", _re.S)

    offenders: list[str] = []
    for f in sorted(SRC.rglob("*.astro")):
        text = f.read_text(encoding="utf-8")
        for m in opener.finditer(text):
            line = text[: m.start()].count("\n") + 1
            offenders.append(f"{f.relative_to(SRC)}:{line}")

    assert not offenders, (
        "an Astro comment cannot open an expression that returns an element — "
        "it is dropped along with the element's attributes, silently. Move it "
        f"above the expression:\n  " + "\n  ".join(offenders[:8])
    )
