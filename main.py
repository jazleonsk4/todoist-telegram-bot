import os
import requests
from datetime import datetime

# Get keys from GitHub Secrets
TODOIST_TOKEN = os.environ.get("TODOIST_TOKEN")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def get_due_tasks():
    # HEADERS: This is how we prove to Todoist who we are
    headers = {"Authorization": f"Bearer {TODOIST_TOKEN}"}
    
    # ENDPOINT: We are using the official REST V2 API
    url = "https://todoist.com"
    
    try:
        # We request the tasks from Todoist
        response = requests.get(url, headers=headers)
        
        # If Todoist says OK (200), we process the data
        if response.status_code == 200:
            tasks = response.json()
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Look for tasks due today
            due_today = []
            for t in tasks:
                due_info = t.get("due")
                if due_info and due_info.get("date") == today:
                    due_today.append(t.get("content", "Untitled Task"))
            return due_today
        else:
            print(f"❌ Todoist error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

def send_to_telegram(msg):
    # This sends the actual message to your bot
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    requests.post(url, data=data)

if __name__ == "__main__":
    tasks = get_due_tasks()
    
    if tasks:
        # If tasks were found, send them!
        task_text = "\n".join([f"▫️ {t}" for t in tasks])
        message = f"📅 *Tasks Due Today:*\n{task_text}"
        send_to_telegram(message)
        print("✅ Success! Check your Telegram.")
    elif tasks == []:
        print("✅ No tasks due today. Everything is clear!")
    else:
        print("⚠️ Script stopped because it couldn't connect to Todoist.")
