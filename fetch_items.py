import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('/mnt/f/stacks/wow-ah-tracker/.env')

CLIENT_ID = os.getenv('BNET_CLIENT_ID')
CLIENT_SECRET = os.getenv('BNET_CLIENT_SECRET')

ITEMS = [
    "Elegant Artisan's Alchemy Coveralls",
    "Elegant Artisan's Cooking Hat",
    "Elegant Artisan's Enchanting Hat",
    "Elegant Artisan's Herbalism Hat",
    "Elegant Artisan's Tailoring Robe",
    "Elegant Artisan's Fishing Hat",
    "Eversong Hunter's Headcover",
    "Improved Right-Handed Magnifying Glass",
    "Junker's Big Ol' Bag",
    "Sin'dorei Alchemist's Hat",
    "Sin'dorei Alchemist's Mixing Rod",
    "Sin'dorei Angler's Rod",
    "Sin'dorei Enchanter's Crystal",
    "Sin'dorei Forgemaster's Cover",
    "Sin'dorei Gilded Hardhat",
    "Sin'dorei Headlamp",
    "Sin'dorei Herbalist's Backpack",
    "Sin'dorei Hunter's Pack",
    "Sin'dorei Jeweler's Cover",
    "Sin'dorei Jeweler's Loupes",
    "Sin'dorei Leathershaper's Smock",
    "Sin'dorei Rolling Pin",
    "Sin'dorei Scribe's Spectacles",
    "Sin'dorei Clampers",
    "Sin'dorei Engineer's Gloves",
    "Sin'dorei Quill",
    "Sin'dorei Snippers",
    "Sun-Blessed Pickaxe",
    "Sun-Blessed Sickle",
    "Sun-Blessed Blacksmith's Hammer",
    "Sun-Blessed Leatherworker's Knife",
    "Sun-Blessed Skinning Knife",
    "Sun-Blessed Blacksmith's Toolbox",
    "Sun-Blessed Leatherworker's Toolset",
    "Sun-Blessed Needle Set",
]

def get_token():
    r = requests.post(
        'https://oauth.battle.net/token',
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={'grant_type': 'client_credentials'}
    )
    return r.json()['access_token']

def search_item(token, name):
    encoded = requests.utils.quote(name)
    r = requests.get(
        f'https://us.api.blizzard.com/data/wow/search/item',
        headers={'Authorization': f'Bearer {token}'},
        params={
            'namespace': 'static-us',
            'locale': 'en_US',
            'name.en_US': name,
            '_pageSize': 10
        }
    )
    results = r.json().get('results', [])
    # Шукаємо точний збіг назви і profession gear
    for res in results:
        d = res['data']
        if (d['name']['en_US'] == name and 
            d.get('item_class', {}).get('id') == 19):
            return d['id'], d['level']
    # Якщо не знайшли profession gear - беремо перший точний збіг
    for res in results:
        d = res['data']
        if d['name']['en_US'] == name:
            return d['id'], d['level']
    return None, None

def get_icon(token, item_id):
    r = requests.get(
        f'https://us.api.blizzard.com/data/wow/media/item/{item_id}',
        headers={'Authorization': f'Bearer {token}'},
        params={'namespace': 'static-us'}
    )
    assets = r.json().get('assets', [])
    for asset in assets:
        if asset['key'] == 'icon':
            return asset['value']
    return None

print("Отримуємо токен...")
token = get_token()

results = []
print(f"\nШукаємо {len(ITEMS)} предметів...\n")

for name in ITEMS:
    item_id, ilvl = search_item(token, name)
    if item_id:
        icon = get_icon(token, item_id)
        results.append({
            'name': name,
            'id': item_id,
            'base_ilvl': ilvl,
            'icon': icon
        })
        print(f"✅ {name}: ID={item_id}, ilvl={ilvl}")
    else:
        print(f"❌ НЕ ЗНАЙДЕНО: {name}")
        results.append({
            'name': name,
            'id': None,
            'base_ilvl': None,
            'icon': None
        })

# Зберігаємо
with open('/mnt/f/stacks/wow-ah-tracker/items.json', 'w') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\n✅ Збережено в items.json")
print(f"Знайдено: {sum(1 for r in results if r['id'])} з {len(ITEMS)}")
