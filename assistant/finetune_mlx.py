"""Fine-tuning backend for Apple Silicon, built on mlx-lm."""

import json
import subprocess
import sys
from pathlib import Path


def train(base_model: str, train_examples: list[dict], valid_examples: list[dict], out_dir: Path, iters: int) -> None:
    # mlx-lm reads its data from a folder holding train.jsonl and valid.jsonl, one chat example per line.
    data_dir = out_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    for name, examples in (("train", train_examples), ("valid", valid_examples)):
        lines = "".join(json.dumps(example, ensure_ascii=False) + "\n" for example in examples)
        (data_dir / f"{name}.jsonl").write_text(lines, encoding="utf-8")
    command = [
        sys.executable, "-m", "mlx_lm", "lora",
        "--model", base_model,
        "--train",
        "--data", str(data_dir),
        "--adapter-path", str(out_dir),
        "--iters", str(iters),
        "--batch-size", "8",
        "--learning-rate", "2e-4",
        "--mask-prompt",  # learn from the expected answer only, not from the prompt
        "--steps-per-report", "25",
        "--steps-per-eval", "100",
        "--val-batches", "10",
        "--seed", "0",
    ]  # fmt: skip
    subprocess.run(command, check=True)


def generate(base_model: str, prompts: list[list[dict]], adapter_dir: Path | None, max_tokens: int) -> list[str]:
    from mlx_lm import batch_generate, load

    model, tokenizer = load(base_model, adapter_path=str(adapter_dir) if adapter_dir else None)
    # batch_generate takes prompts already turned into token ids.
    token_ids = [tokenizer.apply_chat_template(messages, add_generation_prompt=True) for messages in prompts]
    answers: list[str] = []
    for start in range(0, len(token_ids), 16):
        answers += batch_generate(model, tokenizer, token_ids[start : start + 16], max_tokens=max_tokens).texts
    return [answer.strip() for answer in answers]
