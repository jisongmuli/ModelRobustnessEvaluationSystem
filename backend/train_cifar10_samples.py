from __future__ import annotations

import argparse
import json
import random
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms

DATA_DIR = Path(__file__).parent / "data"
UPLOAD_DIR = Path(__file__).parent / "uploads"
RESULTS_DIR = Path(__file__).parent / "results"
MODELS_DB_FILE = UPLOAD_DIR / "models_db.json"
MODEL_CONFIGS_DB_FILE = UPLOAD_DIR / "model_configs_db.json"
RESULTS_SUMMARY_FILE = RESULTS_DIR / "trained_cifar10_models.json"

UPLOAD_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

MODEL_BUILDERS = {
    "resnet18": lambda: models.resnet18(weights=None, num_classes=10),
    "resnet34": lambda: models.resnet34(weights=None, num_classes=10),
    "efficientnet_b0": lambda: models.efficientnet_b0(weights=None, num_classes=10),
    "mobilenet_v2": lambda: models.mobilenet_v2(weights=None, num_classes=10),
    "mobilenet_v3_small": lambda: models.mobilenet_v3_small(weights=None, num_classes=10),
}

DEFAULT_EXPORT_FORMATS = ("checkpoint", "lite", "jit")


@dataclass
class ExportArtifact:
    variant: str
    model_id: str
    filename: str
    path: str
    model_type: str
    img_size: int
    num_classes: int
    is_primary: bool = False


@dataclass
class TrainResult:
    model_id: str
    model_type: str
    epochs: int
    train_loss: float
    train_acc: float
    test_acc: float
    save_path: str
    img_size: int = 32
    num_classes: int = 10
    tag: str = ""
    artifacts: List[ExportArtifact] = field(default_factory=list)


def seed_everything(seed: int = 42):
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def get_device() -> torch.device:
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def load_json(path: Path) -> Dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path: Path, data: Dict):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def make_loaders(batch_size: int, num_workers: int):
    train_transform = transforms.Compose([
        transforms.RandomCrop(32, padding=4),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ])
    test_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ])

    train_dataset = datasets.CIFAR10(root=str(DATA_DIR), train=True, download=False, transform=train_transform)
    test_dataset = datasets.CIFAR10(root=str(DATA_DIR), train=False, download=False, transform=test_transform)

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        persistent_workers=num_workers > 0,
    )
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        persistent_workers=num_workers > 0,
    )
    return train_loader, test_loader


def evaluate(model: nn.Module, loader: DataLoader, device: torch.device):
    model.eval()
    total = 0
    correct = 0
    loss_sum = 0.0
    criterion = nn.CrossEntropyLoss()
    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device)
            labels = labels.to(device)
            logits = model(images)
            loss = criterion(logits, labels)
            loss_sum += loss.item() * labels.size(0)
            correct += (logits.argmax(dim=1) == labels).sum().item()
            total += labels.size(0)
    return loss_sum / max(total, 1), correct / max(total, 1)


def export_artifacts(
    model_name: str,
    best_state: Dict[str, torch.Tensor],
    img_size: int,
    num_classes: int,
    metrics: Dict[str, float],
    tag: str,
    export_formats: Iterable[str],
) -> tuple[str, List[ExportArtifact]]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    tag_part = f"_{tag}" if tag else ""
    model_id = f"model_cifar10_{model_name}{tag_part}_{timestamp}"

    artifacts: List[ExportArtifact] = []

    def add_artifact(variant: str, path: Path, exported_model_type: str, is_primary: bool = False):
        artifacts.append(
            ExportArtifact(
                variant=variant,
                model_id=model_id if is_primary else f"{model_id}_{variant}",
                filename=path.name,
                path=str(path),
                model_type=exported_model_type,
                img_size=img_size,
                num_classes=num_classes,
                is_primary=is_primary,
            )
        )

    export_formats = tuple(export_formats)
    primary_variant = "checkpoint" if "checkpoint" in export_formats else export_formats[0]

    if "checkpoint" in export_formats:
        path = UPLOAD_DIR / f"{model_id}.pth"
        torch.save(
            {
                "model_state_dict": best_state,
                "model_type": model_name,
                "img_size": img_size,
                "metrics": metrics,
            },
            path,
        )
        add_artifact("checkpoint", path, model_name, is_primary=(primary_variant == "checkpoint"))

    if "lite" in export_formats:
        path = UPLOAD_DIR / f"{model_id}_lite.pth"
        torch.save(best_state, path)
        add_artifact("lite", path, model_name, is_primary=(primary_variant == "lite"))

    if "jit" in export_formats:
        path = UPLOAD_DIR / f"{model_id}_jit.pt"
        model = MODEL_BUILDERS[model_name]()
        model.load_state_dict(best_state)
        model.eval()
        scripted = torch.jit.trace(model, torch.randn(1, 3, img_size, img_size))
        scripted.save(str(path))
        add_artifact("jit", path, "TorchScript", is_primary=(primary_variant == "jit"))

    primary_artifact = next(item for item in artifacts if item.is_primary)
    return primary_artifact.model_id, artifacts


