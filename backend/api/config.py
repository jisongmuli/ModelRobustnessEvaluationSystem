from api.auth import require_admin
from fastapi import Depends
"""
参数配置 API - 模拟 RuoYi 系统参数配置功能
"""
from typing import List, Optional, Any
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/system/config", tags=["参数配置"])

CONFIGS = {
    "sys.user.initPassword": "123456",
    "sys.account.registerUser": "false",
}

class BaseResponse(BaseModel):
    code: int = 200
    msg: str = "操作成功"
    data: Optional[Any] = None

@router.get("/configKey/{configKey}", summary="根据参数键名查询参数值")
async def get_config_key(configKey: str):
    msg = CONFIGS.get(configKey, "")
    return BaseResponse(msg=msg)

@router.get("/list", dependencies=[Depends(require_admin)], summary="查询参数列表")
async def list_config():
    return {
        "code": 200,
        "msg": "查询成功",
        "rows": [],
        "total": 0
    }
