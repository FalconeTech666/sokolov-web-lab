from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import Optional

router = APIRouter()


class TaskStatus(str, Enum):
    """
    Статус задачи.

    - todo: задача создана, но ещё не начата
    - in_progress: задача в процессе выполнения
    - done: задача завершена
    """
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class TaskCreate(BaseModel):
    """
    Модель для создания новой задачи.

    Используется в теле запроса POST /tasks:
    - title: обязательный заголовок задачи
    - description: необязательное описание
    """
    title: str
    description: Optional[str] = None


class TaskUpdate(BaseModel):
    """
    Модель для частичного обновления задачи.

    Используется в теле запроса PATCH /tasks/{task_id}.
    Все поля опциональны — можно передать только то,
    что нужно изменить:
    - title: новый заголовок
    - description: новое описание
    - status: новый статус задачи (todo / in_progress / done)
    """
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None


class Task(BaseModel):
    """
    Полная модель задачи, которая хранится на сервере
    и возвращается в ответах API.

    Поля:
    - id: уникальный идентификатор задачи
    - title: заголовок
    - description: описание (может отсутствовать)
    - status: текущий статус
    - created_at: дата и время создания (UTC)
    """
    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.todo
    created_at: datetime


tasks: dict[int, Task] = {}
next_task_id = 1


@router.post("/")
def create_task(payload: TaskCreate):
    """
    Создать новую задачу.

    Тело запроса (JSON):
    - title: строка, обязательное поле
    - description: строка, опционально

    Возвращает созданную задачу с присвоенным id,
    статусом todo и временем создания.
    """
    global next_task_id

    task = Task(
        id=next_task_id,
        title=payload.title,
        description=payload.description,
        status=TaskStatus.todo,
        created_at=datetime.utcnow(),
    )

    tasks[next_task_id] = task
    next_task_id += 1

    return task


@router.get("/")
def list_tasks():
    """
    Получить список всех задач.

    Возвращает массив объектов Task в текущем состоянии.
    """
    return list(tasks.values())


@router.get("/{task_id}")
def get_task(task_id: int):
    """
    Получить одну задачу по её ID.

    Параметры пути:
    - task_id: целое число, идентификатор задачи

    Ошибки:
    - 404, если задачи с таким ID не существует.
    """
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}")
def update_task(task_id: int, payload: TaskUpdate):
    """
    Частично обновить задачу по ID.

    Параметры пути:
    - task_id: идентификатор задачи

    Тело запроса (JSON, все поля опциональны):
    - title: новый заголовок
    - description: новое описание
    - status: новый статус (todo / in_progress / done)

    Ошибки:
    - 404, если задача не найдена.

    Возвращает обновлённую задачу.
    """
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if payload.title is not None:
        task.title = payload.title
    if payload.description is not None:
        task.description = payload.description
    if payload.status is not None:
        task.status = payload.status

    tasks[task_id] = task
    return task


@router.delete("/{task_id}")
def delete_task(task_id: int):
    """
    Удалить задачу по ID.

    Параметры пути:
    - task_id: идентификатор задачи

    Ошибки:
    - 404, если задача не найдена.

    Возвращает служебное сообщение с указанием удалённого ID.
    """
    task = tasks.pop(task_id, None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"detail": f"Task {task_id} deleted"}


@router.get("/stats")
def get_task_stats():
    """
    Получить статистику по задачам.

    Возвращает JSON с полями:
    - total: общее количество задач
    - todo: сколько задач в статусе todo
    - in_progress: сколько задач в статусе in_progress
    - done: сколько задач в статусе done
    """
    all_tasks = list(tasks.values())
    task_quantity = len(all_tasks)

    todo_count = 0
    in_progress_count = 0
    done_count = 0

    for task in all_tasks:
        if task.status == TaskStatus.todo:
            todo_count += 1
        elif task.status == TaskStatus.in_progress:
            in_progress_count += 1
        elif task.status == TaskStatus.done:
            done_count += 1

    return {
        "total": task_quantity,
        "todo": todo_count,
        "in_progress": in_progress_count,
        "done": done_count,
    }