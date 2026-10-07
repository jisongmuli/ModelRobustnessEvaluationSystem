"""
模型上传 API - 支持用户数据隔离
"""
import json
import logging
import shutil
import uuid
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import aiofiles
from fastapi import APIRouter, File, HTTPException, Query, UploadFile, Depends, Header

from core import get_model_loader
from schemas import (
    BaseResponse,
    ModelInfo,
    ModelListResponse,
    ModelStructureConfig,
    UploadResponse,
)
from api.auth import get_current_user
from core.settings import UPLOAD_DIR, DATA_DIR
from core.storage import write_json
from core.archives import extract_dataset
from starlette.concurrency import run_in_threadpool

router = APIRouter(prefix="/model", tags=["模型管理"])
logger = logging.getLogger(__name__)

CUSTOM_DATA_DIR = DATA_DIR / "custom"
CUSTOM_DATA_DIR.mkdir(exist_ok=True)

models_db: Dict[str, ModelInfo] = {}
DB_FILE = UPLOAD_DIR / "models_db.json"
datasets_db: Dict[str, Dict] = {}
DATASETS_DB_FILE = UPLOAD_DIR / "datasets_db.json"
model_configs_db: Dict[str, Dict] = {}
MODEL_CONFIGS_DB_FILE = UPLOAD_DIR / "model_configs_db.json"

ALLOWED_EXTENSIONS = {".pt", ".pth"}
MAX_FILE_SIZE = 500 * 1024 * 1024


def save_models_db():
    data = {key: value.model_dump() for key, value in models_db.items()}
    for item in data.values():
        if isinstance(item.get("upload_time"), datetime):
            item["upload_time"] = item["upload_time"].isoformat()
    write_json(DB_FILE, data)


def load_models_db():
    if not DB_FILE.exists():
        return
    try:
        with open(DB_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        for key, value in data.items():
            if value.get("upload_time") and isinstance(value["upload_time"], str):
                value["upload_time"] = datetime.fromisoformat(value["upload_time"])
            models_db[key] = ModelInfo(**value)
    except Exception as error:
        logger.warning("Failed to load models db: %s", error)


def save_datasets_db():
    write_json(DATASETS_DB_FILE, datasets_db)


def load_datasets_db():
    if not DATASETS_DB_FILE.exists():
        return
    try:
        with open(DATASETS_DB_FILE, "r", encoding="utf-8") as file:
            global datasets_db
            datasets_db = json.load(file)
    except Exception as error:
        logger.warning("Failed to load datasets db: %s", error)


def save_model_configs_db():
    write_json(MODEL_CONFIGS_DB_FILE, model_configs_db)


def load_model_configs_db():
    if not MODEL_CONFIGS_DB_FILE.exists():
        return
    try:
        with open(MODEL_CONFIGS_DB_FILE, "r", encoding="utf-8") as file:
            global model_configs_db
            model_configs_db = json.load(file)
    except Exception as error:
        logger.warning("Failed to load model configs db: %s", error)






load_models_db()
load_datasets_db()
load_model_configs_db()


def get_model_config(model_id: str) -> Optional[Dict]:
    return model_configs_db.get(model_id)


def _build_model_info(
    model_id: str,
    filename: str,
    file_size: int,
    upload_time: datetime,
    user_id: Optional[int] = None,
    info: Optional[Dict[str, Optional[int]]] = None,
    status: str = "ready",
    load_error: Optional[str] = None,
) -> ModelInfo:
    info = info or {}
    img_size = info.get("img_size")
    input_shape = info.get("input_shape")
    if input_shape is None and img_size:
        input_shape = [1, 3, img_size, img_size]
    return ModelInfo(
        id=model_id,
        user_id=user_id,
        filename=filename,
        file_size=file_size,
        upload_time=upload_time,
        model_type=info.get("model_type"),
        num_classes=info.get("num_classes"),
        input_shape=input_shape,
        img_size=img_size,
        status=status,
        load_error=load_error,
    )


@router.post(
    "/upload",
    response_model=UploadResponse,
    summary="上传模型文件",
    description="上传 PyTorch 模型文件（.pt 或 .pth 格式），系统会自动解析模型信息",
)
async def upload_model(
    file: UploadFile = File(..., description="PyTorch 模型文件 (.pt/.pth)"),
    current_user: Dict = Depends(get_current_user)
):
    user_id = current_user.get("userId")
    filename = file.filename or "model.pth"
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的文件格式: {ext}，仅支持 .pt 和 .pth")
    model_id = f"model_{uuid.uuid4().hex[:12]}"
    save_path = UPLOAD_DIR / f"{model_id}{ext}"
    try:
        file_size = 0
        async with aiofiles.open(save_path, "wb") as target_file:
            while chunk := await file.read(1024 * 1024):
                file_size += len(chunk)
                if file_size > MAX_FILE_SIZE:
                    await target_file.close()
                    save_path.unlink(missing_ok=True)
                    raise HTTPException(status_code=413, detail=f"文件过大，最大支持 {MAX_FILE_SIZE // 1024 // 1024}MB")
                await target_file.write(chunk)
    except HTTPException:
        raise
    except Exception as error:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"文件保存失败: {error}")
    upload_time = datetime.now()
    loader_info: Dict[str, Optional[int]] = {}
    load_error = None
    status = "ready"
    response_msg = "上传成功"
    try:
        loader = get_model_loader()
        _, loader_info = await run_in_threadpool(loader.load_model, str(save_path))
    except Exception as error:
        load_error = str(error)
        status = "needs_config"
        response_msg = "上传成功，但模型结构未完全识别，请补充配置参数"
        logger.warning("模型自动解析失败 %s: %s", filename, error)
    model_info = _build_model_info(
        model_id=model_id,
        filename=filename,
        file_size=file_size,
        upload_time=upload_time,
        user_id=user_id,
        info=loader_info,
        status=status,
        load_error=load_error,
    )
    models_db[model_id] = model_info
    save_models_db()
    return UploadResponse(code=200, msg=response_msg, data=model_info)


