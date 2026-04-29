import os
import requests
from datetime import datetime

# Get keys
TODOIST_TOKEN = os.environ.get("TODOIST_TOKEN", "").strip()
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
CHAT_ID = os.environ.get("CHAT_ID", "").strip()

def debug_check():
    print("--- 🔍 DEEP DEBUG START ---")
    if not TODOIST_TOKEN:
        print("❌ ERROR: TODOIST_TOKEN is empty! Check your GitHub Secrets.")
        return
    
    # This prints just the start and end of your token to check for extra spaces
    print(f"Token Check: Starts with '{TODOIST_TOKEN[:3]}...' and ends with '...{TODOIST_TOKEN[-3:]}'")
    print(f"Token Length: {len(TODOIST_TOKEN)} characters")

    headers = {"Authorization": f"Bearer {TODOIST_TOKEN}"}
    url = "https://todoist.com"
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.headers.get('Content-Type')}")
        
        if response.status_code == 200:
            tasks = response.json()
            print(f"✅ SUCCESS: Received {len(tasks)} tasks from Todoist.")
            return tasks
        else:
            print(f"❌ TODOIST REJECTED TOKEN: {response.text}")
    except Exception as e:
        print(f"❌ CRASH: {e}")
    return None

if __name__ == "__main__":
    tasks = debug_check()
    if tasks:
        today = datetime.now().strftime("%Y-%m-%d")
        due_today = [t["content"] for t in tasks if t.get("due") and t["due"]["date"] == today]
        
        if due_today:
            msg = "📅 *Tasks Due Today:*\n" + "\n".join([f"▫️ {t}" for t in due_today])
            url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
            requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
            print("🚀 Telegram message sent!")
        else:
            print("📅 No tasks due today, but the connection worked!")
