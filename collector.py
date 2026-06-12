import requests
import json
import sqlite3
import os
import re
import time
from datetime import datetime, timezone
from dotenv import load_dotenv
from notifier import check_and_notify

load_dotenv('/mnt/f/stacks/wow-ah-tracker/.env')

CLIENT_ID = os.getenv('BNET_CLIENT_ID')
CLIENT_SECRET = os.getenv('BNET_CLIENT_SECRET')

DB_PATH = '/mnt/f/stacks/wow-ah-tracker/ah_data.db'
ITEMS_PATH = '/mnt/f/stacks/wow-ah-tracker/items.json'
DECOR_ITEMS_PATH = '/mnt/f/stacks/wow-ah-tracker/decor_items.json'
DECOR_REAGENTS_PATH = '/mnt/f/stacks/wow-ah-tracker/decor_reagents.json'
TOOLS_REAGENTS_PATH = '/mnt/f/stacks/wow-ah-tracker/tools_reagents.json'

Q5_BONUS_ID = 12502

LUMBER_WORDS = re.compile(r'\b(lumber|log|logs|plank|planks|timber|vellum)\b', re.IGNORECASE)

def get_token():
    r = requests.post(
        'https://oauth.battle.net/token',
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={'grant_type': 'client_credentials'},
        timeout=10
    )
    return r.json()['access_token']

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS realms (
        id INTEGER PRIMARY KEY,
        region TEXT,
        name TEXT,
        total_auctions INTEGER DEFAULT 0,
        last_updated TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        realm_id INTEGER,
        item_id INTEGER,
        min_price INTEGER,
        quantity INTEGER,
        num_auctions INTEGER,
        timestamp TEXT
    )''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_prices_realm_item ON prices(realm_id, item_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_prices_timestamp ON prices(timestamp)')
    c.execute('''CREATE TABLE IF NOT EXISTS commodity_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        region TEXT,
        item_id INTEGER,
        min_price INTEGER,
        quantity INTEGER,
        timestamp TEXT
    )''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_commodity_region_item ON commodity_prices(region, item_id)')
    conn.commit()
    conn.close()

def get_realms(token, region):
    namespace = f'dynamic-{region}'
    base_url = f'https://{region}.api.blizzard.com'
    r = requests.get(
        f'{base_url}/data/wow/connected-realm/index',
        headers={'Authorization': f'Bearer {token}'},
        params={'namespace': namespace},
        timeout=10
    )
    realm_links = r.json().get('connected_realms', [])
    realms = []
    for link in realm_links:
        href = link['href']
        realm_id = int(href.split('/connected-realm/')[1].split('?')[0])
        r2 = requests.get(
            href,
            headers={'Authorization': f'Bearer {token}'},
            timeout=10
        )
        data = r2.json()
        realm_list = data.get('realms', [])
        if realm_list:
            name_data = realm_list[0].get('name', {})
            if isinstance(name_data, dict):
                name = name_data.get('en_US', str(realm_id))
            else:
                name = str(name_data)
        else:
            name = str(realm_id)
        pop = data.get('population', {})
        tier = pop.get('name', {}).get('en_US', '') if isinstance(pop, dict) else ''
        realms.append({'id': realm_id, 'name': name, 'region': region, 'tier': tier})
        time.sleep(0.1)
    return realms

def fetch_auctions(token, region, realm_id, q5_item_ids, any_item_ids):
    namespace = f'dynamic-{region}'
    base_url = f'https://{region}.api.blizzard.com'
    try:
        r = requests.get(
            f'{base_url}/data/wow/connected-realm/{realm_id}/auctions',
            headers={'Authorization': f'Bearer {token}'},
            params={'namespace': namespace},
            timeout=30
        )
        if r.status_code != 200:
            return None, 0
        data = r.json()
        auctions = data.get('auctions', [])
        total = len(auctions)
        results = {}
        all_tracked = q5_item_ids | any_item_ids
        for a in auctions:
            item = a.get('item', {})
            item_id = item.get('id')
            if item_id not in all_tracked:
                continue
            buyout = a.get('buyout', 0)
            if buyout == 0:
                continue
            # Q5 фільтр тільки для profession tools
            if item_id in q5_item_ids:
                bonus_lists = item.get('bonus_lists', [])
                if Q5_BONUS_ID not in bonus_lists:
                    continue
            if item_id not in results:
                results[item_id] = {'prices': [], 'quantity': 0}
            results[item_id]['prices'].append(buyout)
            results[item_id]['quantity'] += a.get('quantity', 1)
        return results, total
    except Exception as e:
        print(f"  Помилка: {e}")
        return None, 0

def save_results(realm_id, region, realm_name, results, total_auctions, timestamp, tier=''):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO realms (id, region, name, total_auctions, last_updated, tier)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (realm_id, region, str(realm_name), total_auctions, timestamp, tier))
    for item_id, data in results.items():
        prices = sorted(data['prices'])
        min_price = prices[0] if prices else 0
        c.execute('''INSERT INTO prices (realm_id, item_id, min_price, quantity, num_auctions, timestamp)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (realm_id, item_id, min_price, data['quantity'], len(prices), timestamp))
    conn.commit()
    conn.close()

def fetch_commodities(token, region, item_ids):
    """Один запит до регіонального commodity ринку для всіх реагентів."""
    base_url = f'https://{region}.api.blizzard.com'
    namespace = f'dynamic-{region}'
    try:
        r = requests.get(
            f'{base_url}/data/wow/auctions/commodities',
            headers={'Authorization': f'Bearer {token}'},
            params={'namespace': namespace},
            timeout=60
        )
        if r.status_code != 200:
            print(f"  Commodities {region.upper()} помилка: {r.status_code}")
            return {}
        auctions = r.json().get('auctions', [])
        results = {}
        for a in auctions:
            item_id = a['item']['id']
            if item_id not in item_ids:
                continue
            price = a.get('unit_price', 0)
            if price == 0:
                continue
            qty = a.get('quantity', 1)
            if item_id not in results:
                results[item_id] = {'min_price': price, 'quantity': 0}
            elif price < results[item_id]['min_price']:
                results[item_id]['min_price'] = price
            results[item_id]['quantity'] += qty
        return results
    except Exception as e:
        print(f"  Commodities {region.upper()} помилка: {e}")
        return {}

def save_commodities(region, results, timestamp):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for item_id, data in results.items():
        c.execute('''INSERT INTO commodity_prices (region, item_id, min_price, quantity, timestamp)
                     VALUES (?, ?, ?, ?, ?)''',
                  (region, item_id, data['min_price'], data['quantity'], timestamp))
    conn.commit()
    conn.close()

def main():
    print(f"=== Collector старт: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

    with open(ITEMS_PATH) as f:
        items = json.load(f)
    q5_item_ids = set(item['id'] for item in items if item['id'])

    with open(DECOR_ITEMS_PATH) as f:
        decor_items = json.load(f)
    decor_item_ids = set(item['id'] for item in decor_items if item['id'])

    with open(DECOR_REAGENTS_PATH) as f:
        reagents = json.load(f)
    reagent_ids = set(
        r['id'] for r in reagents
        if r['id'] and not LUMBER_WORDS.search(r['name'])
    )

    with open(TOOLS_REAGENTS_PATH) as f:
        tools_reagents = json.load(f)
    tools_reagent_ids = set(r['id'] for r in tools_reagents if r['id'])

    any_item_ids = decor_item_ids | reagent_ids | tools_reagent_ids
    item_ids = q5_item_ids  # для сумісності з notifier
    print(f"Prof tools (Q5): {len(q5_item_ids)}, Decor: {len(decor_item_ids)}, Decor reagents: {len(reagent_ids)}, Tools reagents: {len(tools_reagent_ids)}")

    init_db()
    token = get_token()
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    total_realms = 0
    total_found = 0

    for region in ['eu', 'us']:
        print(f"\n--- Отримуємо реалми {region.upper()} ---")
        realms = get_realms(token, region)
        print(f"Знайдено реалмів: {len(realms)}")

        for i, realm in enumerate(realms):
            print(f"[{i+1}/{len(realms)}] {region.upper()} {realm['name']} (id={realm['id']})...", end=' ', flush=True)

            if i > 0 and i % 50 == 0:
                token = get_token()

            results, total = fetch_auctions(token, region, realm['id'], q5_item_ids, any_item_ids)

            if results is None:
                print("пропущено")
                continue

            found = sum(len(v['prices']) for v in results.values())
            total_found += found
            save_results(realm['id'], region, realm['name'], results, total, timestamp, realm.get('tier', ''))
            print(f"АГ={total}, Q5 лотів={found}")
            total_realms += 1
            time.sleep(0.2)

        # Commodities для цього регіону — один запит після всіх реалмів
        print(f"\n--- Commodities {region.upper()} ---")
        commodity_ids = reagent_ids | tools_reagent_ids
        commodity_results = fetch_commodities(token, region, commodity_ids)
        save_commodities(region, commodity_results, timestamp)
        print(f"Знайдено commodity items: {len(commodity_results)} / {len(commodity_ids)}")

    print(f"\n=== Готово! Реалмів: {total_realms}, Q5 лотів знайдено: {total_found} ===")

    # Telegram алерти
    with open('/mnt/f/stacks/wow-ah-tracker/settings.json') as f:
        settings = json.load(f)
    with open('/mnt/f/stacks/wow-ah-tracker/recipes.json') as f:
        recipes = json.load(f)

    from app import calc_min_prices
    profit_margin = settings.get('profit_margin', 1000)
    threshold = settings.get('alert_threshold', 5)
    min_prices = calc_min_prices(recipes, profit_margin)
    check_and_notify(min_prices, item_ids, threshold, timestamp)

if __name__ == '__main__':
    main()
