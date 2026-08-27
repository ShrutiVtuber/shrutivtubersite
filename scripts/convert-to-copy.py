"""
Route a page's literal prose through the copy helper.

Deliberately conservative. It only touches text that is unambiguously a text
node — no braces, no tags, inside an element — and it leaves everything else
exactly as written. A page it cannot convert cleanly is a page a person should
convert, not one a script should guess at: a broken page is worse than an
uneditable one.
"""
import re, sys, pathlib

STOP = {"and","the","for","with","from","that","this","your","you","are","its",
        "was","not","but","all","one","two","has","have","can","will","who",
        "what","when","where","how","why","into","than","then","they","them"}

def slug(text):
    """A heading as a key segment: "Fan art" -> "fan-art"."""
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:24] or "text"


def key_for(section, used):
    """
    Keyed by the section it sits under, numbered in order.

    Not by its own words: a key derived from the text stops describing it the
    moment she rewrites the text, which is the entire point of this table.
    "fan-art.3" still means the third line under Fan art after every word in it
    has changed.
    """
    base = section or "text"
    n = 1
    while f"{base}.{n}" in used:
        n += 1
    key = f"{base}.{n}"
    used.add(key)
    return key

def convert(path, page):
    src = pathlib.Path(path).read_text(encoding="utf-8")
    # A page converted once still has prose the first pass would not take —
    # anything that was wrapped across lines, or sat inside a conditional. So a
    # second run is allowed; it just must not add the import twice, and must
    # not reuse a key the first run already claimed.
    again = 'copy("' in src
    parts = src.split("---", 2)
    if len(parts) < 3:
        return None, "no frontmatter"
    head, tpl = parts[1], parts[2]

    used = set(re.findall(r't\(\s*["\'`]([^"\'`]+?)["\'`]', src))
    count = 0

    section = ""

    def repl(m):
        nonlocal count, section
        open_tag, text, close = m.group(1), m.group(2), m.group(3)
        # A heading names the section everything after it belongs to — and is
        # itself the section's first string.
        if re.match(r"<h[1-6][\s>]", open_tag):
            section = slug(text.strip())
        stripped = text.strip()
        # Headings are short and are precisely what somebody rewriting copy
        # wants to change, so they get a lower bar than body text.
        floor = 3 if re.match(r"<h[1-6][\s>]", open_tag) else 18
        # Not prose: too short, has markup or an expression, or is all symbols.
        if len(stripped) < floor or any(c in text for c in "{}<>"):
            return m.group(0)
        if not re.search(r"[a-z]{3}", stripped):
            return m.group(0)
        k = key_for(section, used)
        count += 1
        esc = stripped.replace("\\", "\\\\").replace('"', '\\"')
        # Collapse the source's own wrapping — the string is one line now.
        esc = " ".join(esc.split())
        return f'{open_tag}{{t("{k}", "{esc}")}}{close}'

    # <tag ...>  text  </tag>  with nothing but text between.
    tpl2 = re.sub(r"(<[a-zA-Z][^<>]*>)([^<>{}]+?)(</[a-zA-Z][a-zA-Z0-9]*>)", repl, tpl, flags=re.S)

    if count == 0:
        return None, "nothing convertible"

    if again:
        return f"---{head}---{tpl2}", count

    # The helper, declared after the last import so it can be awaited.
    imports = list(re.finditer(r"^import .*?;$", head, re.M))
    at = imports[-1].end() if imports else 0
    head2 = (head[:at]
             + '\nimport { copy } from "' + ("../" * (len(pathlib.Path(path).relative_to("frontend/site/src/pages").parts) - 1) + "../lib/copy") + '";'
             + f'\n\n/* Every word on this page, editable from the admin. The defaults below are\n   what it was written with and what still renders if nothing was changed. */\nconst t = await copy("{page}");\n'
             + head[at:])
    return f"---{head2}---{tpl2}", count

if __name__ == "__main__":
    path, page = sys.argv[1], sys.argv[2]
    out, info = convert(path, page)
    if out is None:
        print(f"  {path}: {info}")
    else:
        pathlib.Path(path).write_text(out, encoding="utf-8")
        print(f"  {path}: {info} strings")
