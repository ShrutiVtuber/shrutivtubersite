"""
Route a file's literal prose through the copy helper.

Handles what the first version missed, which was most of it:

  - **Attribute prose.** `title="..."`, `placeholder="..."`, `alt="..."` are
    read by people just as much as text between tags.
  - **Components.** They were never touched. A component does not know what
    page it is on, so its strings live under a namespace of their own —
    `component:SubscribeBlock` — which is also the correct behaviour: she
    edits the subscribe wording once and it changes on every page that shows
    it.
  - **Second passes.** A file converted once still has prose the first pass
    could not take.

Still conservative. Anything holding an expression, a component, or markup it
cannot represent is left exactly as written and reported, because a broken page
is worse than an uneditable one.
"""
import re, sys, pathlib

# Attributes whose value a person reads on the page.
# Guessed at first, and the guess cost a bug: `subtitle` was missing, so the
# home page's hero line stayed hardcoded while an identical meta description
# sat in the panel next to it. Editing the field changed the meta tag, the page
# kept showing the hardcoded line, and the field then vanished into "not
# visible" because its new text matched nothing. Both of her symptoms, one
# omission.
#
# So this list was rebuilt by SCANNING for attributes that actually hold
# sentences, rather than by imagining which ones might.
PROSE_ATTRS = ("title", "label", "body", "lede", "eyebrow", "placeholder",
               "alt", "aria-label", "description", "cta", "summary", "help",
               "note", "hint", "caption", "ruleLabel",
               "subtitle", "greeting", "why", "legend", "explanation",
               "wording", "byline", "undefinedReason", "emptyMonthNote",
               "rule", "ogImageAlt", "content")

def slug(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:24] or "text"

def key_for(section, used):
    """
    Keyed by the section it sits under, numbered in order — never by its own
    words. A key derived from the text stops describing it the moment she
    rewrites the text, which is the whole point of the table.
    """
    base = section or "text"
    n = 1
    while f"{base}.{n}" in used:
        n += 1
    key = f"{base}.{n}"
    used.add(key)
    return key

def esc(s):
    return " ".join(s.replace("\\", "\\\\").replace('"', '\\"').split())

def is_prose(t):
    """
    A sentence, not code that happens to sit between two string literals.

    The tighter checks are here because a naive scan matched from the closing
    quote of one literal, across `: await renderMarkdown(x ?? `, into the
    opening quote of the next — and produced a "string" that was really a
    line of code with quotes at both ends.
    """
    t = t.strip()
    if len(t) < 12 or len(t.split()) < 2: return False
    if re.search(r"[{}<>=;]|=>|\breturn\b", t): return False
    # Brackets are allowed ONLY as a markdown link — [text](/href).
    stripped = re.sub(r"\[[^\]]+\]\([^)\s]+\)", "", t)
    if re.search(r"[()\[\]]|\?\?|\bawait\b", stripped): return False
    if not re.search(r"[a-z]{3}", t): return False
    return sum(c.isalpha() or c.isspace() for c in t) / len(t) > 0.7

def mask_client_code(tpl):
    """
    Hide <script> and <style> bodies from the substitutions.

    `say()` is a SERVER-side helper. A page's client script often builds markup
    in a JS string — `n.innerHTML = '<li><span>No place of that name…</span>'` —
    and the text-node regex matches happily inside it, producing a literal
    `{say("text.3", "…")}` in the browser's output. It renders as those exact
    characters on the page, and nothing in a build or a typecheck says a word.

    Three pages shipped that before this was added.
    """
    held = []
    def hide(m):
        held.append(m.group(0))
        return f"\x00HELD{len(held) - 1}\x00"
    masked = re.sub(r"<(script|style)[\s>].*?</\1>", hide, tpl, flags=re.S | re.I)
    return masked, held


def unmask_client_code(tpl, held):
    return re.sub(r"\x00HELD(\d+)\x00", lambda m: held[int(m.group(1))], tpl)


