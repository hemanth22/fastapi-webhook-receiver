import logging
logger = logging.getLogger(__name__)
from fastapi import APIRouter, Request
from shared import stockdatastore

router = APIRouter()

@router.post("/maswebhook")
async def maswebhook(request: Request):
    content_type = request.headers.get("Content-Type")
    if content_type == "application/json":
        payload = await request.json()
        logger.info("Webhook received (JSON):", payload)
        stockdatastore(payload)
    if content_type != "application/json":
        logger.info("Received Invalid Data")
