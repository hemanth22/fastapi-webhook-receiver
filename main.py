from fastapi import FastAPI, HTTPException
from fastapi import Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    content_type = request.headers.get("Content-Type")

    if content_type == "application/json":
        # Handle JSON payload
        payload = await request.json()
        print("Webhook received (JSON):", payload)
        #source = payload["source"]
        source = data.get("source", "Unknown source")
        #message = payload["message"]
        message = data.get("message", "No message")
        #incident_detected = data["incident"]["detector"]["display_name"]
        incident = data.get("incident", {})
        detector = incident.get("detector", None)
        if detector and isinstance(detector, dict):
            display_name = detector.get("display_name", "Policy Break")
        else:
            display_name = "Policy Break"
            
        global CommandCenterResponse
        #CommandCenterResponse = f"A message from Command Center, {message} reported by {source}"
        if display_name != "Policy Break":
            CommandCenterResponse = f"A message from Command Center, {message} and type of secret leak is {display_name} reported by {source}"

        if display_name == "Policy Break":
            CommandCenterResponse = f"A message from Command Center, {message} and {display_name} detected, reported by {source}"

        if source == "circleci":
            CommandCenterResponse = f"A message from Command Center, {message} reported by {source}"

        print(CommandCenterResponse)
        # Handle the JSON payload as needed
    elif content_type == "application/x-www-form-urlencoded":
        # Handle form data
        form_data = await request.form()
        print("Webhook received (Form data):", form_data)
        # Handle the form data as needed
    else:
        raise HTTPException(status_code=400, detail="Unsupported content type")

    return {"status": "Webhook received successfully"}

@app.get("/latest-notification")
async def get_latest_notification():
    return JSONResponse(CommandCenterResponse)
