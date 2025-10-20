from fastapi import FastAPI, Request, Form, HTTPException
from pydantic import BaseModel, Field
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from datetime import date
import asyncpg
import os
import requests
import time

# === Template for WhatsApp URL ===
WHATSAPP_URL_TEMPLATE = os.getenv('WHATSAPP_URL', 'https://wa.me/{number}')

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

#global CommandCenterResponse

async def call_insert_remainder(p_date: str, p_message: str):
    conn = await asyncpg.connect(**DB_CONFIG)
    try:
        await conn.execute("SELECT insert_remainder($1, $2);", p_date, p_message)
    finally:
        await conn.close()


BOT_TOKEN = os.environ.get('telegram_api_key')
CHAT_ID = os.environ.get('telegram_id')
CHANNEL_CHAT_ID = '-1003097875450'
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def send_with_retries(url, payload, max_retries=10, delay=61):
    """
    Send a POST request with retries in case of failure.
    Parameters:
    - url: The URL to send the POST request to.
    - payload: The data to send in the POST request.
    - max_retries: Maximum number of retry attempts.
    - delay: Delay in seconds between retry attempts.
    """
    time.sleep(0.1)  # Sleep for 0.1 seconds to avoid hitting rate limits
    for attempt in range(max_retries):
        try:
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                print("✅ Request successful.")
                return response.json()  # Return the successful response
            if response.status_code == 429:
                print("⚠️ Rate limit exceeded. Waiting for 61 seconds before retrying...")
                continue  # Retry the request after waiting
            if response.status_code != 200 and response.status_code != 429:
                print(f"⚠️ Failed to send message. Status code: {response.status_code}. Response: {response.text}")
                return {"error": f"Failed to send message. Status code: {response.status_code}"}
        except requests.RequestException as e:
            print(f"❌ Error sending request: {e}")
        time.sleep(delay)  # Wait before the next retry
    return {"error": f"Failed to send message after {max_retries} attempts."}

# === Send MultiMedia Group ===
def send_media_group(chat_id: str, caption: str, image_urls: list):
    media_group = []
    for i, url in enumerate(image_urls):
        media = {
            'type': 'photo',
            'media': url
        }
        if i == 0:
            media['caption'] = caption
            media['parse_mode'] = 'HTML'
        media_group.append(media)

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMediaGroup"
    payload = {
        'chat_id': chat_id,
        'media': media_group
    }
    return requests.post(url, json=payload)

# === Send WhatsApp + Order Button ===
def send_dual_button(chat_id: str, whatsapp_url: str, order_url: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': "🛒 Ready to order?",
        'reply_markup': {
            'inline_keyboard': [[
                {'text': '📞 Order on WhatsApp', 'url': whatsapp_url},
                {'text': '🛒 Order Now', 'url': order_url}
            ]]
        }
    }
    return requests.post(url, json=payload)

def masstockdatastore(data):
    formatted_message = (
    f"Source: {data['source']}\n"
    f"Stock Symbol: {data['symbol']}\n"
    f"Company Name: {data['companyName']}\n"
    f"Volume: {data['volume']}\n"
    f"Last Traded Price: {data['lastPrice']}\n"
    f"Total Traded Volume: {data['totalTradedVolume']}\n"
    f"Percentage: {data['pChange']}"
    )
    payload_masstockdatastore = {
        'chat_id': CHANNEL_CHAT_ID,
        'text': formatted_message,
        'parse_mode': 'Markdown'  # Optional: Use 'HTML' if you prefer HTML formatting
        }
    response = send_with_retries(url, payload_masstockdatastore)
    print("Final Response:", response)
    # Send the message
    #time.sleep(0.1) # Sleep for 0.1 seconds to avoid hitting rate limits
    #response = requests.post(url, data=payload_masstockdatastore)
    #print("Debug Response:", response.json())
    # Check for successful response
    #if response.status_code == 200:
    #    return "Message sent successfully."
    #if response.status_code == 429:
    #    print("Rate limit exceeded. Waiting for 60 seconds before retrying...")
    #    time.sleep(60)  # Wait for 60 seconds before retrying
    #    response = requests.post(url, data=payload_masstockdatastore)
    #    if response.status_code == 200:
    #        return "Message sent successfully after retry."
    #    else:
    #        return f"Failed to send message after retry. Status code: {response.status_code}"
    #else:
    #    return f"Failed to send message. Status code: {response.status_code}"
    #    return f"Response: {response.text}"

