from core.passwords import hash_password, verify_password
"""
用户认证 API - 兼容 RuoYi-Vue 前端
"""
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, Header, Body
from pydantic import BaseModel, Field, validator
import bcrypt
import re

router = APIRouter(tags=["系统认证"])

from sqlalchemy.orm import Session
from core.database import get_db
from models.system import User, Role

TOKENS_DB: Dict[str, Dict[str, Any]] = {}
TOKEN_EXPIRE_HOURS = 24


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    code: Optional[str] = Field(default="", description="验证码")
    uuid: Optional[str] = Field(default="", description="验证码UUID")


class RegisterRequest(BaseModel):
    """注册请求"""
    username: str = Field(..., min_length=2, max_length=20, description="用户名")
    password: str = Field(..., min_length=5, max_length=20, description="密码")
    confirm_password: str = Field(..., alias="confirmPassword", description="确认密码")
    nick_name: Optional[str] = Field(default=None, alias="nickName", max_length=30, description="昵称")
    email: Optional[str] = Field(default="", max_length=50, description="邮箱")
    phonenumber: Optional[str] = Field(default="", max_length=11, description="手机号")
    code: Optional[str] = Field(default="", description="验证码")
    uuid: Optional[str] = Field(default="", description="验证码UUID")

    class Config:
        populate_by_name = True

    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v

    @validator('password')
    def validate_password(cls, v):
        if not re.match(r'^[a-zA-Z0-9_!@#$%^&*]+$', v):
            raise ValueError('密码包含非法字符')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('两次输入的密码不一致')
        return v


class LoginResponse(BaseModel):
    """登录响应 - 兼容 RuoYi 格式"""
    code: int = 200
    msg: str = "操作成功"
    token: Optional[str] = None


class RegisterResponse(BaseModel):
    """注册响应"""
    code: int = 200
    msg: str = "操作成功"
    data: Optional[Dict[str, Any]] = None


class UserInfoResponse(BaseModel):
    """用户信息响应"""
    code: int = 200
    msg: str = "操作成功"
    user: Optional[Dict[str, Any]] = None
    roles: list = []
    permissions: list = []


class RoutersResponse(BaseModel):
    """路由响应"""
    code: int = 200
    msg: str = "操作成功"
    data: list = []


# ==================== 辅助函数 ====================

def generate_token() -> str:
    """生成 token"""
    return str(uuid.uuid4()).replace("-", "")


def get_current_user(authorization: Optional[str] = Header(None, alias='Authorization'), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='未提供有效的认证信息')
    token = authorization[7:].strip()
    token_data = TOKENS_DB.get(token)
    if token_data is None or datetime.now() > token_data['expire_time']:
        TOKENS_DB.pop(token, None)
        raise HTTPException(status_code=401, detail='登录已过期，请重新登录')
    account = db.query(User).filter(User.user_id == token_data['user']['userId']).first()
    if account is None or account.status != '0' or account.del_flag != '0':
        TOKENS_DB.pop(token, None)
        raise HTTPException(status_code=401, detail='账户已停用或删除')
    roles = [role.role_key for role in account.roles if role.status == '0' and role.del_flag == '0']
    return dict(userId=account.user_id, userName=account.user_name, nickName=account.nick_name,
                avatar=account.avatar, roles=roles,
                permissions=['*:*:*'] if 'admin' in roles else ['robustness:*'])


# ==================== API 接口 ====================

