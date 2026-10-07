import os
import sys
import tempfile
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
test_runtime = tempfile.TemporaryDirectory(prefix='robustness-tests-')
os.environ['ROBUSTNESS_STORAGE_DIR'] = test_runtime.name
os.environ['DATABASE_URL'] = f'sqlite:///{Path(test_runtime.name).as_posix()}/test.sqlite3'

from core.database import Base, engine, SessionLocal
from core.passwords import hash_password
from models.system import User, Role
from api import auth, upload, attack
from main import app
from fastapi.testclient import TestClient

@pytest.fixture(scope='session', autouse=True)
def cleanup_test_runtime():
    yield
    engine.dispose()
    assert Path(test_runtime.name).resolve().parent == Path(tempfile.gettempdir()).resolve()
    test_runtime.cleanup()

@pytest.fixture
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    auth.TOKENS_DB.clear()
    upload.models_db.clear()
    upload.model_configs_db.clear()
    upload.datasets_db.clear()
    attack.tasks_db.clear()
    hashed = hash_password('Initial42!')
    with SessionLocal() as db:
        admin = Role(role_id=1, role_name='管理员', role_key='admin', role_sort=1)
        common = Role(role_id=2, role_name='用户', role_key='common', role_sort=2)
        db.add_all([admin, common])
        for user_id, username, role in [(1, 'admin', admin), (2, 'alice', common), (3, 'bob', common)]:
            account = User(user_id=user_id, user_name=username, nick_name=username, password=hashed)
            account.roles.append(role)
            db.add(account)
        db.commit()
    with TestClient(app) as result:
        yield result

def login(client, username='alice', password='Initial42!'):
    result = client.post('/login', json=dict(username=username, password=password))
    assert result.json()['code'] == 200, result.text
    return {'Authorization': 'Bearer ' + result.json()['token']}