@router.post(
    "/configure",
    response_model=UploadResponse,
    summary="手动配置模型结构",
    description="当模型无法自动识别时，手动指定模型类型、类别数、输入尺寸和分类头结构",
)
async def configure_model(config: ModelStructureConfig, current_user: Dict = Depends(get_current_user)):
    user_id = current_user.get("userId")
    if config.model_id not in models_db:
        raise HTTPException(status_code=404, detail="模型不存在")
    existing_model = models_db[config.model_id]
    if "admin" not in current_user.get("roles", []) and existing_model.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权操作此模型")
    try:
        model_path = get_model_path(config.model_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    try:
        loader = get_model_loader()
        _, loader_info = await run_in_threadpool(loader.load_model, str(model_path), model_config=config.model_dump())
    except Exception as error:
        raise HTTPException(status_code=400, detail=f"模型配置无效: {error}")
    model_configs_db[config.model_id] = config.model_dump()
    save_model_configs_db()
    updated_model = _build_model_info(
        model_id=existing_model.id,
        filename=existing_model.filename,
        file_size=existing_model.file_size,
        upload_time=existing_model.upload_time,
        user_id=existing_model.user_id,
        info=loader_info,
        status="ready",
        load_error=None,
    )
    models_db[config.model_id] = updated_model
    save_models_db()
    return UploadResponse(code=200, msg="模型配置已更新", data=updated_model)


@router.get(
    "/config/{model_id}",
    response_model=BaseResponse,
    summary="获取模型结构配置",
    description="获取模型的手动结构配置，如果没有则返回空",
)
async def get_model_config_detail(model_id: str, current_user: Dict = Depends(get_current_user)):
    if model_id not in models_db:
        raise HTTPException(status_code=404, detail="模型不存在")
    if "admin" not in current_user.get("roles", []) and models_db[model_id].user_id != current_user["userId"]:
        raise HTTPException(status_code=403, detail="无权访问此模型配置")
    return BaseResponse(data=model_configs_db.get(model_id))


@router.get(
    "/list",
    response_model=ModelListResponse,
    summary="获取模型列表",
    description="获取当前用户已上传的模型列表，支持分页和文件名筛选",
)
async def list_models(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=10, ge=1, le=100, description="每页数量"),
    filename: Optional[str] = Query(default=None, description="按文件名模糊筛选"),
    current_user: Dict = Depends(get_current_user)
):
    user_id = current_user.get("userId")
    is_admin = "admin" in current_user.get("roles", [])
    model_list = list(models_db.values())
    if not is_admin:
        model_list = [item for item in model_list if item.user_id == user_id]
    if filename:
        keyword = filename.strip().lower()
        model_list = [item for item in model_list if keyword in item.filename.lower()]
    total = len(model_list)
    start = (page - 1) * page_size
    end = start + page_size
    return ModelListResponse(code=200, msg="success", data=model_list[start:end], total=total)