def train_one_model(
    model_name: str,
    epochs: int,
    batch_size: int,
    lr: float,
    num_workers: int,
    device: torch.device,
    tag: str,
    export_formats: Iterable[str],
) -> TrainResult:
    train_loader, test_loader = make_loaders(batch_size=batch_size, num_workers=num_workers)
    model = MODEL_BUILDERS[model_name]().to(device)
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    best_state = None
    best_test_acc = -1.0
    last_train_loss = 0.0
    last_train_acc = 0.0

    print(f"\n=== Training {model_name} on {device} ===", flush=True)
    for epoch in range(1, epochs + 1):
        model.train()
        total = 0
        correct = 0
        loss_sum = 0.0
        for step, (images, labels) in enumerate(train_loader, start=1):
            images = images.to(device)
            labels = labels.to(device)

            optimizer.zero_grad(set_to_none=True)
            logits = model(images)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()

            loss_sum += loss.item() * labels.size(0)
            correct += (logits.argmax(dim=1) == labels).sum().item()
            total += labels.size(0)

            if step % 100 == 0 or step == len(train_loader):
                print(
                    f"[{model_name}] epoch {epoch}/{epochs} step {step}/{len(train_loader)} "
                    f"loss={loss_sum / max(total, 1):.4f} acc={correct / max(total, 1):.4f}",
                    flush=True,
                )

        scheduler.step()
        last_train_loss = loss_sum / max(total, 1)
        last_train_acc = correct / max(total, 1)
        test_loss, test_acc = evaluate(model, test_loader, device)
        print(
            f"[{model_name}] epoch {epoch} done train_loss={last_train_loss:.4f} "
            f"train_acc={last_train_acc:.4f} test_loss={test_loss:.4f} test_acc={test_acc:.4f}",
            flush=True,
        )

        if test_acc > best_test_acc:
            best_test_acc = test_acc
            best_state = {key: value.detach().cpu() for key, value in model.state_dict().items()}

    metrics = {
        "train_loss": last_train_loss,
        "train_acc": last_train_acc,
        "test_acc": best_test_acc,
        "epochs": epochs,
    }
    model_id, artifacts = export_artifacts(
        model_name=model_name,
        best_state=best_state,
        img_size=32,
        num_classes=10,
        metrics=metrics,
        tag=tag,
        export_formats=export_formats,
    )
    primary_artifact = next(item for item in artifacts if item.is_primary)

    return TrainResult(
        model_id=model_id,
        model_type=model_name,
        epochs=epochs,
        train_loss=last_train_loss,
        train_acc=last_train_acc,
        test_acc=best_test_acc,
        save_path=primary_artifact.path,
        tag=tag,
        artifacts=artifacts,
    )


def register_results(results: Iterable[TrainResult]):
    models_db = load_json(MODELS_DB_FILE)
    model_configs_db = load_json(MODEL_CONFIGS_DB_FILE)
    summary = load_json(RESULTS_SUMMARY_FILE)
    now = datetime.now().isoformat()

    for result in results:
        summary[result.model_id] = {
            **asdict(result),
            "artifacts": [asdict(item) for item in result.artifacts],
        }
        for artifact in result.artifacts:
            save_path = Path(artifact.path)
            models_db[artifact.model_id] = {
                "id": artifact.model_id,
                "filename": artifact.filename,
                "file_size": save_path.stat().st_size,
                "upload_time": now,
                "model_type": artifact.model_type,
                "num_classes": artifact.num_classes,
                "input_shape": [1, 3, artifact.img_size, artifact.img_size],
                "img_size": artifact.img_size,
                "status": "ready",
                "load_error": None,
            }
            model_configs_db.pop(artifact.model_id, None)

    save_json(MODELS_DB_FILE, models_db)
    save_json(MODEL_CONFIGS_DB_FILE, model_configs_db)
    save_json(RESULTS_SUMMARY_FILE, summary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--models",
        nargs="+",
        default=["resnet18", "mobilenet_v2", "mobilenet_v3_small"],
    )
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--num-workers", type=int, default=2)
    parser.add_argument("--tag", default="")
    parser.add_argument(
        "--export-formats",
        nargs="+",
        default=list(DEFAULT_EXPORT_FORMATS),
        choices=list(DEFAULT_EXPORT_FORMATS),
    )
    args = parser.parse_args()

    seed_everything(42)
    device = get_device()
    print(f"Using device: {device}", flush=True)

    results: List[TrainResult] = []
    for model_name in args.models:
        if model_name not in MODEL_BUILDERS:
            raise ValueError(f"Unsupported model: {model_name}")
        results.append(
            train_one_model(
                model_name=model_name,
                epochs=args.epochs,
                batch_size=args.batch_size,
                lr=args.lr,
                num_workers=args.num_workers,
                device=device,
                tag=args.tag,
                export_formats=args.export_formats,
            )
        )

    register_results(results)
    print("\nTraining complete:")
    print(json.dumps([asdict(item) for item in results], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
