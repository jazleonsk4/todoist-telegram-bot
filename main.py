import os
import requests
from datetime import datetime

# Get keys from GitHub Secrets
TODOIST_TOKEN = os.environ.get("TODOIST_TOKEN", "").strip()
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
CHAT_ID = os.environ.get("CHAT_ID", "").strip()

def get_due_tasks():
    # Adding a 'User-Agent' makes the script look like a real browser
    headers = {
        "Authorization": f"Bearer {TODOIST_TOKEN}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
    }
    url = "https://todoist.com"
    
    try:
        # Using a standard GET request to avoid the 405 'Method Not Allowed' error
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            tasks = response.json()
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Find tasks where the due date is today
            due_today = []
            for t in tasks:
                due_info = t.get("due")
                if due_info and due_info.get("date") == today:
                    due_today.append(t.get("content", "Untitled Task"))
            return due_today
        else:
            print(f"❌ Error from Todoist: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

def send_to_telegram(msg):
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    requests.post(url, data=payload, timeout=10)

if __name__ == "__main__":
    tasks = get_due_tasks()
    
    if tasks:
        task_text = "\n".join([f"▫️ {t}" for t in tasks])
        message = f"📅 *Tasks Due Today:*\n{task_text}"
        send_to_telegram(message)
        print("✅ Success! Message sent to Telegram.")
    elif tasks == []:
        print("✅ Success! No tasks due today.")
    else:
        print("⚠️ Script stopped due to a connection error.")
