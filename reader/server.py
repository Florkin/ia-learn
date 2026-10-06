"""IA Learn reader: the lessons of this repository, laid out for a phone.

One process, standard library only, no build step. Every page is rendered from the markdown
files at request time: what the repository holds is what shows.

Run: python3 reader/server.py   then open http://localhost:8000
"""

import html
import os
import re
from dataclasses import dataclass
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

NAME = "IA Learn"
ROOT = Path(__file__).resolve().parent.parent
MODULES = ROOT / "modules"
STATIC = Path(__file__).resolve().parent / "static"
REPOSITORY = "https://github.com/Florkin/ia-learn"
# Set where the reader sits behind a launcher page, so that its home leads back to it.
DASHBOARD_URL = os.environ.get("DASHBOARD_URL", "")


# ── Catalogue ────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Module:
    slug: str  # folder under modules/, "04-embeddings"
    number: str
    title: str
    summary: str
    duration: str
    group: str


GROUP_ROW = re.compile(r"\|\s*\|\s*\*\*(.+?)\*\*")
MODULE_ROW = re.compile(r"\|\s*(\d+)\s*\|\s*\[(.+?)\]\(modules/([\w-]+)/LESSON\.md\)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|")


def load_modules(readme=None):
    """Modules in course order. Titles, summaries, durations and groups come from the table of the
    README; a folder the table does not mention yet is listed last, under a heading of its own."""
    if readme is None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
    on_disk = sorted(folder.name for folder in MODULES.iterdir() if (folder / "LESSON.md").is_file())
    listed, group = {}, ""
    for line in readme.splitlines():
        if row := GROUP_ROW.match(line):
            group = row.group(1)
        elif (row := MODULE_ROW.match(line)) and row.group(3) in on_disk:
            listed[row.group(3)] = Module(row.group(3), row.group(1), row.group(2), row.group(4), row.group(5), group)
    modules = list(listed.values())
    for slug in on_disk:
        if slug not in listed:
            heading = (MODULES / slug / "LESSON.md").read_text(encoding="utf-8").split("\n", 1)[0]
            title = re.sub(r"^#\s*(\d+\s*·\s*)?", "", heading).strip()
            modules.append(Module(slug, slug[:2], title, "", "", "Autres modules"))
    return modules


# ── Markdown ─────────────────────────────────────────────────────────────────

# ponytail: renders the subset the course uses, not the whole of markdown: no nested list, no
# image, no setext heading, no reference link. test_server.py compares it with markdown-it-py on
# every course file; if a lesson ever needs more, swap this section for that library.

FENCE = re.compile(r"(`{3,})\s*([\w+-]*)\s*$")
HEADING = re.compile(r"(#{1,6})\s+(.*?)\s*$")
ITEM = re.compile(r"(?:[-*]|(\d+)[.)])\s+(.*)")
TABLE_RULE = re.compile(r"\|\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$")
CODE_SPAN = re.compile(r"(`+)(.+?)(?<!`)\1(?!`)", re.S)
LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
COURSE_LINK = re.compile(r"(?:\./)?modules/([\w-]+)/(LESSON|DEEPER)\.md$")
SAFE_LINK = re.compile(r"https?://|mailto:|/|#")


def text(value):
    """Escapes outside text the way the reference implementation does."""
    return html.escape(value, quote=False).replace('"', "&quot;")


def link(match):
    label, target = match.group(1), match.group(2)
    if course := COURSE_LINK.match(target):
        target = f"/modules/{course.group(1)}" + ("/deeper" if course.group(2) == "DEEPER" else "")
    elif not SAFE_LINK.match(target):
        return match.group(0)  # an unknown scheme or a file of the repository: left as text
    return f'<a href="{target}">{label}</a>'


def inline(source):
    spans = []

    def keep(match):
        code = match.group(2).replace("\n", " ")
        if code.startswith(" ") and code.endswith(" ") and code.strip():
            code = code[1:-1]
        spans.append(f"<code>{text(code)}</code>")
        return f"\x00{len(spans) - 1}\x00"

    # Code spans leave first, so that nothing inside them is read as markdown.
    out = text(CODE_SPAN.sub(keep, source))
    out = LINK.sub(link, out)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out, flags=re.S)
    out = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"<em>\1</em>", out, flags=re.S)
    return re.sub(r"\x00(\d+)\x00", lambda match: spans[int(match.group(1))], out)


def cells(row):
    return [cell.strip() for cell in row.strip().strip("|").split("|")]


