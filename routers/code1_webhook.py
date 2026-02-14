from fastapi import APIRouter, Request, HTTPException
from shared import gitGuardianAlert, customMessage, bitroidcustomMessage, newsAlert

router = APIRouter()

@router.post("/webhook")
async def webhook(request: Request):
    content_type = request.headers.get("Content-Type")

    if content_type == "application/json":
        # Handle JSON payload
        payload = await request.json()
        print("Webhook received (JSON):", payload)
        
        source = payload.get("source", "Unknown source")
        message = payload.get("message", "No message")
        
        incident = payload.get("incident", {})
        gitguardian_url = incident.get("gitguardian_url", "Missing url")
        detector = incident.get("detector", None)
        
        if detector and isinstance(detector, dict):
            display_name = detector.get("display_name", "Policy Break")
        else:
            display_name = "Policy Break"

        if display_name != "Policy Break" and source == "GitGuardian":
            gitGuardianAlert(source, display_name, message, gitguardian_url)

        if display_name == "Policy Break" and source == "GitGuardian":
            gitGuardianAlert(source, display_name, message, gitguardian_url)

        if source == "circleci":
            customMessage(source, message)

        if source == "bitroidnews":
            bitroidcustomMessage(source, message)

        if source == "github":
            customMessage(source, message)

        if source == "news":
            newsAlert(source, message)

    elif content_type == "application/x-www-form-urlencoded":
        # Handle form data
        form_data = await request.form()
        print("Webhook received (Form data):", form_data)
        # Handle the form data as needed
    else:
        raise HTTPException(status_code=400, detail="Unsupported content type")

    return {"status": "Webhook received successfully"}
