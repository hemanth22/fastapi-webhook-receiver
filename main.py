from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import (
    code1_webhook,
    code2_etf,
    code3_mvetf,
    code4_newsapi,
    code5_gnews,
    code6_mas,
    code7_webhookmas,
    code8_telegram_ad,
    code9_telegram_link,
    code10_gallery,
    code11_form,
    code13_telegram_message
)

app = FastAPI()

# Include Routers
app.include_router(code1_webhook.router)
app.include_router(code2_etf.router)
app.include_router(code3_mvetf.router)
app.include_router(code4_newsapi.router)
app.include_router(code5_gnews.router)
app.include_router(code6_mas.router)
app.include_router(code7_webhookmas.router)
app.include_router(code8_telegram_ad.router)
app.include_router(code9_telegram_link.router)
app.include_router(code10_gallery.router)
app.include_router(code11_form.router)
app.include_router(code13_telegram_message.router)

# Optional: Mount static files if needed (not explicitly used in previous main.py but imported)
# app.mount("/static", StaticFiles(directory="static"), name="static")

print("Application started and routers included.")
