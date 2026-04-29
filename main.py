import os
import html
import json
from pathlib import Path
from datetime import datetime

import pytz
import requests
from todoist_api_python.api import TodoistAPI


TODOIST_TOKEN = os.environ.get("TODOIST_TOKEN", "").strip()
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
CHAT_ID = os.environ.get("CHAT_ID", "").strip()
RUN_MODE = os.environ.get("RUN_MODE", "send_report").strip()

MY_TZ = pytz.timezone("Asia/Kuala_Lumpur")
STATE_FILE = Path("telegram_offset.txt")


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


def get_task_due_date(task):
    if not task.due or not task.due.date:
        return None

    # Todoist due.date is normally YYYY-MM-DD.
    # This also works safely if it ever includes time info.
    return str(task.due.date)[:10]


def get_overdue_and_today_tasks():
    today_str = datetime.now(MY_TZ).date().isoformat()

    overdue_tasks = []
    today_tasks = []

    try:
        with TodoistAPI(TODOIST_TOKEN) as api:
            # get_tasks() returns pages/lists of tasks
            for page in api.get_tasks(limit=200):
                for task in page:
                    due_date = get_task_due_date(task)

                    if not due_date:
                        continue

                    if due_date < today_str:
                        overdue_tasks.append(task.content)
                    elif due_date == today_str:
                        today_tasks.append(task.content)

        return overdue_tasks, today_tasks, None

    except Exception as e:
        print(f"❌ Todoist Error: {e}")
        return [], [], str(e)


def format_task_list(tasks, empty_text):
    if not tasks:
        return empty_text

    return "\n".join(f"▫️ {html.escape(task)}" for task in tasks)


def build_report():
    overdue_tasks, today_tasks, error = get_overdue_and_today_tasks()
    now_text = datetime.now(MY_TZ).strftime("%Y-%m-%d %I:%M %p")

    if error:
        return (
            "⚠️ <b>Todoist Check Failed</b>\n"
            f"{html.escape(error)}"
        )

    overdue_text = format_task_list(overdue_tasks, "No overdue tasks.")
    today_text = format_task_list(today_tasks, "No tasks due today.")

    return (
        f"🕒 <b>Todoist Check</b>\n"
        f"{html.escape(now_text)}\n\n"
        f"⚠️ <b>Overdue</b> ({len(overdue_tasks)})\n"
        f"{overdue_text}\n\n"
        f"📅 <b>Due Today</b> ({len(today_tasks)})\n"
        f"{today_text}"
    )


def send_to_telegram(text):
    max_length = 3900
    lines = text.splitlines()

    chunks = []
    current_chunk = ""

    for line in lines:
        next_chunk = f"{current_chunk}\n{line}" if current_chunk else line

        if len(next_chunk) > max_length:
            chunks.append(current_chunk)
            current_chunk = line
        else:
            current_chunk = next_chunk

    if current_chunk:
        chunks.append(current_chunk)

    for chunk in chunks:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

        response = requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "text": chunk,
                "parse_mode": "HTML",
            },
            timeout=20,
        )

        response.raise_for_status()

    print("✅ Telegram message sent")


def read_last_update_id():
    if not STATE_FILE.exists():
        return None

    try:
        return int(STATE_FILE.read_text().strip() or "0")
    except ValueError:
        return 0


def write_last_update_id(update_id):
    STATE_FILE.write_text(str(update_id) + "\n")


def get_telegram_updates(offset):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"

    params = {
        "timeout": 0,
        "allowed_updates": json.dumps(["message"]),
    }

    if offset is not None:
        params["offset"] = offset

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()

    if not data.get("ok"):
        raise RuntimeError(data.get("description", "Telegram getUpdates failed"))

    return data.get("result", [])


def is_check_command(text):
    text = (text or "").strip().lower()

    if text == "check":
        return True

    first_word = text.split()[0] if text else ""

    return first_word == "/check" or first_word.startswith("/check@")


def handle_check_commands():
    last_update_id = read_last_update_id()

    # First run: initialize offset so old Telegram messages do not trigger replies.
    if last_update_id is None:
        updates = get_telegram_updates(offset=-1)
        newest_id = max(
            [update.get("update_id", 0) for update in updates],
            default=0,
        )
        write_last_update_id(newest_id)
        print("✅ Telegram offset initialized. Send 'Check' again after this run.")
        return

    updates = get_telegram_updates(offset=last_update_id + 1)
    newest_id = last_update_id

    for update in updates:
        update_id = update.get("update_id")

        if isinstance(update_id, int):
            newest_id = max(newest_id, update_id)

        message = update.get("message", {})
        chat = message.get("chat", {})
        incoming_chat_id = str(chat.get("id", ""))

        # Only respond to your configured chat/group
        if incoming_chat_id != CHAT_ID:
            continue

        text = message.get("text", "")

        if is_check_command(text):
            print("✅ Received Check command")
            send_to_telegram(build_report())

    if newest_id != last_update_id:
        write_last_update_id(newest_id)


if __name__ == "__main__":
    validate_env()

    if RUN_MODE == "poll_check":
        handle_check_commands()
    else:
        send_to_telegram(build_report())