def stockdatastore(data):
    formatted_message = (
    f"Source: {data['source']}\n"
    f"Stock Symbol: {data['symbol']}\n"
    f"Company Name: {data['companyName']}\n"
    f"Volume: {data['volume']}\n"
    f"Last Traded Price: {data['ltp']}\n"
    f"Percentage: {data['pChange']}"
    )
    payload_stockdatastore = {
        'chat_id': CHANNEL_CHAT_ID,
        'text': formatted_message,
        'parse_mode': 'Markdown'  # Optional: Use 'HTML' if you prefer HTML formatting
        }
    response = send_with_retries(url, payload_stockdatastore)
    print("Final Response:", response)
    # Send the message
    #time.sleep(0.1) # Sleep for 0.1 seconds to avoid hitting rate limits
    #response = requests.post(url, data=payload_stockdatastore)
    #print("Debug Response:", response.json())
    # Check for successful response
    #if response.status_code == 200:
    #    return "Message sent successfully."
    #if response.status_code == 429:
    #    print("Rate limit exceeded. Waiting for 60 seconds before retrying...")
    #    time.sleep(60)  # Wait for 60 seconds before retrying
    #    response = requests.post(url, data=payload_stockdatastore)
    #    if response.status_code == 200:
    #        return "Message sent successfully after retry."
    #    else:
    #        return f"Failed to send message after retry. Status code: {response.status_code}"
    #else:
    #    return f"Failed to send message. Status code: {response.status_code}"
    #    return f"Response: {response.text}"

def gnewsstore(data):
    formatted_message = (
    f"Source: {data['source']}\n"
    f"Title: {data['title']}\n"
    f"Description: {data['description']}\n"
    f"Url: {data['url']}\n"
    f"Publish: {data['publishedTime']}\n"
    f"SourceName: {data['sourcename']}"
    )
    payload_gnewsstore = {
        'chat_id': CHANNEL_CHAT_ID,
        'text': formatted_message,
        'parse_mode': 'Markdown'  # Optional: Use 'HTML' if you prefer HTML formatting
        }

    # Send the message
    response = requests.post(url, data=payload_gnewsstore)
    # Check for successful response
    if response.status_code == 200:
        return "Message sent successfully."
    else:
        return f"Failed to send message. Status code: {response.status_code}"
        return f"Response: {response.text}"


def newsapistore(data):
    formatted_message = (
    f"Source: {data['source']}\n"
    f"Title: {data['title']}\n"
    f"Description: {data['description']}\n"
    f"Url: {data['url']}\n"
    f"Publish: {data['publishedTime']}\n"
    f"SourceName: {data['sourcename']}\n"
    f"Author: {data['author']}"
    )
    payload_newsapistore = {
        'chat_id': CHANNEL_CHAT_ID,
        'text': formatted_message,
        'parse_mode': 'Markdown'  # Optional: Use 'HTML' if you prefer HTML formatting
        }

    # Send the message
    time.sleep(0.1) # Sleep for 0.1 seconds to avoid hitting rate limits
    response = requests.post(url, data=payload_newsapistore)
    # Check for successful response
    if response.status_code == 200:
        return "Message sent successfully."
    else:
        return f"Failed to send message. Status code: {response.status_code}"
        return f"Response: {response.text}"


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
        'chat_id': CHANNEL_CHAT_ID,
        'text': formatted_message,
        'parse_mode': 'Markdown'  # Optional: Use 'HTML' if you prefer HTML formatting
        }
    response = send_with_retries(url, payload_mveftstore)
    print("Final Response:", response)
    # Send the message
    #time.sleep(0.1) # Sleep for 0.1 seconds to avoid hitting rate limits
    #response = requests.post(url, data=payload_mveftstore)
    # Check for successful response
    #if response.status_code == 200:
    #    return "Message sent successfully."
    #if response.status_code == 429:
    #    print("Rate limit exceeded. Waiting for 60 seconds before retrying...")
    #    time.sleep(60)  # Wait for 60 seconds before retrying
    #    response = requests.post(url, data=payload_mveftstore)
    #    if response.status_code == 200:
    #        return "Message sent successfully after retry."
    #    else:
    #        return f"Failed to send message after retry. Status code: {response.status_code}"
    #else:
    #    return f"Failed to send message. Status code: {response.status_code}"
    #    return f"Response: {response.text}"

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
        'chat_id': CHANNEL_CHAT_ID,
        'text': formatted_message,
        'parse_mode': 'Markdown'  # Optional: Use 'HTML' if you prefer HTML formatting
        }
    response = send_with_retries(url, payload_eftstore)
    print("Final Response:", response)
    # Send the message
    #time.sleep(0.1) # Sleep for 0.1 seconds to avoid hitting rate limits
    #response = requests.post(url, data=payload_eftstore)
    # Check for successful response
    #if response.status_code == 200:
    #    return "Message sent successfully."
    #if response.status_code == 429:
    #    print("Rate limit exceeded. Waiting for 60 seconds before retrying...")
    #    time.sleep(60)  # Wait for 60 seconds before retrying
    #    response = requests.post(url, data=payload_eftstore)
    #    if response.status_code == 200:
    #        return "Message sent successfully after retry."
    #    else:
    #        return f"Failed to send message after retry. Status code: {response.status_code}"
    #else:
    #    return f"Failed to send message. Status code: {response.status_code}"
    #    return f"Response: {response.text}"



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

