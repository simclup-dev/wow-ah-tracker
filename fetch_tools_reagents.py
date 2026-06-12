"""
Збирає item ID і іконки для всіх tools reagents.
Також оновлює recipes.json для Elegant Artisan's items (нові Midnight рецепти).
"""
import requests
import json
import os
import time
from dotenv import load_dotenv

load_dotenv('/mnt/f/stacks/wow-ah-tracker/.env')
CLIENT_ID = os.getenv('BNET_CLIENT_ID')
CLIENT_SECRET = os.getenv('BNET_CLIENT_SECRET')

RECIPES_PATH = '/mnt/f/stacks/wow-ah-tracker/recipes.json'
TOOLS_REAGENTS_PATH = '/mnt/f/stacks/wow-ah-tracker/tools_reagents.json'

# Повний mapping: key в recipes.json → {rank1_id, rank2_id, name}
TOOLS_REAGENT_MAP = {
    'hide':    {'rank1': None,   'rank2': 238529, 'name': 'Majestic Hide'},
    'claw':    {'rank1': None,   'rank2': 238528, 'name': 'Majestic Claw'},
    'fin':     {'rank1': None,   'rank2': 238530, 'name': 'Majestic Fin'},
    'alloy':   {'rank1': 238204, 'rank2': 238205, 'name': 'Sterling Alloy'},
    'gemdust': {'rank1': 242620, 'rank2': 242621, 'name': 'Glimmering Gemdust'},
    'lens':    {'rank1': 240972, 'rank2': 240973, 'name': "Sin'dorei Lens"},
    'crystal': {'rank1': 243605, 'rank2': 243606, 'name': 'Dawn Crystal'},
    'mun_ink': {'rank1': 245801, 'rank2': 245802, 'name': 'Munsell Ink'},
    'sie_ink': {'rank1': 245805, 'rank2': 245806, 'name': 'Sienna Ink'},
    'azeroot': {'rank1': 236774, 'rank2': 236775, 'name': 'Azeroot'},
    'lotus':   {'rank1': None,   'rank2': 236780, 'name': 'Nocturnal Lotus'},
    # LW hunter items (leather*100 + scale*100)
    'leather': {'rank1': None,   'rank2': 251665, 'name': 'Silverleaf Thread'},
    'scale':   {'rank1': None,   'rank2': 236949, 'name': 'Mote of Light'},
    # Tailoring - OLD Dragonflight bolts (formulas потребують оновлення)
    # Нові Midnight рецепти для Elegant Artisan's використовують Embroidery Floss + Motes
    'arc_bolt':  {'rank1': None, 'rank2': None, 'name': 'Arcane Bolt (outdated)'},
    'sun_bolt':  {'rank1': None, 'rank2': None, 'name': 'Sun Bolt (outdated)'},
    # flora - не використовується в жодній формулі
    'flora':   {'rank1': None,   'rank2': None, 'name': 'Flora (unused)'},
    # Нові Midnight tailoring реагенти
    'embroidery_floss':        {'rank1': None, 'rank2': 251691, 'name': 'Embroidery Floss'},
    'mote_light':              {'rank1': None, 'rank2': 236949, 'name': 'Mote of Light'},
    'mote_primal_energy':      {'rank1': None, 'rank2': 236950, 'name': 'Mote of Primal Energy'},
    'mote_wild_magic':         {'rank1': None, 'rank2': 236951, 'name': 'Mote of Wild Magic'},
    'mote_void':               {'rank1': None, 'rank2': 236952, 'name': 'Mote of Pure Void'},
}


def get_token():
    r = requests.post('https://oauth.battle.net/token',
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={'grant_type': 'client_credentials'}, timeout=10)
    return r.json()['access_token']


def get_item_media(token, item_id):
    r = requests.get(
        f'https://us.api.blizzard.com/data/wow/media/item/{item_id}',
        headers={'Authorization': f'Bearer {token}'},
        params={'namespace': 'static-us'}, timeout=10)
    for a in r.json().get('assets', []):
        if a.get('key') == 'icon':
            return a.get('value')
    return None


def main():
    print("Отримуємо токен...")
    token = get_token()

    result = []
    for key, data in TOOLS_REAGENT_MAP.items():
        for rank in ['rank1', 'rank2']:
            item_id = data.get(rank)
            if not item_id:
                continue
            print(f"  {key} {rank} (id={item_id}) {data['name']}...", end=' ', flush=True)
            icon = get_item_media(token, item_id)
            result.append({
                'key': key,
                'rank': rank,
                'id': item_id,
                'name': data['name'],
                'icon': icon or '',
            })
            print('✓')
            time.sleep(0.12)

    with open(TOOLS_REAGENTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n✅ tools_reagents.json: {len(result)} реагентів")

    # Попередження про застарілі формули
    print("\n⚠️  УВАГА: Рецепти Elegant Artisan's змінились в Midnight!")
    print("   Нові рецепти використовують:")
    print("   - Embroidery Floss (251691) x2")
    print("   - Mote of Primal Energy / Mote of Light / Mote of Wild Magic / Mote of Pure Void x5")
    print("   Оновіть формули в recipes.json для arc_bolt/sun_bolt items")


if __name__ == '__main__':
    main()
