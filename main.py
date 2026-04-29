import os
import requests
from datetime import datetime

# Get keys
TODOIST_TOKEN = os.environ.get("TODOIST_TOKEN")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def get_due_tasks():
    headers = {"Authorization": f"Bearer {TODOIST_TOKEN}"}
    url = "https://todoist.com"
    
    try:
        response = requests.get(url, headers=headers)
        # Safety check: if response is empty or not 200
        if response.status_code != 200 or not response.text.strip():
            print(f"Note: Todoist returned status {response.status_code} with no data.")
            return []
            
        tasks = response.json()
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Filter tasks safely
        due_today = []
        for t in tasks:
            if isinstance(t, dict) and t.get("due") and t["due"].get("date") == today:
                due_today.append(t.get("content", "Untitled Task"))
        return due_today
        
    except Exception as e:
        print(f"Search error: {e}")
        return []

if __name__ == "__main__":
    tasks = get_due_tasks()
    if tasks:
        msg = "📅 *Tasks Due Today:*\n" + "\n".join([f"▫️ {t}" for t in tasks])
        url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
        print("✅ Message sent to Telegram!")
    else:
        print("✅ No tasks due today. Everything is up to date!")