@router.get(
    "/{model_id}",
    response_model=UploadResponse,
    summary="获取模型详情",
    description="根据模型ID获取模型详细信息",
)
async def get_model(model_id: str, current_user: Dict = Depends(get_current_user)):
    user_id = current_user.get("userId")
    is_admin = "admin" in current_user.get("roles", [])
    if model_id not in models_db:
        raise HTTPException(status_code=404, detail="模型不存在")
    model_info = models_db[model_id]
    if not is_admin and model_info.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权访问此模型")
    return UploadResponse(code=200, msg="success", data=model_info)


@router.delete(
    "/{model_id}",
    response_model=BaseResponse,
    summary="删除模型",
    description="根据模型ID删除模型文件和记录",
)
async def delete_model(model_id: str, current_user: Dict = Depends(get_current_user)):
    user_id = current_user.get("userId")
    is_admin = "admin" in current_user.get("roles", [])
    if model_id not in models_db:
        raise HTTPException(status_code=404, detail="模型不存在")
    model_info = models_db[model_id]
    if not is_admin and model_info.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权删除此模型")
    from api.attack import tasks_db as attack_tasks
    if any(task["model_id"] == model_id and task["status"] in ("pending", "running") for task in attack_tasks.values()):
        raise HTTPException(status_code=400, detail="模型仍有待执行或运行中的任务")
    for ext in ALLOWED_EXTENSIONS:
        file_path = UPLOAD_DIR / f"{model_id}{ext}"
        if file_path.exists():
            file_path.unlink()
            break
    del models_db[model_id]
    save_models_db()
    if model_id in model_configs_db:
        del model_configs_db[model_id]
        save_model_configs_db()
    return BaseResponse(code=200, msg="删除成功", data={"id": model_id, "filename": model_info.filename})


@router.post(
    "/dataset/upload",
    response_model=BaseResponse,
    summary="上传数据集",
    description="上传自定义数据集 (.zip)，需符合 ImageFolder 格式 (root/class/image.jpg)",
)
async def upload_dataset(file: UploadFile = File(...), current_user: Dict = Depends(get_current_user)):
    filename = file.filename or ''
    if Path(filename).suffix.lower() != '.zip':
        raise HTTPException(status_code=400, detail='仅支持 .zip 格式')
    dataset_id = f'dataset_{uuid.uuid4().hex[:12]}'
    save_path = CUSTOM_DATA_DIR / f'{dataset_id}.zip'
    extract_path = CUSTOM_DATA_DIR / dataset_id
    try:
        size = 0
        async with aiofiles.open(save_path, 'wb') as target:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_FILE_SIZE:
                    raise HTTPException(status_code=413, detail='数据集压缩包最大为 500 MB')
                await target.write(chunk)
        actual_root = await run_in_threadpool(extract_dataset, save_path, extract_path)
        from torchvision.datasets import ImageFolder
        dataset = await run_in_threadpool(ImageFolder, str(actual_root))
        dataset_info = dict(id=dataset_id, user_id=current_user['userId'], name=filename,
                            classes=dataset.classes, num_classes=len(dataset.classes),
                            num_images=len(dataset), path=str(actual_root), upload_time=datetime.now().isoformat())
        datasets_db[dataset_id] = dataset_info
        save_datasets_db()
        return BaseResponse(msg='上传成功', data={key: value for key, value in dataset_info.items() if key != 'path'})
    except Exception as error:
        # Only a generated direct child of CUSTOM_DATA_DIR may be removed recursively.
        if extract_path.resolve().parent != CUSTOM_DATA_DIR.resolve():
            raise RuntimeError('Invalid cleanup target') from error
        shutil.rmtree(extract_path, ignore_errors=True)
        if isinstance(error, HTTPException):
            raise
        raise HTTPException(status_code=400, detail=f'数据集解压或图像结构校验失败: {error}') from error
    finally:
        save_path.unlink(missing_ok=True)
        await file.close()


@router.get("/dataset/list", summary="获取数据集列表")
async def list_datasets(current_user: Dict = Depends(get_current_user)):
    user_id = current_user.get("userId")
    is_admin = "admin" in current_user.get("roles", [])
    dataset_list = list(datasets_db.values())
    if not is_admin:
        dataset_list = [item for item in dataset_list if item.get("user_id") == user_id]
    return BaseResponse(data=[{key: value for key, value in item.items() if key != "path"} for item in dataset_list])


def get_model_path(model_id: str) -> Path:
    if model_id not in models_db:
        raise ValueError(f"模型不存在: {model_id}")
    for ext in ALLOWED_EXTENSIONS:
        file_path = UPLOAD_DIR / f"{model_id}{ext}"
        if file_path.exists():
            return file_path
    raise ValueError(f"模型文件不存在: {model_id}")
