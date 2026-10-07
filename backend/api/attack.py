"""
对抗攻击 API - 支持用户数据隔离和时间记录
"""
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Depends
from torch.utils.data import DataLoader, TensorDataset

from core import get_attack_engine, get_model_loader
from core.dataset import get_cifar10_dataloader, get_custom_dataloader, NORMALIZATIONS
from core.preprocessing import NormalizedModel
from core.settings import UPLOAD_DIR, RESULTS_DIR
from core.storage import write_json
from threading import Lock

EVALUATION_LOCK = Lock()
from schemas import (
    AttackRequest,
    AttackResultResponse,
    AttackStartResponse,
    BaseResponse,
    TaskInfo,
    TaskListResponse,
    TaskStatus,
    TaskStatusResponse,
)
from api.auth import get_current_user

router = APIRouter(prefix="/attack", tags=["对抗攻击"])
logger = logging.getLogger(__name__)

TASKS_DB_FILE = UPLOAD_DIR / "tasks_db.json"
tasks_db: Dict[str, Dict[str, Any]] = {}


def save_tasks_db():
    TASKS_DB_FILE.parent.mkdir(exist_ok=True)
    write_json(TASKS_DB_FILE, tasks_db)


def load_tasks_db():
    if not TASKS_DB_FILE.exists():
        return
    try:
        with open(TASKS_DB_FILE, "r", encoding="utf-8") as file:
            global tasks_db
            tasks_db = json.load(file)
    except Exception as error:
        logger.warning("Failed to load tasks db: %s", error)


load_tasks_db()
for interrupted_task in tasks_db.values():
    if interrupted_task['status'] in ('pending', 'running'):
        interrupted_task.update(status='failed', error_msg='服务重启，任务已中断，请重新创建', end_time=datetime.now().isoformat())
if tasks_db:
    save_tasks_db()




def _run_attack_task(
    task_id: str,
    model_id: str,
    model_path: str,
    attack_configs: List[Dict],
    batch_size: int,
    num_samples: int,
    dataset_id: str = None,
    normalization: str = "auto",
    seed: int = 42,
):
    task = tasks_db[task_id]
    try:
        task["status"] = TaskStatus.RUNNING.value
        task["start_time"] = datetime.now().isoformat()
        save_tasks_db()
        from api.upload import datasets_db, get_model_config, models_db
        loader = get_model_loader()
        stored_model = models_db.get(model_id)
        model_config = get_model_config(model_id)
        if model_config is None and stored_model is not None:
            model_config = {
                "model_type": stored_model.model_type,
                "num_classes": stored_model.num_classes,
                "img_size": stored_model.img_size,
            }
        model, model_info = loader.load_model(model_path, model_config=model_config)
        num_classes = model_info.get("num_classes") or 10
        img_size = model_info.get("img_size") or 224
        if dataset_id:
            if dataset_id not in datasets_db:
                raise ValueError('自定义数据集已不存在，不会替换为其他数据')
            record = datasets_db[dataset_id]
            if record['num_classes'] != num_classes:
                raise ValueError('数据集类别数与模型输出维度不一致')
            dataloader = get_custom_dataloader(record['path'], batch_size, num_samples, img_size, seed)
        else:
            if num_classes != 10:
                raise ValueError('CIFAR-10 为 10 类，请选择与模型一致的自定义数据集')
            dataloader = get_cifar10_dataloader(train=False, batch_size=batch_size,
                                              num_samples=num_samples, img_size=img_size, seed=seed)
        normalization = ('imagenet' if dataset_id else 'cifar10') if normalization == 'auto' else normalization
        model = NormalizedModel(model, NORMALIZATIONS[normalization]).to(loader.device).eval()
        engine = get_attack_engine(model, loader.device)
        total_attacks = len(attack_configs)
        completed_attacks = 0

        def progress_callback(attack_type: str, batch_current: int, batch_total: int):
            nonlocal completed_attacks
            attack_progress = batch_current / batch_total
            overall_progress = (completed_attacks + attack_progress) / total_attacks * 100
            task["progress"] = int(overall_progress)
            task["current_attack"] = attack_type

        results = []
        for config in attack_configs:
            attack_type = config.get("attack_type", "fgsm")
            eps = config.get("eps", 0.03)
            steps = config.get("steps", 10)
            alpha = config.get("alpha")
            task["current_attack"] = attack_type
            attack = engine.create_attack(attack_type, eps, steps, alpha)
            result = engine.evaluate(
                attack,
                dataloader,
                attack_type,
                eps,
                lambda current, total: progress_callback(attack_type, current, total),
            )
            results.append(result.to_dict())
            completed_attacks += 1
        task["status"] = TaskStatus.COMPLETED.value
        task["progress"] = 100
        task["end_time"] = datetime.now().isoformat()
        task["results"] = {
            "metrics": results,
            "summary": {
                "total_attacks": len(results),
                "avg_clean_accuracy": sum(item["clean_accuracy"] for item in results) / len(results),
                "avg_robust_accuracy": sum(item["robust_accuracy"] for item in results) / len(results),
                "avg_attack_success_rate": sum(item["attack_success_rate"] for item in results) / len(results),
                "dataset_id": dataset_id or "cifar10",
                "normalization": normalization,
                "seed": seed,
                "num_classes": num_classes,
                "img_size": img_size,
            },
        }
        save_tasks_db()
    except Exception as error:
        task["status"] = TaskStatus.FAILED.value
        task["error_msg"] = str(error)
        task["end_time"] = datetime.now().isoformat()
        save_tasks_db()
        logger.error("Attack task %s failed: %s", task_id, error)


