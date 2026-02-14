from fastapi import APIRouter, HTTPException
import requests
from shared import AdRequest, WHATSAPP_URL_TEMPLATE, BOT_TOKEN

router = APIRouter()

@router.post("/telegram-send-ad-image/")
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
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"❌ Failed to send ad: {response.text}")
