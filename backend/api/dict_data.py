from api.auth import get_current_user
from fastapi import Depends
"""
字典数据 API - 模拟 RuoYi 系统字典数据功能
"""
from typing import List, Optional, Any
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/system/dict/data", dependencies=[Depends(get_current_user)], tags=["字典数据"])

# 模拟字典数据
DICTS = {
    "sys_normal_disable": [
        {"dictCode": 6, "dictSort": 1, "dictLabel": "正常", "dictValue": "0", "dictType": "sys_normal_disable", "cssClass": "", "listClass": "primary", "isDefault": "Y", "status": "0", "default": True},
        {"dictCode": 7, "dictSort": 2, "dictLabel": "停用", "dictValue": "1", "dictType": "sys_normal_disable", "cssClass": "", "listClass": "danger", "isDefault": "N", "status": "0", "default": False}
    ],
    "sys_user_sex": [
        {"dictCode": 1, "dictSort": 1, "dictLabel": "男", "dictValue": "0", "dictType": "sys_user_sex", "cssClass": "", "listClass": "", "isDefault": "Y", "status": "0", "default": True},
        {"dictCode": 2, "dictSort": 2, "dictLabel": "女", "dictValue": "1", "dictType": "sys_user_sex", "cssClass": "", "listClass": "", "isDefault": "N", "status": "0", "default": False},
        {"dictCode": 3, "dictSort": 3, "dictLabel": "未知", "dictValue": "2", "dictType": "sys_user_sex", "cssClass": "", "listClass": "", "isDefault": "N", "status": "0", "default": False}
    ],
    "sys_show_hide": [
        {"dictCode": 4, "dictSort": 1, "dictLabel": "显示", "dictValue": "0", "dictType": "sys_show_hide", "cssClass": "", "listClass": "primary", "isDefault": "Y", "status": "0", "default": True},
        {"dictCode": 5, "dictSort": 2, "dictLabel": "隐藏", "dictValue": "1", "dictType": "sys_show_hide", "cssClass": "", "listClass": "danger", "isDefault": "N", "status": "0", "default": False}
    ]
}

class BaseResponse(BaseModel):
    code: int = 200
    msg: str = "操作成功"
    data: Optional[Any] = None

@router.get("/type/{dictType}", summary="根据字典类型查询字典数据信息")
async def get_dict_data(dictType: str):
    data = DICTS.get(dictType, [])
    return BaseResponse(data=data)

@router.get("/list", summary="查询字典数据列表")
async def list_data():
    return {
        "code": 200,
        "msg": "查询成功",
        "rows": [],  # 暂不返回列表，仅支持类型查询
        "total": 0
    }
