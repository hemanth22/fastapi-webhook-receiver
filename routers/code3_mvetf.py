import logging
logger = logging.getLogger(__name__)
from fastapi import APIRouter, Request
from shared import mvetfstore

router = APIRouter()

@router.post("/mvetfwebhook")
async def mvetfwebhook(request: Request):
    content_type = request.headers.get("Content-Type")
    if content_type == "application/json":
        payload = await request.json()
        logger.info("Webhook received (JSON):", payload)
        mvetfstore(payload)
    if content_type != "application/json":
        logger.info("Received Invalid Data")
