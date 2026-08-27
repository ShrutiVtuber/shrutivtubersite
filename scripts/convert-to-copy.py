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
PROSE_ATTRS = ("title", "label", "body", "lede", "eyebrow", "placeholder",
               "alt", "aria-label", "description", "cta", "summary", "help",
               "note", "hint", "caption", "ruleLabel")

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
    t = t.strip()
    if len(t) < 12 or len(t.split()) < 2: return False
    if re.search(r"[{}<>=;]|=>|\breturn\b", t): return False
    if not re.search(r"[a-z]{3}", t): return False
    return sum(c.isalpha() or c.isspace() for c in t) / len(t) > 0.7

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
    tpl = re.sub(r'\b(' + "|".join(PROSE_ATTRS) + r')=(["\'])((?:(?!\2)[^\n])+)\2',
                 attr_repl, tpl)

    # 2. Text nodes.
    def text_repl(m):
        open_tag, text, close = m.group(1), m.group(2), m.group(3)
        nonlocal section
        if re.match(r"<h[1-6][\s>]", open_tag):
            plain = text.strip()
            if plain and "{" not in plain: section = slug(plain)
        floor = 3 if re.match(r"<h[1-6][\s>]", open_tag) else 12
        stripped = text.strip()
        if len(stripped) < floor or any(c in text for c in "{}<>"): return m.group(0)
        if not re.search(r"[a-z]{3}", stripped): return m.group(0)
        if len(stripped.split()) < 2 and floor > 3: return m.group(0)
        return f"{open_tag}{take(stripped)}{close}"
    tpl = re.sub(r"(<[a-zA-Z][^<>]*>)([^<>{}]+?)(</[a-zA-Z][a-zA-Z0-9]*>)", text_repl, tpl, flags=re.S)

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
