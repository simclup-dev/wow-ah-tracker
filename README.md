# WoW Auction House Tracker

Price intelligence across **175 game-economy markets** (92 EU + 83 US realms). Collects auction prices for 200+ tracked items every hour through the official Blizzard API and answers: **"which items are worth crafting today, and where?"**

![Dashboard](docs/screenshot.png)

## What it does

- Hourly collection from all 175 connected realms in two regions — **1.9M+ price points** stored
- Tracks profession tools, decor items, and their reagents (209 distinct items)
- Computes per-item profit margins: materials cost vs. sale price, per realm
- React dashboard with region tabs, sortable columns, and expandable per-realm rows
- Telegram notifications for standout price opportunities

## Architecture

```
collector.py (hourly, cron) ──> Blizzard API (OAuth client-credentials)
        │                          realms / auctions / commodities
        └──> SQLite (prices, commodity_prices, realms)
                 │
app.py (Flask) ──> REST API (/api/realms, /api/min_prices, …)
                 └──> static/ React dashboard
notifier.py ──> Telegram alerts
```

The collector survives token expiry mid-run (re-auths and retries) and skips unreachable realms without aborting the sweep.

## Setup

```bash
pip install -r requirements.txt   # flask, requests, python-dotenv
cp .env.example .env              # add your Blizzard + Telegram credentials
python collector.py               # one collection sweep (schedule hourly via cron)
python app.py                     # dashboard on :5900
```

Get Blizzard API credentials at [develop.battle.net](https://develop.battle.net/). Item lists live in `items.json` / `decor_items.json`; helper scripts (`fetch_items.py`, `fetch_decor_recipes.py`, …) rebuild them from the game API.

## Stack

Python · Flask · React · Blizzard API (OAuth) · SQLite · Telegram Bot API
