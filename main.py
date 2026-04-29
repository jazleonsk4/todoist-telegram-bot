import os
import pytz
import requests
from datetime import datetime
from todoist_api_python.api import TodoistAPI

# 1. Setup keys and Timezone
TODOIST_TOKEN = os.environ.get("TODOIST_TOKEN", "").strip()
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
CHAT_ID = os.environ.get("CHAT_ID", "").strip()

# Set Malaysia Timezone
MY_TZ = pytz.timezone('Asia/Kuala_Lumpur')

def get_tasks_due_today():
    api = TodoistAPI(TODOIST_TOKEN)
    try:
        # Get today's date in Malaysia time
        today_str = datetime.now(MY_TZ).strftime("%Y-%m-%d")
        print(f"DEBUG: Looking for tasks due on: {today_str}")
        
        all_tasks = api.get_tasks()
        due_today = []
        
        for task in all_tasks:
            # Check if task has a due date and if it matches today
            if task.due and task.due.date == today_str:
                due_today.append(task.content)
        
        return due_today
    except Exception as e:
        print(f"❌ Todoist Error: {e}")
        return None

def send_to_telegram(task_list):
    # This URL is now hard-coded to be impossible to break
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    
    if not task_list:
        text = "✅ *Good news!* You have no tasks due today in Todoist."
    else:
        formatted_tasks = "\n".join([f"▫️ {t}" for t in task_list])
        text = f"📅 *Tasks Due Today ({datetime.now(MY_TZ).strftime('%d %b')}):*\n{formatted_tasks}"
    
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("🚀 SUCCESS! Check your Telegram now.")
        else:
            print(f"❌ Telegram Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")

if __name__ == "__main__":
    tasks = get_due_tasks_due_today() if 'get_due_tasks_due_today' in locals() else get_tasks_due_today()
    send_to_telegram(tasks)
