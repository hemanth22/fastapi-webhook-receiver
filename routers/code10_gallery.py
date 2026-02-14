from fastapi import APIRouter
from shared import AdRequestMultiImg, send_media_group, send_dual_button

router = APIRouter()

@router.post("/send-multimgad-galary")
async def send_gallery(data: AdRequestMultiImg):
    image_urls = [data.ImageURL1, data.ImageURL2, data.ImageURL3]
    gallery_response = send_media_group(data.telegram_channel_id, data.caption, image_urls)

    whatsapp_url = f"https://wa.me/{data.WhatsAppNumber}?text=I'm%20interested%20in%20ordering!"
    button_response = send_dual_button(data.telegram_channel_id, whatsapp_url, str(data.ORDER_URL))

    return {
        "gallery_status": gallery_response.status_code,
        "gallery_detail": gallery_response.text,
        "button_status": button_response.status_code,
        "button_detail": button_response.text
    }
