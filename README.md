# fastapi-webhook-receiver

FastAPI service that accepts reminders, stores them in a database, and uses a Redis sorted-set queue to fire IFTTT webhooks at the scheduled time. Redis handles the hot queue so the database is not polled every minute.

## Prerequisites
- Python 3.10+
- Redis running locally (or provide `REDIS_URL`)
- PostgreSQL if you want production storage (defaults to SQLite for local dev)

## Configuration
Environment variables (defaults shown):
- `DATABASE_URL`: `sqlite+aiosqlite:///./reminders.db`
- `REDIS_URL`: `redis://localhost:6379/0`
- `REDIS_QUEUE_KEY`: `ifttt_reminders_queue`
- `DISPATCH_INTERVAL`: `60` (seconds between queue checks)
- `IFTTT_EVENT`: IFTTT event name (required to actually send)
- `IFTTT_KEY`: IFTTT webhook key (required to actually send)

## Install & Run
```bash
python -m venv .venv && .venv/Scripts/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## API
- `POST /reminders` – Schedule a reminder.
	```json
	{
		"when": "2026-01-07T10:00:00Z",
		"message1": "Value 1",
		"message2": "Value 2",
		"message3": "Value 3"
	}
	```
	Response: `{ "status": "scheduled", "execution_time": "...", "id": 1 }`

- `GET /health` – Basic health check.

## How it works
1) The reminder is written to the database (system of record).
2) The reminder payload is added to a Redis ZSET with the execution timestamp as the score.
3) A background scheduler wakes every `DISPATCH_INTERVAL` seconds, reads due entries from Redis only, dispatches to IFTTT, and removes them from the queue.

[![Docker Repository on Quay](https://quay.io/repository/hemanth22/fastapi-webhook-receiver/status "Docker Repository on Quay")](https://quay.io/repository/hemanth22/fastapi-webhook-receiver)
