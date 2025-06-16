import os
import time
import threading
import requests
from datetime import datetime, timedelta

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

reminders = []

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

def scheduler_loop():
    while True:
        now = datetime.now()
        for r in reminders[:]:
            if now >= r["time"]:
                send_message(r["text"])
                reminders.remove(r)
        time.sleep(30)

if __name__ == "__main__":
    # Получим chat_id заранее
    if not CHAT_ID:
        updates = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates").json()
        if updates["result"]:
            chat = updates["result"][-1]["message"]["chat"]["id"]
            os.environ["CHAT_ID"] = str(chat)
            send_message("✅ Бот на Render: связь установлена!")
    threading.Thread(target=scheduler_loop, daemon=True).start()
    print("Сервис запущен.")
    # Базовая обработка команд из Telegram
    offset = None
    while True:
        params = {"timeout": 30}
        if offset: params["offset"] = offset
        resp = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates", params=params).json()
        for u in resp["result"]:
            offset = u["update_id"] + 1
            msg = u["message"]["text"]
            if msg.lower().startswith("remind "):
                parts = msg[7:].split(";",1)
                dt = datetime.strptime(parts[0].strip(), "%Y-%m-%d %H:%M")
                reminders.append({"time": dt, "text": parts[1].strip()})
                send_message(f"🔔 Напоминание установлено на {dt.strftime('%Y-%m-%d %H:%M')}")
