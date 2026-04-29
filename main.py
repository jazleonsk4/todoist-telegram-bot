import os
import requests
from datetime import datetime

TODOIST_TOKEN = os.environ.get("TODOIST_TOKEN", "").strip()
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
CHAT_ID = os.environ.get("CHAT_ID", "").strip()

def get_due_tasks():
    headers = {"Authorization": f"Bearer {TODOIST_TOKEN}"}
    url = "https://todoist.com"
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        # DEBUG: Let's see what Todoist actually sent
        content_preview = response.text[:100]
        print(f"Response Preview: {content_preview}")

        if not response.text.strip():
            print("⚠️ Todoist sent an empty response.")
            return []

        if response.status_code == 200:
            tasks = response.json()
            today = datetime.now().strftime("%Y-%m-%d")
            return [t["content"] for t in tasks if t.get("due") and t["due"]["date"] == today]
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def send_to_telegram(msg):
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

if __name__ == "__main__":
    tasks = get_due_tasks()
    if tasks:
        send_to_telegram(f"📅 *Tasks Due Today:*\n" + "\n".join([f"▫️ {t}" for t in tasks]))
        print("✅ Message sent!")
    elif tasks == []:
        print("✅ No tasks due today.")
    else:
        print("⚠️ Script stopped.")
