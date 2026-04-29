import os
import requests
from datetime import datetime

# Get keys from GitHub Secrets
TODOIST_TOKEN = os.environ.get("TODOIST_TOKEN")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def get_due_tasks():
    headers = {"Authorization": f"Bearer {TODOIST_TOKEN}"}
    url = "https://todoist.com"
    
    print(f"DEBUG: Attempting to connect to Todoist...")
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ ERROR: Todoist returned status {response.status_code}")
        print(f"DEBUG: Response body: {response.text}")
        return None

    tasks = response.json()
    today = datetime.now().strftime("%Y-%m-%d")
    return [t["content"] for t in tasks if t.get("due") and t["due"]["date"] == today]

def send_telegram(msg):
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

if __name__ == "__main__":
    tasks = get_due_tasks()
    if tasks is None:
        print("Stopping due to connection error.")
    elif tasks:
        task_list = "\n".join([f"▫️ {t}" for t in tasks])
        send_telegram(f"📅 *Tasks Due Today:*\n{task_list}")
        print("✅ Success: Message sent to Telegram.")
    else:
        print("✅ Success: No tasks due today.")
