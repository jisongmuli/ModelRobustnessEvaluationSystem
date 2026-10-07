"""Hash new passwords and migrate legacy local database credentials on login."""
import bcrypt
import hashlib
import hmac
from fastapi import HTTPException

def hash_password(password):
    if not isinstance(password, str) or not 5 <= len(password.encode('utf-8')) <= 72:
        raise HTTPException(status_code=400, detail='密码需要 5–72 个 UTF-8 字节')
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('ascii')

def verify_password(password, stored):
    if not isinstance(password, str) or not stored:
        return False
    try:
        if stored.startswith(('$2a$', '$2b$', '$2y$')):
            return bcrypt.checkpw(password.encode('utf-8'), stored.encode('ascii'))
        # Compatibility for existing local databases only; new passwords are always bcrypt.
        return hmac.compare_digest(stored, hashlib.md5(password.encode('utf-8')).hexdigest()) or hmac.compare_digest(stored.encode('utf-8'), password.encode('utf-8'))
    except (ValueError, UnicodeError):
        return False
