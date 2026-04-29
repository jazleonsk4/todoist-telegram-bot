import os
import requests
from datetime import datetime

# 1. Get secrets from GitHub Environment
TODOIST_TOKEN = os.environ.get("TODOIST_TOKEN")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def get_due_tasks():
    headers = {"Authorization": f"Bearer {TODOIST_TOKEN}"}
    # Fetch active tasks
    response = requests.get("https://todoist.com", headers=headers)
    response.raise_for_status()
    tasks = response.json()
    
    # Get today's date in YYYY-MM-DD format
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Find tasks where 'due.date' is today
    due_today = []
    for task in tasks:
        due_info = task.get("due")
        if due_info and due_info.get("date") == today:
            due_today.append(task["content"])
            
    return due_today

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=payload)

if __name__ == "__main__":
    try:
        tasks = get_due_tasks()
        if tasks:
            # Format the message list
            task_list = "\n".join([f"▫️ {t}" for t in tasks])
            text = f"📅 *Tasks Due Today:*\n{task_list}"
            send_telegram_message(text)
            print("Message sent successfully.")
        else:
            print("No tasks due today.")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
