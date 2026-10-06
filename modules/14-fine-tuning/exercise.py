"""Module 14: fine-tuning. Read LESSON.md first. Needs the dependency groups: uv sync --all-groups

Run this file to fine-tune a small language model and compare its answers before and after.
"""


import random

from assistant import finetune
from assistant.chunking import Chunk, chunk_corpus
from assistant.config import DATA_DIR, settings
from assistant.finetune import INSTRUCTION, excerpt


def build_examples(chunks: list[Chunk]) -> list[dict]:
    """One training example per chunk, in the chat format every fine-tuning tool reads:

        {"messages": [
            {"role": "system", "content": INSTRUCTION},
            {"role": "user", "content": excerpt(chunk)},
            {"role": "assistant", "content": chunk.section},
        ]}

    The assistant message is the answer we want the model to learn.
    """
    raise NotImplementedError


def split_examples(examples: list[dict], valid_ratio: float = 0.1, seed: int = 0) -> tuple[list[dict], list[dict]]:
    """Returns (train, valid): a shuffled copy of the examples, cut in two.

    Shuffle a copy with random.Random(seed).shuffle(copy), so that the same seed gives the same split
    and the list received is left untouched. valid holds round(len(examples) * valid_ratio) examples.
    """
    raise NotImplementedError


if __name__ == "__main__":
    train, valid = split_examples(build_examples(chunk_corpus()))
    test = valid[:100]
    prompts = [example["messages"][:-1] for example in test]
    expected = [example["messages"][-1]["content"] for example in test]
    print(f"{len(train)} exemples d'entraînement, {len(valid)} de validation, moteur : {settings.finetune_backend}")
    print(f"\nConsigne : {INSTRUCTION}\nPassage  : {test[0]['messages'][1]['content']}\nAttendu  : {expected[0]}\n")

    before = finetune.generate(prompts)
    adapter = finetune.train(train, valid, DATA_DIR / f"learner-{settings.learner or 'demo'}-14-{settings.finetune_backend}")
    after = finetune.generate(prompts, adapter)

    print("\nattendu                  avant affinage                        après affinage")
    for label, old, new in list(zip(expected, before, after))[:10]:
        print(f"{label:24s} {old[:36]:37s} {new}")
    score = lambda answers: sum(answer == label for answer, label in zip(answers, expected)) / len(expected)
    print(f"\nBonnes réponses sur {len(test)} passages : {score(before):.0%} avant, {score(after):.0%} après")
