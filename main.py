import os
import pytz
import requests
from datetime import datetime
from todoist_api_python.api import TodoistAPI

# 1. Setup keys and Timezone
TODOIST_TOKEN = os.environ.get("TODOIST_TOKEN", "").strip()
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
CHAT_ID = os.environ.get("CHAT_ID", "").strip()
MY_TZ = pytz.timezone('Asia/Kuala_Lumpur')

def get_tasks_due_today():
    api = TodoistAPI(TODOIST_TOKEN)
    try:
        # Get today's date in Malaysia
        today_str = datetime.now(MY_TZ).strftime("%Y-%m-%d")
        print(f"DEBUG: Checking for date: {today_str}")
        
        # Fetch all tasks
        tasks = api.get_tasks()
        due_today = []
        
        # Loop through tasks individually
        for task in tasks:
            # We use .get() style or direct attribute check for safety
            task_due_date = getattr(task.due, 'date', None) if task.due else None
            
            if task_due_date == today_str:
                print(f"✅ Found task due today: {task.content}")
                due_today.append(task.content)
        
        return due_today
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def send_to_telegram(task_list):
    if not task_list:
        print("✅ No tasks due today. No message sent.")
        return

    formatted_tasks = "\n".join([f"▫️ {t}" for t in task_list])
    text = f"📅 *Tasks Due Today:*\n{formatted_tasks}"
    
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    
    requests.post(url, data=payload)
    print("🚀 Success! Message sent.")

if __name__ == "__main__":
    tasks = get_tasks_due_today()
    if tasks is not None:
        send_to_telegram(tasks)
