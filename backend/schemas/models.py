"""
Pydantic 数据模型定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


# ==================== 枚举类型 ====================

class AttackType(str, Enum):
    """攻击类型枚举"""
    FGSM = "fgsm"
    PGD = "pgd"
    BIM = "bim"
    CW = "cw"
    DEEPFOOL = "deepfool"


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# ==================== 请求模型 ====================

class AttackConfig(BaseModel):
    """攻击配置"""
    attack_type: AttackType = Field(..., description="攻击类型")
    eps: float = Field(default=0.03, ge=0, le=1, description="扰动强度 (epsilon)")
    steps: int = Field(default=10, ge=1, le=100, description="迭代步数 (PGD/BIM)")
    alpha: Optional[float] = Field(default=None, gt=0, le=1, description="步长 (可选，默认 2*eps/steps)")

    class Config:
        json_schema_extra = {
            "example": {
                "attack_type": "pgd",
                "eps": 0.03,
                "steps": 10,
                "alpha": 0.007
            }
        }


class AttackRequest(BaseModel):
    """启动攻击请求"""
    model_id: str = Field(..., description="模型ID")
    dataset_id: Optional[str] = Field(default=None, description="数据集ID (为空则使用默认CIFAR-10)")
    attacks: List[AttackConfig] = Field(..., min_length=1, max_length=20, description="攻击配置列表")
    batch_size: int = Field(default=32, ge=1, le=128, description="批次大小")
    num_samples: int = Field(default=1000, ge=1, le=10000, description="测试样本数量")
    normalization: str = Field(default="auto", pattern="^(auto|none|cifar10|imagenet)$", description="必须与模型训练时一致；auto 为 CIFAR-10 或自定义数据的 ImageNet 标准化")
    seed: int = Field(default=42, ge=0, le=2147483647, description="采样与攻击随机种子")

    class Config:
        json_schema_extra = {
            "example": {
                "model_id": "model_abc123",
                "attacks": [
                    {"attack_type": "fgsm", "eps": 0.03},
                    {"attack_type": "pgd", "eps": 0.03, "steps": 10}
                ],
                "batch_size": 32,
                "num_samples": 1000
            }
        }


# ==================== 响应模型 ====================

class ModelInfo(BaseModel):
    """模型信息"""
    id: str = Field(..., description="模型唯一ID")
    user_id: Optional[int] = Field(default=None, description="所属用户ID")
    filename: str = Field(..., description="原始文件名")
    file_size: int = Field(..., description="文件大小(字节)")
    upload_time: datetime = Field(..., description="上传时间")
    model_type: Optional[str] = Field(default=None, description="模型类型")
    num_classes: Optional[int] = Field(default=None, description="分类数量")
    input_shape: Optional[List[int]] = Field(default=None, description="输入形状")
    img_size: Optional[int] = Field(default=None, description="图像尺寸")
    status: str = Field(default="ready", description="模型状态")
    load_error: Optional[str] = Field(default=None, description="模型加载失败原因")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "model_abc123",
                "filename": "resnet18.pth",
                "file_size": 46827520,
                "upload_time": "2024-01-20T10:30:00",
                "model_type": "ResNet",
                "num_classes": 10,
                "input_shape": [1, 3, 224, 224],
                "img_size": 224,
                "status": "ready",
                "load_error": None
            }
        }


class UploadResponse(BaseModel):
    """上传响应"""
    code: int = Field(default=200, description="状态码")
    msg: str = Field(default="success", description="消息")
    data: ModelInfo = Field(..., description="模型信息")


class ModelListResponse(BaseModel):
    """模型列表响应"""
    code: int = Field(default=200, description="状态码")
    msg: str = Field(default="success", description="消息")
    data: List[ModelInfo] = Field(..., description="模型列表")
    total: int = Field(..., description="总数")


class AttackMetrics(BaseModel):
    """单个攻击的评估指标"""
    attack_type: str = Field(..., description="攻击类型")
    eps: float = Field(..., description="扰动强度")
    clean_accuracy: float = Field(..., description="原始准确率")
    robust_accuracy: float = Field(..., description="对抗准确率")
    attack_success_rate: float = Field(..., description="攻击成功率")
    avg_perturbation_l2: float = Field(..., description="平均L2扰动")
    avg_perturbation_linf: float = Field(..., description="平均L∞扰动")
    avg_confidence_drop: float = Field(..., description="平均置信度下降")

    class Config:
        json_schema_extra = {
            "example": {
                "attack_type": "pgd",
                "eps": 0.03,
                "clean_accuracy": 0.92,
                "robust_accuracy": 0.34,
                "attack_success_rate": 0.63,
                "avg_perturbation_l2": 1.23,
                "avg_perturbation_linf": 0.03,
                "avg_confidence_drop": 0.45
            }
        }


class TaskInfo(BaseModel):
    """任务信息"""
    task_id: str = Field(..., description="任务ID")
    model_id: str = Field(..., description="模型ID")
    status: TaskStatus = Field(..., description="任务状态")
    progress: int = Field(default=0, ge=0, le=100, description="进度百分比")
    current_attack: Optional[str] = Field(default=None, description="当前攻击类型")
    create_time: datetime = Field(..., description="创建时间")
    start_time: Optional[datetime] = Field(default=None, description="开始时间")
    end_time: Optional[datetime] = Field(default=None, description="结束时间")
    error_msg: Optional[str] = Field(default=None, description="错误信息")


class AttackStartResponse(BaseModel):
    """启动攻击响应"""
    code: int = Field(default=200, description="状态码")
    msg: str = Field(default="success", description="消息")
    data: TaskInfo = Field(..., description="任务信息")


class AttackResultResponse(BaseModel):
    """攻击结果响应"""
    code: int = Field(default=200, description="状态码")
    msg: str = Field(default="success", description="消息")
    data: Dict[str, Any] = Field(..., description="结果数据")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "success",
                "data": {
                    "task_id": "task_xyz789",
                    "model_id": "model_abc123",
                    "status": "completed",
                    "metrics": [
                        {
                            "attack_type": "fgsm",
                            "eps": 0.03,
                            "clean_accuracy": 0.92,
                            "robust_accuracy": 0.45,
                            "attack_success_rate": 0.51
                        }
                    ],
                    "sample_images": [
                        {
                            "original": "/api/images/orig_001.png",
                            "adversarial": "/api/images/adv_001.png",
                            "perturbation": "/api/images/pert_001.png"
                        }
                    ]
                }
            }
        }


class TaskStatusResponse(BaseModel):
    """任务状态响应"""
    code: int = Field(default=200, description="状态码")
    msg: str = Field(default="success", description="消息")
    data: TaskInfo = Field(..., description="任务信息")


class TaskListResponse(BaseModel):
    """任务列表响应"""
    code: int = Field(default=200, description="状态码")
    msg: str = Field(default="success", description="消息")
    data: List[TaskInfo] = Field(..., description="任务列表")
    total: int = Field(..., description="总数")


class FCLayerConfig(BaseModel):
    """FC 层配置"""
    index: int = Field(..., ge=0, le=100, description="层索引")
    layer_type: str = Field(..., pattern="^(linear|relu|dropout|identity)$", description="层类型")
    in_features: Optional[int] = Field(default=None, ge=1, le=32768, description="输入特征数 (仅 linear)")
    out_features: Optional[int] = Field(default=None, ge=1, le=10000, description="输出特征数 (仅 linear)")
    dropout_p: Optional[float] = Field(default=0.5, ge=0, le=1, description="Dropout 概率 (仅 dropout)")

    class Config:
        json_schema_extra = {
            "example": {
                "index": 1,
                "layer_type": "linear",
                "in_features": 512,
                "out_features": 512
            }
        }


class ModelStructureConfig(BaseModel):
    """模型结构配置"""
    model_id: str = Field(..., description="模型ID")
    model_type: str = Field(..., description="模型类型: resnet18, resnet34, etc.")
    num_classes: int = Field(..., ge=1, le=10000, description="分类数量")
    img_size: int = Field(default=224, ge=16, le=1024, description="图像尺寸")
    head_name: Optional[str] = Field(default=None, description="分类头名称: fc, classifier, head")
    has_custom_fc: bool = Field(default=False, description="是否有自定义 FC 层")
    fc_layers: Optional[List[FCLayerConfig]] = Field(default=None, description="自定义 FC 层配置")

    class Config:
        json_schema_extra = {
            "example": {
                "model_id": "model_abc123",
                "model_type": "resnet18",
                "num_classes": 102,
                "img_size": 224,
                "head_name": "fc",
                "has_custom_fc": True,
                "fc_layers": [
                    {"index": 1, "layer_type": "linear", "in_features": 512, "out_features": 512},
                    {"index": 2, "layer_type": "relu"},
                    {"index": 3, "layer_type": "dropout", "dropout_p": 0.5},
                    {"index": 4, "layer_type": "linear", "in_features": 512, "out_features": 102}
                ]
            }
        }


class BaseResponse(BaseModel):
    """通用响应"""
    code: int = Field(default=200, description="状态码")
    msg: str = Field(default="success", description="消息")
    data: Optional[Any] = Field(default=None, description="数据")
