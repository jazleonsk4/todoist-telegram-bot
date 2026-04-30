import os
import html
import json
from datetime import datetime

import pytz
import requests
from todoist_api_python.api import TodoistAPI


# =========================
# Setup
# =========================

TODOIST_TOKEN = os.environ.get("TODOIST_TOKEN", "").strip()
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
CHAT_ID = os.environ.get("CHAT_ID", "").strip()

# RUN_MODE:
# - send_report = send scheduled Todoist report
# - poll_check  = check Telegram messages for "check"
RUN_MODE = os.environ.get("RUN_MODE", "send_report").strip()

MY_TZ = pytz.timezone("Asia/Kuala_Lumpur")


# =========================
# Basic checks
# =========================

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


# =========================
# Todoist
# =========================

def get_task_due_date(task):
    """
    Returns Todoist task due date as YYYY-MM-DD, or None.
    """
    if not task.due or not task.due.date:
        return None

    return str(task.due.date)[:10]


def get_all_tasks(api):
    """
    Supports both possible SDK return styles:
    - list of tasks
    - pages/lists of tasks
    """
    result = api.get_tasks()

    for item in result:
        if isinstance(item, list):
            for task in item:
                yield task
        else:
            yield item


def get_overdue_and_today_tasks():
    today_str = datetime.now(MY_TZ).date().isoformat()

    overdue_tasks = []
    today_tasks = []

    try:
        api = TodoistAPI(TODOIST_TOKEN)

        for task in get_all_tasks(api):
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


# =========================
# Telegram report formatting
# =========================

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

def telegram_request(method, data=None, params=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/{method}"

    response = requests.post(
        url,
        data=data,
        params=params,
        timeout=20,
    )

    try:
        payload = response.json()
    except Exception:
        payload = {}

    if not response.ok or not payload.get("ok"):
        raise RuntimeError(
            f"Telegram {method} failed: "
            f"HTTP {response.status_code} - {response.text[:1000]}"
        )

    return payload
    
def send_to_telegram(text):
    """
    Telegram message limit is around 4096 characters.
    This splits long reports safely.
    """
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

                telegram_request(
            "sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": chunk,
                "parse_mode": "HTML",
            },
        )

    print("✅ Telegram message sent")


# =========================
# Telegram Check command
# =========================

def is_check_command(text):
    text = (text or "").strip().lower()

    if text == "check":
        return True

    first_word = text.split()[0] if text else ""

    return first_word == "/check" or first_word.startswith("/check@")


def get_telegram_updates(offset=None):
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


def confirm_telegram_updates(last_update_id):
    """
    Tells Telegram these updates are already processed.
    This prevents the bot from replying again to the same 'check'.
    """
    if isinstance(last_update_id, int):
        get_telegram_updates(offset=last_update_id + 1)

def delete_telegram_webhook():
    telegram_request(
        "deleteWebhook",
        data={"drop_pending_updates": "false"},
    )
    print("✅ Telegram webhook removed / polling mode enabled")
    
def handle_check_commands():
    updates = get_telegram_updates()

    if not updates:
        print("No Telegram updates found.")
        return

    newest_update_id = None
    replied = False

    try:
        for update in updates:
            update_id = update.get("update_id")

            if isinstance(update_id, int):
                if newest_update_id is None or update_id > newest_update_id:
                    newest_update_id = update_id

            message = update.get("message", {})
            chat = message.get("chat", {})
            incoming_chat_id = str(chat.get("id", ""))
            text = message.get("text", "")

            print(f"Received message from chat_id={incoming_chat_id}: {text}")

            # Only respond to your own configured Telegram chat
            if incoming_chat_id != CHAT_ID:
                print("Ignored message because CHAT_ID does not match.")
                continue

            if is_check_command(text):
                print("✅ Received Check command")
                send_to_telegram(build_report())
                replied = True
            else:
                print("Ignored message because it is not Check.")

    finally:
        confirm_telegram_updates(newest_update_id)

    if not replied:
        print("No valid Check command found.")


# =========================
# Main
# =========================

if __name__ == "__main__":
    validate_env()

    if RUN_MODE == "poll_check":
        handle_check_commands()
    else:
        send_to_telegram(build_report())
