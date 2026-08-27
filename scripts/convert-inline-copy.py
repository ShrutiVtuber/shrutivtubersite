"""
Convert a paragraph carrying inline markup into ONE editable string.

The alternative — splitting at each <strong> or <a> — gives her "Their hours
are in" and " local time" as separate boxes: she cannot see the sentence, and
moving the link means retyping both halves. So the paragraph becomes one string
holding inline markdown, rendered by components/content/Copy.astro.

Only paragraphs whose inline content is entirely convertible. A <p> containing
an expression, a component, or a tag outside the four we render is left exactly
as written — a sentence a person should convert, not one a script should guess
at.
"""
import re, sys, pathlib

OK = {"strong": "**", "b": "**", "em": "*", "i": "*", "code": "`"}

def slug(t):
    s = re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
    return s[:24] or "text"

def to_md(inner):
    """The paragraph's children as inline markdown, or None if unconvertible."""
    out, at = [], 0
    for m in re.finditer(r"<(\w+)([^<>]*)>([^<>{}]*?)</\1>", inner):
        gap = inner[at:m.start()]
        if "<" in gap or ">" in gap or "{" in gap:
            return None
        out.append(gap)
        tag, attrs, text = m.group(1).lower(), m.group(2), m.group(3)
        if tag == "a":
            href = re.search(r'href="([^"]+)"', attrs)
            if not href or "{" in attrs:
                return None
            out.append(f"[{' '.join(text.split())}]({href.group(1)})")
        elif tag in OK:
            if attrs.strip():
                return None
            d = OK[tag]
            out.append(f"{d}{' '.join(text.split())}{d}")
        else:
            return None
        at = m.end()
    tail = inner[at:]
    if "<" in tail or ">" in tail or "{" in tail:
        return None
    out.append(tail)
    md = " ".join("".join(out).split())
    return md if len(md) >= 24 and re.search(r"[a-z]{3}", md) else None

def convert(path, page):
    src = pathlib.Path(path).read_text(encoding="utf-8")
    parts = src.split("---", 2)
    if len(parts) < 3: return None, 0
    head, tpl = parts[1], parts[2]
    used = set(re.findall(r't\(\s*["\'`]([^"\'`]+?)["\'`]', src))
    section, count = "", 0

    def repl(m):
        nonlocal section, count
        open_tag, inner, close = m.group(1), m.group(2), m.group(3)
        if re.match(r"<h[1-6][\s>]", open_tag):
            plain = re.sub(r"<[^<>]+>", "", inner).strip()
            if plain and "{" not in plain: section = slug(plain)
        md = to_md(inner)
        if md is None: return m.group(0)
        n = 1
        while f"{section or 'text'}.{n}" in used: n += 1
        key = f"{section or 'text'}.{n}"
        used.add(key)
        count += 1
        esc = md.replace("\\", "\\\\").replace('"', '\\"')
        return f'{open_tag}<Copy text={{t("{key}", "{esc}")}} />{close}'

    tpl2 = re.sub(r"(<(?:p|li|figcaption|dd|blockquote)(?:\s[^<>]*)?>)([\s\S]*?)(</(?:p|li|figcaption|dd|blockquote)>)",
                  repl, tpl)
    if count == 0: return None, 0

    if "content/Copy.astro" not in head:
        depth = len(pathlib.Path(path).relative_to("frontend/site/src/pages").parts) - 1
        imp = f'import Copy from "{"../" * depth}../components/content/Copy.astro";'
        imports = list(re.finditer(r"^import .*?;$", head, re.M))
        at = imports[-1].end() if imports else 0
        head = head[:at] + "\n" + imp + head[at:]
    if 'copy("' not in src:
        depth = len(pathlib.Path(path).relative_to("frontend/site/src/pages").parts) - 1
        imports = list(re.finditer(r"^import .*?;$", head, re.M))
        at = imports[-1].end() if imports else 0
        head = (head[:at] + f'\nimport {{ copy }} from "{"../" * depth}../lib/copy";'
                + f'\n\nconst t = await copy("{page}");\n' + head[at:])
    return f"---{head}---{tpl2}", count

if __name__ == "__main__":
    out, n = convert(sys.argv[1], sys.argv[2])
    if out is None: print(f"  {sys.argv[1]}: nothing convertible")
    else:
        pathlib.Path(sys.argv[1]).write_text(out, encoding="utf-8")
        print(f"  {sys.argv[1]}: {n} paragraphs")
