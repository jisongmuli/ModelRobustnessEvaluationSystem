"""生成可直接用于当前鲁棒性平台的示例模型文件。"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import torch
import torchvision.models as models

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
MODELS_DB_FILE = UPLOAD_DIR / "models_db.json"
MODEL_CONFIGS_DB_FILE = UPLOAD_DIR / "model_configs_db.json"
MODEL_EXTENSIONS = (".pth", ".pt")

SAMPLE_SPECS = [
    {
        "id": "model_demo_resnet18",
        "filename": "demo_resnet18_cifar10.pth",
        "model_type": "resnet18",
        "img_size": 32,
        "builder": lambda: models.resnet18(weights=None, num_classes=10),
        "format": "pth",
    },
    {
        "id": "model_demo_mobilenetv2",
        "filename": "demo_mobilenet_v2_cifar10.pth",
        "model_type": "mobilenet_v2",
        "img_size": 32,
        "builder": lambda: models.mobilenet_v2(weights=None, num_classes=10),
        "format": "pth",
    },
    {
        "id": "model_demo_efficientnetb0",
        "filename": "demo_efficientnet_b0_cifar10.pth",
        "model_type": "efficientnet_b0",
        "img_size": 32,
        "builder": lambda: models.efficientnet_b0(weights=None, num_classes=10),
        "format": "pth",
    },
    {
        "id": "model_demo_resnet18_jit",
        "filename": "demo_resnet18_cifar10_torchscript.pt",
        "model_type": "TorchScript",
        "img_size": 32,
        "builder": lambda: models.resnet18(weights=None, num_classes=10),
        "format": "pt",
    },
]


def load_json(path: Path):
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path: Path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def make_checkpoint(model, model_type: str, img_size: int):
    return {
        "model_state_dict": model.state_dict(),
        "model_type": model_type,
        "img_size": img_size,
    }


def file_exists_for_model(model_id: str) -> bool:
    return any((UPLOAD_DIR / f"{model_id}{ext}").exists() for ext in MODEL_EXTENSIONS)


def create_samples():
    torch.manual_seed(42)
    models_db = load_json(MODELS_DB_FILE)
    model_configs_db = load_json(MODEL_CONFIGS_DB_FILE)

    for model_id in list(models_db.keys()):
        if not file_exists_for_model(model_id):
            models_db.pop(model_id, None)
            model_configs_db.pop(model_id, None)

    created = []
    now = datetime.now().isoformat()

    for spec in SAMPLE_SPECS:
        model = spec["builder"]()
        model.eval()
        file_ext = spec["format"]
        save_path = UPLOAD_DIR / f"{spec['id']}.{file_ext}"

        if file_ext == "pth":
            payload = make_checkpoint(model, spec["model_type"], spec["img_size"])
            torch.save(payload, save_path)
        else:
            example = torch.randn(1, 3, spec["img_size"], spec["img_size"])
            scripted = torch.jit.trace(model, example)
            scripted.save(str(save_path))

        file_size = save_path.stat().st_size
        models_db[spec["id"]] = {
            "id": spec["id"],
            "filename": spec["filename"],
            "file_size": file_size,
            "upload_time": now,
            "model_type": spec["model_type"],
            "num_classes": 10,
            "input_shape": [1, 3, spec["img_size"], spec["img_size"]],
            "img_size": spec["img_size"],
            "status": "ready",
            "load_error": None,
        }
        model_configs_db.pop(spec["id"], None)
        created.append({
            "id": spec["id"],
            "path": str(save_path),
            "size_mb": round(file_size / 1024 / 1024, 2),
            "model_type": spec["model_type"],
        })

    save_json(MODELS_DB_FILE, models_db)
    save_json(MODEL_CONFIGS_DB_FILE, model_configs_db)
    return created


if __name__ == "__main__":
    result = create_samples()
    print(json.dumps(result, indent=2, ensure_ascii=False))