def table(header, rows):
    head = "".join(f"<th>{inline(cell)}</th>" for cell in cells(header))
    body = "".join("<tr>" + "".join(f"<td>{inline(cell)}</td>" for cell in cells(row)) + "</tr>\n" for row in rows)
    # Its own scrolling box: a wide table must never widen the page.
    return f'<div class="table"><table>\n<thead>\n<tr>{head}</tr>\n</thead>\n<tbody>\n{body}</tbody>\n</table></div>'


def interrupts(line):
    """Whether a line ends the paragraph or the list item above it."""
    if FENCE.match(line) or HEADING.match(line) or line.startswith((">", "|")):
        return True
    item = ITEM.match(line)
    return bool(item) and item.group(1) in (None, "1")


def render(source):
    """Markdown to HTML. Raw HTML in the source is escaped, never passed through."""
    lines = source.splitlines()
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
        elif fence := FENCE.match(line):
            closing = re.compile(rf"`{{{len(fence.group(1))},}}\s*$")
            end = i + 1
            while end < len(lines) and not closing.match(lines[end]):
                end += 1
            code = "".join(row + "\n" for row in lines[i + 1 : end])
            language = f' class="language-{text(fence.group(2))}"' if fence.group(2) else ""
            out.append(f"<pre><code{language}>{text(code)}</code></pre>")
            i = end + 1
        elif heading := HEADING.match(line):
            level = len(heading.group(1))
            out.append(f"<h{level}>{inline(heading.group(2))}</h{level}>")
            i += 1
        elif line.startswith(">"):
            end = i
            while end < len(lines) and lines[end].startswith(">"):
                end += 1
            quoted = "\n".join(re.sub(r"^> ?", "", row) for row in lines[i:end])
            out.append(f"<blockquote>\n{render(quoted)}\n</blockquote>")
            i = end
        elif line.startswith("|") and i + 1 < len(lines) and TABLE_RULE.match(lines[i + 1]):
            end = i + 2
            while end < len(lines) and lines[end].startswith("|"):
                end += 1
            out.append(table(line, lines[i + 2 : end]))
            i = end
        elif first := ITEM.match(line):
            ordered = first.group(1) is not None
            items = []
            while i < len(lines) and (item := ITEM.match(lines[i])) and (item.group(1) is not None) == ordered:
                parts = [item.group(2)]
                i += 1
                while i < len(lines) and lines[i].strip() and not ITEM.match(lines[i]) and not interrupts(lines[i]):
                    parts.append(lines[i].strip())  # a wrapped line of the same item
                    i += 1
                items.append("\n".join(parts))
            tag = "ol" if ordered else "ul"
            start = f' start="{first.group(1)}"' if ordered and first.group(1) != "1" else ""
            out.append(f"<{tag}{start}>\n" + "\n".join(f"<li>{inline(item)}</li>" for item in items) + f"\n</{tag}>")
        else:
            end = i + 1
            while end < len(lines) and lines[end].strip() and not interrupts(lines[end]):
                end += 1
            out.append(f"<p>{inline(chr(10).join(row.strip() for row in lines[i:end]))}</p>")
            i = end
    return "\n".join(out)


# ── Rendering ────────────────────────────────────────────────────────────────

e = html.escape


def document(source):
    """Title and body of a course file: its introduction, then one card per `##` section."""
    title, intro, sections, in_code = "", [], [], False
    current = intro
    for line in source.splitlines():
        if line.startswith("```"):
            in_code = not in_code
        if not in_code and not title and line.startswith("# "):
            title = line[2:].strip()
        elif not in_code and line.startswith("## "):
            current = []
            sections.append((line[3:].strip(), current))
        else:
            current.append(line)
    parts = [f'<div class="intro">{render(chr(10).join(intro))}</div>'] if "".join(intro).strip() else []
    for name, body in sections:
        parts.append(f'<section><h2>{inline(name)}</h2><div class="sheet">{render(chr(10).join(body))}</div></section>')
    return title, "\n".join(parts)


