import os
import pytz
import requests
from datetime import datetime
from todoist_api_python.api import TodoistAPI

# Setup keys
TODOIST_TOKEN = os.environ.get("TODOIST_TOKEN", "").strip()
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
CHAT_ID = os.environ.get("CHAT_ID", "").strip()
MY_TZ = pytz.timezone('Asia/Kuala_Lumpur')

def get_tasks_due_today():
    api = TodoistAPI(TODOIST_TOKEN)
    try:
        today_str = datetime.now(MY_TZ).strftime("%Y-%m-%d")
        all_tasks = api.get_tasks()
        return [t.content for t in all_tasks if t.due and t.due.date == today_str]
    except Exception as e:
        print(f"❌ Todoist Error: {e}")
        return None

def send_to_telegram(task_list):
    # This URL is fixed to prevent the 'Failed to parse' error
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    
    if task_list is None:
        text = "⚠️ Connection to Todoist failed."
    elif not task_list:
        text = "✅ No tasks due today!"
    else:
        tasks_text = "\n".join([f"▫️ {t}" for t in task_list])
        text = f"📅 *Tasks Due Today:*\n{tasks_text}"
    
    print(f"DEBUG: Sending to {url.replace(TELEGRAM_TOKEN, '***')}")
    requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})

if __name__ == "__main__":
    tasks = get_tasks_due_today()
    send_to_telegram(tasks)