def bitroidcustomMessage(source,message):
    # Define the message format
    formatted_message = f"""
    Message from {source}: {message}
    """
    # Define the payload
    payload_bitroidcustomMessage = {
        'chat_id': CHANNEL_CHAT_ID,
        'text': formatted_message,
        'parse_mode': 'Markdown'  # Optional: Use 'HTML' if you prefer HTML formatting
        }

    # Send the message
    response = requests.post(url, data=payload_bitroidcustomMessage)
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

# === Request model ===
#class AdRequest(BaseModel):
#    caption: str
#    ImageURL: str
#    WhatsAppNumber: str
#    telegram_channel_id: str

class AdRequest(BaseModel):
    caption: str = Field(..., example="✨You + Me + Poori 🥔 = the perfect love story\n📞 Call us: +91 9247634520\nLimited-time offer: Buy 2, Get 1 Free!")
    ImageURL: str = Field(..., example="https://www.vidhyashomecooking.com/wp-content/uploads/2021/04/PooriRecipe.jpg")
    WhatsAppNumber: str = Field(..., example="919247634520")
    telegram_channel_id: str = Field(..., example="-1003097875450")

class AdRequestMultiCall(BaseModel):
    caption: str = Field(..., example="✨Hand-painted heritage for the modern muse\n📞 Call us: +91 9247634520\nLimited-time offer: Buy 1, Get 1 Free!")
    ImageURL: str = Field(..., example="https://i.postimg.cc/sXTCSLmy/kalamkaari-image.jpg")
    WhatsAppNumber: str = Field(..., example="919492377210")
    telegram_channel_id: str = Field(..., example="-1003097875450")
    ORDER_URL: str = Field(..., example="https://www.instagram.com/amaravathikalamkari/")

class AdRequestMultiImg(BaseModel):
    caption: str = Field(..., example="🥟 Samosa Fiesta!\nGolden, crispy, and bursting with flavor.\n📞 Call us: +91 9247634520 or tap below to order on WhatsApp!")
    ImageURL1: str = Field(..., example="https://media.karousell.com/media/photos/products/2023/7/4/samosa_ayam__daging_frozen_1688451858_94e31fb5.jpg")
    ImageURL2: str = Field(..., example="https://free-images.com/sm/c66d/punjabi_samosa.jpg")
    ImageURL3: str = Field(..., example="https://pixahive.com/wp-content/uploads/2020/12/Samosa-249334-pixahive.jpg")
    WhatsAppNumber: str = Field(..., example="919247634520")
    telegram_channel_id: str = Field(..., example="-1003097875450")
    ORDER_URL: str = Field(..., example="https://yourstore.com/order-samosa")

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

        #global CommandCenterResponse
        #CommandCenterResponse = f"A message from Command Center, {message} reported by {source}"

        if display_name != "Policy Break" and source == "GitGuardian":
            gitGuardianAlert(source,display_name,message,gitguardian_url)

        if display_name == "Policy Break" and source == "GitGuardian":
            gitGuardianAlert(source,display_name,message,gitguardian_url)

        if source == "circleci":
            customMessage(source,message)

        if source == "bitroidnews":
            bitroidcustomMessage(source,message)

        if source == "github":
            customMessage(source,message)

        if source == "news":
            newsAlert(source, message)

        # Handle the JSON payload as needed
    elif content_type == "application/x-www-form-urlencoded":
        # Handle form data
        form_data = await request.form()
        print("Webhook received (Form data):", form_data)
        # Handle the form data as needed
    else:
        raise HTTPException(status_code=400, detail="Unsupported content type")

    return {"status": "Webhook received successfully"}

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
        print("Received Invalid Data", payload)

