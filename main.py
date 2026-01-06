import json
import logging
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

import httpx
import redis.asyncio as redis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./reminders.db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_QUEUE_KEY = os.getenv("REDIS_QUEUE_KEY", "ifttt_reminders_queue")
DISPATCH_INTERVAL = int(os.getenv("DISPATCH_INTERVAL", "60"))

IFTTT_EVENT = os.getenv("IFTTT_EVENT")
IFTTT_KEY = os.getenv("IFTTT_KEY")
IFTTT_URL_TEMPLATE = "https://maker.ifttt.com/trigger/{event}/with/key/{key}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

redis_client: Optional[redis.Redis] = None
scheduler: Optional[AsyncIOScheduler] = None


class Reminder(Base):
    __tablename__ = "ifttt_remainder"

    id = Column(Integer, primary_key=True)
    datetime_col = Column("datetime", DateTime, nullable=False)
    message1 = Column(String, nullable=False)
    message2 = Column(String, nullable=True)
    message3 = Column(String, nullable=True)


class ReminderCreate(BaseModel):
    when: datetime = Field(..., description="Execution time in ISO 8601 format")
    message1: str = Field(..., description="Primary value for the IFTTT webhook")
    message2: Optional[str] = Field(None, description="Secondary value for the IFTTT webhook")
    message3: Optional[str] = Field(None, description="Tertiary value for the IFTTT webhook")


async def trigger_ifttt(payload: dict) -> None:
    if not IFTTT_EVENT or not IFTTT_KEY:
        logger.warning("IFTTT_EVENT and IFTTT_KEY must be set to dispatch webhooks. Skipping send.")
        return

    ifttt_payload = {
        "value1": payload.get("message1"),
        "value2": payload.get("message2"),
        "value3": payload.get("message3"),
    }

    url = IFTTT_URL_TEMPLATE.format(event=IFTTT_EVENT, key=IFTTT_KEY)

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(url, json=ifttt_payload)
        response.raise_for_status()
        logger.info("Sent IFTTT webhook for id=%s status=%s", payload.get("id"), response.status_code)


async def check_cache_and_fire() -> None:
    if redis_client is None:
        logger.error("Redis client is not initialized; cannot process queue.")
        return

    now_timestamp = time.time()
    due_reminders = await redis_client.zrangebyscore(REDIS_QUEUE_KEY, min=0, max=now_timestamp)

    if not due_reminders:
        return

    logger.info("Processing %s due reminder(s) from Redis", len(due_reminders))

    for reminder_json in due_reminders:
        try:
            data = json.loads(reminder_json)
        except json.JSONDecodeError:
            logger.error("Invalid JSON found in Redis queue, removing entry.")
            await redis_client.zrem(REDIS_QUEUE_KEY, reminder_json)
            continue

        try:
            await trigger_ifttt(data)
            await redis_client.zrem(REDIS_QUEUE_KEY, reminder_json)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to dispatch reminder id=%s: %s", data.get("id"), exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client, scheduler

    redis_client = redis.from_url(REDIS_URL, decode_responses=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_cache_and_fire, "interval", seconds=DISPATCH_INTERVAL)
    scheduler.start()
    logger.info("Scheduler started; polling Redis every %s seconds", DISPATCH_INTERVAL)

    yield

    scheduler.shutdown()
    await redis_client.close()
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.post("/reminders", status_code=201)
async def add_reminder(reminder: ReminderCreate):
    if redis_client is None:
        raise HTTPException(status_code=503, detail="Redis is not ready")

    async with AsyncSessionLocal() as session:
        new_reminder = Reminder(
            datetime_col=reminder.when,
            message1=reminder.message1,
            message2=reminder.message2,
            message3=reminder.message3,
        )
        session.add(new_reminder)
        await session.commit()
        await session.refresh(new_reminder)

    reminder_data = {
        "id": new_reminder.id,
        "message1": reminder.message1,
        "message2": reminder.message2,
        "message3": reminder.message3,
    }

    score = reminder.when.timestamp()
    await redis_client.zadd(REDIS_QUEUE_KEY, {json.dumps(reminder_data): score})
    logger.info("Queued reminder id=%s for %s", new_reminder.id, reminder.when.isoformat())

    return {"status": "scheduled", "execution_time": reminder.when, "id": new_reminder.id}


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
