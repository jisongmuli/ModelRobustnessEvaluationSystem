from api.auth import require_admin
from fastapi import HTTPException
from typing import List, Optional, Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from core.database import get_db
from models.system import Dept

router = APIRouter(prefix="/system/dept", dependencies=[Depends(require_admin)], tags=["部门管理"])

DEPARTMENTS = [
    {
        "deptId": 100,
        "parentId": 0,
        "ancestors": "0",
        "deptName": "若依科技",
        "orderNum": "0",
        "leader": "若依",
        "phone": "15888888888",
        "email": "ry@qq.com",
        "status": "0",
        "delFlag": "0",
        "parentName": None,
        "createTime": "2024-03-01 10:00:00",
        "children": []
    },
    {
        "deptId": 101,
        "parentId": 100,
        "ancestors": "0,100",
        "deptName": "深圳总公司",
        "orderNum": "1",
        "leader": "若依",
        "phone": "15888888888",
        "email": "ry@qq.com",
        "status": "0",
        "delFlag": "0",
        "parentName": "若依科技",
        "createTime": "2024-03-01 10:00:00",
        "children": []
    },
    {
        "deptId": 103,
        "parentId": 101,
        "ancestors": "0,100,101",
        "deptName": "研发部门",
        "orderNum": "1",
        "leader": "若依",
        "phone": "15888888888",
        "email": "ry@qq.com",
        "status": "0",
        "delFlag": "0",
        "parentName": "深圳总公司",
        "createTime": "2024-03-01 10:00:00",
        "children": []
    },
    {
        "deptId": 105,
        "parentId": 101,
        "ancestors": "0,100,101",
        "deptName": "测试部门",
        "orderNum": "3",
        "leader": "若依",
        "phone": "15888888888",
        "email": "ry@qq.com",
        "status": "0",
        "delFlag": "0",
        "parentName": "深圳总公司",
        "createTime": "2024-03-01 10:00:00",
        "children": []
    }
]

class BaseResponse(BaseModel):
    code: int = 200
    msg: str = "操作成功"
    data: Optional[Any] = None

@router.get("/list", summary="获取部门列表")
async def list_dept(db: Session = Depends(get_db)):
    depts = db.query(Dept).filter(Dept.del_flag == "0").all()
    # 转换为字典列表，并处理 None 值
    result = []
    for d in depts:
        result.append({
            "deptId": d.dept_id,
            "parentId": d.parent_id,
            "ancestors": d.ancestors,
            "deptName": d.dept_name,
            "orderNum": d.order_num,
            "leader": d.leader,
            "phone": d.phone,
            "email": d.email,
            "status": d.status,
            "createTime": d.create_time.strftime("%Y-%m-%d %H:%M:%S") if d.create_time else None
        })
    return BaseResponse(data=result)

@router.get("/list/exclude/{deptId}", summary="获取部门列表（排除节点）")
async def list_dept_exclude(deptId: int, db: Session = Depends(get_db)):
    # 实际逻辑应排除自身及子节点
    depts = db.query(Dept).filter(
        Dept.del_flag == "0",
        Dept.dept_id != deptId,
        # 简单排除：祖级列表包含该ID的也排除
        # Dept.ancestors.notlike(f"%{deptId}%")
    ).all()

    result = []
    for d in depts:
        # 排除子节点逻辑（ancestors包含当前id）
        if str(deptId) in (d.ancestors or "").split(","):
            continue

        result.append({
            "deptId": d.dept_id,
            "parentId": d.parent_id,
            "deptName": d.dept_name,
            "orderNum": d.order_num,
            "status": d.status
        })
    return BaseResponse(data=result)

@router.get("/{deptId}", summary="获取部门详情")
async def get_dept(deptId: int, db: Session = Depends(get_db)):
    dept = db.query(Dept).filter(Dept.dept_id == deptId).first()
    if not dept:
        return BaseResponse(code=500, msg="部门不存在")

    data = {
        "deptId": dept.dept_id,
        "parentId": dept.parent_id,
        "ancestors": dept.ancestors,
        "deptName": dept.dept_name,
        "orderNum": dept.order_num,
        "leader": dept.leader,
        "phone": dept.phone,
        "email": dept.email,
        "status": dept.status
    }
    return BaseResponse(data=data)

@router.post("", summary="新增部门")
async def add_dept():
    raise HTTPException(status_code=501, detail="此管理功能尚未实现")

@router.put("", summary="修改部门")
async def update_dept():
    raise HTTPException(status_code=501, detail="此管理功能尚未实现")

@router.delete("/{deptId}", summary="删除部门")
async def del_dept(deptId: int):
    raise HTTPException(status_code=501, detail="此管理功能尚未实现")
