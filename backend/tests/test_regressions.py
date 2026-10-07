import io
import json
import threading
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from torchvision.models import resnet18, resnet34
from PIL import Image

from conftest import login
from api import auth, upload, attack
from core.archives import extract_dataset
from core.attack_engine import AttackEngine
from core.dataset import get_cifar10_dataloader, get_custom_dataloader
from core.database import SessionLocal
from core.model_loader import ModelLoader
from core.preprocessing import NormalizedModel
from models.system import User
from schemas import ModelInfo

def image_bytes(color='white'):
    stream = io.BytesIO()
    Image.new('RGB', (16, 16), color).save(stream, format='PNG')
    return stream.getvalue()

def zip_bytes(names):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w') as archive:
        for name in names:
            archive.writestr(name, image_bytes())
    return stream.getvalue()

def record(owner=2, classes=10):
    return ModelInfo(id='model_test', user_id=owner, filename='test.pth', file_size=1,
                     upload_time=datetime.now(), num_classes=classes, img_size=16)

@pytest.mark.parametrize('endpoint', ['/system/user/list', '/system/role/list', '/system/menu/list', '/system/dept/list', '/api/model/list'])
def test_anonymous_cannot_read_private_endpoints(client, endpoint):
    assert client.get(endpoint).status_code == 401

@pytest.mark.parametrize('endpoint', ['/system/user/list', '/system/role/list', '/system/menu/list', '/system/dept/list'])
def test_regular_account_cannot_use_admin_endpoints(client, endpoint):
    assert client.get(endpoint, headers=login(client)).status_code == 403

def test_profile_static_route_and_no_password_leak(client):
    response = client.get('/system/user/profile', headers=login(client))
    assert response.status_code == 200
    assert response.json()['data']['userName'] == 'alice'
    assert 'password' not in response.text

@pytest.mark.parametrize('flag', ['status', 'del_flag'])
def test_disabled_deleted_users_and_existing_sessions_are_rejected(client, flag):
    headers = login(client)
    with SessionLocal() as db:
        user = db.get(User, 2)
        setattr(user, flag, '1' if flag == 'status' else '2')
        db.commit()
    assert client.get('/getInfo', headers=headers).status_code == 401
    assert client.post('/login', json=dict(username='alice', password='Initial42!')).json()['code'] != 200

def test_admin_reset_password_persists_and_revokes_old_session(client):
    previous = login(client)
    admin = login(client, 'admin')
    response = client.put('/system/user/resetPwd', headers=admin, json=dict(userId=2, password='Changed42!'))
    assert response.json()['code'] == 200
    assert client.get('/getInfo', headers=previous).status_code == 401
    login(client, 'alice', 'Changed42!')
    with SessionLocal() as db:
        assert db.get(User, 2).password.startswith('$2')

def test_add_user_hashes_password_and_saves_roles(client):
    response = client.post('/system/user', headers=login(client, 'admin'), json=dict(userName='carol', nickName='Carol', password='Carol42!', roleIds=[2]))
    assert response.json()['code'] == 200
    login(client, 'carol', 'Carol42!')
    with SessionLocal() as db:
        assert db.query(User).filter_by(user_name='carol').one().password.startswith('$2')

def test_models_configs_and_datasets_are_isolated(client):
    headers = login(client)
    upload.models_db['model_test'] = record(owner=3)
    upload.model_configs_db['model_test'] = dict(model_type='resnet18')
    assert client.get('/api/model/model_test', headers=headers).status_code == 403
    assert client.get('/api/model/config/model_test', headers=headers).status_code == 403
    assert client.get('/api/model/list', headers=headers).json()['data'] == []
    upload.models_db['model_test'] = record(owner=2)
    with patch('api.upload.get_model_path', return_value=Path('unused')):
        upload.datasets_db['foreign'] = dict(id='foreign', user_id=3, num_classes=10)
        request = dict(model_id='model_test', dataset_id='foreign', attacks=[dict(attack_type='fgsm')])
        assert client.post('/api/attack/start', headers=headers, json=request).status_code == 403
        request['dataset_id'] = 'missing'
        assert client.post('/api/attack/start', headers=headers, json=request).status_code == 404

def test_unowned_legacy_records_only_visible_to_admin(client):
    upload.models_db['model_test'] = record(owner=None)
    assert client.get('/api/model/list', headers=login(client)).json()['data'] == []
    assert len(client.get('/api/model/list', headers=login(client, 'admin')).json()['data']) == 1

def test_private_models_metadata_not_public_static_files(client):
    upload.save_models_db()
    assert client.get('/uploads/models_db.json').status_code == 404

@pytest.mark.parametrize('names', [['class_a/img.png'], ['wrapper/class_a/img.png'], ['wrapper/class_a/img.png', 'wrapper/class_b/img.png']])
def test_valid_single_class_and_wrapped_zips(client, names):
    response = client.post('/api/model/dataset/upload', headers=login(client), files={'file': ('DATA.ZIP', zip_bytes(names), 'application/zip')})
    assert response.status_code == 200, response.text
    assert response.json()['data']['num_images'] == len(names)
    assert 'path' not in response.json()['data']

@pytest.mark.parametrize('name', ['../escape.png', '/absolute.png', 'C:/escape.png', '..\\escape.png'])
def test_zip_escape_is_rejected(tmp_path, name):
    archive = tmp_path / 'bad.zip'
    archive.write_bytes(zip_bytes([name]))
    with pytest.raises(ValueError):
        extract_dataset(archive, tmp_path / 'dataset')
    assert not (tmp_path / 'escape.png').exists()

