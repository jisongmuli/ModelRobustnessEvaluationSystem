"""
对抗攻击引擎 - 执行各类对抗攻击
"""
import torch
import torch.nn as nn
import torchattacks
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
import logging
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class AttackResult:
    """攻击结果"""
    attack_type: str
    eps: float
    clean_accuracy: float
    robust_accuracy: float
    attack_success_rate: float
    avg_perturbation_l2: float
    avg_perturbation_linf: float
    avg_confidence_drop: float
    num_samples: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attack_type": self.attack_type,
            "eps": self.eps,
            "clean_accuracy": round(self.clean_accuracy, 4),
            "robust_accuracy": round(self.robust_accuracy, 4),
            "attack_success_rate": round(self.attack_success_rate, 4),
            "avg_perturbation_l2": round(self.avg_perturbation_l2, 4),
            "avg_perturbation_linf": round(self.avg_perturbation_linf, 4),
            "avg_confidence_drop": round(self.avg_confidence_drop, 4),
            "num_samples": self.num_samples
        }


class AttackEngine:
    """对抗攻击引擎"""

    SUPPORTED_ATTACKS = {
        "fgsm": "FGSM",
        "pgd": "PGD",
        "bim": "BIM",
        "cw": "CW",
        "deepfool": "DeepFool"
    }

    def __init__(self, model: nn.Module, device: torch.device = None):
        """
        初始化攻击引擎

        Args:
            model: 目标模型
            device: 计算设备
        """
        self.model = model
        self.device = device or torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self.model.to(self.device)
        self.model.eval()

    def create_attack(self, attack_type: str, eps: float = 0.03,
                      steps: int = 10, alpha: float = None):
        """
        创建攻击实例

        Args:
            attack_type: 攻击类型
            eps: 扰动强度
            steps: 迭代步数
            alpha: 步长

        Returns:
            攻击实例
        """
        attack_type = attack_type.lower()

        if attack_type not in self.SUPPORTED_ATTACKS:
            raise ValueError(f"不支持的攻击类型: {attack_type}，支持: {list(self.SUPPORTED_ATTACKS.keys())}")

        if alpha is None:
            alpha = eps / max(steps, 1) * 2

        if attack_type == "fgsm":
            return torchattacks.FGSM(self.model, eps=eps)
        elif attack_type == "pgd":
            return torchattacks.PGD(self.model, eps=eps, alpha=alpha, steps=steps)
        elif attack_type == "bim":
            return torchattacks.BIM(self.model, eps=eps, alpha=alpha, steps=steps)
        elif attack_type == "cw":
            return torchattacks.CW(self.model, c=1, kappa=0, steps=steps, lr=0.01)
        elif attack_type == "deepfool":
            return torchattacks.DeepFool(self.model, steps=steps)
        else:
            raise ValueError(f"未实现的攻击类型: {attack_type}")

    def evaluate(
        self,
        attack,
        dataloader: torch.utils.data.DataLoader,
        attack_type: str,
        eps: float,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> AttackResult:
        """
        评估攻击效果

        Args:
            attack: 攻击实例
            dataloader: 数据加载器
            attack_type: 攻击类型名称
            eps: 扰动强度
            progress_callback: 进度回调函数

        Returns:
            攻击结果
        """
        self.model.eval()

        total_samples = 0
        clean_correct = 0
        robust_correct = 0
        attack_success = 0

        total_l2_perturbation = 0.0
        total_linf_perturbation = 0.0
        total_confidence_drop = 0.0

        total_batches = len(dataloader)
        if total_batches == 0:
            raise ValueError("数据集中没有可评测的样本")

        with torch.no_grad():
            for batch_idx, (images, labels) in enumerate(dataloader):
                images = images.to(self.device)
                labels = labels.to(self.device)
                batch_size = images.size(0)
                if not torch.isfinite(images).all() or images.min() < 0 or images.max() > 1:
                    raise ValueError("攻击输入必须为 [0, 1] 范围内的有限像素值")

                # 原始预测
                clean_outputs = self.model(images)
                if clean_outputs.ndim != 2 or clean_outputs.shape[0] != batch_size:
                    raise ValueError("模型需要输出 [批次大小, 类别数] 的分类分数")
                if labels.min() < 0 or labels.max() >= clean_outputs.shape[1]:
                    raise ValueError("数据标签超出模型分类范围")
                if not torch.isfinite(clean_outputs).all():
                    raise ValueError("模型输出含无效数值")
                clean_probs = torch.softmax(clean_outputs, dim=1)
                clean_preds = clean_outputs.argmax(dim=1)
                clean_confidence = clean_probs.gather(1, labels.unsqueeze(1)).squeeze(1)

                clean_correct += (clean_preds == labels).sum().item()

                # 生成对抗样本
                with torch.enable_grad():
                    adv_images = attack(images, labels)

                # 对抗预测
                adv_outputs = self.model(adv_images)
                adv_probs = torch.softmax(adv_outputs, dim=1)
                adv_preds = adv_outputs.argmax(dim=1)
                adv_confidence = adv_probs.gather(1, labels.unsqueeze(1)).squeeze(1)

                robust_correct += (adv_preds == labels).sum().item()

                # 攻击成功: 原本正确但被攻击后错误
                originally_correct = (clean_preds == labels)
                now_wrong = (adv_preds != labels)
                attack_success += (originally_correct & now_wrong).sum().item()

                # 计算扰动
                perturbation = adv_images - images
                l2_norm = perturbation.view(batch_size, -1).norm(p=2, dim=1)
                linf_norm = perturbation.view(batch_size, -1).abs().max(dim=1)[0]

                total_l2_perturbation += l2_norm.sum().item()
                total_linf_perturbation += linf_norm.sum().item()

                # 置信度下降
                confidence_drop = (clean_confidence - adv_confidence).clamp(min=0)
                total_confidence_drop += confidence_drop.sum().item()

                total_samples += batch_size

                # 进度回调
                if progress_callback:
                    progress_callback(batch_idx + 1, total_batches)

        # 计算指标
        clean_accuracy = clean_correct / total_samples if total_samples > 0 else 0
        robust_accuracy = robust_correct / total_samples if total_samples > 0 else 0

        # 攻击成功率 = 成功攻击数 / 原本正确的样本数
        attack_success_rate = attack_success / clean_correct if clean_correct > 0 else 0

        avg_l2 = total_l2_perturbation / total_samples if total_samples > 0 else 0
        avg_linf = total_linf_perturbation / total_samples if total_samples > 0 else 0
        avg_conf_drop = total_confidence_drop / total_samples if total_samples > 0 else 0

        return AttackResult(
            attack_type=attack_type,
            eps=eps,
            clean_accuracy=clean_accuracy,
            robust_accuracy=robust_accuracy,
            attack_success_rate=attack_success_rate,
            avg_perturbation_l2=avg_l2,
            avg_perturbation_linf=avg_linf,
            avg_confidence_drop=avg_conf_drop,
            num_samples=total_samples
        )

    def run_attacks(
        self,
        dataloader: torch.utils.data.DataLoader,
        attack_configs: List[Dict[str, Any]],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> List[AttackResult]:
        """
        运行多个攻击

        Args:
            dataloader: 数据加载器
            attack_configs: 攻击配置列表
            progress_callback: 进度回调 (attack_type, current, total)

        Returns:
            攻击结果列表
        """
        results = []
        total_attacks = len(attack_configs)

        for idx, config in enumerate(attack_configs):
            attack_type = config.get("attack_type", "fgsm")
            eps = config.get("eps", 0.03)
            steps = config.get("steps", 10)
            alpha = config.get("alpha")

            logger.info(f"开始攻击 [{idx+1}/{total_attacks}]: {attack_type}, eps={eps}")

            attack = self.create_attack(attack_type, eps, steps, alpha)

            def batch_progress(current, total):
                if progress_callback:
                    progress_callback(attack_type, current, total)

            result = self.evaluate(attack, dataloader, attack_type, eps, batch_progress)
            results.append(result)

            logger.info(f"攻击完成: {attack_type}, 鲁棒准确率={result.robust_accuracy:.4f}, ASR={result.attack_success_rate:.4f}")

        return results


def get_attack_engine(model: nn.Module, device: torch.device = None) -> AttackEngine:
    """获取攻击引擎实例"""
    return AttackEngine(model, device)
