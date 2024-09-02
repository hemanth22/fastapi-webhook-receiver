from fastapi import FastAPI, HTTPException
from fastapi import Request
from fastapi.responses import JSONResponse
import os
import requests

BOT_TOKEN = os.environ.get('telegram_api_key')
CHAT_ID = os.environ.get('telegram_id')
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def gitGuardianAlert(source,display_name,message):
    # Define the message format
    formatted_message = f"""
    System Alert: Incident Update
    Message from {source}:
    {message}
    Type of Secret Leak: {display_name}
    Reported by: {source}
    """
    # Define the payload
    payload_gitguardian = {
        'chat_id': CHAT_ID,
        'text': formatted_message,
        'parse_mode': 'Markdown'  # Optional: Use 'HTML' if you prefer HTML formatting
        }
    
    # Send the message
    response = requests.post(url, data=payload_gitguardian)
    # Check for successful response
    if response.status_code == 200:
        return "Message sent successfully."
    else:
        return f"Failed to send message. Status code: {response.status_code}"
        return f"Response: {response.text}"


def customMessage(source,message):
    # Define the message format
    formatted_message = f"""
    System Alert: Information
    Message from {source}:
    {message}
    Reported by: {source}
    """

def newsAlert(source, message):
    formatted_message = f"""
    System Alert: Information
    Message from {source}:
    Title: {message['title']}
    Description: {message['description']}
    Source of news: {message['source_id']}
    Published Date: {message['pubDate']}
    Reported by: {source}
    """

    # Define the payload
    payload_custom = {
        'chat_id': CHAT_ID,
        'text': formatted_message,
        'parse_mode': 'Markdown'  # Optional: Use 'HTML' if you prefer HTML formatting
        }
    
    # Send the message
    response = requests.post(url, data=payload_custom)
    # Check for successful response
    if response.status_code == 200:
        return "Message sent successfully."
    else:
        return f"Failed to send message. Status code: {response.status_code}"
        return f"Response: {response.text}"

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    content_type = request.headers.get("Content-Type")

    if content_type == "application/json":
        # Handle JSON payload
        payload = await request.json()
        print("Webhook received (JSON):", payload)
        #source = payload["source"]
        source = payload.get("source", "Unknown source")
        #message = payload["message"]
        message = payload.get("message", "No message")
        #incident_detected = payload["incident"]["detector"]["display_name"]
        incident = payload.get("incident", {})
        detector = incident.get("detector", None)
        if detector and isinstance(detector, dict):
            display_name = detector.get("display_name", "Policy Break")
        else:
            display_name = "Policy Break"
            
        global CommandCenterResponse
        #CommandCenterResponse = f"A message from Command Center, {message} reported by {source}"

        
        if display_name != "Policy Break" and source == "GitGuardian":
            CommandCenterResponse = f"A message from Command Center, {message} and type of secret leak is {display_name} reported by {source}"
            gitGuardianAlert(source,display_name,message)

        if display_name == "Policy Break" and source == "GitGuardian":
            CommandCenterResponse = f"A message from Command Center, {message} and {display_name} detected, reported by {source}"
            gitGuardianAlert(source,display_name,message)

        if source == "circleci":
            CommandCenterResponse = f"A message from Command Center, {message} reported by {source}"
            customMessage(source,message)

        if source == "github":
            CommandCenterResponse = f"A message from Command Center, {message} reported by {source}"
            customMessage(source,message)

        if source == "news":
            CommandCenterResponse = f"A message from Command Center, news reported by {source}"
            newsAlert(source, message)

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
