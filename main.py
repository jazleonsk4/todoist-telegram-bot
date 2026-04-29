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
    
    print("--- DEBUG INFO ---")
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Todoist Error Message: {response.text}")
            return None
            
        # Only try to read JSON if status is 200
        tasks = response.json()
        today = datetime.now().strftime("%Y-%m-%d")
        return [t["content"] for t in tasks if t.get("due") and t["due"]["date"] == today]
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

if __name__ == "__main__":
    tasks = get_due_tasks()
    if tasks is not None:
        if tasks:
            msg = "📅 *Tasks Due Today:*\n" + "\n".join([f"▫️ {t}" for t in tasks])
            url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
            requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
            print("✅ Success: Message sent.")
        else:
            print("✅ Success: No tasks due today.")
    else:
        print("❌ Script stopped due to the error shown above.")