@router.post(
    "/start",
    response_model=AttackStartResponse,
    summary="启动对抗攻击测试",
    description="对指定模型启动对抗攻击测试，支持多种攻击类型",
)
async def start_attack(
    request: AttackRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
):
    from api.upload import get_model_config, get_model_path, models_db, datasets_db
    user_id = current_user.get("userId")
    is_admin = "admin" in current_user.get("roles", [])
    if request.model_id not in models_db:
        raise HTTPException(status_code=404, detail="模型不存在")
    model_record = models_db[request.model_id]
    if not is_admin and model_record.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权操作此模型")
    if model_record.status == "needs_config" and not get_model_config(request.model_id):
        raise HTTPException(status_code=400, detail="模型结构尚未识别，请先调用 /api/model/configure 配置模型参数")
    try:
        model_path = get_model_path(request.model_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    if request.dataset_id:
        dataset = datasets_db.get(request.dataset_id)
        if dataset is None:
            raise HTTPException(status_code=404, detail='数据集不存在')
        if not is_admin and dataset.get('user_id') != user_id:
            raise HTTPException(status_code=403, detail='无权使用此数据集')
        expected_classes = dataset['num_classes']
    else:
        expected_classes = 10
    if model_record.num_classes is not None and model_record.num_classes != expected_classes:
        raise HTTPException(status_code=400, detail='数据集类别数与模型输出维度不一致')
    task_id = f"task_{uuid.uuid4().hex[:12]}"
    current_time = datetime.now()
    task_data = {
        "task_id": task_id,
        "model_id": request.model_id,
        "user_id": user_id,
        "status": TaskStatus.PENDING.value,
        "progress": 0,
        "current_attack": None,
        "create_time": current_time.isoformat(),
        "start_time": None,
        "end_time": None,
        "error_msg": None,
        "attack_configs": [config.model_dump() for config in request.attacks],
        "batch_size": request.batch_size,
        "num_samples": request.num_samples,
        "dataset_id": request.dataset_id,
        "normalization": request.normalization,
        "seed": request.seed,
        "results": None,
    }
    tasks_db[task_id] = task_data
    save_tasks_db()
    task_info = TaskInfo(
        task_id=task_id,
        model_id=request.model_id,
        status=TaskStatus.PENDING,
        progress=0,
        current_attack=None,
        create_time=current_time,
        start_time=None,
        end_time=None,
        error_msg=None,
    )
    background_tasks.add_task(
        run_attack_task,
        task_id,
        request.model_id,
        str(model_path),
        [config.model_dump() for config in request.attacks],
        request.batch_size,
        request.num_samples,
        request.dataset_id,
        request.normalization,
        request.seed,
    )
    return AttackStartResponse(code=200, msg="任务已创建", data=task_info)


@router.get(
    "/status/{task_id}",
    response_model=TaskStatusResponse,
    summary="获取任务状态",
    description="根据任务ID获取攻击任务的当前状态和进度",
)
async def get_task_status(
    task_id: str,
    current_user: Dict = Depends(get_current_user)
):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="任务不存在")
    task = tasks_db[task_id]
    user_id = current_user.get("userId")
    is_admin = "admin" in current_user.get("roles", [])
    if not is_admin and task.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="无权访问此任务")
    create_time = task["create_time"]
    if isinstance(create_time, str):
        create_time = datetime.fromisoformat(create_time)
    start_time = task.get("start_time")
    if start_time and isinstance(start_time, str):
        start_time = datetime.fromisoformat(start_time)
    end_time = task.get("end_time")
    if end_time and isinstance(end_time, str):
        end_time = datetime.fromisoformat(end_time)
    task_info = TaskInfo(
        task_id=task["task_id"],
        model_id=task["model_id"],
        status=TaskStatus(task["status"]),
        progress=task["progress"],
        current_attack=task.get("current_attack"),
        create_time=create_time,
        start_time=start_time,
        end_time=end_time,
        error_msg=task.get("error_msg"),
    )
    return TaskStatusResponse(code=200, msg="success", data=task_info)


