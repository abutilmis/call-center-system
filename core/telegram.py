import requests
import os
from django.conf import settings

def send_telegram_message(text):
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    if not token or not chat_id:
        return False, "Telegram credentials not configured."

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'  # optional, you can use Markdown or plain text
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        return True, "Message sent."
    except Exception as e:
        return False, str(e)