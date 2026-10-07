from .upload import router as upload_router
from .attack import router as attack_router
from .auth import router as auth_router
from .user import router as user_router
from .role import router as role_router
from .menu import router as menu_router
from .dept import router as dept_router
from .dict_data import router as dict_data_router
from .config import router as config_router

__all__ = [
    "upload_router",
    "attack_router",
    "auth_router",
    "user_router",
    "role_router",
    "menu_router",
    "dept_router",
    "dict_data_router",
    "config_router"
]
