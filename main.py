import os
from todoist_api_python.api import TodoistAPI
from datetime import datetime
import requests

# Setup keys
TODOIST_TOKEN = os.environ.get("TODOIST_TOKEN", "").strip()
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
CHAT_ID = os.environ.get("CHAT_ID", "").strip()

def get_tasks_due_today():
    api = TodoistAPI(TODOIST_TOKEN)
    try:
        # 1. Fetch all active tasks
        all_tasks = api.get_tasks()
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        due_today = []
        
        # 2. Safely loop through each individual task
        for task in all_tasks:
            # Check if 'due' exists and matches today's date
            if hasattr(task, 'due') and task.due:
                if task.due.date == today_str:
                    due_today.append(task.content)
        
        return due_today
    except Exception as e:
        print(f"❌ Error fetching from Todoist: {e}")
        return None

def send_to_telegram(task_list):
    if not task_list:
        print("✅ No tasks due today. No message sent.")
        return

    # Format and send the message
    formatted_tasks = "\n".join([f"▫️ {t}" for t in task_list])
    text = f"📅 *Tasks Due Today:*\n{formatted_tasks}"
    
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
    else:
        print("⚠️ Failed to connect. Check your TODOIST_TOKEN.")
