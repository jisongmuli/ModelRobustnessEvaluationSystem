"""
模型加载器 - 负责加载和验证 PyTorch 模型
"""
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import torch
import torch.nn as nn
import torchvision.models as models

logger = logging.getLogger(__name__)


SUPPORTED_ARCHITECTURES = {
    "resnet18": lambda num_classes: models.resnet18(weights=None, num_classes=num_classes),
    "resnet34": lambda num_classes: models.resnet34(weights=None, num_classes=num_classes),
    "resnet50": lambda num_classes: models.resnet50(weights=None, num_classes=num_classes),
    "resnet101": lambda num_classes: models.resnet101(weights=None, num_classes=num_classes),
    "vgg16": lambda num_classes: models.vgg16(weights=None, num_classes=num_classes),
    "vgg19": lambda num_classes: models.vgg19(weights=None, num_classes=num_classes),
    "efficientnet_b0": lambda num_classes: models.efficientnet_b0(weights=None, num_classes=num_classes),
    "efficientnet_b1": lambda num_classes: models.efficientnet_b1(weights=None, num_classes=num_classes),
    "mobilenet_v2": lambda num_classes: models.mobilenet_v2(weights=None, num_classes=num_classes),
    "mobilenet_v3_small": lambda num_classes: models.mobilenet_v3_small(weights=None, num_classes=num_classes),
    "densenet121": lambda num_classes: models.densenet121(weights=None, num_classes=num_classes),
}

ARCHITECTURE_HEADS = {
    "resnet18": "fc",
    "resnet34": "fc",
    "resnet50": "fc",
    "resnet101": "fc",
    "vgg16": "classifier",
    "vgg19": "classifier",
    "efficientnet_b0": "classifier",
    "efficientnet_b1": "classifier",
    "mobilenet_v2": "classifier",
    "mobilenet_v3_small": "classifier",
    "densenet121": "classifier",
}

FALLBACK_HEAD_NAMES = ("fc", "classifier", "head")


class CustomFC(nn.Module):
    """自定义分类头，保持原始索引"""

    def __init__(self, layers_dict: Dict[int, nn.Module]):
        super().__init__()
        for idx, layer in layers_dict.items():
            setattr(self, str(idx), layer)
        self.layer_order = sorted(layers_dict.keys())

    def forward(self, x):
        for idx in self.layer_order:
            layer = getattr(self, str(idx))
            x = layer(x)
        return x


class BackboneWrapper(nn.Module):
    """包装模型以支持 backbone 前缀的 state_dict"""

    def __init__(self, backbone: nn.Module):
        super().__init__()
        self.backbone = backbone

    def forward(self, x):
        return self.backbone(x)


