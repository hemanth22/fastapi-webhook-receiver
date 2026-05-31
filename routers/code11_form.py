from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from datetime import date
from shared import call_insert_remainder
from .code12_redisupdate import get_postgres_data, update_redis
import logging
import asyncio
import jinja2

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>FastAPI Remainder Tool</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f6f9;
            display: flex;
            justify-content: center;
            padding: 40px;
        }

        .form-container {
            background-color: #ffffff;
            padding: 30px 40px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 500px;
        }

        h2 {
            text-align: center;
            color: #333;
        }

        label {
            display: block;
            margin: 15px 0 5px;
            font-weight: bold;
        }

        input[type="date"],
        textarea {
            width: 100%;
            padding: 10px;
            border-radius: 4px;
            border: 1px solid #ccc;
            font-size: 14px;
        }

        button {
            padding: 10px 20px;
            margin-right: 10px;
            margin-top: 20px;
            font-size: 14px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }

        button[type="submit"] {
            background-color: #007bff;
            color: white;
        }

        button[type="reset"] {
            background-color: #dc3545;
            color: white;
        }

        .submitted-info {
            margin-top: 30px;
            background: #eaf3ff;
            padding: 15px;
            border-radius: 6px;
        }

        .submitted-info h3 {
            margin-top: 0;
        }
    </style>
</head>
<body>
    <div class="form-container">
        <h2>Remainder Updater</h2>
        <form method="post" action="/submit">
            <label for="date_input">Select Date:</label>
            <input type="date" id="date_input" name="date_input" required>

            <label for="message">Message:</label>
            <textarea id="message" name="message" rows="4" required></textarea>

            <button type="submit">Submit</button>
            <button type="reset">Clear</button>
        </form>

        {% if submitted %}
        <div class="submitted-info">
            <h3>Submitted Info:</h3>
            <p><strong>Date:</strong> {{ date_input }}</p>
            <p><strong>Message:</strong> {{ message }}</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@router.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    t = jinja2.Template(HTML_TEMPLATE)
    return HTMLResponse(t.render(request=request))

@router.post("/submit", response_class=HTMLResponse)
async def handle_form(
    request: Request,
    date_input: date = Form(...),
    message: str = Form(...)
):
    formatted_date = date_input.strftime("%d-%m-%Y")
    await call_insert_remainder(formatted_date, message)
    # Trigger Redis update
    try:
        logger.info("Triggering Redis update...")
        # Run sync functions in thread
        data = await asyncio.to_thread(get_postgres_data)
        if data:
            await asyncio.to_thread(update_redis, data)
            logger.info("Redis update triggered successfully.")
        else:
             if data is not None:
                 await asyncio.to_thread(update_redis, data)
                 logger.info("Redis update triggered (empty data).")
             else:
                 logger.error("Failed to fetch data from postgresql to Redis update.")

    except Exception as e:
        logger.error(f"Error triggering Redis update: {e}")
        
    t = jinja2.Template(HTML_TEMPLATE)
    return HTMLResponse(t.render(
        request=request,
        submitted=True,
        date_input=date_input,
        message=message
    ))
