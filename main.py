import os
from todoist_api_python.api import TodoistAPI
from datetime import datetime
import requests

# 1. Setup keys
TODOIST_TOKEN = os.environ.get("TODOIST_TOKEN", "").strip()
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
CHAT_ID = os.environ.get("CHAT_ID", "").strip()

def get_tasks():
    api = TodoistAPI(TODOIST_TOKEN)
    try:
        # The library handles all the complex connection logic for you
        tasks = api.get_tasks()
        today = datetime.now().strftime("%Y-%m-%d")
        
        due_today = []
        for task in tasks:
            if task.due and task.due.date == today:
                due_today.append(task.content)
        return due_today
    except Exception as error:
        print(f"❌ Todoist Library Error: {error}")
        return None

def send_telegram(msg):
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

if __name__ == "__main__":
    due_tasks = get_tasks()
    
    if due_tasks is not None:
        if due_tasks:
            message = "📅 *Tasks Due Today:*\n" + "\n".join([f"▫️ {t}" for t in due_tasks])
            send_telegram(message)
            print("✅ Success! Message sent to Telegram.")
        else:
            print("✅ Connection successful, but no tasks are due today.")
    else:
        print("⚠️ Failed to retrieve tasks.")
