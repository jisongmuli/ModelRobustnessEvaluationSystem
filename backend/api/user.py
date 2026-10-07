"""
用户管理 API - 模拟 RuoYi 系统用户管理功能
"""
from typing import List, Optional, Any
from fastapi import APIRouter, HTTPException, Query, Depends, UploadFile, File
from api.auth import get_current_user, require_admin, TOKENS_DB
from core.passwords import hash_password, verify_password
from core.settings import AVATAR_DIR
import os
from pathlib import Path
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/system/user", tags=["用户管理"])

from sqlalchemy.orm import Session
from sqlalchemy import func
from core.database import get_db
from models.system import User, Role, Dept, user_role, role_menu
from typing import Optional, Dict, Any, List



# 请求/响应模型
class UserQuery(BaseModel):
    pageNum: int = 1
    pageSize: int = 10
    userName: Optional[str] = None
    phonenumber: Optional[str] = None
    status: Optional[str] = None
    deptId: Optional[int] = None
    beginTime: Optional[str] = None
    endTime: Optional[str] = None

class BaseResponse(BaseModel):
    code: int = 200
    msg: str = "操作成功"
    data: Optional[Any] = None

class PageResponse(BaseResponse):
    total: int
    rows: List[dict]

class UserForm(BaseModel):
    userId: Optional[int] = None
    deptId: Optional[int] = None
    userName: str
    nickName: str
    password: Optional[str] = None
    phonenumber: Optional[str] = None
    email: Optional[str] = None
    sex: Optional[str] = "0"
    status: str = "0"
    remark: Optional[str] = None
    postIds: List[int] = []
    roleIds: List[int] = []

# API 接口实现

@router.get("/deptTree", summary="获取部门树列表", dependencies=[Depends(require_admin)])
async def get_dept_tree(db: Session = Depends(get_db)):
    # 暂未实现完整树构建逻辑，返回简单列表供测试
    depts = db.query(Dept).filter(Dept.del_flag == "0").all()
    # 构造树结构的逻辑可以在此处完善
    # 这里简单构建一个单层结构用于演示
    result = []
    for dept in depts:
        result.append({
            "id": dept.dept_id,
            "label": dept.dept_name,
            "children": []
        })
    return BaseResponse(data=result)

