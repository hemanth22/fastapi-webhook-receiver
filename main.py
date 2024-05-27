from fastapi import FastAPI, Request
from pydantic import BaseModel
import json

app = FastAPI()

class WebhookPayload(BaseModel):
    # Define the expected structure of your webhook payload here.
    # Example fields:
    event: str
    data: dict

@app.post("/webhook")
async def handle_webhook(payload: WebhookPayload):
    # Log the payload or perform any processing you need
    print("Received webhook event:", payload.event)
    print("Payload data:", json.dumps(payload.data, indent=2))

    # Return a response
    return {"message": "Webhook received successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
