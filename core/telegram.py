import requests
import os
from django.conf import settings

def send_telegram_message(text, reply_to_message_id=None):
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    if not token or not chat_id:
        return False, "Telegram credentials not configured."

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    if reply_to_message_id:
        payload['reply_to_message_id'] = reply_to_message_id

    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        resp_data = response.json()
        message_id = resp_data.get('result', {}).get('message_id')
        return True, message_id
    except Exception as e:
        return False, str(e)