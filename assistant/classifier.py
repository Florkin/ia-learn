"""Training a small classifier on embeddings: reference brick for module 13.

Task: predict the documentation section ("Security", "Database"...) a passage comes from, given its embedding.
"""

from dataclasses import dataclass

import numpy as np
import torch
from torch import nn

from assistant.embeddings import embed
from assistant.store import reference_index


@dataclass
class Dataset:
    X_train: torch.Tensor  # (n, 1024) embeddings
    y_train: torch.Tensor  # (n,) index of the section in `labels`
    X_val: torch.Tensor
    y_val: torch.Tensor
    labels: list[str]


def load_dataset(seed: int = 0, validation_share: float = 0.2) -> Dataset:
    """Embeddings and sections of every passage of the reference index, shuffled and split in two."""
    stored = reference_index().get(include=["embeddings", "metadatas"])
    sections = [metadata["section"] for metadata in stored["metadatas"]]
    labels = sorted(set(sections))
    X = torch.tensor(np.array(stored["embeddings"], dtype=np.float32))
    y = torch.tensor([labels.index(section) for section in sections])
    order = torch.randperm(len(y), generator=torch.Generator().manual_seed(seed))
    cut = int(len(y) * (1 - validation_share))
    train, val = order[:cut], order[cut:]
    return Dataset(X[train], y[train], X[val], y[val], labels)


def make_model(n_features: int, n_classes: int, hidden: int = 0) -> nn.Module:
    """One linear layer, or two with a hidden layer in between when `hidden` > 0."""
    if hidden == 0:
        return nn.Linear(n_features, n_classes)
    return nn.Sequential(nn.Linear(n_features, hidden), nn.ReLU(), nn.Linear(hidden, n_classes))


def accuracy(model: nn.Module, X: torch.Tensor, y: torch.Tensor) -> float:
    model.eval()
    with torch.no_grad():
        return (model(X).argmax(dim=1) == y).float().mean().item()


def predict(model: nn.Module, labels: list[str], text: str) -> str:
    model.eval()
    with torch.no_grad():
        return labels[model(torch.tensor(embed([text]))).argmax(dim=1).item()]


# --- Module 13: the training loop ------------------------------------------------------------


def train(model: nn.Module, data: Dataset, epochs: int = 30, lr: float = 1e-2, batch_size: int = 64) -> list[dict]:
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_function = nn.CrossEntropyLoss()
    history = []
    for epoch in range(1, epochs + 1):
        model.train()
        order = torch.randperm(len(data.X_train))
        for start in range(0, len(order), batch_size):
            batch = order[start : start + batch_size]
            loss = loss_function(model(data.X_train[batch]), data.y_train[batch])
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        model.eval()
        with torch.no_grad():
            history.append(
                {
                    "epoch": epoch,
                    "train_loss": loss_function(model(data.X_train), data.y_train).item(),
                    "val_loss": loss_function(model(data.X_val), data.y_val).item(),
                    "val_accuracy": accuracy(model, data.X_val, data.y_val),
                }
            )
    return history
