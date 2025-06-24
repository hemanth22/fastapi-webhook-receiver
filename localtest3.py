import requests
import json
import os
import logging
import uuid
import socket

# Custom JSON Formatter for logging
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            
            'timestamp': self.formatTime(record),
            'message': record.getMessage(),
            'hostname': socket.gethostname(),
            'ip_address': socket.gethostbyname(socket.gethostname()),
            'traceid': str(uuid.uuid4()),
            'level': record.levelname
        }
        return json.dumps(log_record)

# Configure logging with JSONFormatter
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
json_handler = logging.StreamHandler()
json_handler.setFormatter(JSONFormatter())
logger.addHandler(json_handler)

FASTAPI_WEBHOOK = os.environ.get('FASTAPI_WEBHOOK')

payload = json.dumps({
    'source': 'github',
    'message': 'Reminder to book a cab'
})
headers = {
    'Content-Type': 'application/json',
}

logger.debug('Payload prepared: %s', payload)

try:
    logger.info('Sending POST request to webhook')
    response = requests.post(FASTAPI_WEBHOOK, headers=headers, data=payload)
    response.raise_for_status()  # Check for HTTP errors

    # Log detailed response information
    logger.info('Response status code: %s', response.status_code)
    logger.debug('Response headers: %s', response.headers)
    logger.debug('Response content: %s', response.text)
    logger.debug('Response JSON: %s', response.json())
    logger.debug('Response URL: %s', response.url)
    logger.debug('Response elapsed time: %s', response.elapsed)
except requests.exceptions.RequestException as e:
    logger.error('Request failed: %s', e)
    if e.response is not None:
        logger.warning('Response content: %s', e.response.text)