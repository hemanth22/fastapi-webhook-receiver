from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from datetime import date
from shared import call_insert_remainder
from .code12_redisupdate import get_postgres_data, update_redis
import logging
import asyncio

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse(request=request, name="form.html")

@router.post("/submit", response_class=HTMLResponse)
async def handle_form(
    request: Request,
    date_input: date = Form(...),
    message: str = Form(...)
):
    formatted_date = date_input.strftime("%d-%m-%Y")
    await call_insert_remainder(formatted_date, message)
    # Trigger Redis update (asynchronous to not block response too much, but we wait for it here to ensure consistency)
    try:
        logger.info("Triggering Redis update...")
        # Run sync functions in thread
        data = await asyncio.to_thread(get_postgres_data)
        if data:
            await asyncio.to_thread(update_redis, data)
            logger.info("Redis update triggered successfully.")
        else:
             # If no data, we might still want to update redis to clear it or it might be an error. 
             # redis_update.get_postgres_data returns [] if no messages, so we should update with empty list to clear redis if that's the logic.
             # but get_postgres_data returns None on error.
             if data is not None:
                 await asyncio.to_thread(update_redis, data)
                 logger.info("Redis update triggered (empty data).")
             else:
                 logger.error("Failed to fetch data from postgresql to Redis update.")

    except Exception as e:
        logger.error(f"Error triggering Redis update: {e}")
        
    return templates.TemplateResponse(request=request, name="form.html", context={
        "submitted": True,
        "date_input": date_input,
        "message": message
    })
