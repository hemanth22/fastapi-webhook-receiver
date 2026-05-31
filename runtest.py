import requests
import json
import logging
from nsepython import nsefetch
import os
import psycopg2
from datetime import datetime
import pytz



logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_case(url, data):
    logger.debug(f" Input received to function {url} and {data}")
    response = requests.post(url, json=data)
    logger.debug(f" Response status: {response.status_code}")
    logger.debug(f" Response from function: {response.json()}")
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
    assert response.json() == {'status': 'Webhook received successfully'}, f"Expected response {{'status': 'Webhook received successfully'}}, but got {response.json()}"

# Example usage
logger.info("Test Case 1 Started")
webhook_url = "http://127.0.0.1:8000/webhook"

with open("webhook_test1.json", "r") as f:
    logger.debug(f"verify file opened: {f}")
    webhook_test1_data = json.load(f)
    logger.debug(f"verify json loaded data: {webhook_test1_data}")

test_case(webhook_url, webhook_test1_data)
logger.info("Test Case 1 Completed")

logger.info("Test Case 2 started for gitguardian_url")

with open("webhook_gitguardian_test2.json", "r") as f:
    logger.debug(f"verify file opened: {f}")
    webhook_test2_data = json.load(f)
    logger.debug(f"verify json loaded data: {webhook_test2_data}")

test_case(webhook_url, webhook_test2_data)
logger.info("Test Case 2 completed for gitguardian_url")

logger.info("Test Case 3 started for gitguardian_url")

with open("webhook_gitguardian_test3.json", "r") as f:
    logger.debug(f"verify file opened: {f}")
    webhook_test3_data = json.load(f)
    logger.debug(f"verify json loaded data: {webhook_test3_data}")

test_case(webhook_url, webhook_test3_data)
logger.info("Test Case 3 completed for gitguardian_url")

logger.info("Test Case 4 started for nse etf api")

# NSE URL for ETF data
url = "https://www.nseindia.com/api/live-analysis-most-active-etf?index=volume"
webhook_url = "http://127.0.0.1:8000/mvetfwebhook"


# Fetch ETF data
etf_data = nsefetch(url)

