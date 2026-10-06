"""Cutting markdown pages into passages and searching them by brute force: reference brick for module 05."""

import re
from dataclasses import dataclass

import numpy as np

from assistant.corpus import load_pages
from assistant.embeddings import embed

HEADING = re.compile(r"^(#{1,4})\s+(.+)")
# Lines that carry no information: HTML anchors, <div> wrappers, links to another part of the same page.
NOISE = re.compile(r'^\s*(<a name="[^"]*"></a>|</?div[^>]*>|(- )?\[[^\]]+\]\(#[^)]*\))\s*$')


@dataclass(frozen=True)
class Chunk:
    id: str  # "<source>#<position in the page>"
    source: str  # page file name, e.g. "routing.md"
    section: str  # table-of-contents section of the page, e.g. "The Basics"
    heading: str  # heading path, e.g. "Routing > Route Parameters > Optional Parameters"
    text: str

    @property
    def content(self) -> str:
        """What gets embedded and shown to the model: the heading path gives the passage its context."""
        return f"{self.heading}\n\n{self.text}"


def clean(text: str) -> str:
    """Drops the noise lines of the Laravel docs, among them the table of contents at the top of each page."""
    lines = (line for line in text.splitlines() if not NOISE.match(line))
    # Some headings carry a CSS class: "#### `Str::of()` {.collection-method}".
    return "\n".join(re.sub(r"\s*\{\.collection-method[^}]*\}", "", line) for line in lines)


def _blocks(body: str) -> list[str]:
    """Paragraphs of a section body. A fenced code block is one paragraph, blank lines included."""
    blocks, current, in_code = [], [], False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            in_code = not in_code
        if line.strip() or in_code:
            current.append(line)
        elif current:
            blocks.append("\n".join(current))
            current = []
    if current:
        blocks.append("\n".join(current))
    return blocks


def _hard_split(block: str, max_words: int) -> list[str]:
    """Last resort for one paragraph longer than max_words: cut between lines, then between words."""
    pieces, current, count = [], [], 0
    for line in block.splitlines():
        words = line.split()
        while len(words) > max_words:  # a single huge line
            pieces.append(" ".join(words[:max_words]))
            words = words[max_words:]
            line = " ".join(words)
        if count + len(words) > max_words and current:
            pieces.append("\n".join(current))
            current, count = [], 0
        current.append(line)
        count += len(words)
    if current:
        pieces.append("\n".join(current))
    return pieces


def pack_paragraphs(body: str, max_words: int) -> list[str]:
    """Groups the paragraphs of a section into pieces of at most max_words words."""
    pieces, current, count = [], [], 0
    for block in _blocks(body):
        size = len(block.split())
        if count + size > max_words and current:
            pieces.append("\n\n".join(current))
            current, count = [], 0
        if size > max_words:
            pieces += _hard_split(block, max_words)
            continue
        current.append(block)
        count += size
    if current:
        pieces.append("\n\n".join(current))
    return pieces


# --- Module 05: chunking and brute-force search -------------------------------------------


def chunk_markdown(text: str, source: str, section: str = "", max_words: int = 300) -> list[Chunk]:
    chunks: list[Chunk] = []
    levels: list[str | None] = [None] * 4  # current heading at each level, "#" to "####"
    body: list[str] = []
    in_code = False

    def flush() -> None:
        path = " > ".join(title for title in levels if title)
        for piece in pack_paragraphs("\n".join(body), max_words):
            chunks.append(Chunk(f"{source}#{len(chunks)}", source, section, path, piece))
        body.clear()

    for line in clean(text).splitlines():
        if line.lstrip().startswith("```"):
            in_code = not in_code
        heading = None if in_code else HEADING.match(line)
        if heading:
            flush()
            level = len(heading.group(1))
            # A new heading replaces the one at its level and drops the deeper ones.
            levels[level - 1 :] = [heading.group(2).strip()] + [None] * (4 - level)
        else:
            body.append(line)
    flush()
    return chunks


def chunk_corpus(sample: bool = False, max_words: int = 300) -> list[Chunk]:
    return [
        chunk
        for page in load_pages(sample)
        for chunk in chunk_markdown(page.text, page.source, page.section, max_words)
    ]


def search(query: str, chunks: list[Chunk], vectors: np.ndarray, k: int = 5) -> list[tuple[Chunk, float]]:
    """Compares the query with every vector. Assumes unit-length vectors, which bge-m3 returns."""
    scores = vectors @ embed([query])[0]
    best = np.argsort(scores)[::-1][:k]
    return [(chunks[i], float(scores[i])) for i in best]


if __name__ == "__main__":
    chunks = chunk_corpus()
    sizes = sorted(len(chunk.text.split()) for chunk in chunks)
    print(f"{len(chunks)} passages, médiane {sizes[len(sizes) // 2]} mots, maximum {sizes[-1]} mots")
