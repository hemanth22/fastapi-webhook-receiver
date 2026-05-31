import logging
logger = logging.getLogger(__name__)
from fastapi import APIRouter, Request
from shared import etfstore

router = APIRouter()

@router.post("/etfwebhook")
async def etfwebhook(request: Request):
    content_type = request.headers.get("Content-Type")
    if content_type == "application/json":
        payload = await request.json()
        logger.info("Webhook received (JSON):", payload)
        etfstore(payload)
    if content_type != "application/json":
        logger.info("Received Invalid Data")
