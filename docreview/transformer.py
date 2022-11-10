import hashlib, json, random
from pathlib import Path

SOURCE_REPOSITORY = "distilbert/distilbert-base-uncased"
SOURCE_REVISION = "043235d6088ecd3dd5fb5ca3592b6913fd516027"

from dataclasses import dataclass, asdict
import math


@dataclass(frozen=True)
class TrainingConfig:
    epochs: int = 3
    batch_size: int = 4
    max_length: int = 128
    learning_rate: float = 3e-5
    seed: int = 17
    threads: int = 2

    def __post_init__(self):
        if (
            not 1 <= self.epochs <= 20
            or not 1 <= self.batch_size <= 32
            or not 16 <= self.max_length <= 512
            or not math.isfinite(self.learning_rate)
            or not 0 < self.learning_rate <= 0.01
            or not 1 <= self.threads <= 4
        ):
            raise ValueError("Invalid training budget")


class TransformerClassifier:
    def __init__(self, directory, threads=2):
        from .artifacts import verify

        verify(directory)
        import torch
        from transformers import (
            DistilBertTokenizerFast,
            DistilBertForSequenceClassification,
        )

        torch.set_num_threads(threads)
        self.torch = torch
        self.tokenizer = DistilBertTokenizerFast.from_pretrained(
            directory, local_files_only=True
        )
        self.model = DistilBertForSequenceClassification.from_pretrained(
            directory, local_files_only=True
        )
        self.model.eval()
        self.metadata = json.loads((Path(directory) / "training.json").read_text())
        self.labels = self.metadata["labels"]

    def predict(self, texts, temperature=1.0):
        if (
            not isinstance(texts, list)
            or not 1 <= len(texts) <= 128
            or any(
                not isinstance(t, str) or not t.strip() or len(t) > 100000
                for t in texts
            )
        ):
            raise ValueError("Supply 1 to 128 nonempty bounded texts")
        if not math.isfinite(temperature) or temperature <= 0:
            raise ValueError("Invalid temperature")
        results = []
        with self.torch.no_grad():
            for start in range(0, len(texts), 4):
                encoded = self.tokenizer(
                    texts[start : start + 4],
                    padding=True,
                    truncation=True,
                    max_length=self.metadata["config"]["max_length"],
                    return_tensors="pt",
                )
                logits = self.model(**encoded).logits
                probabilities = self.torch.softmax(
                    logits / temperature, dim=-1
                ).tolist()
                for scores in probabilities:
                    index = max(range(len(scores)), key=scores.__getitem__)
                    results.append(
                        {
                            "label": self.labels[index],
                            "confidence": scores[index],
                            "probabilities": dict(zip(self.labels, scores)),
                        }
                    )
        return results


def train_transformer(rows, source, output, config=None):
    config = config or TrainingConfig()
    labels = sorted({r["label"] for r in rows})
    if len(labels) < 2:
        raise ValueError("Training requires at least two classes")
    if any(not r["text"].strip() for r in rows):
        raise ValueError("Empty training text")
    manifest = verify_source(source)
    import numpy as np
    import torch
    from transformers import (
        DistilBertTokenizerFast,
        DistilBertForSequenceClassification,
    )

    torch.set_num_threads(config.threads)
    torch.manual_seed(config.seed)
    np.random.seed(config.seed)
    random.seed(config.seed)
    tokenizer = DistilBertTokenizerFast.from_pretrained(source, local_files_only=True)
    model = DistilBertForSequenceClassification.from_pretrained(
        source,
        num_labels=len(labels),
        id2label=dict(enumerate(labels)),
        label2id={label: i for i, label in enumerate(labels)},
        local_files_only=True,
    )
    encoded = tokenizer(
        [r["text"] for r in rows],
        padding=True,
        truncation=True,
        max_length=config.max_length,
        return_tensors="pt",
    )
    targets = torch.tensor([labels.index(r["label"]) for r in rows])
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate)
    generator = torch.Generator().manual_seed(config.seed)
    history = []
    model.train()
    for epoch in range(config.epochs):
        losses = []
        for indices in torch.randperm(len(rows), generator=generator).split(
            config.batch_size
        ):
            optimizer.zero_grad()
            batch = {k: v[indices] for k, v in encoded.items()}
            loss = model(**batch, labels=targets[indices]).loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            losses.append(float(loss.detach()))
        history.append(sum(losses) / len(losses))
        print(json.dumps({"epoch": epoch + 1, "loss": history[-1]}), flush=True)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(output)
    tokenizer.save_pretrained(output)
    metadata = {
        "source_revision": manifest["revision"],
        "labels": labels,
        "config": asdict(config),
        "train_ids": [r["id"] for r in rows],
        "train_families": sorted({r["family"] for r in rows}),
        "loss": history,
    }
    (output / "training.json").write_text(json.dumps(metadata, indent=2))
    from .artifacts import seal

    seal(output)
    return metadata


def verify_source(directory):
    directory = Path(directory)
    manifest = json.loads((directory / "source-manifest.json").read_text())
    if len(manifest["revision"]) != 40 or not manifest["files"]:
        raise ValueError("Invalid source manifest")
    for filename, metadata in manifest["files"].items():
        path = (directory / filename).resolve()
        if (
            not path.is_relative_to(directory.resolve())
            or hashlib.sha256(path.read_bytes()).hexdigest() != metadata["sha256"]
        ):
            raise ValueError("Transformer source checksum mismatch")
    return manifest
