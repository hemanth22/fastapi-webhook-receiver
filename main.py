from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import datetime

app = FastAPI()

# Store the latest webhook data
latest_webhook_data = {
    "timestamp": None,
    "data": None
}

@app.post("/webhook")
async def receive_webhook(request: Request):
    global latest_webhook_data
    payload = await request.json()
    latest_webhook_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "data": payload
    }
    return {"message": "Webhook received successfully"}

@app.get("/latest-notification")
async def get_latest_notification():
    return JSONResponse(latest_webhook_data)
