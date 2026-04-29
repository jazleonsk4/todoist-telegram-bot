import os
import requests
from datetime import datetime

TODOIST_TOKEN = os.environ.get("TODOIST_TOKEN", "").strip()
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
CHAT_ID = os.environ.get("CHAT_ID", "").strip()

def get_due_tasks():
    # Strict headers to ensure Todoist sends JSON, not a webpage
    headers = {
        "Authorization": f"Bearer {TODOIST_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "TodoistBot/1.0"
    }
    url = "https://todoist.com"
    
    try:
        response = requests.get(url, headers=headers)
        
        # If we still get HTML, try the 'Sync' endpoint as a backup
        if "text/html" in response.headers.get("Content-Type", ""):
            print("⚠️ REST API blocked. Trying Sync API fallback...")
            sync_url = "https://todoist.com"
            sync_data = {"sync_token": "*", "resource_types": '["items"]'}
            response = requests.post(sync_url, headers=headers, data=sync_data)

        if response.status_code == 200:
            data = response.json()
            # Handle both REST (list) and Sync (dict) formats
            tasks = data.get("items", data) if isinstance(data, dict) else data
            today = datetime.now().strftime("%Y-%m-%d")
            
            return [t["content"] for t in tasks if t.get("due") and t["due"]["date"].startswith(today)]
        
        print(f"❌ Error: {response.status_code}")
        return None
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        return None

if __name__ == "__main__":
    tasks = get_due_tasks()
    if tasks:
        msg = f"📅 *Tasks Due Today:*\n" + "\n".join([f"▫️ {t}" for t in tasks])
        requests.post(f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage", 
                      data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
        print("🚀 Success! Message sent.")
    elif tasks == []:
        print("✅ Connection OK. No tasks due today.")
    else:
        print("⚠️ Script could not retrieve tasks.")