# Loop through each ETF and post to the webhook
for etf in etf_data.get('data', []):
    payload = {
        "source": "nseindia",
        "symbol": etf.get('symbol', 'N/A'),
        "assetName": etf.get('identifier', 'N/A'),
        "LastPrice": etf.get('lastPrice', 'N/A'),
        "HIGHVALUE": etf.get('dayHigh', 'N/A'),
        "LOWVALUE": etf.get('dayLow', 'N/A'),
        "tradedVolume": etf.get('totalTradedVolume', 'N/A'),
        "tradedValue": etf.get('totalTradedValue', 'N/A'),
        "nav": etf.get('nav', 'N/A'),
        "closePrice": etf.get('closePrice', 'N/A'),
        "PreviousclosePrice": etf.get('previousClose', 'N/A'),
        "PercentageDiff": etf.get('pChange', 'N/A')
    }

    try:
       logger.info(payload)
       response = requests.post(webhook_url, json=payload)
       if response.status_code == 200:
           logger.info(f"✅ Sent data for {payload['symbol']}")
       else:
          logger.error(f"⚠️ Failed to send {payload['symbol']}: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        logger.error(f"❌ Error sending data for {payload['symbol']}: {e}")

logger.info("Test Case 4 completed for nse etf api")

logger.info("Test Case 5 started for nse stock api")

# NSE URL for stock data
url = "https://www.nseindia.com/api/live-analysis-volume-gainers"

webhook_url = "http://127.0.0.1:8000/maswebhook"


# Fetch stock data
stocks_data = nsefetch(url)
for stockdata in stocks_data.get('data', []):
    payload = {
        "source": "nseindia",
        "symbol": stockdata.get('symbol', 'N/A'),
        "companyName": stockdata.get('companyName', 'N/A'),
        "volume": stockdata.get('volume', 'N/A'),
        "week1AvgVolume": stockdata.get('week1AvgVolume', 'N/A'),
        "week1volChange": stockdata.get('week1volChange', 'N/A'),
        "week2AvgVolume": stockdata.get('week2AvgVolume', 'N/A'),
        "week2volChange": stockdata.get('week2volChange', 'N/A'),
        "ltp": stockdata.get('ltp', 'N/A'),
        "pChange": stockdata.get('pChange', 'N/A')
    }

    try:
       response = requests.post(webhook_url, json=payload)
       if response.status_code == 200:
           logger.info(f"✅ Sent data for {payload['symbol']}")
       else:
          logger.error(f"⚠️ Failed to send {payload['symbol']}: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        logger.error(f"❌ Error sending data for {payload['symbol']}: {e}")

logger.info("Test Case 5 completed for nse stock api")

logger.info("Test Case 6 started for nse most actives")

url = "https://www.nseindia.com/api/live-analysis-most-active-securities?index=volume"
webhook_url = "http://127.0.0.1:8000/webhookmas"


stocks_data = nsefetch(url)
for stockdata in stocks_data.get('data', []):
    payload = {
        "source": "nseindia",
        "symbol": stockdata.get('symbol', 'N/A'),
        "companyName": stockdata.get('identifier', 'N/A'),
        "pChange": stockdata.get('pChange', 'N/A'),
        "volume": stockdata.get('quantityTraded', 'N/A'),
        "totalTradedVolume": stockdata.get('totalTradedVolume', 'N/A'),
        "totalTradedValue": stockdata.get('totalTradedValue', 'N/A'),
        "previousClose": stockdata.get('previousClose', 'N/A'),
        "lastPrice": stockdata.get('lastPrice', 'N/A')
    }

    try:
       response = requests.post(webhook_url, json=payload)
       if response.status_code == 200:
           logger.info(f"✅ Sent data for {payload['symbol']}")
       else:
          logger.error(f"⚠️ Failed to send {payload['symbol']}: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        logger.error(f"❌ Error sending data for {payload['symbol']}: {e}")

logger.info("Test Case 6 Completed for nse most actives")


logger.info("Test Case 7 started for get remainders")
#https://github.com/hemanth22/pysnips_test/blob/main/telegram_group_snippet/tele_group.py
bot_token = os.environ.get('Priyoid_bot')

with open('remainder_today.txt','r') as file:
    file_contents = file.read()

message = file_contents


def telegram_send_message(message):
    url = "https://api.telegram.org/bot{}/sendMessage?chat_id=-1001943848370&text={}".format(bot_token, message)
    requests.get(url)

#telegram_send_message(message)
for new_sendMessage_tele in message.split("\n"):
    telegram_send_message(new_sendMessage_tele)
logger.info("Test Case 7 Completed for get remainders")

logger.info("Test Case 8 Started for get remainders")


postgres_hostname = os.environ.get('postgres_host')
postgres_database = os.environ.get('postgres_db')
postgres_port = os.environ.get('postgres_port')
postgres_username = os.environ.get('postgres_user')
postgres_password = os.environ.get('postgres_password')
bot_token = os.environ.get('Priyoid_bot')

  
def telegram_send_message(message):
    url = "https://api.telegram.org/bot{}/sendMessage?chat_id=-1001943848370&text={}".format(bot_token, message)
    requests.get(url)

def fetch_message_for_date(date_str):
    connection = None
    cursor = None
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(database=postgres_database, user=postgres_username, password=postgres_password, host=postgres_hostname, port=postgres_port)
        cursor = connection.cursor()

        # Define the query with parameterized inputs
        query = """
        SELECT message 
        FROM remainder_messages 
        WHERE message_date = %s;
        """
        # Execute the query
        cursor.execute(query, (date_str,))
        results = cursor.fetchall()

        # Return messages if they exist
        if results:
            messages = [row[0] for row in results]
            return messages
        else:
            return ["No messages found for this date."]

    except (Exception, psycopg2.Error) as error:
        return [f"Error while connecting to PostgreSQL: {error}"]

    finally:
        # Close the database connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Usage example
if __name__ == "__main__":
    # Specify the date in YYYY-MM-DD format
    ist_timezone = pytz.timezone("Asia/Kolkata")
    # Create a datetime object
    current_date = datetime.now(ist_timezone)
    # Format it to YYYY-MM-DD
    formatted_date = current_date.strftime("%Y-%m-%d")
    logger.info(f"Formatted Date: {formatted_date}")
    date_to_query = formatted_date
    message = fetch_message_for_date(date_to_query)
    #telegram_send_message(message)
    for new_sendMessage_tele in message:
        telegram_send_message(new_sendMessage_tele)
    logger.info(f"Message for {date_to_query}: {message}")

logger.info("Test Case 8 Completed for get remainders")

logger.info("Test Case 9 Started for get remainders")

postgres_hostname = os.environ.get('postgres_host')
postgres_database = os.environ.get('postgres_db')
postgres_port = os.environ.get('postgres_port')
postgres_username = os.environ.get('postgres_user')
postgres_password = os.environ.get('postgres_password')
bot_token = os.environ.get('Priyoid_bot')

# Establishing the connection
conn = psycopg2.connect(
    database=postgres_database, 
    user=postgres_username, 
    password=postgres_password, 
    host=postgres_hostname, 
    port=postgres_port
)
# Creating a cursor object using the cursor() method
cursor = conn.cursor()

# Executing an MYSQL function using the execute() method
cursor.execute("select version()")

# Fetch a single row using fetchone() method.
data = cursor.fetchone()
logger.info("Connection established to: ", data)

# Closing the connection
conn.close()

logger.info("Test Case 9 Completed for get remainders")