class ModelLoader:
    """PyTorch 模型加载器"""

    SUPPORTED_EXTENSIONS = {".pt", ".pth"}

    def __init__(self, device: str = None):
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        logger.info("模型加载器初始化，使用设备: %s", self.device)

    def validate_file(self, file_path: str) -> bool:
        path = Path(file_path)
        if not path.exists():
            logger.error("文件不存在: %s", file_path)
            return False
        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            logger.error("不支持的文件格式: %s", path.suffix)
            return False
        return True

    def _remove_prefix(self, state_dict: Dict[str, torch.Tensor], prefix: str) -> Dict[str, torch.Tensor]:
        new_state_dict = {}
        for key, value in state_dict.items():
            if key.startswith(prefix):
                new_state_dict[key[len(prefix):]] = value
            else:
                new_state_dict[key] = value
        return new_state_dict

    def _get_head_names(self, model_type: Optional[str], override_head_name: Optional[str] = None) -> List[str]:
        names: List[str] = []
        if override_head_name:
            names.append(override_head_name.lower())
        if model_type:
            default_head = ARCHITECTURE_HEADS.get(model_type.lower())
            if default_head:
                names.append(default_head)
        for fallback_name in FALLBACK_HEAD_NAMES:
            if fallback_name not in names:
                names.append(fallback_name)
        return names

    def _find_head_weight_keys(
        self,
        state_dict: Dict[str, torch.Tensor],
        head_name: str,
        prefix: str = ""
    ) -> List[str]:
        head_prefix = f"{prefix}{head_name}."
        indexed_keys: List[Tuple[int, str]] = []
        direct_keys: List[str] = []

        for key, value in state_dict.items():
            if not isinstance(value, torch.Tensor) or len(value.shape) != 2:
                continue
            if not key.startswith(head_prefix) or not key.endswith(".weight"):
                continue

            suffix = key[len(head_prefix):]
            if suffix == "weight":
                direct_keys.append(key)
                continue

            parts = suffix.split(".")
            if len(parts) == 2 and parts[0].isdigit() and parts[1] == "weight":
                indexed_keys.append((int(parts[0]), key))

        if indexed_keys:
            return [key for _, key in sorted(indexed_keys, key=lambda item: item[0])]
        return direct_keys

    def _infer_num_classes(
        self,
        state_dict: Dict[str, torch.Tensor],
        model_type: Optional[str] = None,
        head_name: Optional[str] = None
    ) -> int:
        for prefix in ("", "backbone."):
            for candidate_head in self._get_head_names(model_type, head_name):
                weight_keys = self._find_head_weight_keys(state_dict, candidate_head, prefix)
                if weight_keys:
                    return state_dict[weight_keys[-1]].shape[0]

        for key in sorted(state_dict.keys(), reverse=True):
            value = state_dict[key]
            if not isinstance(value, torch.Tensor) or len(value.shape) != 2 or not key.endswith(".weight"):
                continue
            parts = key.split(".")
            if len(parts) >= 2 and parts[-2] in FALLBACK_HEAD_NAMES:
                return value.shape[0]

        return 10

    def _build_head_from_layer_configs(self, layer_configs: List[Dict[str, Any]]) -> CustomFC:
        layers_dict: Dict[int, nn.Module] = {}
        for raw_config in layer_configs:
            layer_config = raw_config.model_dump() if hasattr(raw_config, "model_dump") else dict(raw_config)
            idx = int(layer_config["index"])
            layer_type = layer_config["layer_type"].lower()

            if layer_type == "linear":
                in_features = layer_config.get("in_features")
                out_features = layer_config.get("out_features")
                if in_features is None or out_features is None:
                    raise ValueError("linear 层必须提供 in_features 和 out_features")
                layers_dict[idx] = nn.Linear(in_features, out_features)
            elif layer_type == "relu":
                layers_dict[idx] = nn.ReLU(inplace=True)
            elif layer_type == "dropout":
                layers_dict[idx] = nn.Dropout(layer_config.get("dropout_p", 0.5))
            elif layer_type == "identity":
                layers_dict[idx] = nn.Identity()
            else:
                raise ValueError(f"不支持的层类型: {layer_type}")

        if not layers_dict:
            raise ValueError("fc_layers 不能为空")
        return CustomFC(layers_dict)

    def _detect_head_structure(
        self,
        state_dict: Dict[str, torch.Tensor],
        head_name: str,
        prefix: str = ""
    ) -> Optional[nn.Module]:
        head_prefix = f"{prefix}{head_name}."
        head_keys = [key for key in state_dict.keys() if key.startswith(head_prefix)]
        if not head_keys:
            return None

        has_sequential = False
        for key in head_keys:
            suffix = key[len(head_prefix):]
            parts = suffix.split(".")
            if len(parts) >= 2 and parts[0].isdigit():
                has_sequential = True
                break
        if not has_sequential:
            return None

        layer_info: Dict[int, Dict[str, torch.Tensor]] = {}
        for key in head_keys:
            suffix = key[len(head_prefix):]
            parts = suffix.split(".")
            if len(parts) < 2 or not parts[0].isdigit():
                continue
            idx = int(parts[0])
            layer_info.setdefault(idx, {})
            if parts[1] == "weight":
                layer_info[idx]["weight"] = state_dict[key]
            elif parts[1] == "bias":
                layer_info[idx]["bias"] = state_dict[key]

        if not layer_info:
            return None

        min_idx = min(layer_info.keys())
        max_idx = max(layer_info.keys())
        layers_dict: Dict[int, nn.Module] = {}

        for idx in range(min_idx, max_idx + 1):
            if idx in layer_info and "weight" in layer_info[idx]:
                weight = layer_info[idx]["weight"]
                if len(weight.shape) == 2:
                    out_features, in_features = weight.shape
                    layers_dict[idx] = nn.Linear(in_features, out_features)
                    logger.info("检测到 %s.%s: Linear(%s, %s)", head_name, idx, in_features, out_features)
            else:
                if idx == min_idx:
                    layers_dict[idx] = nn.Identity()
                    logger.info("检测到 %s.%s: Identity", head_name, idx)
                elif idx == max_idx - 1:
                    layers_dict[idx] = nn.Dropout(0.5)
                    logger.info("检测到 %s.%s: Dropout", head_name, idx)
                else:
                    layers_dict[idx] = nn.ReLU(inplace=True)
                    logger.info("检测到 %s.%s: ReLU", head_name, idx)

        return CustomFC(layers_dict) if layers_dict else None

    def _get_last_linear_layer(self, module: Optional[nn.Module]) -> Optional[nn.Linear]:
        if module is None:
            return None
        if isinstance(module, nn.Linear):
            return module
        if isinstance(module, CustomFC):
            for idx in reversed(module.layer_order):
                layer = getattr(module, str(idx))
                if isinstance(layer, nn.Linear):
                    return layer
            return None
        if isinstance(module, nn.Sequential):
            for layer in reversed(list(module.children())):
                if isinstance(layer, nn.Linear):
                    return layer
        return None

    def load_model(self, file_path, model_class=None, model_config=None):
        if not self.validate_file(file_path):
            raise ValueError('无效的模型文件')
        import zipfile
        if zipfile.is_zipfile(file_path):
            with zipfile.ZipFile(file_path) as archive:
                if any(name.endswith('/constants.pkl') for name in archive.namelist()):
                    raise ValueError('上传接口只接收权重 checkpoint；请在可信环境中将 TorchScript 导出为 state_dict')
        try:
            checkpoint = torch.load(file_path, map_location='cpu', weights_only=True)
        except Exception as error:
            raise ValueError('无法安全读取权重；请上传 state_dict 或仅含张量和基础元数据的 checkpoint') from error
        if not isinstance(checkpoint, dict):
            raise ValueError('仅支持 state_dict / checkpoint，不支持序列化 Python 模型对象')
        config = model_config or {}
        state_dict = checkpoint.get('model_state_dict', checkpoint.get('state_dict', checkpoint.get('model', checkpoint)))
        if not isinstance(state_dict, dict) or not state_dict or not all(isinstance(k, str) and isinstance(v, torch.Tensor) for k, v in state_dict.items()):
            raise ValueError('checkpoint 中没有有效的 state_dict')
        state_dict = self._remove_prefix(state_dict, 'module.')
        has_backbone = all(key.startswith('backbone.') for key in state_dict)
        bare_state = self._remove_prefix(state_dict, 'backbone.') if has_backbone else state_dict
        model_type = config.get('model_type') or checkpoint.get('model_type') or self._detect_model_type(bare_state)
        if model_type:
            model_type = str(model_type).lower()
        img_size = config.get('img_size') or checkpoint.get('img_size') or 224
        if not isinstance(img_size, int) or not 16 <= img_size <= 1024:
            raise ValueError('输入图像尺寸必须为 16–1024 的整数')
        num_classes = config.get('num_classes') or self._infer_num_classes(bare_state, model_type)
        if model_type in SUPPORTED_ARCHITECTURES:
            base_model = SUPPORTED_ARCHITECTURES[model_type](num_classes)
            head_name = self._get_head_names(model_type, config.get('head_name'))[0]
            if config.get('has_custom_fc'):
                if not config.get('fc_layers'):
                    raise ValueError('自定义分类头必须明确提供 fc_layers，不能从权重猜测激活层')
                custom_head = self._build_head_from_layer_configs(config['fc_layers'])
                setattr(base_model, head_name, custom_head)
                last_linear = self._get_last_linear_layer(custom_head)
                if last_linear is None or last_linear.out_features != num_classes:
                    raise ValueError('分类头输出维度与 num_classes 不一致')
            model = BackboneWrapper(base_model) if has_backbone else base_model
        elif model_class is not None:
            model = model_class()
            state_dict = bare_state
            model_type = model.__class__.__name__
            head_name = None
        else:
            raise ValueError('无法唯一识别模型结构，请在模型配置中选择实际架构与分类头')
        try:
            model.load_state_dict(state_dict, strict=True)
        except RuntimeError as error:
            raise ValueError('模型结构与权重不一致或权重不完整，请补充正确配置；不会使用随机权重继续评测') from error
        model = model.to(self.device).eval()
        info = dict(model_type=model_type, num_classes=num_classes, img_size=img_size,
                    input_shape=[1, 3, img_size, img_size], is_jit=False, head_name=head_name)
        return model, info

    def _detect_model_type(self, state_dict):
        import re
        keys = set(state_dict)
        # All block counts distinguish ResNet-18/34/50/101; the first 40 keys do not.
        counts = []
        for layer in range(1, 5):
            indices = [int(match.group(1)) for key in keys
                       if (match := re.match(rf'^layer{layer}\.(\d+)\.conv1\.weight$', key))]
            counts.append(max(indices) + 1 if indices else 0)
        bottleneck = any(re.match(r'^layer\d+\.\d+\.conv3\.weight$', key) for key in keys)
        resnets = {(False, (2, 2, 2, 2)): 'resnet18', (False, (3, 4, 6, 3)): 'resnet34',
                   (True, (3, 4, 6, 3)): 'resnet50', (True, (3, 4, 23, 3)): 'resnet101'}
        if (bottleneck, tuple(counts)) in resnets:
            return resnets[bottleneck, tuple(counts)]
        if 'features.denseblock1.denselayer1.conv1.weight' in keys:
            return 'densenet121'
        if 'features.1.conv.0.0.weight' in keys and 'features.18.0.weight' in keys:
            return 'mobilenet_v2'
        if 'features.0.weight' in keys and 'classifier.6.weight' in keys:
            conv_count = sum(key.startswith('features.') and key.endswith('.weight') and value.ndim == 4 for key, value in state_dict.items())
            return {13: 'vgg16', 16: 'vgg19'}.get(conv_count)
        # Similar MobileNet/EfficientNet variants require explicit metadata/config.
        return None

    def _update_model_info(self, model: nn.Module, info: Dict[str, Any]) -> None:
        try:
            target_model = model.backbone if hasattr(model, "backbone") else model
            head_name = info.get("head_name")

            if info.get("num_classes") is None:
                head_candidates = self._get_head_names(info.get("model_type"), head_name)
                for candidate_head in head_candidates:
                    if hasattr(target_model, candidate_head):
                        last_linear = self._get_last_linear_layer(getattr(target_model, candidate_head))
                        if last_linear is not None:
                            info["num_classes"] = last_linear.out_features
                            break
        except Exception as error:
            logger.debug("无法推断类别数: %s", error)

    def get_sample_input(self, input_shape: Tuple[int, ...] = (1, 3, 224, 224)) -> torch.Tensor:
        return torch.randn(input_shape, device=self.device)


_model_loader: Optional[ModelLoader] = None


def get_model_loader() -> ModelLoader:
    global _model_loader
    if _model_loader is None:
        _model_loader = ModelLoader()
    return _model_loader
