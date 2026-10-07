from api.auth import require_admin
from fastapi import HTTPException
from typing import List, Optional, Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from core.database import get_db
from models.system import Role

router = APIRouter(prefix="/system/role", dependencies=[Depends(require_admin)], tags=["角色管理"])

ROLES = [
    {
        "roleId": 1,
        "roleName": "超级管理员",
        "roleKey": "admin",
        "roleSort": 1,
        "dataScope": "1",
        "menuCheckStrictly": True,
        "deptCheckStrictly": True,
        "status": "0",
        "delFlag": "0",
        "createTime": "2024-03-01 10:00:00",
        "flag": False,
        "menuIds": [],
        "deptIds": [],
        "admin": True
    },
    {
        "roleId": 2,
        "roleName": "普通角色",
        "roleKey": "common",
        "roleSort": 2,
        "dataScope": "2",
        "menuCheckStrictly": True,
        "deptCheckStrictly": True,
        "status": "0",
        "delFlag": "0",
        "createTime": "2024-03-01 10:00:00",
        "flag": False,
        "menuIds": [],
        "deptIds": [],
        "admin": False
    }
]

class BaseResponse(BaseModel):
    code: int = 200
    msg: str = "操作成功"
    data: Optional[Any] = None

class PageResponse(BaseResponse):
    total: int
    rows: List[dict]

@router.get("/list", summary="获取角色列表")
async def list_role(db: Session = Depends(get_db)):
    roles = db.query(Role).filter(Role.del_flag == "0").all()

    # 转换为字典列表
    rows = []
    for r in roles:
        rows.append({
            "roleId": r.role_id,
            "roleName": r.role_name,
            "roleKey": r.role_key,
            "roleSort": r.role_sort,
            "dataScope": r.data_scope,
            "status": r.status,
            "createTime": r.create_time.strftime("%Y-%m-%d %H:%M:%S") if r.create_time else None,
            "admin": r.role_key == "admin"
        })

    return PageResponse(total=len(rows), rows=rows)

@router.get("/{roleId}", summary="获取角色详情")
async def get_role(roleId: int, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.role_id == roleId).first()
    if not role:
        return BaseResponse(code=500, msg="角色不存在")

    data = {
        "roleId": role.role_id,
        "roleName": role.role_name,
        "roleKey": role.role_key,
        "roleSort": role.role_sort,
        "dataScope": role.data_scope,
        "status": role.status,
        "remark": role.remark
    }
    return BaseResponse(data=data)

@router.post("", summary="新增角色")
async def add_role():
    raise HTTPException(status_code=501, detail="此管理功能尚未实现")

@router.put("", summary="修改角色")
async def update_role():
    raise HTTPException(status_code=501, detail="此管理功能尚未实现")

@router.delete("/{roleIds}", summary="删除角色")
async def del_role(roleIds: str):
    raise HTTPException(status_code=501, detail="此管理功能尚未实现")

@router.put("/changeStatus", summary="修改角色状态")
async def change_status():
    raise HTTPException(status_code=501, detail="此管理功能尚未实现")
