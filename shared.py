import os
import time
import requests
import asyncpg
from pydantic import BaseModel, Field
from typing import List, Optional
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# === Environment Variables & Constants ===
WHATSAPP_URL_TEMPLATE = os.getenv('WHATSAPP_URL', 'https://wa.me/{number}')
logger.debug("Loaded Whatsapp Template")
POSTGRES_USER = os.environ.get('postgres_user')
POSTFRES_PASSWORD = os.environ.get('postgres_password')
POSTFRES_DBNAME = os.environ.get('postgres_db')
POSTFRES_HOSTNAME = os.environ.get('postgres_host')
POSTFRES_PORT = os.environ.get('postgres_port')
logger.debug("Loaded Postgres Environment Variables")

DB_CONFIG = {
    "user": POSTGRES_USER,
    "password": POSTFRES_PASSWORD,
    "database": POSTFRES_DBNAME,
    "host": POSTFRES_HOSTNAME,
    "port": POSTFRES_PORT
}

logger.debug("Loaded Postgres Configuration")

BOT_TOKEN = os.environ.get('telegram_api_key')
logger.debug("Loaded Telegram Token")
CHAT_ID = os.environ.get('telegram_id')
logger.debug("Loaded Telegram Chat ID")
CHANNEL_CHAT_ID = '-1003097875450'
logger.debug("Loaded Telegram Channel Chat ID")
BROAODCAST_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage" # Renamed from 'url' to be more descriptive, but keeping 'url' alias if needed or just using this.
# The original code used 'url' as a global variable for sendMessage.
logger.debug("Loaded Telegram Broadcast URL")
TELEGRAM_SEND_MESSAGE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
logger.debug("Loaded Telegram Send Message URL")


# === Models ===
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

logger.debug("Class Models loaded for telegram ADS")

# === Helper Functions ===

async def call_insert_remainder(p_date: str, p_message: str):
    conn = await asyncpg.connect(**DB_CONFIG)
    try:
        await conn.execute("SELECT insert_remainder($1, $2);", p_date, p_message)
    finally:
        await conn.close()

def send_with_retries(target_url, payload, max_retries=10, delay=61):
    """
    Send a POST request with retries in case of failure.
    """
    time.sleep(1)  # Sleep for 1 seconds to avoid hitting rate limits
    for attempt in range(max_retries):
        try:
            response = requests.post(target_url, data=payload)
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

# === Store Functions ===

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
        'parse_mode': 'Markdown'
        }
    response = send_with_retries(TELEGRAM_SEND_MESSAGE_URL, payload_masstockdatastore)
    print("Final Response:", response)

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
        'parse_mode': 'Markdown'
        }
    response = send_with_retries(TELEGRAM_SEND_MESSAGE_URL, payload_stockdatastore)
    print("Final Response:", response)

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
        'parse_mode': 'Markdown'
        }
    response = requests.post(TELEGRAM_SEND_MESSAGE_URL, data=payload_gnewsstore)
    if response.status_code == 200:
        return "Message sent successfully."
    if response.status_code != 200:
        return f"Failed to send message. Status code: {response.status_code}"

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
        'parse_mode': 'Markdown'
        }
    time.sleep(0.1)
    response = requests.post(TELEGRAM_SEND_MESSAGE_URL, data=payload_newsapistore)
    if response.status_code == 200:
        return "Message sent successfully."
    else:
        return f"Failed to send message. Status code: {response.status_code}"

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
        'parse_mode': 'Markdown'
        }
    response = send_with_retries(TELEGRAM_SEND_MESSAGE_URL, payload_mveftstore)
    print("Final Response:", response)

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
        'parse_mode': 'Markdown'
        }
    response = send_with_retries(TELEGRAM_SEND_MESSAGE_URL, payload_eftstore)
    print("Final Response:", response)

# === Alert Functions ===

def gitGuardianAlert(source, display_name, message, gitguardian_url):
    formatted_message = f"""
    System Alert: Incident Update
    Message from {source}:
    {message}
    Type of Secret Leak: {display_name}
    Incident Reference: {gitguardian_url}
    Reported by: {source}
    """
    payload_gitguardian = {
        'chat_id': CHAT_ID,
        'text': formatted_message,
        'parse_mode': 'Markdown'
        }
    response = requests.post(TELEGRAM_SEND_MESSAGE_URL, data=payload_gitguardian)
    if response.status_code == 200:
        return "Message sent successfully."
    if response.status_code != 200:
        return f"Failed to send message. Status code: {response.status_code}"

def bitroidcustomMessage(source, message):
    formatted_message = f"""
    Message from {source}: {message}
    """
    payload_bitroidcustomMessage = {
        'chat_id': CHANNEL_CHAT_ID,
        'text': formatted_message,
        'parse_mode': 'Markdown'
        }
    response = requests.post(TELEGRAM_SEND_MESSAGE_URL, data=payload_bitroidcustomMessage)
    if response.status_code == 200:
        return "Message sent successfully."
    if response.status_code != 200:
        return f"Failed to send message. Status code: {response.status_code}"

def customMessage(source, message):
    formatted_message = f"""
    System Alert: Information
    Message from {source}:
    {message}
    Reported by: {source}
    """
    payload_gitguardian = {
        'chat_id': CHAT_ID,
        'text': formatted_message,
        'parse_mode': 'Markdown'
        }
    response = requests.post(TELEGRAM_SEND_MESSAGE_URL, data=payload_gitguardian)
    if response.status_code == 200:
        return "Message sent successfully."
    if response.status_code != 200:
        return f"Failed to send message. Status code: {response.status_code}"

def newsAlert(source, message):
    formatted_message = f"""
    System Alert: Information
    Message from {source}:
    Title: {message.get('title', 'No Title')}
    Description: {message.get('description', 'No Description')}
    Source of news: {message.get('source_id', 'Unknown')}
    Published Date: {message.get('pubDate', 'Unknown')}
    Reported by: {source}
    """
    payload_custom = {
        'chat_id': CHAT_ID,
        'text': formatted_message,
        'parse_mode': 'Markdown'
        }
    response = requests.post(TELEGRAM_SEND_MESSAGE_URL, data=payload_custom)
    if response.status_code == 200:
        return "Message sent successfully."
    if response.status_code != 200:
        return f"Failed to send message. Status code: {response.status_code}"

def redistotelegramDataAlert(source, data_list):
    if not data_list:
        return "No data to send."
    
    # Send initial greeting
    greeting_payload = {
        'chat_id': CHAT_ID,
        'text': "Hello Priya and Hemanth",
        'parse_mode': 'Markdown'
    }
    requests.post(TELEGRAM_SEND_MESSAGE_URL, data=greeting_payload)
    
    # Send each item separately
    response = None
    for item in data_list:
        msg = item.get("message", "No Message")
        redis_telegram_payload_custom = {
            'chat_id': CHAT_ID,
            'text': msg,
            'parse_mode': 'Markdown'
        }
        response = send_with_retries(TELEGRAM_SEND_MESSAGE_URL, redis_telegram_payload_custom)
        
    if isinstance(response, dict):
        if "error" not in response:
            return "Messages sent successfully."
        else:
            error_msg = response.get("error", "Unknown error")
            print(f"Debug [redistotelegramDataAlert]: Failed sending messages. Last response: {response}")
            return f"Finished sending messages. Last error: {error_msg}"
    elif response is None:
        return "No messages were processed."
    else:
        # Fallback if somehow it's not a dict
        print(f"Debug [redistotelegramDataAlert]: Unexpected response type {type(response)}: {response}")
        return f"Finished sending messages. Unexpected response format."

