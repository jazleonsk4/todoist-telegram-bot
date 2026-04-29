import os
import html
import pytz
import requests
from datetime import datetime
from todoist_api_python.api import TodoistAPI

TODOIST_TOKEN = os.environ.get("TODOIST_TOKEN", "").strip()
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
CHAT_ID = os.environ.get("CHAT_ID", "").strip()

MY_TZ = pytz.timezone("Asia/Kuala_Lumpur")


def validate_env():
    missing = []

    if not TODOIST_TOKEN:
        missing.append("TODOIST_TOKEN")
    if not TELEGRAM_TOKEN:
        missing.append("TELEGRAM_TOKEN")
    if not CHAT_ID:
        missing.append("CHAT_ID")

    if missing:
        raise RuntimeError(f"Missing GitHub secret(s): {', '.join(missing)}")


def get_tasks_due_today():
    api = TodoistAPI(TODOIST_TOKEN)
    today_str = datetime.now(MY_TZ).strftime("%Y-%m-%d")

    tasks_due_today = []

    try:
        # get_tasks() returns pages/lists of tasks, so we need two loops
        for page in api.get_tasks():
            for task in page:
                if task.due and str(task.due.date).startswith(today_str):
                    tasks_due_today.append(task.content)

        return tasks_due_today

    except Exception as e:
        print(f"❌ Todoist Error: {e}")
        return None


def send_to_telegram(task_list):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    if task_list is None:
        text = "⚠️ Failed to connect to Todoist."
    elif not task_list:
        text = "✅ <b>Good News!</b> No tasks due today in Todoist."
    else:
        tasks_text = "\n".join(
            [f"▫️ {html.escape(task)}" for task in task_list]
        )
        text = f"📅 <b>Tasks Due Today:</b>\n{tasks_text}"

    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
        },
        timeout=20,
    )

    response.raise_for_status()
    print("✅ Telegram message sent")


if __name__ == "__main__":
    validate_env()
    tasks = get_tasks_due_today()
    send_to_telegram(tasks)
