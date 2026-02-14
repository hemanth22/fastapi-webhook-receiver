from fastapi import APIRouter, HTTPException
import requests
from shared import AdRequestMultiCall, BOT_TOKEN

router = APIRouter()

@router.post("/telegram-send-ad-image-link/")
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
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"❌ Failed to send ad: {response.text}")
