import requests
import json
import os
import time
from dotenv import load_dotenv

load_dotenv('/mnt/f/stacks/wow-ah-tracker/.env')

CLIENT_ID = os.getenv('BNET_CLIENT_ID')
CLIENT_SECRET = os.getenv('BNET_CLIENT_SECRET')

PROFESSION_IDS = [164, 171, 165, 197, 333, 202, 773, 755, 185]
# Blacksmithing, Alchemy, Leatherworking, Tailoring, Enchanting, Engineering, Inscription, Jewelcrafting, Cooking

EXPANSION_KEYWORDS = [
    'pandaria', 'legion', 'kul tiran', 'zandalari', 'cataclysm',
    'outland', 'draenor', 'midnight', 'khaz algar', 'shadowlands',
    'northrend', 'dragon isles', 'classic',
]

DECOR_ITEMS_PATH = '/mnt/f/stacks/wow-ah-tracker/decor_items.json'
DECOR_RECIPES_PATH = '/mnt/f/stacks/wow-ah-tracker/decor_recipes.json'
DECOR_REAGENTS_PATH = '/mnt/f/stacks/wow-ah-tracker/decor_reagents.json'


def get_token():
    r = requests.post(
        'https://oauth.battle.net/token',
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={'grant_type': 'client_credentials'},
        timeout=10
    )
    return r.json()['access_token']


def get_tier_recipes(token, prof_id, tier_id):
    r = requests.get(
        f'https://us.api.blizzard.com/data/wow/profession/{prof_id}/skill-tier/{tier_id}',
        headers={'Authorization': f'Bearer {token}'},
        params={'namespace': 'static-us', 'locale': 'en_US'},
        timeout=15
    )
    if r.status_code != 200:
        return []
    recipes = []
    for cat in r.json().get('categories', []):
        for recipe in cat.get('recipes', []):
            recipes.append({'id': recipe['id'], 'name': recipe['name']})
    return recipes


def get_recipe_detail(token, recipe_id):
    r = requests.get(
        f'https://us.api.blizzard.com/data/wow/recipe/{recipe_id}',
        headers={'Authorization': f'Bearer {token}'},
        params={'namespace': 'static-us', 'locale': 'en_US'},
        timeout=10
    )
    if r.status_code != 200:
        return None
    return r.json()


def get_item_media(token, item_id):
    r = requests.get(
        f'https://us.api.blizzard.com/data/wow/media/item/{item_id}',
        headers={'Authorization': f'Bearer {token}'},
        params={'namespace': 'static-us'},
        timeout=10
    )
    if r.status_code != 200:
        return None
    for a in r.json().get('assets', []):
        if a.get('key') == 'icon':
            return a.get('value')
    return None


def main():
    print("Завантажуємо decor_items.json...")
    with open(DECOR_ITEMS_PATH) as f:
        decor_items = json.load(f)

    # Індекс: назва -> item data
    decor_by_name = {item['name'].lower(): item for item in decor_items}
    decor_ids = {item['id'] for item in decor_items if item['id']}

    print(f"Децор предметів: {len(decor_items)}, з ID: {len(decor_ids)}")

    token = get_token()
    req_count = 0

    # Збираємо всі тири для кожної профессії динамічно
    all_tier_recipes = {}
    print("\n--- Збираємо списки рецептів по тирах ---")

    for prof_id in PROFESSION_IDS:
        req_count += 1
        if req_count % 80 == 0:
            token = get_token()
        r = requests.get(
            f'https://us.api.blizzard.com/data/wow/profession/{prof_id}',
            headers={'Authorization': f'Bearer {token}'},
            params={'namespace': 'static-us', 'locale': 'en_US'},
            timeout=10
        )
        prof_data = r.json()
        prof_name = prof_data.get('name', str(prof_id))
        tiers = prof_data.get('skill_tiers', [])
        print(f"  {prof_name}: {len(tiers)} тирів")

        for tier in tiers:
            tier_id = tier['id']
            tier_name = tier['name'].lower()
            # Беремо всі тири (фільтруємо пізніше по назві рецепту)
            req_count += 1
            if req_count % 80 == 0:
                token = get_token()
            recipes = get_tier_recipes(token, prof_id, tier_id)
            for rec in recipes:
                all_tier_recipes[rec['id']] = {
                    'name': rec['name'],
                    'prof_id': prof_id,
                    'prof_name': prof_name,
                    'tier_id': tier_id,
                    'tier_name': tier['name'],
                }
            time.sleep(0.1)

    print(f"Всього рецептів у тирах: {len(all_tier_recipes)}")

    # Фільтруємо рецепти чиї назви збігаються з нашими decor items
    matching = {}
    for recipe_id, rdata in all_tier_recipes.items():
        name_lower = rdata['name'].lower()
        if name_lower in decor_by_name:
            matching[recipe_id] = rdata

    print(f"Збігів з decor items: {len(matching)}")

    # Отримуємо деталі кожного рецепту
    print("\n--- Отримуємо деталі рецептів ---")
    decor_recipes = []
    all_reagents = {}  # item_id -> {name, icon, price}

    for i, (recipe_id, rdata) in enumerate(matching.items()):
        print(f"[{i+1}/{len(matching)}] {rdata['name']}...", end=' ', flush=True)

        req_count += 1
        if req_count % 80 == 0:
            token = get_token()

        detail = get_recipe_detail(token, recipe_id)
        if not detail:
            print("помилка")
            continue

        reagents = []
        for reg in detail.get('reagents', []):
            r_item = reg.get('reagent', {})
            r_id = r_item.get('id')
            r_name = r_item.get('name', '')
            r_qty = reg.get('quantity', 1)
            reagents.append({'id': r_id, 'name': r_name, 'quantity': r_qty})
            if r_id and r_id not in all_reagents:
                all_reagents[r_id] = {'name': r_name, 'icon': None, 'price': 0}

        decor_item = decor_by_name[rdata['name'].lower()]
        decor_recipes.append({
            'item_id': decor_item['id'],
            'name': rdata['name'],
            'recipe_id': recipe_id,
            'expansion': decor_item['expansion'],
            'profession': decor_item['profession'],
            'reagents': reagents,
            'cost': 0,
        })
        print(f"✓ {len(reagents)} реагентів")
        time.sleep(0.12)

    # Іконки для реагентів
    print(f"\n--- Отримуємо іконки для {len(all_reagents)} реагентів ---")
    for i, (r_id, rdata) in enumerate(all_reagents.items()):
        req_count += 1
        if req_count % 80 == 0:
            token = get_token()
        icon = get_item_media(token, r_id)
        all_reagents[r_id]['icon'] = icon or ''
        time.sleep(0.1)

    # Зберігаємо
    with open(DECOR_RECIPES_PATH, 'w', encoding='utf-8') as f:
        json.dump(decor_recipes, f, indent=2, ensure_ascii=False)

    reagents_list = [{'id': k, **v} for k, v in all_reagents.items()]
    reagents_list.sort(key=lambda x: x['name'])
    with open(DECOR_REAGENTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(reagents_list, f, indent=2, ensure_ascii=False)

    not_found = [item['name'] for item in decor_items
                 if item['name'].lower() not in {r['name'].lower() for r in decor_recipes}]

    print(f"\n✅ decor_recipes.json: {len(decor_recipes)} рецептів")
    print(f"✅ decor_reagents.json: {len(reagents_list)} унікальних реагентів")
    if not_found:
        print(f"⚠️  Рецептів не знайдено для ({len(not_found)}):")
        for n in not_found:
            print(f"   - {n}")


if __name__ == '__main__':
    main()
