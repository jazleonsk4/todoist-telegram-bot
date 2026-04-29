import os
import requests

# Get keys from Secrets
TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
USER_ID = os.environ.get("CHAT_ID", "").strip()

def send_fake_message():
    # The URL that we finally fixed!
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    print(f"DEBUG: Sending to {url.replace(TOKEN, '***')}")
    
    # This is the "fake" message you requested
    text = "✅ **Todoist Update:** No tasks due today! Have a great day."
    
    payload = {
        "chat_id": USER_ID,
        "text": text,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("🚀 SUCCESS! Check your Telegram phone app now.")
        else:
            print(f"❌ ERROR {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")

if __name__ == "__main__":
    send_fake_message()
