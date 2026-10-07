from api.auth import require_admin
from fastapi import HTTPException
from typing import List, Optional, Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from core.database import get_db
from models.system import Menu

router = APIRouter(prefix="/system/menu", dependencies=[Depends(require_admin)], tags=["菜单管理"])

# 模拟菜单数据
MENUS = [
    {
        "menuId": 1,
        "menuName": "系统管理",
        "parentName": None,
        "parentId": 0,
        "orderNum": "1",
        "path": "system",
        "component": None,
        "isFrame": "1",
        "isCache": "0",
        "menuType": "M",
        "visible": "0",
        "status": "0",
        "perms": "",
        "icon": "system",
        "createTime": "2024-03-01 10:00:00",
        "children": []
    },
    {
        "menuId": 100,
        "menuName": "用户管理",
        "parentName": "系统管理",
        "parentId": 1,
        "orderNum": "1",
        "path": "user",
        "component": "system/user/index",
        "isFrame": "1",
        "isCache": "0",
        "menuType": "C",
        "visible": "0",
        "status": "0",
        "perms": "system:user:list",
        "icon": "user",
        "createTime": "2024-03-01 10:00:00",
        "children": []
    },
    {
        "menuId": 101,
        "menuName": "角色管理",
        "parentName": "系统管理",
        "parentId": 1,
        "orderNum": "2",
        "path": "role",
        "component": "system/role/index",
        "isFrame": "1",
        "isCache": "0",
        "menuType": "C",
        "visible": "0",
        "status": "0",
        "perms": "system:role:list",
        "icon": "peoples",
        "createTime": "2024-03-01 10:00:00",
        "children": []
    },
    {
        "menuId": 102,
        "menuName": "菜单管理",
        "parentName": "系统管理",
        "parentId": 1,
        "orderNum": "3",
        "path": "menu",
        "component": "system/menu/index",
        "isFrame": "1",
        "isCache": "0",
        "menuType": "C",
        "visible": "0",
        "status": "0",
        "perms": "system:menu:list",
        "icon": "tree-table",
        "createTime": "2024-03-01 10:00:00",
        "children": []
    },
    {
        "menuId": 103,
        "menuName": "部门管理",
        "parentName": "系统管理",
        "parentId": 1,
        "orderNum": "4",
        "path": "dept",
        "component": "system/dept/index",
        "isFrame": "1",
        "isCache": "0",
        "menuType": "C",
        "visible": "0",
        "status": "0",
        "perms": "system:dept:list",
        "icon": "tree",
        "createTime": "2024-03-01 10:00:00",
        "children": []
    },
    # 鲁棒性测试模块
    {
        "menuId": 2,
        "menuName": "鲁棒性测试",
        "parentName": None,
        "parentId": 0,
        "orderNum": "2",
        "path": "robustness",
        "component": None,
        "isFrame": "1",
        "isCache": "0",
        "menuType": "M",
        "visible": "0",
        "status": "0",
        "perms": "",
        "icon": "monitor",
        "createTime": "2024-03-01 10:00:00",
        "children": []
    },
    {
        "menuId": 201,
        "menuName": "模型管理",
        "parentName": "鲁棒性测试",
        "parentId": 2,
        "orderNum": "1",
        "path": "model",
        "component": "robustness/model/index",
        "isFrame": "1",
        "isCache": "0",
        "menuType": "C",
        "visible": "0",
        "status": "0",
        "perms": "robustness:model:list",
        "icon": "component",
        "createTime": "2024-03-01 10:00:00",
        "children": []
    }
]

class BaseResponse(BaseModel):
    code: int = 200
    msg: str = "操作成功"
    data: Optional[Any] = None

@router.get("/list", summary="获取菜单列表")
async def list_menu(db: Session = Depends(get_db)):
    menus = db.query(Menu).filter(Menu.status == "0").order_by(Menu.order_num).all()
    # 转换为字典
    result = []
    for m in menus:
        result.append({
            "menuId": m.menu_id,
            "menuName": m.menu_name,
            "parentId": m.parent_id,
            "orderNum": m.order_num,
            "path": m.path,
            "component": m.component,
            "isFrame": str(m.is_frame),
            "isCache": str(m.is_cache),
            "menuType": m.menu_type,
            "visible": m.visible,
            "status": m.status,
            "perms": m.perms,
            "icon": m.icon,
            "createTime": m.create_time.strftime("%Y-%m-%d %H:%M:%S") if m.create_time else None
        })
    return BaseResponse(data=result)

@router.get("/treeselect", summary="获取菜单下拉树列表")
async def treeselect(db: Session = Depends(get_db)):
    menus = db.query(Menu).filter(Menu.status == "0").order_by(Menu.order_num).all()

    # 构建树
    def build_tree(items, parent_id=0):
        result = []
        for item in items:
            if item.parent_id == parent_id:
                children = build_tree(items, item.menu_id)
                node = {
                    "id": item.menu_id,
                    "label": item.menu_name,
                    "children": children
                }
                result.append(node)
        return result

    tree = build_tree(menus)
    return BaseResponse(data=tree)

@router.get("/roleMenuTreeselect/{roleId}", summary="获取角色菜单列表")
async def role_menu_treeselect(roleId: int, db: Session = Depends(get_db)):
    # 获取角色关联的菜单ID
    # 这里需要关联查询，暂时简单处理：查询所有菜单
    menus = db.query(Menu).filter(Menu.status == "0").order_by(Menu.order_num).all()

    checkedKeys = [m.menu_id for m in menus] # 简单全选，实际应查 sys_role_menu

    def build_tree(items, parent_id=0):
        result = []
        for item in items:
            if item.parent_id == parent_id:
                children = build_tree(items, item.menu_id)
                node = {
                    "id": item.menu_id,
                    "label": item.menu_name,
                    "children": children
                }
                result.append(node)
        return result

    return {
        "code": 200,
        "msg": "操作成功",
        "menus": build_tree(menus),
        "checkedKeys": checkedKeys
    }

@router.post("", summary="新增菜单")
async def add_menu():
    raise HTTPException(status_code=501, detail="此管理功能尚未实现")

@router.put("", summary="修改菜单")
async def update_menu():
    raise HTTPException(status_code=501, detail="此管理功能尚未实现")

@router.delete("/{menuId}", summary="删除菜单")
async def del_menu(menuId: int):
    raise HTTPException(status_code=501, detail="此管理功能尚未实现")