@router.post("/login", response_model=LoginResponse, summary="用户登录")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录接口 - 兼容 RuoYi-Vue
    """
    username = request.username
    password = request.password

    # 查询用户
    user = db.query(User).filter(User.user_name == username).first()

    if not user:
        return LoginResponse(code=500, msg="用户不存在")

    if user.status != '0' or user.del_flag != '0':
        return LoginResponse(code=500, msg='账户已停用或删除')

    if not verify_password(password, user.password):
        return LoginResponse(code=500, msg='密码错误')
    if not user.password.startswith(('$2a$', '$2b$', '$2y$')):
        user.password = hash_password(password)
        db.commit()

    # 生成 token
    token = generate_token()

    # 获取用户角色和权限
    roles = [role.role_key for role in user.roles]
    permissions = []
    if "admin" in roles:
        permissions = ["*:*:*"]
    else:
        # 这里简化处理，实际应查询菜单权限
        permissions = ["system:user:list", "system:user:query"]

    user_data = {
        "userId": user.user_id,
        "userName": user.user_name,
        "nickName": user.nick_name,
        "avatar": user.avatar,
        "roles": roles,
        "permissions": permissions
    }

    # 存储 token
    TOKENS_DB[token] = {
        "user": user_data,
        "expire_time": datetime.now() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    }

    return LoginResponse(code=200, msg="登录成功", token=token)


@router.get("/getInfo", response_model=UserInfoResponse, summary="获取用户信息")
async def get_info(current_user: Dict = Depends(get_current_user)):
    """获取当前登录用户信息"""
    user_data = current_user

    return UserInfoResponse(
        code=200,
        msg="操作成功",
        user={
            "userId": user_data["userId"],
            "userName": user_data["userName"],
            "nickName": user_data["nickName"],
            "avatar": user_data.get("avatar", ""),
            "admin": "admin" in user_data.get("roles", [])
        },
        roles=user_data.get("roles", []),
        permissions=user_data.get("permissions", [])
    )


@router.get("/getRouters", response_model=RoutersResponse, summary="获取路由菜单")
async def get_routers(current_user: Dict = Depends(get_current_user)):
    """获取用户路由菜单 - 返回我们的业务菜单"""

    # 定义我们的业务菜单
    menus = [
        {
            "name": "Robustness",
            "path": "/robustness",
            "hidden": False,
            "redirect": "noRedirect",
            "component": "Layout",
            "alwaysShow": True,
            "meta": {
                "title": "鲁棒性测试",
                "icon": "monitor",
                "noCache": False,
                "link": None
            },
            "children": [
                {
                    "name": "ModelManage",
                    "path": "model",
                    "hidden": False,
                    "component": "robustness/model/index",
                    "meta": {
                        "title": "模型管理",
                        "icon": "component",
                        "noCache": False,
                        "link": None
                    }
                },
                {
                    "name": "AttackTest",
                    "path": "attack",
                    "hidden": False,
                    "component": "robustness/attack/index",
                    "meta": {
                        "title": "攻击测试",
                        "icon": "bug",
                        "noCache": False,
                        "link": None
                    }
                },
                {
                    "name": "TaskList",
                    "path": "task",
                    "hidden": False,
                    "component": "robustness/task/index",
                    "meta": {
                        "title": "任务列表",
                        "icon": "list",
                        "noCache": False,
                        "link": None
                    }
                },
                {
                    "name": "ResultView",
                    "path": "result/:taskId",
                    "hidden": True,
                    "component": "robustness/result/index",
                    "meta": {
                        "title": "测试结果",
                        "icon": "chart",
                        "noCache": True,
                        "link": None
                    }
                }
            ]
        },
        {
            "name": "System",
            "path": "/system",
            "hidden": False,
            "redirect": "noRedirect",
            "component": "Layout",
            "alwaysShow": True,
            "meta": {
                "title": "系统管理",
                "icon": "system",
                "noCache": False,
                "link": None
            },
            "children": [
                {
                    "name": "User",
                    "path": "user",
                    "hidden": False,
                    "component": "system/user/index",
                    "meta": {
                        "title": "用户管理",
                        "icon": "user",
                        "noCache": False,
                        "link": None
                    }
                },
                {
                    "name": "Role",
                    "path": "role",
                    "hidden": False,
                    "component": "system/role/index",
                    "meta": {
                        "title": "角色管理",
                        "icon": "peoples",
                        "noCache": False,
                        "link": None
                    }
                },
                {
                    "name": "Menu",
                    "path": "menu",
                    "hidden": False,
                    "component": "system/menu/index",
                    "meta": {
                        "title": "菜单管理",
                        "icon": "tree-table",
                        "noCache": False,
                        "link": None
                    }
                },
                {
                    "name": "Dept",
                    "path": "dept",
                    "hidden": False,
                    "component": "system/dept/index",
                    "meta": {
                        "title": "部门管理",
                        "icon": "tree",
                        "noCache": False,
                        "link": None
                    }
                }
            ]
        },
        {
            "name": "Help",
            "path": "/help",
            "hidden": False,
            "redirect": "noRedirect",
            "component": "Layout",
            "alwaysShow": True,
            "meta": {
                "title": "帮助与文档",
                "icon": "question",
                "noCache": False,
                "link": None
            },
            "children": [
                {
                    "name": "SystemInfo",
                    "path": "info",
                    "hidden": False,
                    "component": "help/info/index",
                    "meta": {
                        "title": "系统介绍",
                        "icon": "question",
                        "noCache": False,
                        "link": None
                    }
                },
                {
                    "name": "OperationGuide",
                    "path": "guide",
                    "hidden": False,
                    "component": "help/guide/index",
                    "meta": {
                        "title": "操作指南",
                        "icon": "guide",
                        "noCache": False,
                        "link": None
                    }
                },
                {
                    "name": "ApiDoc",
                    "path": "api",
                    "hidden": False,
                    "component": "help/api/index",
                    "meta": {
                        "title": "API文档",
                        "icon": "documentation",
                        "noCache": False,
                        "link": None
                    }
                },
                {
                    "name": "Faq",
                    "path": "faq",
                    "hidden": False,
                    "component": "help/faq/index",
                    "meta": {
                        "title": "常见问题",
                        "icon": "message",
                        "noCache": False,
                        "link": None
                    }
                }
            ]
        }
    ]

    if 'admin' not in current_user.get('roles', []):
        menus = [menu for menu in menus if menu['name'] != 'System']
    return RoutersResponse(code=200, msg="操作成功", data=menus)


@router.post("/register", response_model=RegisterResponse, summary="用户注册")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    用户注册接口
    """
    existing_user = db.query(User).filter(User.user_name == request.username).first()
    if existing_user:
        return RegisterResponse(code=500, msg="用户名已存在")

    if request.email:
        existing_email = db.query(User).filter(User.email == request.email).first()
        if existing_email:
            return RegisterResponse(code=500, msg="邮箱已被注册")

    if request.phonenumber:
        existing_phone = db.query(User).filter(User.phonenumber == request.phonenumber).first()
        if existing_phone:
            return RegisterResponse(code=500, msg="手机号已被注册")

    password_hash = hash_password(request.password)

    new_user = User(
        user_name=request.username,
        nick_name=request.nick_name or request.username,
        password=password_hash,
        email=request.email or "",
        phonenumber=request.phonenumber or "",
        sex="0",
        status="0",
        del_flag="0",
        dept_id=103,
        create_by="register",
        create_time=datetime.now()
    )

    db.add(new_user)
    db.flush()

    common_role = db.query(Role).filter(Role.role_key == "common").first()
    if common_role:
        new_user.roles.append(common_role)

    db.commit()
    db.refresh(new_user)

    return RegisterResponse(
        code=200,
        msg="注册成功",
        data={
            "userId": new_user.user_id,
            "userName": new_user.user_name,
            "nickName": new_user.nick_name
        }
    )


@router.post("/logout", summary="退出登录")
async def logout(authorization: str = Header(None, alias="Authorization")):
    """退出登录"""
    if authorization:
        token = authorization.replace("Bearer ", "").strip()
        if token in TOKENS_DB:
            del TOKENS_DB[token]

    return {"code": 200, "msg": "退出成功"}


@router.get("/captchaImage", summary="获取验证码")
async def get_captcha():
    """
    获取验证码 - 简化版，直接返回空验证码
    RuoYi 默认需要验证码，这里禁用
    """
    return {
        "code": 200,
        "msg": "操作成功",
        "captchaEnabled": False,  # 禁用验证码
        "uuid": str(uuid.uuid4()),
        "img": ""
    }




def require_admin(current_user: Dict = Depends(get_current_user)):
    if 'admin' not in current_user.get('roles', []):
        raise HTTPException(status_code=403, detail='需要管理员权限')
    return current_user
