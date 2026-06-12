from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3, json, os, math
from datetime import datetime, timezone

app = Flask(__name__, static_folder='static')
CORS(app)

import re

DB_PATH = '/mnt/f/stacks/wow-ah-tracker/ah_data.db'
ITEMS_PATH = '/mnt/f/stacks/wow-ah-tracker/items.json'
RECIPES_PATH = '/mnt/f/stacks/wow-ah-tracker/recipes.json'
SETTINGS_PATH = '/mnt/f/stacks/wow-ah-tracker/settings.json'
DECOR_ITEMS_PATH = '/mnt/f/stacks/wow-ah-tracker/decor_items.json'
DECOR_RECIPES_PATH = '/mnt/f/stacks/wow-ah-tracker/decor_recipes.json'
DECOR_REAGENTS_PATH = '/mnt/f/stacks/wow-ah-tracker/decor_reagents.json'
TOOLS_REAGENTS_PATH = '/mnt/f/stacks/wow-ah-tracker/tools_reagents.json'

LUMBER_WORDS = re.compile(r'\b(lumber|log|logs|plank|planks|timber|vellum)\b', re.IGNORECASE)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def load_json(path, default=None):
    try:
        with open(path) as f: return json.load(f)
    except: return default or {}

def save_json(path, data):
    with open(path, 'w') as f: json.dump(data, f, indent=2, ensure_ascii=False)

ITEM_QUANTITY = {238017:2, 238016:2, 238018:2, 244708:2, 244714:2, 245776:2}

def calc_min_prices(recipes, profit_margin=1000):
    r = recipes.get('reagents', {})
    prices = {}
    for item in recipes.get('items', []):
        try:
            cost = eval(item['formula'], {"__builtins__": {}}, {
                'hide': r.get('hide',{}).get('rank2',0),
                'fin': r.get('fin',{}).get('rank2',0),
                'claw': r.get('claw',{}).get('rank2',0),
                'alloy': r.get('alloy',{}).get('rank2',0),
                'gemdust': r.get('gemdust',{}).get('rank2',0),
                'gemdust_r1': r.get('gemdust',{}).get('rank1',0),
                'lens': r.get('lens',{}).get('rank2',0),
                'lens_r1': r.get('lens',{}).get('rank1',0),
                'crystal': r.get('crystal',{}).get('rank2',0),
                'lotus': r.get('lotus',{}).get('rank2',0),
                'azeroot': r.get('azeroot',{}).get('rank2',0),
                'mun_ink': r.get('mun_ink',{}).get('rank2',0),
                'sie_ink': r.get('sie_ink',{}).get('rank2',0),
                'leather': r.get('leather',{}).get('rank2',0),
                'scale': r.get('scale',{}).get('rank2',0),
                'arc_bolt': r.get('arc_bolt',{}).get('rank2',0),
                'arc_bolt_r1': r.get('arc_bolt',{}).get('rank1',0),
                'sun_bolt': r.get('sun_bolt',{}).get('rank2',0),
                'sun_bolt_r1': r.get('sun_bolt',{}).get('rank1',0),
                'flora': r.get('flora',{}).get('rank2',0),
            })
            prices[item['id']] = {'cost': round(cost), 'min_price': round(cost) + profit_margin}
        except: prices[item['id']] = {'cost': 0, 'min_price': profit_margin}
    return prices

@app.route('/')
def index(): return send_from_directory('static', 'index.html')

