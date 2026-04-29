import os
import requests
import json

TODOIST_TOKEN = os.environ.get("TODOIST_TOKEN", "").strip()
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
CHAT_ID = os.environ.get("CHAT_ID", "").strip()

def get_due_tasks():
    # We switch to the 'Sync' API which is more robust
    url = "https://todoist.com"
    headers = {"Authorization": f"Bearer {TODOIST_TOKEN}"}
    
    # We ask only for 'items' (tasks)
    data = {
        "sync_token": "*",
        "resource_types": '["items"]'
    }
    
    try:
        response = requests.post(url, headers=headers, data=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error from Todoist: {response.text}")
            return []

        result = response.json()
        tasks = result.get("items", [])
        
        # Get today's date in Todoist format
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        
        due_today = []
        for t in tasks:
            due = t.get("due")
            # Check if the task is due today and not completed
            if due and due.get("date").startswith(today) and t.get("checked") == 0:
                due_today.append(t.get("content"))
        
        return due_today
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def send_to_telegram(tasks):
    if not tasks:
        print("✅ No tasks due today. No message sent.")
        return
        
    msg = "📅 *Tasks Due Today:*\n" + "\n".join([f"▫️ {t}" for t in tasks])
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    requests.post(url, data=payload)
    print("🚀 Message sent to Telegram!")

if __name__ == "__main__":
    tasks = get_due_tasks()
    send_to_telegram(tasks)
