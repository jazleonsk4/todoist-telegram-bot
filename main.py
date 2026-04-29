import os
import pytz
import requests
from datetime import datetime
from todoist_api_python.api import TodoistAPI

# 1. Setup keys and Timezone
TODOIST_TOKEN = os.environ.get("TODOIST_TOKEN", "").strip()
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
CHAT_ID = os.environ.get("CHAT_ID", "").strip()

# Set your local timezone (Malaysia/Kuala Lumpur)
MY_TZ = pytz.timezone('Asia/Kuala_Lumpur')

def get_tasks_due_today():
    api = TodoistAPI(TODOIST_TOKEN)
    try:
        # Get today's date in YOUR timezone
        today_str = datetime.now(MY_TZ).strftime("%Y-%m-%d")
        print(f"DEBUG: The Robot is checking tasks for: {today_str}")
        
        all_tasks = api.get_tasks()
        due_today = []
        
        for task in all_tasks:
            # Check if task has a due date and matches today's local date
            if task.due and task.due.date == today_str:
                due_today.append(task.content)
        
        return due_today
    except Exception as e:
        print(f"❌ Error fetching from Todoist: {e}")
        return None

def send_to_telegram(task_list):
    if not task_list:
        print("✅ No tasks due today in your timezone. No message sent.")
        return

    formatted_tasks = "\n".join([f"▫️ {t}" for t in task_list])
    text = f"📅 *Tasks Due Today ({datetime.now(MY_TZ).strftime('%d %b')}):*\n{formatted_tasks}"
    
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("🚀 Success! Message sent to Telegram.")
    else:
        print(f"❌ Telegram Error: {response.text}")

if __name__ == "__main__":
    tasks = get_tasks_due_today()
    if tasks is not None:
        send_to_telegram(tasks)
