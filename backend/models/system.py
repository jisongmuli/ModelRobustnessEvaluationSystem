from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base

# 用户和角色关联表
user_role = Table(
    'sys_user_role',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('sys_user.user_id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('sys_role.role_id'), primary_key=True)
)

# 角色和菜单关联表
role_menu = Table(
    'sys_role_menu',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('sys_role.role_id'), primary_key=True),
    Column('menu_id', Integer, ForeignKey('sys_menu.menu_id'), primary_key=True)
)

class User(Base):
    __tablename__ = "sys_user"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dept_id = Column(Integer, index=True)
    user_name = Column(String(30), unique=True, index=True, nullable=False)
    nick_name = Column(String(30), nullable=False)
    user_type = Column(String(2), default="00")
    email = Column(String(50), default="")
    phonenumber = Column(String(11), default="")
    sex = Column(String(1), default="0")
    avatar = Column(String(100), default="")
    password = Column(String(100), default="")
    status = Column(String(1), default="0")
    del_flag = Column(String(1), default="0")
    login_ip = Column(String(128), default="")
    login_date = Column(DateTime)
    create_by = Column(String(64), default="")
    create_time = Column(DateTime, default=datetime.now)
    update_by = Column(String(64), default="")
    update_time = Column(DateTime)
    remark = Column(String(500), default=None)

    # 关联
    roles = relationship("Role", secondary=user_role, back_populates="users")

class Role(Base):
    __tablename__ = "sys_role"

    role_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role_name = Column(String(30), nullable=False)
    role_key = Column(String(100), nullable=False)
    role_sort = Column(Integer, nullable=False)
    data_scope = Column(String(1), default="1")
    menu_check_strictly = Column(Boolean, default=True)
    dept_check_strictly = Column(Boolean, default=True)
    status = Column(String(1), default="0")
    del_flag = Column(String(1), default="0")
    create_by = Column(String(64), default="")
    create_time = Column(DateTime, default=datetime.now)
    update_by = Column(String(64), default="")
    update_time = Column(DateTime)
    remark = Column(String(500), default=None)

    # 关联
    users = relationship("User", secondary=user_role, back_populates="roles")
    menus = relationship("Menu", secondary=role_menu, back_populates="roles")

class Menu(Base):
    __tablename__ = "sys_menu"

    menu_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    menu_name = Column(String(50), nullable=False)
    parent_id = Column(Integer, default=0)
    order_num = Column(Integer, default=0)
    path = Column(String(200), default="")
    component = Column(String(255), default=None)
    query = Column(String(255), default=None)
    is_frame = Column(Integer, default=1)
    is_cache = Column(Integer, default=0)
    menu_type = Column(String(1), default="")
    visible = Column(String(1), default="0")
    status = Column(String(1), default="0")
    perms = Column(String(100), default=None)
    icon = Column(String(100), default="#")
    create_by = Column(String(64), default="")
    create_time = Column(DateTime, default=datetime.now)
    update_by = Column(String(64), default="")
    update_time = Column(DateTime)
    remark = Column(String(500), default="")

    # 关联
    roles = relationship("Role", secondary=role_menu, back_populates="menus")

class Dept(Base):
    __tablename__ = "sys_dept"

    dept_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    parent_id = Column(Integer, default=0)
    ancestors = Column(String(50), default="")
    dept_name = Column(String(30), default="")
    order_num = Column(Integer, default=0)
    leader = Column(String(20), default=None)
    phone = Column(String(11), default=None)
    email = Column(String(50), default=None)
    status = Column(String(1), default="0")
    del_flag = Column(String(1), default="0")
    create_by = Column(String(64), default="")
    create_time = Column(DateTime, default=datetime.now)
    update_by = Column(String(64), default="")
    update_time = Column(DateTime)