@app.post("/newsapiwebhook")
async def newsapiwebhook(request: Request):
    content_type = request.headers.get("Content-Type")
    if content_type == "application/json":
        payload = await request.json()
        print("Webhook received (JSON):", payload)
        newsapistore(payload)
    if content_type != "application/json":
        print("Received Invalid Data", payload)

@app.post("/gnewswebhook")
async def gnewswebhook(request: Request):
    content_type = request.headers.get("Content-Type")
    if content_type == "application/json":
        payload = await request.json()
        print("Webhook received (JSON):", payload)
        gnewsstore(payload)
    if content_type != "application/json":
        print("Received Invalid Data", payload)

@app.post("/maswebhook")
async def maswebhook(request: Request):
    content_type = request.headers.get("Content-Type")
    if content_type == "application/json":
        payload = await request.json()
        print("Webhook received (JSON):", payload)
        stockdatastore(payload)
    if content_type != "application/json":
        print("Received Invalid Data", payload)

@app.post("/webhookmas")
async def maswebhook(request: Request):
    content_type = request.headers.get("Content-Type")
    if content_type == "application/json":
        payload = await request.json()
        print("Webhook received (JSON):", payload)
        masstockdatastore(payload)
    if content_type != "application/json":
        print("Received Invalid Data", payload)

@app.post("/telegram-send-ad-image/")
def telegram_send_ad_image(request: AdRequest):
    whatsapp_url = WHATSAPP_URL_TEMPLATE.format(number=request.WhatsAppNumber)
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

    payload = {
        'chat_id': request.telegram_channel_id,
        'photo': request.ImageURL,
        'caption': request.caption,
        'parse_mode': 'HTML',
        'reply_markup': {
            'inline_keyboard': [[
                {'text': '📞 Call Now on WhatsApp', 'url': whatsapp_url}
            ]]
        }
    }

    response = requests.post(telegram_url, json=payload)
    if response.status_code == 200:
        return {"status": "✅ Advertisement sent successfully!"}
    else:
        raise HTTPException(status_code=response.status_code, detail=f"❌ Failed to send ad: {response.text}")

@app.post("/telegram-send-ad-image-link/")
def telegram_send_ad_image_link(request: AdRequestMultiCall):
    whatsapp_url = f"https://wa.me/{request.WhatsAppNumber}"
    telegram_api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

    payload = {
        "chat_id": request.telegram_channel_id,
        "photo": request.ImageURL,
        "caption": request.caption,
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": [[
                {"text": "📞 Call Now on WhatsApp", "url": whatsapp_url},
                {"text": "🛒 Order Now", "url": request.ORDER_URL}
            ]]
        }
    }

    response = requests.post(telegram_api_url, json=payload)
    if response.status_code == 200:
        return {"status": "✅ Advertisement sent successfully!"}
    else:
        raise HTTPException(status_code=response.status_code, detail=f"❌ Failed to send ad: {response.text}")

@app.post("/send-multimgad-galary")
async def send_gallery(data: AdRequestMultiImg):
    image_urls = [data.ImageURL1, data.ImageURL2, data.ImageURL3]
    gallery_response = send_media_group(data.telegram_channel_id, data.caption, image_urls)

    whatsapp_url = f"https://wa.me/{data.WhatsAppNumber}?text=I'm%20interested%20in%20ordering%20samosas!"
    button_response = send_dual_button(data.telegram_channel_id, whatsapp_url, str(data.ORDER_URL))

    return {
        "gallery_status": gallery_response.status_code,
        "gallery_detail": gallery_response.text,
        "button_status": button_response.status_code,
        "button_detail": button_response.text
    }