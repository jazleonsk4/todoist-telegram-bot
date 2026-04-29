import os
import requests

# 1. Setup keys
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
CHAT_ID = os.environ.get("CHAT_ID", "").strip()

def send_test_message():
    # Correct Telegram API URL format
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    
    print(f"DEBUG: Testing Telegram connection...")
    payload = {
        "chat_id": CHAT_ID, 
        "text": "🚀 *TEST SUCCESS!* Your Telegram setup is now working.",
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ SUCCESS! Check your Telegram phone app now.")
        else:
            print(f"❌ ERROR {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ CRASH: {e}")

if __name__ == "__main__":
    send_test_message()
