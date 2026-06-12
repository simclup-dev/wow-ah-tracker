import os
import json
import sqlite3
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv('/mnt/f/stacks/wow-ah-tracker/.env')

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
DB_PATH = '/mnt/f/stacks/wow-ah-tracker/ah_data.db'
STATE_PATH = '/mnt/f/stacks/wow-ah-tracker/notifier_state.json'


def send_telegram(text):
    if not BOT_TOKEN or not CHAT_ID:
        return
    try:
        requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
            json={'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'HTML'},
            timeout=10
        )
    except Exception as e:
        print(f"Telegram error: {e}")


def load_state():
    """Завантажує останній відправлений стан per realm."""
    try:
        with open(STATE_PATH) as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(state):
    with open(STATE_PATH, 'w') as f:
        json.dump(state, f, indent=2)


def get_passing_count(conn, realm_id, min_prices, item_ids, timestamp):
    rows = conn.execute(
        'SELECT item_id, min_price FROM prices WHERE realm_id=? AND timestamp=?',
        (realm_id, timestamp)
    ).fetchall()
    price_map = {row[0]: row[1] for row in rows}
    passing = 0
    for iid in item_ids:
        mp = min_prices.get(iid, {})
        row_price = price_map.get(iid)
        if row_price and row_price // 10000 >= mp.get('min_price', 0):
            passing += 1
    return passing


def check_and_notify(min_prices, item_ids, threshold, current_timestamp):
    conn = sqlite3.connect(DB_PATH)
    realms = conn.execute('SELECT id, name, region FROM realms').fetchall()

    # Завантажуємо останній стан (що вже було відправлено)
    state = load_state()
    new_state = dict(state)

    alerts = []

    for realm_id, realm_name, region in realms:
        current = get_passing_count(conn, realm_id, min_prices, item_ids, current_timestamp)
        if current == 0:
            continue  # реалм без даних — пропускаємо

        key = f"{region}_{realm_id}"
        last_alerted = state.get(key)  # None якщо ще не алертили

        if last_alerted is None:
            # Перший запуск — запам'ятовуємо, не шлемо
            new_state[key] = current
            continue

        diff = current - last_alerted

        if abs(diff) >= threshold:
            direction = "⬆️ зріс" if diff > 0 else "⬇️ впав"
            emoji = "🟢" if diff > 0 else "🔴"
            alerts.append(
                f"{emoji} <b>{realm_name} {region.upper()}</b>\n"
                f"   Passing: було {last_alerted} → стало {current} ({direction} на {abs(diff)})"
            )
            new_state[key] = current  # оновлюємо базову точку тільки якщо відправили алерт

    conn.close()
    save_state(new_state)

    if alerts:
        header = f"🎮 <b>WoW AH Alert</b> | {datetime.now().strftime('%H:%M')}\n\n"
        batch = header
        for alert in alerts:
            if len(batch) + len(alert) + 2 > 4000:
                send_telegram(batch)
                batch = alert + "\n"
            else:
                batch += alert + "\n"
        if batch.strip():
            send_telegram(batch)
        print(f"Відправлено {len(alerts)} алертів")
    else:
        print("Алертів немає")
