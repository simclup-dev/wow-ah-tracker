import requests
import json
import os
import time
from dotenv import load_dotenv

load_dotenv('/mnt/f/stacks/wow-ah-tracker/.env')

CLIENT_ID = os.getenv('BNET_CLIENT_ID')
CLIENT_SECRET = os.getenv('BNET_CLIENT_SECRET')

DECOR_ITEMS = [
    # Pandaria
    {"name": "Mushan Dumpling Stack",         "expansion": "pandaria", "profession": "cooking",       "category": "Accents"},
    {"name": "Pandaren Fireplace",             "expansion": "pandaria", "profession": "blacksmithing", "category": "Lighting"},
    {"name": "Pandaren Signal Brazier",        "expansion": "pandaria", "profession": "blacksmithing", "category": "Lighting"},
    {"name": "Intense Mogu Brazier",           "expansion": "pandaria", "profession": "enchanting",    "category": "Lighting"},
    {"name": "Pandaren Table Lamp",            "expansion": "pandaria", "profession": "enchanting",    "category": "Lighting"},
    {"name": "Halfhill Cookpot",               "expansion": "pandaria", "profession": "engineering",   "category": "Functional"},
    {"name": "Reconstructed Mogu Lightning Drill", "expansion": "pandaria", "profession": "engineering", "category": "Miscellaneous"},
    {"name": "Hanging Paper Lanterns",         "expansion": "pandaria", "profession": "inscription",   "category": "Accents"},
    {"name": "Lorewalker's Bookcase",          "expansion": "pandaria", "profession": "inscription",   "category": "Furnishings"},
    {"name": "Lucky Traveler's Bench",         "expansion": "pandaria", "profession": "inscription",   "category": "Furnishings"},
    {"name": "Pandaren Wooden Table",          "expansion": "pandaria", "profession": "inscription",   "category": "Furnishings"},
    {"name": "Square Pandaren Table",          "expansion": "pandaria", "profession": "inscription",   "category": "Furnishings"},
    {"name": "Jade Temple Dragon Fountain",    "expansion": "pandaria", "profession": "jewelcrafting", "category": "Structural"},
    {"name": "Pandaren Stone Post",            "expansion": "pandaria", "profession": "jewelcrafting", "category": "Structural"},
    {"name": "Pandaren Stone Wall",            "expansion": "pandaria", "profession": "jewelcrafting", "category": "Structural"},
    {"name": "Wise Pandaren's Bed",            "expansion": "pandaria", "profession": "leatherworking","category": "Furnishings"},
    {"name": "Pandaren Meander Rug",           "expansion": "pandaria", "profession": "tailoring",     "category": "Accents"},

    # Legion
    {"name": "Arcan'dor Cutting Fountain",    "expansion": "legion",   "profession": "alchemy",       "category": "Miscellaneous"},
    {"name": "Starry Scrying Pool",            "expansion": "legion",   "profession": "alchemy",       "category": "Miscellaneous"},
    {"name": "Tauren Soup Pot",               "expansion": "legion",   "profession": "blacksmithing", "category": "Accents"},
    {"name": "Suramar Fence",                  "expansion": "legion",   "profession": "blacksmithing", "category": "Structural"},
    {"name": "Suramar Fencepost",              "expansion": "legion",   "profession": "blacksmithing", "category": "Structural"},
    {"name": "Nightspire Fountain",            "expansion": "legion",   "profession": "enchanting",    "category": "Miscellaneous"},
    {"name": "Suramar Containment Cell",       "expansion": "legion",   "profession": "enchanting",    "category": "Structural"},
    {"name": "Dalaran Auto-Hammer",            "expansion": "legion",   "profession": "engineering",   "category": "Miscellaneous"},
    {"name": "Failed Failure Detection Pylon", "expansion": "legion",   "profession": "engineering",   "category": "Miscellaneous"},
    {"name": "Covered Square Suramar Table",   "expansion": "legion",   "profession": "inscription",   "category": "Furnishings"},
    {"name": "Dalaran Display Shelves",        "expansion": "legion",   "profession": "inscription",   "category": "Miscellaneous"},
    {"name": "Nightborne Jeweler's Table",     "expansion": "legion",   "profession": "inscription",   "category": "Furnishings"},
    {"name": "Suramar Dresser",                "expansion": "legion",   "profession": "inscription",   "category": "Furnishings"},
    {"name": "Suramar Storage Crate",          "expansion": "legion",   "profession": "inscription",   "category": "Furnishings"},
    {"name": "Tauren Storage Chest",           "expansion": "legion",   "profession": "inscription",   "category": "Furnishings"},
    {"name": "Suramar Jeweler's Assortment",   "expansion": "legion",   "profession": "jewelcrafting", "category": "Miscellaneous"},
    {"name": "Shaded Suramar Window",          "expansion": "legion",   "profession": "jewelcrafting", "category": "Structural"},
    {"name": "Highmountain Tanner's Frame",    "expansion": "legion",   "profession": "leatherworking","category": "Accents"},
    {"name": "Tauren Fencepost",               "expansion": "legion",   "profession": "leatherworking","category": "Structural"},
    {"name": "Tauren Leather Fence",           "expansion": "legion",   "profession": "leatherworking","category": "Structural"},
    {"name": "Beloved Raptor Plushie",         "expansion": "legion",   "profession": "tailoring",     "category": "Accents"},
    {"name": "Circular Shal'dorei Rug",        "expansion": "legion",   "profession": "tailoring",     "category": "Accents"},
    {"name": "Shal'dorei Open-Air Tent",       "expansion": "legion",   "profession": "tailoring",     "category": "Structural"},

    # Kul Tiran / Zandalari
    {"name": "Zandalari Bottle Shipment",      "expansion": "kul_tiran","profession": "alchemy",       "category": "Miscellaneous"},
    {"name": "Brennadam Grinder",              "expansion": "kul_tiran","profession": "blacksmithing", "category": "Furnishings"},
    {"name": "Stormsong Stove",                "expansion": "kul_tiran","profession": "blacksmithing", "category": "Miscellaneous"},
    {"name": "Drust Enchanter's Rod",          "expansion": "kul_tiran","profession": "enchanting",    "category": "Miscellaneous"},
    {"name": "Tidesage's Totem",               "expansion": "kul_tiran","profession": "enchanting",    "category": "Miscellaneous"},
    {"name": "Mechagon Miniature Artificial Sun","expansion": "kul_tiran","profession": "engineering",  "category": "Miscellaneous"},
    {"name": "Deactivated Atomic Recalibrator","expansion": "kul_tiran","profession": "engineering",   "category": "Structural"},
    {"name": "Gnomish Tesla Mega-Coil",        "expansion": "kul_tiran","profession": "engineering",   "category": "Structural"},
    {"name": "Boralus Barrel",                 "expansion": "kul_tiran","profession": "inscription",   "category": "Furnishings"},
    {"name": "Boralus Bookshelf",              "expansion": "kul_tiran","profession": "inscription",   "category": "Furnishings"},
    {"name": "Gilded Zandalari Table",         "expansion": "kul_tiran","profession": "inscription",   "category": "Furnishings"},
    {"name": "Proudmoore Shipping Crate",      "expansion": "kul_tiran","profession": "inscription",   "category": "Furnishings"},
    {"name": "Zuldazar Fence",                 "expansion": "kul_tiran","profession": "inscription",   "category": "Structural"},
    {"name": "Zuldazar Fencepost",             "expansion": "kul_tiran","profession": "inscription",   "category": "Structural"},
    {"name": "Zandalari Skullfire Lamp",       "expansion": "kul_tiran","profession": "jewelcrafting", "category": "Lighting"},
    {"name": "Zandalari Ritual Drum",          "expansion": "kul_tiran","profession": "leatherworking","category": "Accents"},
    {"name": "Sandfury Diplomat's Banner",     "expansion": "kul_tiran","profession": "leatherworking","category": "Miscellaneous"},
    {"name": "Red Dazar'alor Rug",             "expansion": "kul_tiran","profession": "tailoring",     "category": "Accents"},
    {"name": "Zanchuli Tapestry",              "expansion": "kul_tiran","profession": "tailoring",     "category": "Accents"},

    # Outland
    {"name": "Draenei Holo-Path",              "expansion": "outland",  "profession": "enchanting",    "category": "Accents"},
    {"name": "Aldor Stellar Console",          "expansion": "outland",  "profession": "enchanting",    "category": "Miscellaneous"},
    {"name": "Draenei Holo-Projector Pedestal","expansion": "outland",  "profession": "engineering",   "category": "Miscellaneous"},
    {"name": "Draenei Transmitter",            "expansion": "outland",  "profession": "engineering",   "category": "Miscellaneous"},
    {"name": "Tempest Keep Cryo-Pod",          "expansion": "outland",  "profession": "engineering",   "category": "Miscellaneous"},
    {"name": "Aldor Bookcase",                 "expansion": "outland",  "profession": "inscription",   "category": "Miscellaneous"},
    {"name": "Crystal Signpost",               "expansion": "outland",  "profession": "inscription",   "category": "Miscellaneous"},
    {"name": "Gilded Draenei Round Table",     "expansion": "outland",  "profession": "inscription",   "category": "Furnishings"},
    {"name": "Halaa Bench",                    "expansion": "outland",  "profession": "inscription",   "category": "Furnishings"},
    {"name": "Talon King's Totem",             "expansion": "outland",  "profession": "inscription",   "category": "Miscellaneous"},
    {"name": "Shattrath Lamppost",             "expansion": "outland",  "profession": "jewelcrafting", "category": "Lighting"},
    {"name": "Shattrath Sconce",               "expansion": "outland",  "profession": "jewelcrafting", "category": "Lighting"},
    {"name": "Outland Mag'har Banner",         "expansion": "outland",  "profession": "leatherworking","category": "Accents"},
    {"name": "Arakkoa Decoy Scarecrow",        "expansion": "outland",  "profession": "leatherworking","category": "Miscellaneous"},
    {"name": "Draenei Smith's Anvil",          "expansion": "outland",  "profession": "blacksmithing", "category": "Furnishings"},
    {"name": "Bronze Banner of the Exiled",    "expansion": "outland",  "profession": "blacksmithing", "category": "Miscellaneous"},
    {"name": "Draenei Crystal Forge",          "expansion": "outland",  "profession": "blacksmithing", "category": "Miscellaneous"},

    # Draenor
    {"name": "Draenethyst String Lights",      "expansion": "draenor",  "profession": "enchanting",    "category": "Miscellaneous"},
    {"name": "Tauren Fencepost",               "expansion": "draenor",  "profession": "leatherworking","category": "Structural"},

    # Midnight (observe)
    {"name": "Haranir Preserving Agents",      "expansion": "midnight", "profession": "alchemy",       "category": "Accents"},
    {"name": "Riftstone",                      "expansion": "midnight", "profession": "alchemy",       "category": "Accents"},
    {"name": "Rootbound Vat",                  "expansion": "midnight", "profession": "alchemy",       "category": "Accents"},
    {"name": "Sunsmoke Censer",                "expansion": "midnight", "profession": "alchemy",       "category": "Accents"},
    {"name": "Silvermoon Spire Fountain",      "expansion": "midnight", "profession": "alchemy",       "category": "Miscellaneous"},
    {"name": "Gilded Silvermoon Anvil",        "expansion": "midnight", "profession": "blacksmithing", "category": "Accents"},
    {"name": "Gilded Silvermoon Hanger",       "expansion": "midnight", "profession": "blacksmithing", "category": "Accents"},
    {"name": "Masterwork Crafting Hammer",     "expansion": "midnight", "profession": "blacksmithing", "category": "Accents"},
    {"name": "Ornamental Silvermoon Hanger",   "expansion": "midnight", "profession": "blacksmithing", "category": "Accents"},
    {"name": "Ren'dorei Anvil",                "expansion": "midnight", "profession": "blacksmithing", "category": "Accents"},
    {"name": "Animated Sin'dorei Hammer",      "expansion": "midnight", "profession": "enchanting",    "category": "Accents"},
    {"name": "Animated Sin'dorei Pick",        "expansion": "midnight", "profession": "enchanting",    "category": "Accents"},
    {"name": "Ensorcelled Broom",              "expansion": "midnight", "profession": "enchanting",    "category": "Accents"},
    {"name": "Font of Gleaming Water",         "expansion": "midnight", "profession": "enchanting",    "category": "Accents"},
    {"name": "Ren'dorei Postal Repository",    "expansion": "midnight", "profession": "enchanting",    "category": "Accents"},
    {"name": "Rootflame Campfire",             "expansion": "midnight", "profession": "enchanting",    "category": "Accents"},
    {"name": "Self-Pouring Thalassian Sunwine","expansion": "midnight", "profession": "enchanting",    "category": "Accents"},
    {"name": "Spellbound Tome of Thalassian Magics","expansion": "midnight","profession": "enchanting", "category": "Accents"},
    {"name": "Endless Codex of the Voidtouched","expansion": "midnight","profession": "enchanting",    "category": "Accents"},
    {"name": "Endless Codex of Nature's Grace","expansion": "midnight", "profession": "enchanting",    "category": "Accents"},
    {"name": "Ambient Aethercharged Crystal",  "expansion": "midnight", "profession": "engineering",   "category": "Accents"},
    {"name": "Ren'dorei Crafting Framework",   "expansion": "midnight", "profession": "engineering",   "category": "Accents"},
    {"name": "Ren'dorei Void Projector",       "expansion": "midnight", "profession": "engineering",   "category": "Accents"},
    {"name": "Ren'dorei Lightpost",            "expansion": "midnight", "profession": "engineering",   "category": "Lights"},
    {"name": "Small Telogrus Lamp",            "expansion": "midnight", "profession": "engineering",   "category": "Lights"},
    {"name": "Ren'dorei Stargazer",            "expansion": "midnight", "profession": "engineering",   "category": "Miscellaneous"},
    {"name": "Ren'dorei Warp Orb",             "expansion": "midnight", "profession": "engineering",   "category": "Miscellaneous"},
    {"name": "Floating Void-Touched Tome",     "expansion": "midnight", "profession": "inscription",   "category": "Accents"},
    {"name": "Gilded Eversong Book",           "expansion": "midnight", "profession": "inscription",   "category": "Accents"},
    {"name": "Harandar Signpost",              "expansion": "midnight", "profession": "inscription",   "category": "Accents"},
    {"name": "Lively Songwriter's Quill",      "expansion": "midnight", "profession": "inscription",   "category": "Accents"},
    {"name": "Opened Sin'dorei Scroll",        "expansion": "midnight", "profession": "inscription",   "category": "Accents"},
    {"name": "Sin'dorei Phoenix Quill",        "expansion": "midnight", "profession": "inscription",   "category": "Accents"},
    {"name": "Wild Hanging Scroll",            "expansion": "midnight", "profession": "inscription",   "category": "Accents"},
    {"name": "Homely Sin'dorei Shelf",         "expansion": "midnight", "profession": "inscription",   "category": "Furnishings"},
    {"name": "Homely Wall Shelves",            "expansion": "midnight", "profession": "inscription",   "category": "Furnishings"},
    {"name": "Magnificent Towering Bookcase",  "expansion": "midnight", "profession": "inscription",   "category": "Furnishings"},
    {"name": "Restful Bronze Bench",           "expansion": "midnight", "profession": "inscription",   "category": "Furnishings"},
    {"name": "Sturdy Ren'dorei Cask",          "expansion": "midnight", "profession": "inscription",   "category": "Furnishings"},
    {"name": "Bejeweled Sin'dorei Lyre",       "expansion": "midnight", "profession": "jewelcrafting", "category": "Accents"},
    {"name": "Brilliant Phoenix Harp",         "expansion": "midnight", "profession": "jewelcrafting", "category": "Accents"},
    {"name": "Replica Haranir Mural",          "expansion": "midnight", "profession": "jewelcrafting", "category": "Accents"},
    {"name": "Shining Sin'dorei Hourglass",    "expansion": "midnight", "profession": "jewelcrafting", "category": "Accents"},
    {"name": "Resplendent Highborne Statue",   "expansion": "midnight", "profession": "jewelcrafting", "category": "Accents"},
    {"name": "Tenebrous Ren'dorei Armillary",  "expansion": "midnight", "profession": "jewelcrafting", "category": "Accents"},
    {"name": "Plush Haranir Leather Pillow",   "expansion": "midnight", "profession": "leatherworking","category": "Accents"},
    {"name": "Embossed Sin'dorei Fur Rug",     "expansion": "midnight", "profession": "leatherworking","category": "Furnishings"},
    {"name": "Haranir Canopy Bed",             "expansion": "midnight", "profession": "leatherworking","category": "Furnishings"},
    {"name": "Leather-Bound Haranir Wall Shelf","expansion": "midnight","profession": "leatherworking","category": "Furnishings"},
    {"name": "Stitched Haranir Rug",           "expansion": "midnight", "profession": "leatherworking","category": "Furnishings"},
    {"name": "Sturdy Haranir Chair",           "expansion": "midnight", "profession": "leatherworking","category": "Furnishings"},
    {"name": "Chic Silvermoon Pillow",         "expansion": "midnight", "profession": "tailoring",     "category": "Accents"},
    {"name": "Silvermoon Curtains",            "expansion": "midnight", "profession": "tailoring",     "category": "Accents"},
    {"name": "Lush Telogrus Carpet",           "expansion": "midnight", "profession": "tailoring",     "category": "Furnishings"},
    {"name": "Luxurious Silvermoon Lounge Cushion","expansion": "midnight","profession": "tailoring",  "category": "Furnishings"},
    {"name": "Plush Silvermoon Bed",           "expansion": "midnight", "profession": "tailoring",     "category": "Furnishings"},
    {"name": "Voidstrider Saddlebag",          "expansion": "midnight", "profession": "tailoring",     "category": "Furnishings"},

    # Cataclysm
    {"name": "Gilnean Cauldron",               "expansion": "cataclysm","profession": "alchemy",       "category": "Accents"},
    {"name": "Gilnean Green Potion",           "expansion": "cataclysm","profession": "alchemy",       "category": "Accents"},
    {"name": "Standing Smoke Lamp",            "expansion": "cataclysm","profession": "blacksmithing", "category": "Lighting"},
    {"name": "Gilnean Pitchfork",              "expansion": "cataclysm","profession": "blacksmithing", "category": "Miscellaneous"},
    {"name": "Pyrewood Glass Bottle",          "expansion": "cataclysm","profession": "enchanting",    "category": "Accents"},
    {"name": "Twilight Fire Canister",         "expansion": "cataclysm","profession": "enchanting",    "category": "Accents"},
    {"name": "Gilnean Problem Solver",         "expansion": "cataclysm","profession": "engineering",   "category": "Accents"},
    {"name": "Small Gilnean Windmill",         "expansion": "cataclysm","profession": "engineering",   "category": "Structural"},
    {"name": "Gilnean Map",                    "expansion": "cataclysm","profession": "inscription",   "category": "Accents"},
    {"name": "Gilnean Rocking Chair",          "expansion": "cataclysm","profession": "inscription",   "category": "Furnishings"},
    {"name": "Gilnean Wall Shelf",             "expansion": "cataclysm","profession": "inscription",   "category": "Furnishings"},
    {"name": "Gilnean Wooden Table",           "expansion": "cataclysm","profession": "inscription",   "category": "Furnishings"},
    {"name": "Gilnean Postbox",                "expansion": "cataclysm","profession": "inscription",   "category": "Miscellaneous"},
    {"name": "Smoke Sconce",                   "expansion": "cataclysm","profession": "jewelcrafting", "category": "Lighting"},
    {"name": "Smoke Lamp",                     "expansion": "cataclysm","profession": "jewelcrafting", "category": "Miscellaneous"},
    {"name": "Scaled Twilight Mosaic",         "expansion": "cataclysm","profession": "leatherworking","category": "Miscellaneous"},
    {"name": "\"Unity of Thorns\" Tapestry",   "expansion": "cataclysm","profession": "tailoring",     "category": "Miscellaneous"},
    {"name": "Surwich Expedition Tent",        "expansion": "cataclysm","profession": "tailoring",     "category": "Structural"},

    # Khaz Algar (observe)
    {"name": "Boulder Springs Hot Tub",        "expansion": "khaz_algar","profession": "alchemy",      "category": "Furnishings"},
    {"name": "Nerubian Alchemist's Retort",    "expansion": "khaz_algar","profession": "alchemy",      "category": "Miscellaneous"},
    {"name": "Rusting Bolted Bench",           "expansion": "khaz_algar","profession": "blacksmithing","category": "Furnishings"},
    {"name": "Shredderwheel Storage Chest",    "expansion": "khaz_algar","profession": "blacksmithing","category": "Furnishings"},
    {"name": "Dornic Sliced Mineloaf",         "expansion": "khaz_algar","profession": "cooking",      "category": "Accents"},
    {"name": "Earthen Hospitality Cheese-Like Brick","expansion": "khaz_algar","profession": "cooking","category": "Accents"},
    {"name": "Kaheti Predator's Assortment",   "expansion": "khaz_algar","profession": "cooking",      "category": "Accents"},
    {"name": "Replica Awakening Machine Stasis Pod","expansion": "khaz_algar","profession": "enchanting","category": "Accents"},
    {"name": "Dornogal Hanging Sconce",        "expansion": "khaz_algar","profession": "enchanting",   "category": "Lighting"},
    {"name": "Replica Rumbling Wastes Drill Pod","expansion": "khaz_algar","profession": "engineering","category": "Miscellaneous"},
    {"name": "Schmancy Goblin String Lights",  "expansion": "khaz_algar","profession": "engineering",  "category": "Miscellaneous"},
    {"name": "Dornogal Bookcase",              "expansion": "khaz_algar","profession": "inscription",  "category": "Furnishings"},
    {"name": "Freywold Table",                 "expansion": "khaz_algar","profession": "inscription",  "category": "Furnishings"},
    {"name": "Meadery Storage Chest",          "expansion": "khaz_algar","profession": "inscription",  "category": "Furnishings"},
    {"name": "Algari Fence",                   "expansion": "khaz_algar","profession": "inscription",  "category": "Miscellaneous"},
    {"name": "Algari Fencepost",               "expansion": "khaz_algar","profession": "inscription",  "category": "Miscellaneous"},
    {"name": "Gundargaz Candelabra",           "expansion": "khaz_algar","profession": "jewelcrafting","category": "Lighting"},
    {"name": "Octagonal Ochre Window",         "expansion": "khaz_algar","profession": "jewelcrafting","category": "Structural"},
    {"name": "Zhevra-Stripe Rug",              "expansion": "khaz_algar","profession": "leatherworking","category": "Accents"},
    {"name": "Well-Lit Incontinental Couch",   "expansion": "khaz_algar","profession": "leatherworking","category": "Furnishings"},
    {"name": "Dornogal Framed Rug",            "expansion": "khaz_algar","profession": "tailoring",    "category": "Accents"},
    {"name": "Undermine Bean Bag Chair",       "expansion": "khaz_algar","profession": "tailoring",    "category": "Furnishings"},
]


