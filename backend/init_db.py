"""Create a local database and set an administrator password without embedding one."""
import getpass
import os
from core.database import Base, engine, SessionLocal
from core.passwords import hash_password
from models.system import User, Role, Dept

def initialize(password=None):
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.query(User).filter(User.user_name == 'admin').first():
            print('管理员已存在；未重置任何账号或数据。')
            return
        password = password or os.environ.get('BOOTSTRAP_ADMIN_PASSWORD') or getpass.getpass('设置管理员密码（至少 5 个字符）：')
        hashed = hash_password(password)
        roles = {}
        for key, name, order in [('admin', '管理员', 1), ('common', '普通用户', 2)]:
            role = db.query(Role).filter(Role.role_key == key).first()
            if role is None:
                role = Role(role_key=key, role_name=name, role_sort=order, status='0', del_flag='0')
                db.add(role)
            roles[key] = role
        if db.query(Dept).filter(Dept.dept_id == 103).first() is None:
            db.add(Dept(dept_id=103, dept_name='研究与测试', status='0', del_flag='0'))
        admin = User(user_name='admin', nick_name='管理员', password=hashed, status='0', del_flag='0', dept_id=103)
        admin.roles.append(roles['admin'])
        db.add(admin)
        db.commit()
        print('数据库已初始化。请使用 admin 和刚设置的密码登录。')

if __name__ == '__main__':
    initialize()