@router.get(
    "/result/{task_id}",
    response_model=AttackResultResponse,
    summary="获取攻击结果",
    description="获取已完成任务的详细攻击结果和评估指标",
)
async def get_attack_result(
    task_id: str,
    current_user: Dict = Depends(get_current_user)
):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="任务不存在")
    task = tasks_db[task_id]
    user_id = current_user.get("userId")
    is_admin = "admin" in current_user.get("roles", [])
    if not is_admin and task.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="无权访问此任务")
    if task["status"] == TaskStatus.PENDING.value:
        raise HTTPException(status_code=400, detail="任务尚未开始")
    if task["status"] == TaskStatus.RUNNING.value:
        raise HTTPException(status_code=400, detail="任务正在执行中")
    if task["status"] == TaskStatus.FAILED.value:
        raise HTTPException(status_code=500, detail=f"任务执行失败: {task.get('error_msg')}")
    create_time = task["create_time"]
    start_time = task.get("start_time")
    end_time = task.get("end_time")
    return AttackResultResponse(
        code=200,
        msg="success",
        data={
            "task_id": task_id,
            "model_id": task["model_id"],
            "status": task["status"],
            "metrics": task["results"]["metrics"] if task.get("results") else [],
            "summary": task["results"]["summary"] if task.get("results") else {},
            "create_time": create_time,
            "start_time": start_time,
            "end_time": end_time,
        },
    )


@router.get(
    "/tasks",
    response_model=TaskListResponse,
    summary="获取任务列表",
    description="获取当前用户的攻击任务列表，支持分页和状态筛选",
)
async def list_tasks(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=10, ge=1, le=100, description="每页数量"),
    status: Optional[TaskStatus] = Query(default=None, description="任务状态筛选"),
    current_user: Dict = Depends(get_current_user)
):
    user_id = current_user.get("userId")
    is_admin = "admin" in current_user.get("roles", [])
    task_list = []
    for task in tasks_db.values():
        if status is None or task["status"] == status.value:
            if not is_admin and task.get("user_id") != user_id:
                continue
            create_time = task["create_time"]
            if isinstance(create_time, str):
                create_time = datetime.fromisoformat(create_time)
            start_time = task.get("start_time")
            if start_time and isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time)
            end_time = task.get("end_time")
            if end_time and isinstance(end_time, str):
                end_time = datetime.fromisoformat(end_time)
            task_list.append(
                TaskInfo(
                    task_id=task["task_id"],
                    model_id=task["model_id"],
                    status=TaskStatus(task["status"]),
                    progress=task["progress"],
                    current_attack=task.get("current_attack"),
                    create_time=create_time,
                    start_time=start_time,
                    end_time=end_time,
                    error_msg=task.get("error_msg"),
                )
            )
    task_list.sort(key=lambda x: x.create_time, reverse=True)
    total = len(task_list)
    start = (page - 1) * page_size
    end = start + page_size
    return TaskListResponse(code=200, msg="success", data=task_list[start:end], total=total)


@router.delete(
    "/task/{task_id}",
    response_model=BaseResponse,
    summary="删除任务",
    description="删除指定的攻击任务记录",
)
async def delete_task(
    task_id: str,
    current_user: Dict = Depends(get_current_user)
):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="任务不存在")
    task = tasks_db[task_id]
    user_id = current_user.get("userId")
    is_admin = "admin" in current_user.get("roles", [])
    if not is_admin and task.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="无权删除此任务")
    if task["status"] in (TaskStatus.PENDING.value, TaskStatus.RUNNING.value):
        raise HTTPException(status_code=400, detail="无法删除待执行或运行中的任务")
    del tasks_db[task_id]
    save_tasks_db()
    return BaseResponse(code=200, msg="删除成功", data={"task_id": task_id})


@router.get("/supported", summary="获取支持的攻击类型")
async def get_supported_attacks():
    return BaseResponse(data=[
        {"type": "fgsm", "name": "FGSM", "description": "快速梯度符号法"},
        {"type": "pgd", "name": "PGD", "description": "投影梯度下降"},
        {"type": "bim", "name": "BIM", "description": "基本迭代法"},
        {"type": "cw", "name": "C&W", "description": "Carlini & Wagner攻击"},
        {"type": "deepfool", "name": "DeepFool", "description": "最小扰动攻击"},
    ])


def run_attack_task(*args, **kwargs):
    # A synchronous background job runs in Starlette's thread pool, not the API event loop.
    with EVALUATION_LOCK:
        devices = list(range(torch.cuda.device_count())) if torch.cuda.is_available() else []
        with torch.random.fork_rng(devices=devices):
            seed = kwargs.get('seed', args[8] if len(args) > 8 else 42)
            torch.manual_seed(seed)
            return _run_attack_task(*args, **kwargs)
