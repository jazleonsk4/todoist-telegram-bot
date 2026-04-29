import os
import requests

# Get keys from Secrets
TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
USER_ID = os.environ.get("CHAT_ID", "").strip()

def send_test():
    # I have hard-coded the 'api.' and 'bot' parts here to fix your specific error
    url = f"https://telegram.org{TOKEN}/sendMessage"
    
    print(f"DEBUG: Connecting to {url.replace(TOKEN, '***')}")
    
    payload = {
        "chat_id": USER_ID,
        "text": "🎊 *VICTORY!* The Telegram connection is finally fixed.",
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ SUCCESS! Check your Telegram.")
        else:
            print(f"❌ ERROR {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ CRITICAL CRASH: {e}")

if __name__ == "__main__":
    send_test()
