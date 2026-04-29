import os
import requests
from datetime import datetime

# 1. Get secrets
TODOIST_TOKEN = os.environ.get("TODOIST_TOKEN")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def get_due_tasks():
    headers = {"Authorization": f"Bearer {TODOIST_TOKEN}"}
    response = requests.get("https://todoist.com", headers=headers)
    
    # Check if the API call was successful
    if response.status_code != 200:
        print(f"❌ Todoist Error {response.status_code}: {response.text}")
        return None

    tasks = response.json()
    today = datetime.now().strftime("%Y-%m-%d")
    
    due_today = [task["content"] for task in tasks if task.get("due") and task["due"]["date"] == today]
    return due_today

def send_telegram(message):
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    res = requests.post(url, data=payload)
    if res.status_code != 200:
        print(f"❌ Telegram Error {res.status_code}: {res.text}")

if __name__ == "__main__":
    tasks = get_due_tasks()
    
    if tasks is None:
        print("Stopping because of Todoist error.")
    elif tasks:
        task_list = "\n".join([f"▫️ {t}" for t in tasks])
        send_telegram(f"📅 *Tasks Due Today:*\n{task_list}")
        print("✅ Message sent!")
    else:
        print("✅ No tasks due today. Script finished.")
