# Delta EMA Crossover Telegram Bot

This small bot fetches candles from Delta Exchange and sends Telegram alerts when EMA(9) and EMA(21) cross.

## Files
- `bot.py` : main script
- `requirements.txt` : Python dependencies
- `README.md` : this file

## Environment Variables (set on Render)
- `DELTA_API_KEY` = Your Delta API key (optional for public endpoints)
- `SYMBOL` = e.g. BTCUSD
- `RESOLUTION` = e.g. 1m, 5m, 1h
- `EMA_SHORT` = 9
- `EMA_LONG` = 21
- `POLL_INTERVAL` = 60
- `TELEGRAM_TOKEN` = Your Telegram bot token
- `TELEGRAM_CHAT_ID` = Your Telegram chat id

## Quick local run
```bash
pip install -r requirements.txt
export DELTA_API_KEY="your_key"
export TELEGRAM_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
python bot.py
```

## Deploy on Render
1. Push repo to GitHub.
2. Create a **Background Worker** on Render.
3. Build command: `pip install -r requirements.txt`
4. Start command: `python bot.py`
5. Add environment variables in Render dashboard and deploy.
