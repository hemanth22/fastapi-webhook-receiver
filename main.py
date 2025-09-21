from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from datetime import date
import asyncpg
import os
import requests

POSTGRES_USER = os.environ.get('postgres_user')
POSTFRES_PASSWORD = os.environ.get('postgres_password')
POSTFRES_DBNAME = os.environ.get('postgres_db')
POSTFRES_HOSTNAME = os.environ.get('postgres_host')
POSTFRES_PORT = os.environ.get('postgres_port')

DB_CONFIG = {
    "user": POSTGRES_USER,
    "password": POSTFRES_PASSWORD,
    "database": POSTFRES_DBNAME,
    "host": POSTFRES_HOSTNAME,
    "port": POSTFRES_PORT
}

async def call_insert_remainder(p_date: str, p_message: str):
    conn = await asyncpg.connect(**DB_CONFIG)
    try:
        await conn.execute("SELECT insert_remainder($1, $2);", p_date, p_message)
    finally:
        await conn.close()


BOT_TOKEN = os.environ.get('telegram_api_key')
CHAT_ID = os.environ.get('telegram_id')
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


def mvetfstore(data):
    formatted_message = (
    f"Symbol: {data['symbol']}\n"
    f"Asset Name: {data['assetName']}\n"
    f"Last Price: {data['LastPrice']}\n"
    f"High Value: {data['HIGHVALUE']}\n"
    f"Low Value: {data['LOWVALUE']}\n"
    f"Traded Volume: {data['tradedVolume']}\n"
    f"Traded Value: {data['tradedValue']}\n"
    f"Close Price: {data['closePrice']}\n"
    f"Previous Close Price: {data['PreviousclosePrice']}\n"
    f"Percentage Change: {data['PercentageDiff']}\n"
    f"NAV: {data['nav']}"
    )
    payload_mveftstore = {
        'chat_id': CHAT_ID,
        'text': formatted_message,
        'parse_mode': 'Markdown'  # Optional: Use 'HTML' if you prefer HTML formatting
        }

    # Send the message
    response = requests.post(url, data=payload_mveftstore)
    # Check for successful response
    if response.status_code == 200:
        return "Message sent successfully."
    else:
        return f"Failed to send message. Status code: {response.status_code}"
        return f"Response: {response.text}"

def etfstore(data):
    formatted_message = (
    f"Symbol: {data['symbol']}\n"
    f"Asset Name: {data['assetName']}\n"
    f"Open Value: {data['OPENVALUE']}\n"
    f"High Value: {data['HIGHVALUE']}\n"
    f"Low Value: {data['LOWVALUE']}\n"
    f"Traded Volume: {data['tradedVolume']}\n"
    f"Traded Value: {data['tradedValue']}\n"
    f"Company Name: {data['company_name']}"
    )
    payload_eftstore = {
        'chat_id': CHAT_ID,
        'text': formatted_message,
        'parse_mode': 'Markdown'  # Optional: Use 'HTML' if you prefer HTML formatting
        }

    # Send the message
    response = requests.post(url, data=payload_eftstore)
    # Check for successful response
    if response.status_code == 200:
        return "Message sent successfully."
    else:
        return f"Failed to send message. Status code: {response.status_code}"
        return f"Response: {response.text}"



def gitGuardianAlert(source,display_name,message,gitguardian_url):
    # Define the message format
    formatted_message = f"""
    System Alert: Incident Update
    Message from {source}:
    {message}
    Type of Secret Leak: {display_name}
    Incident Reference: {gitguardian_url}
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
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/submit", response_class=HTMLResponse)
async def handle_form(
    request: Request,
    date_input: date = Form(...),
    message: str = Form(...)
):
    formatted_date = date_input.strftime("%d-%m-%Y")
    await call_insert_remainder(formatted_date, message)
    return templates.TemplateResponse("form.html", {
        "request": request,
        "submitted": True,
        "date_input": date_input,
        "message": message
    })


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
        gitguardian_url = incident.get("gitguardian_url", "Missing url")
        detector = incident.get("detector", None)
        if detector and isinstance(detector, dict):
            display_name = detector.get("display_name", "Policy Break")
        else:
            display_name = "Policy Break"

        global CommandCenterResponse
        #CommandCenterResponse = f"A message from Command Center, {message} reported by {source}"

        if display_name != "Policy Break" and source == "GitGuardian":
            CommandCenterResponse = f"A message from Command Center, {message} and type of secret leak is {display_name} reported by {source}"
            gitGuardianAlert(source,display_name,message,gitguardian_url)

        if display_name == "Policy Break" and source == "GitGuardian":
            CommandCenterResponse = f"A message from Command Center, {message} and {display_name} detected, reported by {source}"
            gitGuardianAlert(source,display_name,message,gitguardian_url)

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

@app.post("/etfwebhook")
async def etfwebhook(request: Request):
    content_type = request.headers.get("Content-Type")
    if content_type == "application/json":
        payload = await request.json()
        print("Webhook received (JSON):", payload)
        etfstore(payload)
    if content_type != "application/json":
        print("Received Invalid Dat", payload)

@app.post("/mvetfwebhook")
async def mvetfwebhook(request: Request):
    content_type = request.headers.get("Content-Type")
    if content_type == "application/json":
        payload = await request.json()
        print("Webhook received (JSON):", payload)
        mvetfstore(payload)
    if content_type != "application/json":
        print("Received Invalid Dat", payload)
