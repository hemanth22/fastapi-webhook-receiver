import logging
logger = logging.getLogger(__name__)
from fastapi import APIRouter, Request
from shared import gnewsstore

router = APIRouter()

@router.post("/gnewswebhook")
async def gnewswebhook(request: Request):
    content_type = request.headers.get("Content-Type")
    if content_type == "application/json":
        payload = await request.json()
        logger.info("Webhook received (JSON):", payload)
        gnewsstore(payload)
    if content_type != "application/json":
        logger.info("Received Invalid Data")