def get_token():
    r = requests.post(
        'https://oauth.battle.net/token',
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={'grant_type': 'client_credentials'},
        timeout=10
    )
    return r.json()['access_token']


def search_item(token, name, region='us'):
    r = requests.get(
        f'https://{region}.api.blizzard.com/data/wow/search/item',
        headers={'Authorization': f'Bearer {token}'},
        params={
            'namespace': f'static-{region}',
            'name.en_US': name,
            '_pageSize': 20,
        },
        timeout=10
    )
    if r.status_code != 200:
        return None
    results = r.json().get('results', [])
    # Exact match
    for res in results:
        data = res.get('data', {})
        item_name = data.get('name', {}).get('en_US', '')
        if item_name.lower() == name.lower():
            return data.get('id'), item_name
    # Fallback: case-insensitive contains
    for res in results:
        data = res.get('data', {})
        item_name = data.get('name', {}).get('en_US', '')
        if name.lower() in item_name.lower():
            return data.get('id'), item_name
    return None


def get_item_media(token, item_id, region='us'):
    r = requests.get(
        f'https://{region}.api.blizzard.com/data/wow/media/item/{item_id}',
        headers={'Authorization': f'Bearer {token}'},
        params={'namespace': f'static-{region}'},
        timeout=10
    )
    if r.status_code != 200:
        return None
    assets = r.json().get('assets', [])
    for a in assets:
        if a.get('key') == 'icon':
            return a.get('value')
    return None


