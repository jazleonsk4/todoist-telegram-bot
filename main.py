import os
import requests

# Get keys
TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
USER_ID = os.environ.get("CHAT_ID", "").strip()

def main():
    # This URL is completely fixed and cannot be changed by secrets
    url = f"https://telegram.org{TOKEN}/sendMessage"
    
    print(f"--- Attempting to send to Telegram ---")
    data = {"chat_id": USER_ID, "text": "✅ It worked! Your script is finally updated."}
    
    response = requests.post(url, data=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    main()
