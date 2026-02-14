from fastapi import APIRouter, Request
from shared import newsapistore

router = APIRouter()

@router.post("/newsapiwebhook")
async def newsapiwebhook(request: Request):
    content_type = request.headers.get("Content-Type")
    if content_type == "application/json":
        payload = await request.json()
        print("Webhook received (JSON):", payload)
        newsapistore(payload)
    if content_type != "application/json":
        print("Received Invalid Data")