def main():
    print("Отримуємо токен...")
    token = get_token()

    results = []
    not_found = []

    for i, item in enumerate(DECOR_ITEMS):
        name = item['name']
        print(f"[{i+1}/{len(DECOR_ITEMS)}] {name}...", end=' ', flush=True)

        found = search_item(token, name)
        if found:
            item_id, found_name = found
            icon = get_item_media(token, item_id)
            results.append({
                'name': found_name,
                'id': item_id,
                'icon': icon or '',
                'expansion': item['expansion'],
                'profession': item['profession'],
                'category': item['category'],
            })
            print(f"✓ id={item_id}")
        else:
            not_found.append(name)
            results.append({
                'name': name,
                'id': None,
                'icon': '',
                'expansion': item['expansion'],
                'profession': item['profession'],
                'category': item['category'],
            })
            print("✗ не знайдено")

        time.sleep(0.15)

        # Оновлюємо токен кожні 100 запитів
        if (i + 1) % 100 == 0:
            token = get_token()

    with open('/mnt/f/stacks/wow-ah-tracker/decor_items.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Збережено {len(results)} предметів у decor_items.json")
    if not_found:
        print(f"⚠️  Не знайдено ({len(not_found)}):")
        for n in not_found:
            print(f"   - {n}")


if __name__ == '__main__':
    main()
