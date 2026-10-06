"""Module 05: chunking and brute-force search. Read LESSON.md first.

Run this file to cut the sample pages into chunks and search them from your terminal.
"""

import numpy as np

from assistant.chunking import HEADING, Chunk, clean, pack_paragraphs
from assistant.corpus import load_pages
from assistant.embeddings import embed


def chunk_markdown(text: str, source: str, section: str = "", max_words: int = 300) -> list[Chunk]:
    """Cuts a markdown page into chunks: at least one per heading that has text under it.

    1. Walk through clean(text) line by line. clean() removes the table of contents and the HTML anchors.
    2. A line starting with ``` opens or closes a code block. Inside a code block, nothing is a heading.
    3. A heading, detected with HEADING.match(line), closes the section in progress. Turn the lines gathered
       so far into chunks: pack_paragraphs(body, max_words) returns the pieces, build one Chunk per piece.
    4. Keep the heading path up to date. "# Cache", then "## Usage", then "### Storing items" gives
       "Cache > Usage > Storing items". A new "##" replaces the previous "##" and drops the "###" under it.
    5. Do not forget the last section when the loop ends.

    Chunk ids are f"{source}#{n}", n being the position of the chunk in the page: 0, 1, 2...
    HEADING.match(line).group(1) is the run of "#", group(2) is the title.
    """
    raise NotImplementedError


def search(query: str, chunks: list[Chunk], vectors: np.ndarray, k: int = 5) -> list[tuple[Chunk, float]]:
    """Returns the k chunks closest to the query, as (chunk, score) pairs, best first.

    vectors[i] is the embedding of chunks[i]. The vectors have length 1, so the cosine similarity
    with the query vector is a plain dot product: `vectors @ query_vector` scores every chunk at once.
    np.argsort sorts in ascending order.
    """
    raise NotImplementedError


if __name__ == "__main__":
    chunks = [
        chunk
        for page in load_pages(sample=True)
        for chunk in chunk_markdown(page.text, page.source, page.section)
    ]
    sizes = sorted(len(chunk.text.split()) for chunk in chunks)
    print(f"{len(chunks)} passages, médiane {sizes[len(sizes) // 2]} mots, maximum {sizes[-1]} mots")
    print("Calcul des embeddings...")
    vectors = embed([chunk.content for chunk in chunks])

    print("Pose une question sur le routage, les middlewares, le cache ou le hachage (ligne vide pour quitter).")
    while query := input("> ").strip():
        for chunk, score in search(query, chunks, vectors, k=3):
            first_line = chunk.text.strip().splitlines()[0][:100]
            print(f"  {score:.3f}  {chunk.source}  {chunk.heading}\n         {first_line}")