@router.get("/list", summary="获取用户列表", dependencies=[Depends(require_admin)])
async def list_user(
    pageNum: int = Query(1, ge=1, alias="pageNum"),
    pageSize: int = Query(10, ge=1, le=100, alias="pageSize"),
    userName: Optional[str] = None,
    phonenumber: Optional[str] = None,
    status: Optional[str] = None,
    deptId: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(User).filter(User.del_flag == "0")

    if userName:
        query = query.filter(User.user_name.like(f"%{userName}%"))
    if phonenumber:
        query = query.filter(User.phonenumber.like(f"%{phonenumber}%"))
    if status:
        query = query.filter(User.status == status)
    if deptId:
        query = query.filter(User.dept_id == deptId)

    total = query.count()
    users = query.offset((pageNum - 1) * pageSize).limit(pageSize).all()

    # 格式化返回
    rows = []
    for u in users:
        # 获取部门详情
        dept = db.query(Dept).filter(Dept.dept_id == u.dept_id).first()
        dept_name = dept.dept_name if dept else ""

        row = {
            "userId": u.user_id,
            "deptId": u.dept_id,
            "userName": u.user_name,
            "nickName": u.nick_name,
            "email": u.email,
            "phonenumber": u.phonenumber,
            "sex": u.sex,
            "avatar": u.avatar,
            "status": u.status,
            "createTime": u.create_time.strftime("%Y-%m-%d %H:%M:%S") if u.create_time else "",
            "dept": {"deptName": dept_name}
        }
        rows.append(row)

    return PageResponse(
        code=200,
        msg="查询成功",
        total=total,
        rows=rows
    )


@router.get("/", summary="获取新增用户信息", dependencies=[Depends(require_admin)])
async def get_add_info(db: Session = Depends(get_db)):
    roles = db.query(Role).all()
    role_list = [{"roleId": r.role_id, "roleName": r.role_name} for r in roles]
    return {
        "code": 200,
        "msg": "操作成功",
        "posts": [{"postId": 1, "postName": "普通员工"}],
        "roles": role_list
    }

@router.post("", summary="新增用户", dependencies=[Depends(require_admin)])
async def add_user(user: UserForm, db: Session = Depends(get_db)):
    # 检查用户名是否已存在
    if db.query(User).filter(User.user_name == user.userName).first():
        return BaseResponse(code=500, msg="用户账号已存在")

    new_user = User(
        dept_id=user.deptId,
        user_name=user.userName,
        nick_name=user.nickName,
        password=hash_password(user.password),
        email=user.email,
        phonenumber=user.phonenumber,
        sex=user.sex,
        status=user.status,
        remark=user.remark
    )
    roles = db.query(Role).filter(Role.role_id.in_(user.roleIds)).all() if user.roleIds else db.query(Role).filter(Role.role_key == 'common').all()
    if user.roleIds and len(roles) != len(set(user.roleIds)):
        raise HTTPException(status_code=400, detail='角色不存在')
    new_user.roles = roles
    db.add(new_user)
    db.commit()
    return BaseResponse(msg="新增成功")

@router.put("", summary="修改用户", dependencies=[Depends(require_admin)])
async def update_user(user: UserForm, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.user_id == user.userId).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    roles = db.query(Role).filter(Role.role_id.in_(user.roleIds)).all()
    if len(roles) != len(set(user.roleIds)):
        raise HTTPException(status_code=400, detail='角色不存在')
    db_user.roles = roles
    db_user.dept_id = user.deptId
    db_user.nick_name = user.nickName
    db_user.email = user.email
    db_user.phonenumber = user.phonenumber
    db_user.sex = user.sex
    db_user.status = user.status
    db_user.remark = user.remark

    db.commit()
    return BaseResponse(msg="修改成功")

@router.delete("/{user_ids}", summary="删除用户", dependencies=[Depends(require_admin)])
async def del_user(user_ids: str, db: Session = Depends(get_db)):
    ids = [int(i) for i in user_ids.split(",")]
    db.query(User).filter(User.user_id.in_(ids)).update({"del_flag": "2"}, synchronize_session=False)
    db.commit()
    return BaseResponse(msg="删除成功")

@router.put("/changeStatus", summary="修改状态", dependencies=[Depends(require_admin)])
async def change_status(data: dict, db: Session = Depends(get_db)):
    user_id = data.get("userId")
    status = data.get("status")

    db_user = db.query(User).filter(User.user_id == user_id).first()
    if db_user:
        db_user.status = status
        db.commit()

    return BaseResponse(msg="修改成功")

@router.put("/resetPwd", summary="重置密码", dependencies=[Depends(require_admin)])
async def reset_pwd(data: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == data.get('userId'), User.del_flag == '0').first()
    if user is None:
        raise HTTPException(status_code=404, detail='用户不存在')
    user.password = hash_password(data.get('password'))
    db.commit()
    for token in list(TOKENS_DB):
        if TOKENS_DB[token]['user']['userId'] == user.user_id:
            TOKENS_DB.pop(token, None)
    return BaseResponse(msg='重置成功')

@router.get("/profile", summary="个人信息")
async def get_profile(current_user: Dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    获取当前登录用户的个人信息
    """
    user_id = current_user.get("userId")
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        return {"code": 500, "msg": "用户不存在"}

    # 获取用户角色
    roles = [role.role_name for role in user.roles]

    user_data = {
        "userId": user.user_id,
        "userName": user.user_name,
        "nickName": user.nick_name,
        "email": user.email,
        "phonenumber": user.phonenumber,
        "sex": user.sex,
        "avatar": user.avatar,
        "createTime": user.create_time.strftime("%Y-%m-%d %H:%M:%S") if user.create_time else ""
    }

    return {
        "code": 200,
        "msg": "操作成功",
        "data": user_data,
        "roleGroup": ",".join(roles),
        "postGroup": ""
    }


@router.put("/profile", summary="更新个人信息")
async def update_profile(data: dict, current_user: Dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    更新当前登录用户的个人信息
    """
    user_id = current_user.get("userId")
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        return {"code": 500, "msg": "用户不存在"}

    # 更新用户信息
    if "nickName" in data:
        user.nick_name = data["nickName"]
    if "phonenumber" in data:
        user.phonenumber = data["phonenumber"]
    if "email" in data:
        user.email = data["email"]
    if "sex" in data:
        user.sex = data["sex"]

    user.update_time = datetime.now()
    user.update_by = current_user.get("userName")

    db.commit()

    return {"code": 200, "msg": "更新成功"}


@router.put("/profile/updatePwd", summary="修改密码")
async def update_password(data: dict, current_user: Dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == current_user['userId']).first()
    if not verify_password(data.get('oldPassword'), user.password):
        raise HTTPException(status_code=400, detail='旧密码错误')
    user.password = hash_password(data.get('newPassword'))
    db.commit()
    for token in list(TOKENS_DB):
        if TOKENS_DB[token]['user']['userId'] == user.user_id:
            TOKENS_DB.pop(token, None)
    return {'code': 200, 'msg': '密码修改成功，请重新登录'}


@router.post("/profile/avatar", summary="上传头像")
async def upload_avatar(avatarfile: UploadFile = File(...), current_user: Dict = Depends(get_current_user), db: Session = Depends(get_db)):
    import io
    import uuid
    from PIL import Image
    data = await avatarfile.read(2 * 1024 * 1024 + 1)
    await avatarfile.close()
    if len(data) > 2 * 1024 * 1024:
        raise HTTPException(status_code=413, detail='头像最大为 2 MB')
    try:
        image = Image.open(io.BytesIO(data))
        if image.width * image.height > 16000000 or image.format not in ('PNG', 'JPEG', 'WEBP'):
            raise ValueError('invalid avatar')
        image = image.convert('RGB')
        image.thumbnail((512, 512))
    except Exception as error:
        raise HTTPException(status_code=400, detail='请上传有效的 PNG、JPEG 或 WebP 头像') from error
    filename = f'{uuid.uuid4().hex}.png'
    image.save(AVATAR_DIR / filename, format='PNG')
    user = db.query(User).filter(User.user_id == current_user['userId']).first()
    user.avatar = f'/uploads/avatars/{filename}'
    db.commit()
    return {'code': 200, 'msg': '上传成功', 'imgUrl': user.avatar}


@router.get("/{user_id}", summary="获取详细信息", dependencies=[Depends(require_admin)])
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()

    # 模拟数据
    posts = [{"postId": 1, "postName": "普通员工"}]
    roles = db.query(Role).all()
    role_list = [{"roleId": r.role_id, "roleName": r.role_name} for r in roles]

    # 构造返回数据
    data = {}
    if user:
        data = {
            "userId": user.user_id,
            "userName": user.user_name,
            "nickName": user.nick_name,
            "email": user.email,
            "phonenumber": user.phonenumber,
            "sex": user.sex,
            "status": user.status,
            "remark": user.remark,
            "postIds": [],
            "roleIds": [r.role_id for r in user.roles]
        }

    return {
        "code": 200,
        "msg": "操作成功",
        "data": data,
        "postIds": [],
        "roleIds": data.get("roleIds", []),
        "posts": posts,
        "roles": role_list
    }
