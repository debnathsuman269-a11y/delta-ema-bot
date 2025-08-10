import os
import time
import requests
import pandas as pd

# ===== Config =====
DELTA_API_KEY = os.getenv("i1fFKKOR5Yk1MNpd4j70dW6Bj3xOJ0")
SYMBOL = os.getenv("SYMBOL", "SOLUSD")
RESOLUTION = os.getenv("RESOLUTION", "5m")
EMA_SHORT = int(os.getenv("EMA_SHORT", 9))
EMA_LONG = int(os.getenv("EMA_LONG", 21))
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 60))
TELEGRAM_TOKEN = os.getenv("7290896681:AAFhqeFdiJcm1r4x8gHZhZyo09ObYNG83mU")
TELEGRAM_CHAT_ID = os.getenv("6422526794")

last_signal = None

# Resolution to seconds
def res_to_seconds(res):
    unit = res[-1]
    val = int(res[:-1])
    if unit == "m": return val * 60
    if unit == "h": return val * 3600
    if unit == "d": return val * 86400
    raise ValueError("Invalid resolution")

# Fetch candle data
def fetch_candles(symbol, resolution, limit=100):
    end = int(time.time())
    sec = res_to_seconds(resolution)
    start = end - sec * limit
    url = "https://api.delta.exchange/v2/history/candles"
    params = {
        "symbol": symbol,
        "resolution": resolution,
        "start": str(start),
        "end": str(end)
    }
    headers = {"api-key": DELTA_API_KEY} if DELTA_API_KEY else {}
    r = requests.get(url, params=params, headers=headers, timeout=10)
    r.raise_for_status()
    data = r.json().get("result", [])
    if not data:
        raise ValueError("No candle data")
    df = pd.DataFrame(data)
    # try to handle both possible time/close formats
    if 'close' not in df.columns and len(df.columns) >= 5:
        # fallback: if response is list of arrays like Binance style
        # assume close at index 4 and time at index 0
        df = df.iloc[:, :6]
        df.columns = ['time','open','high','low','close','volume']
    df["close"] = df["close"].astype(float)
    # if time looks like epoch seconds or ms, try to normalize
    if df["time"].dtype == 'int64' or df["time"].dtype == 'float64':
        # guess: if milliseconds (>=1e12), convert from ms
        if df["time"].astype(int).max() > 1_000_000_000_000:
            df["time"] = pd.to_datetime(df["time"], unit='ms')
        else:
            df["time"] = pd.to_datetime(df["time"], unit='s')
    else:
        # try parse
        df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)
    return df

# EMA calculation
def compute_emas(df):
    df["ema_short"] = df["close"].ewm(span=EMA_SHORT, adjust=False).mean()
    df["ema_long"] = df["close"].ewm(span=EMA_LONG, adjust=False).mean()
    return df

# Crossover check
def check_crossover(df):
    global last_signal
    if len(df) < 2:
        return
    prev_s, prev_l = df["ema_short"].iloc[-2], df["ema_long"].iloc[-2]
    curr_s, curr_l = df["ema_short"].iloc[-1], df["ema_long"].iloc[-1]

    if prev_s <= prev_l and curr_s > curr_l:
        signal = "BULLISH CROSS"
    elif prev_s >= prev_l and curr_s < curr_l:
        signal = "BEARISH CROSS"
    else:
        signal = None

    if signal and signal != last_signal:
        last_signal = signal
        send_telegram_alert(signal, df["close"].iloc[-1], df["time"].iloc[-1])

# Telegram alert
def send_telegram_alert(signal, price, candle_time):
    text = f"{signal} on {SYMBOL}\nPrice: {price}\nTime: {candle_time}\nResolution: {RESOLUTION}"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text})
        print("Alert sent:", text)
    except Exception as e:
        print("Failed to send telegram:", e)

# Main loop
if __name__ == "__main__":
    print("Starting Delta EMA bot for", SYMBOL, "interval", RESOLUTION)
    while True:
        try:
            df = fetch_candles(SYMBOL, RESOLUTION)
            df = compute_emas(df)
            check_crossover(df)
        except Exception as e:
            print("Error:", e)
        time.sleep(POLL_INTERVAL)
