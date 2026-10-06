"""The course corpus: the Laravel 13 documentation, pinned to one commit and downloaded on first use."""

import io
import re
import tarfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from assistant.config import CORPUS_DIR

DOCS_COMMIT = "07b6889f3f7291a762a451449002b85f11eb2f9c"
DOCS_URL = f"https://github.com/laravel/docs/archive/{DOCS_COMMIT}.tar.gz"

# Sections of the table of contents left out: release notes and optional packages.
EXCLUDED_SECTIONS = ("Prologue", "Packages")

# Small subset used by modules 4 to 6 so their checks stay fast on a CPU-only machine.
SAMPLE_PAGES = (
    "routing.md",
    "middleware.md",
    "rate-limiting.md",
    "cache.md",
    "hashing.md",
    "seeding.md",
    "eloquent-collections.md",
)


@dataclass(frozen=True)
class Page:
    source: str  # file name, e.g. "routing.md"
    section: str  # table-of-contents section, e.g. "The Basics"
    title: str
    text: str


def ensure_corpus() -> Path:
    """Returns the folder holding the markdown pages, downloading the pinned archive if needed."""
    docs_dir = CORPUS_DIR / f"docs-{DOCS_COMMIT}"
    if not docs_dir.exists():
        print(f"Téléchargement de la documentation Laravel ({DOCS_COMMIT[:8]})...")
        with urllib.request.urlopen(DOCS_URL, timeout=60) as response:
            archive = io.BytesIO(response.read())
        CORPUS_DIR.mkdir(parents=True, exist_ok=True)
        with tarfile.open(fileobj=archive, mode="r:gz") as tar:
            tar.extractall(CORPUS_DIR, filter="data")
    return docs_dir


def load_toc(docs_dir: Path) -> dict[str, tuple[str, str]]:
    """Maps each page file name to (section, title), read from documentation.md."""
    toc: dict[str, tuple[str, str]] = {}
    section = ""
    for line in (docs_dir / "documentation.md").read_text(encoding="utf-8").splitlines():
        if heading := re.match(r"- ## (.+)", line):
            section = heading.group(1).strip()
        elif link := re.match(r"\s+- \[(.+?)\]\(/docs/\{\{version\}\}/([\w-]+)\)", line):
            # A page listed twice (dusk) keeps its first section.
            toc.setdefault(f"{link.group(2)}.md", (section, link.group(1)))
    return toc


def load_pages(sample: bool = False) -> list[Page]:
    docs_dir = ensure_corpus()
    pages = []
    for source, (section, title) in load_toc(docs_dir).items():
        if section in EXCLUDED_SECTIONS or (sample and source not in SAMPLE_PAGES):
            continue
        pages.append(Page(source, section, title, (docs_dir / source).read_text(encoding="utf-8")))
    return pages


if __name__ == "__main__":
    pages = load_pages()
    sections: dict[str, int] = {}
    for page in pages:
        sections[page.section] = sections.get(page.section, 0) + 1
    for section, count in sections.items():
        print(f"{count:3d}  {section}")
    print(f"{len(pages):3d}  pages, {sum(len(p.text.split()) for p in pages)} mots")
    print("Échantillon :", ", ".join(f"{p.source} ({len(p.text.split())} mots)" for p in load_pages(sample=True)))
