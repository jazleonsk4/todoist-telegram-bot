import os
import requests

# Get keys from Secrets
TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
USER_ID = os.environ.get("CHAT_ID", "").strip()

def send_test():
    # This line is now hard-coded to prevent the previous error
    url = "https://telegram.org" + TOKEN + "/sendMessage"
    
    # This will print the URL to the log so we can see if it's correct
    print(f"DEBUG: The Robot is going to: {url.replace(TOKEN, 'TOKEN_HIDDEN')}")
    
    payload = {
        "chat_id": USER_ID,
        "text": "🎊 *ULTIMATE VICTORY!* It is finally working.",
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ SUCCESS! Check your Telegram app.")
        else:
            print(f"❌ ERROR {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ CRITICAL CRASH: {e}")

if __name__ == "__main__":
    send_test()