def test_dataset_load_failure_never_uses_random_data():
    with patch('core.dataset.torchvision.datasets.CIFAR10', side_effect=OSError('offline')):
        with pytest.raises(ValueError, match='不会使用随机数据'):
            get_cifar10_dataloader(num_samples=10)

def test_sampling_reproducible_and_inputs_in_pixel_space(tmp_path):
    category = tmp_path / 'category'
    category.mkdir()
    for index in range(12):
        (category / f'{index}.png').write_bytes(image_bytes())
    a = get_custom_dataloader(str(tmp_path), num_samples=5, seed=42, img_size=16)
    b = get_custom_dataloader(str(tmp_path), num_samples=5, seed=42, img_size=16)
    assert a.dataset.indices == b.dataset.indices
    images, _ = next(iter(a))
    assert images.min() >= 0 and images.max() <= 1

class TinyClassifier(nn.Module):
    def forward(self, images):
        mean = images.flatten(1).mean(1)
        return torch.stack([(.5 - mean) * 8, (mean - .5) * 8], dim=1)

def test_pixel_epsilon_and_normalization_apply_at_model_boundary():
    model = NormalizedModel(TinyClassifier(), ((.5, .5, .5), (.25, .25, .25)))
    engine = AttackEngine(model, torch.device('cpu'))
    images = torch.full((2, 3, 4, 4), .8)
    labels = torch.ones(2, dtype=torch.long)
    attacker = engine.create_attack('fgsm', eps=.03)
    adversarial = attacker(images, labels)
    assert float((adversarial - images).abs().max()) <= .030001
    result = engine.evaluate(attacker, DataLoader(TensorDataset(images, labels), batch_size=1), 'fgsm', .03)
    assert result.num_samples == 2 and result.clean_accuracy == 1
    assert result.avg_perturbation_linf <= .030001

@pytest.mark.parametrize('factory, expected', [(resnet18, 'resnet18'), (resnet34, 'resnet34')])
def test_real_resnet_architecture_detection(factory, expected):
    assert ModelLoader('cpu')._detect_model_type(factory(num_classes=3).state_dict()) == expected

def test_safe_checkpoint_infers_class_count_and_rejects_missing_weights(tmp_path):
    loader = ModelLoader('cpu')
    state = resnet18(num_classes=3).state_dict()
    path = tmp_path / 'model.pth'
    torch.save(dict(model_type='resnet18', state_dict=state, img_size=32), path)
    loaded, info = loader.load_model(str(path))
    assert info['num_classes'] == loaded.fc.out_features == 3
    del state['layer1.0.conv1.weight']
    torch.save(dict(model_type='resnet18', state_dict=state), path)
    with pytest.raises(ValueError, match='不会使用随机权重'):
        loader.load_model(str(path))

def test_python_model_objects_are_not_deserialized(tmp_path):
    path = tmp_path / 'unsafe.pth'
    torch.save(TinyClassifier(), path)
    with pytest.raises(ValueError, match='安全读取'):
        ModelLoader('cpu').load_model(str(path))

def test_api_remains_responsive_during_background_evaluation(client):
    headers = login(client)
    upload.models_db['model_test'] = record()
    entered, release = threading.Event(), threading.Event()
    def slow_task(*args):
        entered.set()
        release.wait(5)
    request = dict(model_id='model_test', attacks=[dict(attack_type='fgsm')])
    with patch('api.upload.get_model_path', return_value=Path('unused')), patch('api.attack._run_attack_task', side_effect=slow_task):
        with ThreadPoolExecutor() as pool:
            future = pool.submit(client.post, '/api/attack/start', headers=headers, json=request)
            try:
                assert entered.wait(3)
                assert client.get('/api/attack/tasks', headers=headers).status_code == 200
            finally:
                release.set()
            assert future.result().status_code == 200

@pytest.mark.parametrize('sample_count', [10, 1])
def test_tiny_real_image_evaluation_completes_and_records_settings(client, tmp_path, sample_count):
    headers = login(client)
    for category, color in [('a_dark', 'black'), ('b_light', 'white')]:
        directory = tmp_path / category
        directory.mkdir()
        for index in range(5):
            (directory / f'{index}.png').write_bytes(image_bytes(color))
    upload.models_db['model_test'] = record(classes=2)
    upload.datasets_db['own'] = dict(id='own', user_id=2, num_classes=2, path=str(tmp_path))
    class Loader:
        device = torch.device('cpu')
        def load_model(self, *args, **kwargs):
            return TinyClassifier(), dict(num_classes=2, img_size=16)
    with patch('api.upload.get_model_path', return_value=Path('unused')), patch('api.attack.get_model_loader', return_value=Loader()):
        result = client.post('/api/attack/start', headers=headers, json=dict(model_id='model_test', dataset_id='own', attacks=[dict(attack_type='fgsm', eps=.01)], normalization='none', seed=17, num_samples=sample_count))
    task_id = result.json()['data']['task_id']
    response = client.get(f'/api/attack/result/{task_id}', headers=headers)
    assert response.status_code == 200, response.text
    metrics = response.json()['data']['metrics'][0]
    assert metrics['num_samples'] == sample_count and metrics['clean_accuracy'] == 1
    assert response.json()['data']['summary']['seed'] == 17

def test_pending_task_cannot_be_deleted(client):
    headers = login(client)
    attack.tasks_db['pending'] = dict(task_id='pending', user_id=2, model_id='model_test', status='pending')
    assert client.delete('/api/attack/task/pending', headers=headers).status_code == 400

def test_avatar_upload_rejects_non_image(client):
    response = client.post('/system/user/profile/avatar', headers=login(client), files={'avatarfile': ('x.html', b'<html>bad</html>', 'text/html')})
    assert response.status_code == 400
