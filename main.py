from fastapi import FastAPI, HTTPException # type: ignore
from fastapi import Request # type: ignore
import json

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    content_type = request.headers.get("Content-Type")

    if content_type == "application/json":
        # Handle JSON payload
        payload = await request.json()
        print("Webhook received (JSON):", payload)
        global last_item
        last_item = payload
        # Handle the JSON payload as needed
    elif content_type == "application/x-www-form-urlencoded":
        # Handle form data
        form_data = await request.form()
        print("Webhook received (Form data):", form_data)
        # Handle the form data as needed
    else:
        raise HTTPException(status_code=400, detail="Unsupported content type")

    return {"status": "Webhook received successfully"}

@app.post("/incomng")
async def get_last_incoming():
    # Parse the JSON message
    data_incoming = json.loads(last_item)
    source = data_incoming.get('source')
    message = data_incoming.get('message', 'there is an alert')
    if source:
        outmessage = f"Command Center, {message}, reported by {source}"
    else:
        outmessage = f"Command Center, {message}"

    if last_item is None:
        return {"message": "No items have been posted yet."}
    return {
        "incoming_message": "outmessage"
    }