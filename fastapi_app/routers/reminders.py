from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime
from typing import Dict
import asyncio

router = APIRouter()

class ReminderCreate(BaseModel):
    message: str
    delay_seconds: int

class Reminder(BaseModel):
    id: int
    message: str
    delay_seconds: int
    created_at: datetime

async def process_reminder(reminder_id: int, message: str, delay: int):
    await asyncio.sleep(delay)
    with open("reminders.log", "a", encoding="utf-8") as f:
        f.write(f"[REMINDER] id={reminder_id} delay={delay}s: {message}\n")

reminders: Dict[int, Reminder] = {}
next_reminder_id = 1

@router.post("/")
def create_reminder(payload: ReminderCreate, background_tasks: BackgroundTasks):
    global next_reminder_id

    reminder = Reminder(
        id=next_reminder_id,
        message= payload.message,
        delay_seconds= payload.delay_seconds,
        created_at=datetime.utcnow(),
    )

    reminders[next_reminder_id] = reminder

    background_tasks.add_task(
        process_reminder,
        reminder_id=next_reminder_id,
        message=reminder.message,
        delay=reminder.delay_seconds,
    )

    next_reminder_id += 1

    return reminder