def page(title, body, back=None, status=""):
    crumb = f'<a class="back" href="{e(back[0])}">‹ {e(back[1])}</a>' if back else ""
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#F3F1EC">
<title>{e(title if title == NAME else f"{title} · {NAME}")}</title>
<link rel="icon" href="/icon.svg">
<link rel="stylesheet" href="/style.css">
</head>
<body>
<main>
{crumb}
<header><h1>{e(title)}</h1>{status}</header>
{body}
</main>
</body>
</html>
"""


def index_page(modules):
    groups = {}
    for module in modules:
        groups.setdefault(module.group, []).append(module)
    sections = []
    for name, members in groups.items():
        rows = "".join(
            f'<a class="item" href="/modules/{module.slug}"><span class="num">{e(module.number)}</span>'
            f'<span class="name"><b>{e(module.title)}</b><small>{e(module.summary)}</small></span>'
            f'<span class="size">{e(module.duration)}</span><i>›</i></a>'
            for module in members
        )
        sections.append(f'<section><h2>{e(name)}</h2><div class="list">{rows}</div></section>')
    links = f'<nav class="links"><a href="/guide">Mode d\'emploi</a><a href="{REPOSITORY}">Dépôt GitHub</a></nav>'
    back = (DASHBOARD_URL, "Tableau de bord") if DASHBOARD_URL else None
    return page(NAME, "\n".join(sections) + "\n" + links, back, f'<p id="status">{len(modules)} modules</p>')


def step(module, label, primary=False):
    """One half of the bottom bar: the previous or the next module, within reach of the thumb."""
    if not module:
        return '<span class="button" aria-disabled="true"></span>'
    kind = "button primary" if primary else "button"
    return f'<a class="{kind}" href="/modules/{module.slug}"><small>{label}</small><b>{e(module.number)} · {e(module.title)}</b></a>'


def lesson_page(modules, position, deeper):
    module = modules[position]
    folder = MODULES / module.slug
    title, body = document((folder / ("DEEPER.md" if deeper else "LESSON.md")).read_text(encoding="utf-8"))
    here = f"/modules/{module.slug}"
    if deeper:
        back = (here, f"{module.number} · {module.title}")
    else:
        back = ("/", "Parcours")
        if (folder / "DEEPER.md").is_file():
            body += (
                f'\n<a class="tile" href="{here}/deeper"><span class="row"><b>Pour aller plus loin</b><i>›</i></span>'
                "<small>Des exercices facultatifs, à reprendre quand tu veux</small></a>"
            )
    previous = modules[position - 1] if position else None
    following = modules[position + 1] if position + 1 < len(modules) else None
    bar = f'\n<nav class="bar">{step(previous, "Précédent")}{step(following, "Suivant", primary=True)}</nav>'
    return page(title, body + bar, back)


def not_found_page():
    body = '<p class="empty">Cette page n\'existe pas, ou plus.</p>\n<nav class="links"><a href="/">Retour au parcours</a></nav>'
    return page("Page introuvable", body, ("/", "Parcours"))


# ── Serving ──────────────────────────────────────────────────────────────────

HTML = "text/html; charset=utf-8"
MODULE_PATH = re.compile(r"/modules/([^/]+)(/deeper)?/?")


def respond(path):
    """(status, content type, body) for a page of the site; None for anything else."""
    path = path.split("?", 1)[0]
    if path == "/":
        return 200, HTML, index_page(load_modules()).encode()
    if path == "/guide":
        _, body = document((ROOT / "README.md").read_text(encoding="utf-8"))
        return 200, HTML, page("Mode d'emploi", body, ("/", "Parcours")).encode()
    if path.startswith("/modules/"):
        modules = load_modules()
        slugs = [module.slug for module in modules]
        # The slug is looked up among the folders that exist: a path can name a module, never a file.
        asked = MODULE_PATH.fullmatch(path)
        if asked and asked.group(1) in slugs:
            deeper = bool(asked.group(2))
            if not deeper or (MODULES / asked.group(1) / "DEEPER.md").is_file():
                return 200, HTML, lesson_page(modules, slugs.index(asked.group(1)), deeper).encode()
        return 404, HTML, not_found_page().encode()
    return None


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC), **kwargs)

    def do_GET(self):
        if self.path.split("?", 1)[0] == "/health":
            return self.send_body(200, "text/plain", b"ok")
        try:
            answer = respond(self.path)
        except Exception as error:  # a broken lesson must not take the other pages down
            print(f"render failed for {self.path!r}: {error!r}", flush=True)
            return self.send_error(500)
        if answer:
            self.send_body(*answer)
        else:
            super().do_GET()  # the stylesheet and the icon, from static/

    def send_body(self, status, content_type, body):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Security-Policy", "default-src 'self'")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def list_directory(self, path):
        self.send_error(404)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    print(f"{NAME} : http://localhost:{port}", flush=True)
    ThreadingHTTPServer(("", port), Handler).serve_forever()
