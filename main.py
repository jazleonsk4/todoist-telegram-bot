import os
import requests

# Get keys from Secrets
TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
USER_ID = os.environ.get("CHAT_ID", "").strip()

def send_final_test():
    # We manually build the URL to be 100% sure it is correct
    url = f"https://telegram.org{TOKEN}/sendMessage"
    
    print(f"DEBUG: Checking connection to Telegram...")
    
    payload = {
        "chat_id": USER_ID,
        "text": "🎊 *SUCCESS!* Your Telegram Bot is finally connected correctly.",
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ DONE! Check your Telegram app.")
        else:
            print(f"❌ ERROR {response.status_code}")
            print(f"Details: {response.text}")
    except Exception as e:
        print(f"❌ CRASHED: {e}")

if __name__ == "__main__":
    send_final_test()
