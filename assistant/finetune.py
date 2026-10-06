"""Fine-tuning a small language model with LoRA: reference brick for module 14.

Task: the same as module 13. Given a passage of the documentation, name the section it comes from.
Two interchangeable backends: mlx (Apple Silicon) and peft (PyTorch, any machine).
"""

import random
from pathlib import Path

from assistant.chunking import Chunk
from assistant.config import settings

BASE_MODEL = "HuggingFaceTB/SmolLM2-360M-Instruct"

SECTIONS = [
    "AI", "Architecture Concepts", "Database", "Digging Deeper", "Eloquent ORM",
    "Getting Started", "Security", "Testing", "The Basics",
]  # fmt: skip

INSTRUCTION = (
    "Classify the passage of the Laravel documentation into one of these sections: "
    + ", ".join(SECTIONS)
    + ". Reply with the section name only."
)


def excerpt(chunk: Chunk, max_words: int = 40) -> str:
    """The beginning of a passage, heading path included. Short inputs keep training fast."""
    return " ".join(chunk.content.split()[:max_words])


def _backend(name: str | None):
    name = name or settings.finetune_backend
    if name == "mlx":
        from assistant import finetune_mlx

        return finetune_mlx
    if name == "peft":
        from assistant import finetune_peft

        return finetune_peft
    raise ValueError(f"FINETUNE_BACKEND doit valoir mlx ou peft, obtenu : {name!r}")


def train(train_examples: list[dict], valid_examples: list[dict], out_dir: Path, iters: int | None = None, backend: str | None = None) -> Path:
    """Trains a LoRA adapter on the examples and saves it in out_dir. FINETUNE_ITERS sets the default length."""
    out_dir.mkdir(parents=True, exist_ok=True)
    _backend(backend).train(BASE_MODEL, train_examples, valid_examples, out_dir, iters or settings.finetune_iters)
    return out_dir


def generate(prompts: list[list[dict]], adapter_dir: Path | None = None, backend: str | None = None, max_tokens: int = 8) -> list[str]:
    """Answers each prompt (a list of messages) with the base model, or with the adapter when one is given."""
    return _backend(backend).generate(BASE_MODEL, prompts, adapter_dir, max_tokens)


def accuracy(examples: list[dict], adapter_dir: Path | None = None, backend: str | None = None) -> float:
    """Share of examples for which the model writes exactly the expected answer."""
    answers = generate([example["messages"][:-1] for example in examples], adapter_dir, backend)
    expected = [example["messages"][-1]["content"] for example in examples]
    return sum(answer == label for answer, label in zip(answers, expected)) / len(examples)


# --- Module 14: preparing the data -----------------------------------------------------------


def build_examples(chunks: list[Chunk]) -> list[dict]:
    return [
        {
            "messages": [
                {"role": "system", "content": INSTRUCTION},
                {"role": "user", "content": excerpt(chunk)},
                {"role": "assistant", "content": chunk.section},
            ]
        }
        for chunk in chunks
    ]


def split_examples(examples: list[dict], valid_ratio: float = 0.1, seed: int = 0) -> tuple[list[dict], list[dict]]:
    shuffled = examples[:]
    random.Random(seed).shuffle(shuffled)
    cut = round(len(shuffled) * valid_ratio)
    return shuffled[cut:], shuffled[:cut]