def convert(path, page):
    src = pathlib.Path(path).read_text(encoding="utf-8")
    parts = src.split("---", 2)
    if len(parts) < 3:
        return None, 0, "no frontmatter"
    head, tpl = parts[1], parts[2]
    again = 'copy("' in src
    used = set(re.findall(r'say\(\s*["\'`]([^"\'`]+?)["\'`]', src))
    section = ""
    count = 0

    def take(text):
        nonlocal count
        k = key_for(section, used)
        count += 1
        return f'{{say("{k}", "{esc(text)}")}}'

    # 1. Prose in attributes, before text nodes — the same regex would
    #    otherwise treat an attribute's quotes as part of a tag.
    def attr_repl(m):
        whole, name, val = m.group(0), m.group(1), m.group(3)
        if not is_prose(val): return whole
        return f'{name}={take(val)}'
    # The delimiter is BACK-REFERENCED, not "either quote". Written as
    # ["\'] on both ends, an apostrophe inside a double-quoted value closes
    # it early — "...credit yourself, don't sell..." truncated at "don" and
    # left the rest of the sentence dangling outside the attribute, which is a
    # syntax error the build only reports as a column number.
    tpl, _held = mask_client_code(tpl)

    tpl = re.sub(r'\b(' + "|".join(PROSE_ATTRS) + r')=(["\'])((?:(?!\2)[^\n])+)\2',
                 attr_repl, tpl)

    # 2. Text nodes.
    def text_repl(m):
        open_tag, text, close = m.group(1), m.group(2), m.group(3)
        nonlocal section
        if re.match(r"<h[1-6][\s>]", open_tag):
            plain = text.strip()
            if plain and "{" not in plain: section = slug(plain)
        # Tags whose contents are DATA, not prose. A planet name in a table
        # cell, a command in <code>, a timestamp — none of those is a sentence
        # somebody rewrites, and turning them into editable copy fills the
        # panel with noise and invites a table to be edited into nonsense.
        if re.match(r"<(code|pre|kbd|samp|var|time|option|td|th|abbr)[\s>]", open_tag):
            return m.group(0)
        stripped = text.strip()
        # The regex above already guarantees this is the WHOLE content of a
        # leaf element with no braces and no nested tags, which is what makes
        # a short one safe: "Offline" here is a complete label, not seven
        # letters found inside a paragraph. The old floor of twelve characters
        # and two words is what left every one-word label on the site
        # uneditable — "Published", "Offline", "Discord", "here now".
        if len(stripped) < 3 or any(c in text for c in "{}<>"): return m.group(0)
        if not re.search(r"[a-z]{3}", stripped): return m.group(0)
        return f"{open_tag}{take(stripped)}{close}"
    tpl = re.sub(r"(<[a-zA-Z][^<>]*>)([^<>{}]+?)(</[a-zA-Z][a-zA-Z0-9]*>)", text_repl, tpl, flags=re.S)

    tpl = unmask_client_code(tpl, _held)

    if count == 0:
        return None, 0, "nothing convertible"

    if not again:
        rel = pathlib.Path(path).relative_to("frontend/site/src")
        up = "../" * (len(rel.parts) - 1)
        imports = list(re.finditer(r"^import .*?;$", head, re.M))
        at = imports[-1].end() if imports else 0
        head = (head[:at]
                + f'\nimport {{ copy }} from "{up}lib/copy";'
                + f'\n\n/* Every word here, editable from the admin. The defaults below are what\n'
                  f'   it was written with and what still renders if nothing was changed. */\n'
                  f'const say = await copy("{page}");\n'
                + head[at:])
    return f"---{head}---{tpl}", count, "ok"

if __name__ == "__main__":
    out, n, why = convert(sys.argv[1], sys.argv[2])
    if out is None:
        print(f"  {sys.argv[1]}: {why}")
    else:
        pathlib.Path(sys.argv[1]).write_text(out, encoding="utf-8")
        print(f"  {sys.argv[1]}: {n} strings")