@app.route('/api/realms')
def get_realms():
    region = request.args.get('region', 'eu').lower()
    conn = get_db()
    realms = conn.execute('SELECT * FROM realms WHERE region=? ORDER BY total_auctions DESC', (region,)).fetchall()
    conn.close()
    recipes = load_json(RECIPES_PATH)
    items_data = load_json(ITEMS_PATH, [])
    settings = load_json(SETTINGS_PATH, {'hidden_realms': []})
    profit_margin = settings.get('profit_margin', 1000)
    min_prices = calc_min_prices(recipes, profit_margin)
    item_ids = [i['id'] for i in items_data if i['id']]
    hidden = settings.get('hidden_realms', [])
    conn = get_db()
    result = []
    for realm in realms:
        rid = realm['id']
        if rid in hidden: continue
        latest_ts = conn.execute('SELECT MAX(timestamp) FROM prices WHERE realm_id=?', (rid,)).fetchone()[0]
        price_map = {}
        if latest_ts:
            rows = conn.execute('SELECT item_id, min_price, num_auctions FROM prices WHERE realm_id=? AND timestamp=?', (rid, latest_ts)).fetchall()
            price_map = {row['item_id']: row for row in rows}
        passing = 0; total_profit = 0
        for iid in item_ids:
            mp = min_prices.get(iid, {})
            row = price_map.get(iid)
            if row and row['min_price'] // 10000 >= mp.get('min_price', 0):
                qty = ITEM_QUANTITY.get(iid, 1)
                total_profit += (row['min_price'] // 10000 - mp.get('cost', 0)) * qty
                passing += 1
        result.append({'id': rid, 'name': realm['name'], 'region': realm['region'], 'total_auctions': realm['total_auctions'], 'last_updated': realm['last_updated'], 'passing': passing, 'total': len(item_ids), 'total_profit': total_profit, 'tier': realm['tier'] if realm['tier'] else ''})
    conn.close()
    result.sort(key=lambda x: x['total_auctions'], reverse=True)
    return jsonify(result)

@app.route('/api/realm/<int:realm_id>')
def get_realm_detail(realm_id):
    recipes = load_json(RECIPES_PATH)
    items_data = load_json(ITEMS_PATH, [])
    settings = load_json(SETTINGS_PATH, {})
    profit_margin = settings.get('profit_margin', 1000)
    min_prices = calc_min_prices(recipes, profit_margin)
    conn = get_db()
    latest_ts = conn.execute('SELECT MAX(timestamp) FROM prices WHERE realm_id=?', (realm_id,)).fetchone()[0]
    price_map = {}
    if latest_ts:
        rows = conn.execute('SELECT item_id, min_price, num_auctions FROM prices WHERE realm_id=? AND timestamp=?', (realm_id, latest_ts)).fetchall()
        price_map = {row['item_id']: row for row in rows}
    conn.close()
    result = []
    for item in items_data:
        if not item['id']: continue
        iid = item['id']
        mp = min_prices.get(iid, {})
        row = price_map.get(iid)
        ah_price = row['min_price'] // 10000 if row else None
        qty = ITEM_QUANTITY.get(iid, 1)
        profit = (ah_price - mp.get('cost', 0)) * qty if ah_price else None
        result.append({'id': iid, 'name': item['name'], 'icon': item['icon'], 'ah_price': ah_price, 'my_min': mp.get('min_price', 0), 'cost': mp.get('cost', 0), 'profit': profit, 'num_auctions': row['num_auctions'] if row else 0, 'passing': ah_price is not None and ah_price >= mp.get('min_price', 0), 'quantity': qty})
    return jsonify({'items': result, 'last_updated': latest_ts})

@app.route('/api/recipes', methods=['GET','POST'])
def recipes():
    if request.method == 'POST':
        save_json(RECIPES_PATH, request.json)
        return jsonify({'ok': True})
    return jsonify(load_json(RECIPES_PATH))

@app.route('/api/settings', methods=['GET','POST'])
def settings():
    if request.method == 'POST':
        save_json(SETTINGS_PATH, request.json)
        return jsonify({'ok': True})
    return jsonify(load_json(SETTINGS_PATH, {'hidden_realms': [], 'alert_threshold': 5}))

@app.route('/api/realms/all')
def all_realms():
    conn = get_db()
    realms = conn.execute('SELECT id, name, region, total_auctions FROM realms ORDER BY total_auctions DESC').fetchall()
    conn.close()
    return jsonify([dict(r) for r in realms])


@app.route('/api/min_prices')
def get_min_prices():
    region = request.args.get('region', '').lower()
    recipes = load_json(RECIPES_PATH)
    settings = load_json(SETTINGS_PATH, {})
    profit_margin = settings.get('profit_margin', 1000)

    if region in ('eu', 'us'):
        # Рахуємо з commodity_prices для регіону
        tools_reagents = load_json(TOOLS_REAGENTS_PATH, [])
        ids = [r['id'] for r in tools_reagents if r.get('id')]
        if ids:
            conn = get_db()
            ph = ','.join('?' * len(ids))
            rows = conn.execute(
                f'''SELECT item_id, MIN(min_price) FROM commodity_prices
                    WHERE region=? AND item_id IN ({ph})
                    AND timestamp >= datetime('now', '-2 hours')
                    GROUP BY item_id''',
                [region] + ids
            ).fetchall()
            conn.close()
            commodity = {row[0]: max(1, math.ceil(row[1] / 10000)) for row in rows if row[1]}
            # Будуємо reagents dict: commodity для major tradeable items (>= 10g),
            # для решти (arc_bolt, sun_bolt, leather, scale тощо) — manual prices
            manual = recipes.get('reagents', {})
            r = {}
            for tr in tools_reagents:
                key = tr['key']
                rank = tr['rank']
                commodity_price = commodity.get(tr['id'], 0)
                manual_price = manual.get(key, {}).get(rank, 0)
                # Використовуємо commodity якщо вона значима (>=10g) І не менше 50% від manual
                # (захист від занижених цін типу azeroot 38g vs manual 250g)
                if manual_price > 0 and commodity_price < manual_price * 0.5:
                    price = manual_price
                elif commodity_price >= 10:
                    price = commodity_price
                else:
                    price = manual_price
                if key not in r:
                    r[key] = {'rank1': 0, 'rank2': 0}
                r[key][rank] = price
            # Fallback: ключі з recipes.json яких немає в tools_reagents (arc_bolt, sun_bolt...)
            for key, ranks in manual.items():
                if key not in r:
                    r[key] = ranks
            regional_recipes = {**recipes, 'reagents': r}
            min_prices = calc_min_prices(regional_recipes, profit_margin)
        else:
            min_prices = calc_min_prices(recipes, profit_margin)
    else:
        min_prices = calc_min_prices(recipes, profit_margin)

    return jsonify({str(k): v['min_price'] for k, v in min_prices.items()})

def calc_decor_costs(region, conn=None):
    """Розраховує собівартість кожного decor item для регіону."""
    decor_recipes = load_json(DECOR_RECIPES_PATH, [])
    decor_reagents = load_json(DECOR_REAGENTS_PATH, [])
    settings = load_json(SETTINGS_PATH, {})

    reagent_overrides = settings.get('reagent_prices', {}).get(region, {})
    close_conn = conn is None
    if conn is None:
        conn = get_db()

    # Batch запит з commodity_prices (регіональний ринок сировини)
    non_lumber_ids = [r['id'] for r in decor_reagents if r['id'] and not LUMBER_WORDS.search(r['name'])]
    ah_prices = {}
    if non_lumber_ids:
        placeholders = ','.join('?' * len(non_lumber_ids))
        rows = conn.execute(
            f'''SELECT item_id, MIN(min_price) FROM commodity_prices
                WHERE region=? AND item_id IN ({placeholders})
                AND timestamp >= datetime('now', '-2 hours')
                GROUP BY item_id''',
            [region] + non_lumber_ids
        ).fetchall()
        ah_prices = {row[0]: max(1, math.ceil(row[1] / 10000)) for row in rows if row[1]}
        # Fallback: предмети що не є commodities — шукаємо в per-realm prices
        missing_ids = [iid for iid in non_lumber_ids if iid not in ah_prices]
        if missing_ids:
            ph2 = ','.join('?' * len(missing_ids))
            rows2 = conn.execute(
                f'''SELECT p.item_id, MIN(p.min_price) FROM prices p
                    JOIN realms r ON r.id = p.realm_id
                    WHERE r.region=? AND p.item_id IN ({ph2})
                    AND p.timestamp >= datetime('now', '-2 hours')
                    GROUP BY p.item_id''',
                [region] + missing_ids
            ).fetchall()
            for row in rows2:
                if row[1]:
                    ah_prices[row[0]] = max(1, math.ceil(row[1] / 10000))

    reagent_prices = {}
    for r in decor_reagents:
        rid = r['id']
        if LUMBER_WORDS.search(r['name']):
            reagent_prices[rid] = 200
        elif str(rid) in reagent_overrides:
            reagent_prices[rid] = reagent_overrides[str(rid)]
        else:
            reagent_prices[rid] = ah_prices.get(rid, 0)

    if close_conn:
        conn.close()

    costs = {}
    for recipe in decor_recipes:
        iid = recipe['item_id']
        total = 0
        known = True
        for reg in recipe['reagents']:
            p = reagent_prices.get(reg['id'], 0)
            if p == 0:
                known = False
            total += p * reg['quantity']
        costs[iid] = {'cost': round(total), 'cost_known': known}
    return costs


@app.route('/api/decor')
def get_decor_realms():
    region = request.args.get('region', 'eu').lower()
    expansion_filter = request.args.get('expansion', '').lower()
    profession_filter = request.args.get('profession', '').lower()
    conn = get_db()
    realms = conn.execute(
        'SELECT * FROM realms WHERE region=? ORDER BY total_auctions DESC', (region,)
    ).fetchall()

    settings = load_json(SETTINGS_PATH, {'hidden_realms': []})
    hidden = settings.get('hidden_realms', [])
    decor_margin = settings.get('decor_profit_margin', 0)

    decor_items_data = load_json(DECOR_ITEMS_PATH, [])
    # Фільтруємо предмети по expansion/profession
    if expansion_filter:
        decor_items_data = [i for i in decor_items_data if i.get('expansion', '').lower() == expansion_filter]
    if profession_filter:
        decor_items_data = [i for i in decor_items_data if i.get('profession', '').lower() == profession_filter]
    decor_item_ids = [i['id'] for i in decor_items_data if i['id']]
    decor_costs = calc_decor_costs(region, conn)

    visible_realm_ids = [realm['id'] for realm in realms if realm['id'] not in hidden]

    # Batch: останній timestamp для кожного реалму
    ph = ','.join('?' * len(visible_realm_ids))
    latest_ts_map = {}
    if visible_realm_ids:
        rows = conn.execute(
            f'SELECT realm_id, MAX(timestamp) FROM prices WHERE realm_id IN ({ph}) GROUP BY realm_id',
            visible_realm_ids
        ).fetchall()
        latest_ts_map = {row[0]: row[1] for row in rows}

    # Batch: всі ціни decor items для всіх реалмів одним запитом
    all_prices = {}
    if visible_realm_ids and decor_item_ids:
        item_ph = ','.join('?' * len(decor_item_ids))
        rows = conn.execute(
            f'''SELECT p.realm_id, p.item_id, p.min_price, p.num_auctions
                FROM prices p
                WHERE p.realm_id IN ({ph})
                AND p.item_id IN ({item_ph})
                AND p.timestamp = (SELECT MAX(p2.timestamp) FROM prices p2 WHERE p2.realm_id=p.realm_id)''',
            visible_realm_ids + decor_item_ids
        ).fetchall()
        for row in rows:
            if row[0] not in all_prices:
                all_prices[row[0]] = {}
            all_prices[row[0]][row[1]] = row

    result = []
    for realm in realms:
        rid = realm['id']
        if rid in hidden:
            continue
        price_map = all_prices.get(rid, {})
        profitable = 0
        total_profit = 0
        for iid in decor_item_ids:
            row = price_map.get(iid)
            if not row:
                continue
            cost_data = decor_costs.get(iid, {})
            ah_price = row[2] // 10000
            cost = cost_data.get('cost', 0)
            cost_known = cost_data.get('cost_known', False)
            profit = ah_price - cost - decor_margin
            if cost_known and cost > 0 and profit > 0:
                profitable += 1
                total_profit += profit

        result.append({
            'id': rid,
            'name': realm['name'],
            'region': realm['region'],
            'total_auctions': realm['total_auctions'],
            'last_updated': latest_ts_map.get(rid, realm['last_updated']),
            'tier': realm['tier'] if realm['tier'] else '',
            'profitable': profitable,
            'total': len(decor_item_ids),
            'total_profit': round(total_profit),
        })
    conn.close()
    result.sort(key=lambda x: x['total_auctions'], reverse=True)
    return jsonify(result)


@app.route('/api/decor/realm/<int:realm_id>')
def get_decor_realm_detail(realm_id):
    conn = get_db()
    realm = conn.execute('SELECT region FROM realms WHERE id=?', (realm_id,)).fetchone()
    region = realm[0] if realm else 'eu'

    latest_ts = conn.execute(
        'SELECT MAX(timestamp) FROM prices WHERE realm_id=?', (realm_id,)
    ).fetchone()[0]
    price_map = {}
    if latest_ts:
        rows = conn.execute(
            'SELECT item_id, min_price, num_auctions FROM prices WHERE realm_id=? AND timestamp=?',
            (realm_id, latest_ts)
        ).fetchall()
        price_map = {row[0]: row for row in rows}

    decor_items_data = load_json(DECOR_ITEMS_PATH, [])
    decor_recipes = load_json(DECOR_RECIPES_PATH, [])
    recipe_map = {r['item_id']: r for r in decor_recipes}
    decor_costs = calc_decor_costs(region, conn)
    conn.close()
    settings = load_json(SETTINGS_PATH, {})
    decor_margin = settings.get('decor_profit_margin', 0)

    result = []
    for item in decor_items_data:
        iid = item['id']
        if not iid:
            continue
        row = price_map.get(iid)
        ah_price = row[1] // 10000 if row else None
        cost_data = decor_costs.get(iid, {})
        cost = cost_data.get('cost', 0)
        cost_known = cost_data.get('cost_known', False)
        profit = (ah_price - cost - decor_margin) if (ah_price and cost > 0) else None
        result.append({
            'id': iid,
            'name': item['name'],
            'icon': item['icon'],
            'expansion': item['expansion'],
            'profession': item['profession'],
            'category': item['category'],
            'ah_price': ah_price,
            'cost': cost,
            'cost_known': cost_known,
            'profit': profit,
            'num_auctions': row[2] if row else 0,
        })
    return jsonify({'items': result, 'last_updated': latest_ts})


@app.route('/api/reagent_prices')
def get_reagent_prices():
    """Мінімальні ціни реагентів по регіону з АГ — один batch запит."""
    region = request.args.get('region', 'eu').lower()
    decor_reagents = load_json(DECOR_REAGENTS_PATH, [])
    conn = get_db()

    non_lumber = [(r['id'], r['name'], r.get('icon','')) for r in decor_reagents
                  if r['id'] and not LUMBER_WORDS.search(r.get('name',''))]
    lumber = [(r['id'], r['name'], r.get('icon','')) for r in decor_reagents
              if r['id'] and LUMBER_WORDS.search(r.get('name',''))]

    # Batch запит з commodity_prices
    ah_prices = {}
    if non_lumber:
        ids = [x[0] for x in non_lumber]
        ph = ','.join('?' * len(ids))
        rows = conn.execute(
            f'''SELECT item_id, MIN(min_price) FROM commodity_prices
                WHERE region=? AND item_id IN ({ph})
                AND timestamp >= datetime('now', '-2 hours')
                GROUP BY item_id''',
            [region] + ids
        ).fetchall()
        ah_prices = {row[0]: max(1, math.ceil(row[1] / 10000)) for row in rows if row[1]}
        # Fallback на per-realm для non-commodity предметів
        missing_ids = [iid for iid in ids if iid not in ah_prices]
        if missing_ids:
            ph2 = ','.join('?' * len(missing_ids))
            rows2 = conn.execute(
                f'''SELECT p.item_id, MIN(p.min_price) FROM prices p
                    JOIN realms r ON r.id = p.realm_id
                    WHERE r.region=? AND p.item_id IN ({ph2})
                    AND p.timestamp >= datetime('now', '-2 hours')
                    GROUP BY p.item_id''',
                [region] + missing_ids
            ).fetchall()
            for row in rows2:
                if row[1]:
                    ah_prices[row[0]] = max(1, math.ceil(row[1] / 10000))

    conn.close()
    result = {}
    for rid, name, icon in non_lumber:
        result[rid] = {'name': name, 'price': ah_prices.get(rid, 0), 'icon': icon, 'is_lumber': False}
    for rid, name, icon in lumber:
        result[rid] = {'name': name, 'price': 200, 'icon': icon, 'is_lumber': True}
    return jsonify(result)


@app.route('/api/tools_reagent_prices')
def get_tools_reagent_prices():
    """Ціни tools reagents з АГ по регіону — batch запит."""
    region = request.args.get('region', 'eu').lower()
    tools_reagents = load_json(TOOLS_REAGENTS_PATH, [])
    valid = [r for r in tools_reagents if r.get('id')]
    if not valid:
        return jsonify({})
    conn = get_db()
    ids = [r['id'] for r in valid]
    ph = ','.join('?' * len(ids))
    rows = conn.execute(
        f'''SELECT item_id, MIN(min_price) FROM commodity_prices
            WHERE region=? AND item_id IN ({ph})
            AND timestamp >= datetime('now', '-2 hours')
            GROUP BY item_id''',
        [region] + ids
    ).fetchall()
    conn.close()
    ah_prices = {row[0]: max(1, math.ceil(row[1] / 10000)) for row in rows if row[1]}
    result = {}
    for r in valid:
        result[r['id']] = {
            'key': r['key'], 'rank': r['rank'],
            'name': r['name'], 'icon': r.get('icon', ''),
            'price': ah_prices.get(r['id'], 0),
        }
    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5900, debug=False)

