"""Fine-tuning backend for any machine, built on PyTorch, transformers and peft.

The training loop is the one of module 13: compute the loss, compute the gradients, move the parameters.
"""

import os
import random
from pathlib import Path

import torch
from peft import LoraConfig, PeftModel, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

BATCH_SIZE = 8
LEARNING_RATE = 5e-4


def device() -> str:
    """NVIDIA card if there is one, Apple GPU otherwise, processor as a last resort. FINETUNE_DEVICE overrides."""
    if forced := os.environ.get("FINETUNE_DEVICE"):
        return forced
    if torch.cuda.is_available():
        return "cuda"
    return "mps" if torch.backends.mps.is_available() else "cpu"


def _load(base_model: str):
    # The model is published in 16-bit floats, which processors compute very slowly: 32-bit is far faster there.
    return AutoModelForCausalLM.from_pretrained(base_model, dtype=torch.float32)


def _encode(tokenizer, example: dict) -> tuple[list[int], list[int]]:
    """Token ids of a whole example, and the labels: -100 hides the prompt so only the answer is learned."""
    prompt = tokenizer.apply_chat_template(example["messages"][:-1], add_generation_prompt=True, tokenize=False)
    full = tokenizer.apply_chat_template(example["messages"], tokenize=False)
    prompt_ids = tokenizer(prompt, add_special_tokens=False).input_ids
    answer_ids = tokenizer(full[len(prompt) :], add_special_tokens=False).input_ids
    return prompt_ids + answer_ids, [-100] * len(prompt_ids) + answer_ids


def _batch(tokenizer, examples: list[dict], target: str) -> dict[str, torch.Tensor]:
    encoded = [_encode(tokenizer, example) for example in examples]
    width = max(len(ids) for ids, _ in encoded)
    pad = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else tokenizer.eos_token_id
    return {
        "input_ids": torch.tensor([ids + [pad] * (width - len(ids)) for ids, _ in encoded], device=target),
        "attention_mask": torch.tensor([[1] * len(ids) + [0] * (width - len(ids)) for ids, _ in encoded], device=target),
        "labels": torch.tensor([labels + [-100] * (width - len(labels)) for _, labels in encoded], device=target),
    }


def train(base_model: str, train_examples: list[dict], valid_examples: list[dict], out_dir: Path, iters: int) -> None:
    target = device()
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    model = _load(base_model).to(target)
    # LoRA: the base weights are frozen, small matrices added to the attention layers are trained instead.
    lora = LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj", "k_proj", "v_proj", "o_proj"], task_type="CAUSAL_LM")
    model = get_peft_model(model, lora)
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"Paramètres entraînés : {trainable:,} sur {total:,} ({trainable / total:.2%}), sur {target}")

    optimizer = torch.optim.AdamW((p for p in model.parameters() if p.requires_grad), lr=LEARNING_RATE)
    picker = random.Random(0)
    model.train()
    running = 0.0
    for step in range(1, iters + 1):
        loss = model(**_batch(tokenizer, picker.sample(train_examples, BATCH_SIZE), target)).loss
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        running += loss.item()
        if step % 25 == 0:
            print(f"  itération {step:4d}   perte d'entraînement {running / 25:.3f}")
            running = 0.0
        if step % 100 == 0 or step == iters:
            model.eval()
            with torch.no_grad():
                batches = [valid_examples[i : i + BATCH_SIZE] for i in range(0, min(len(valid_examples), 80), BATCH_SIZE)]
                validation = sum(model(**_batch(tokenizer, batch, target)).loss.item() for batch in batches) / len(batches)
            print(f"  itération {step:4d}   perte de validation   {validation:.3f}")
            model.train()
    model.save_pretrained(out_dir)


def generate(base_model: str, prompts: list[list[dict]], adapter_dir: Path | None, max_tokens: int) -> list[str]:
    target = device()
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    model = _load(base_model)
    if adapter_dir:
        model = PeftModel.from_pretrained(model, adapter_dir)
    model.to(target).eval()
    answers = []
    for messages in prompts:
        prompt = tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
        inputs = tokenizer(prompt, add_special_tokens=False, return_tensors="pt").to(target)
        with torch.no_grad():
            output = model.generate(**inputs, max_new_tokens=max_tokens, do_sample=False, pad_token_id=tokenizer.eos_token_id)
        answers.append(tokenizer.decode(output[0, inputs.input_ids.shape[1] :], skip_special_tokens=True).strip())
    return answers
