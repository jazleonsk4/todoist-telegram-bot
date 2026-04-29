import os
import requests

# 1. Setup keys
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
CHAT_ID = os.environ.get("CHAT_ID", "").strip()

def send_test_message():
    print(f"DEBUG: Attempting to send to Chat ID: {CHAT_ID}")
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": "🚀 *Hello!* If you see this, your Telegram Bot is working perfectly!",
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ SUCCESS! Telegram message sent.")
        else:
            print(f"❌ TELEGRAM ERROR {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ CRASH: {e}")

if __name__ == "__main__":
    send_test_message()
