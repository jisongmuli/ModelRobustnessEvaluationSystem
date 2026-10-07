"""
模型鲁棒性测试平台 - FastAPI 后端入口

启动命令:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Swagger 文档:
    http://localhost:8000/docs

ReDoc 文档:
    http://localhost:8000/redoc
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from core.settings import CORS_ORIGINS, AVATAR_DIR

from api import (
    upload_router,
    attack_router,
    auth_router,
    user_router,
    role_router,
    menu_router,
    dept_router,
    dict_data_router,
    config_router
)

# 创建 FastAPI 应用
app = FastAPI(
    title="模型鲁棒性测试平台 API",
    description="""
## 概述

本平台提供深度学习模型的对抗鲁棒性评估服务。用户可以上传 PyTorch 模型文件（.pt/.pth），
系统将自动执行多种对抗攻击测试，并返回详细的评估指标。

## 主要功能

- **模型管理**: 上传、查询、删除模型文件
- **对抗攻击**: 支持 FGSM、PGD、BIM、C&W、DeepFool 等主流攻击
- **评估指标**: 包括原始准确率、鲁棒准确率、攻击成功率、扰动量等

## 支持的攻击类型

| 攻击方法 | 说明 |
|----------|------|
| FGSM | 快速梯度符号法，单步攻击 |
| PGD | 投影梯度下降，迭代攻击 |
| BIM | 基本迭代法 |
| C&W | Carlini & Wagner 攻击 |
| DeepFool | 最小扰动攻击 |

## 使用流程

1. 调用 `/api/model/upload` 上传模型
2. 调用 `/api/attack/start` 启动攻击测试
3. 调用 `/api/attack/status/{task_id}` 查询任务进度
4. 调用 `/api/attack/result/{task_id}` 获取评估结果

## 初始化

首次运行前执行 `python init_db.py`，交互设置管理员密码。
    """,
    version="1.0.0",
    contact={
        "name": "技术支持",
        "email": "support@example.com"
    },
    license_info={
        "name": "MIT License"
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "系统认证",
            "description": "用户登录、登出、获取用户信息"
        },
        {
            "name": "模型管理",
            "description": "模型文件的上传、查询和删除操作"
        },
        {
            "name": "对抗攻击",
            "description": "对抗攻击任务的创建、状态查询和结果获取"
        }
    ]
)

# CORS 配置 - 允许 RuoYi 前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 注册路由 - 注意 RuoYi 前端调用认证接口不带 /api 前缀
app.include_router(auth_router, prefix="")  # 登录等接口在根路径
app.include_router(upload_router, prefix="/api")
app.include_router(attack_router, prefix="/api")
app.include_router(user_router, prefix="")
app.include_router(role_router, prefix="")
app.include_router(menu_router, prefix="")
app.include_router(dept_router, prefix="")
app.include_router(dict_data_router, prefix="")
app.include_router(config_router, prefix="")

# Only public avatars are served; model files and metadata require authenticated APIs.
app.mount("/uploads/avatars", StaticFiles(directory=AVATAR_DIR), name="avatars")


@app.get("/", include_in_schema=False)
async def root():
    """根路径重定向到 Swagger 文档"""
    return RedirectResponse(url="/docs")


@app.get("/api/health", tags=["系统"], summary="健康检查")
async def health_check():
    """
    系统健康检查接口

    返回系统运行状态
    """
    import torch
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "status": "healthy",
            "cuda_available": torch.cuda.is_available(),
            "cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0
        }
    }


@app.get("/api/attacks/supported", tags=["系统"], summary="获取支持的攻击类型")
async def get_supported_attacks():
    """
    获取系统支持的所有对抗攻击类型
    """
    return {
        "code": 200,
        "msg": "success",
        "data": [
            {
                "type": "fgsm",
                "name": "FGSM",
                "description": "快速梯度符号法 (Fast Gradient Sign Method)",
                "params": {
                    "eps": {"type": "float", "default": 0.03, "description": "扰动强度"}
                }
            },
            {
                "type": "pgd",
                "name": "PGD",
                "description": "投影梯度下降 (Projected Gradient Descent)",
                "params": {
                    "eps": {"type": "float", "default": 0.03, "description": "扰动强度"},
                    "steps": {"type": "int", "default": 10, "description": "迭代步数"},
                    "alpha": {"type": "float", "default": None, "description": "步长"}
                }
            },
            {
                "type": "bim",
                "name": "BIM",
                "description": "基本迭代法 (Basic Iterative Method)",
                "params": {
                    "eps": {"type": "float", "default": 0.03, "description": "扰动强度"},
                    "steps": {"type": "int", "default": 10, "description": "迭代步数"},
                    "alpha": {"type": "float", "default": None, "description": "步长"}
                }
            },
            {
                "type": "cw",
                "name": "C&W",
                "description": "Carlini & Wagner 攻击",
                "params": {
                    "steps": {"type": "int", "default": 50, "description": "迭代步数"}
                }
            },
            {
                "type": "deepfool",
                "name": "DeepFool",
                "description": "最小扰动攻击",
                "params": {
                    "steps": {"type": "int", "default": 50, "description": "最大迭代步数"}
                }
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
