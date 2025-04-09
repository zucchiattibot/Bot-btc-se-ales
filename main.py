import time
import requests
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
import telegram

# === CONFIGURACIÓN ===
TELEGRAM_TOKEN = "7746262990:AAEOSEwj3ttReuKEIBeK-NabP_fv2QLcbNs"
TELEGRAM_CHAT_ID = "328697032"
PAIR = "BTC-USDT"
INTERVAL = "1m"
LIMIT = 100
SIGNAL_STATE = None

bot = telegram.Bot(token=TELEGRAM_TOKEN)

def get_klines():
    url = f"https://api.kucoin.com/api/v1/market/candles?type={INTERVAL}&symbol={PAIR}&limit={LIMIT}"
    response = requests.get(url)
    data = response.json()
    klines = pd.DataFrame(data['data'], columns=["time", "open", "close", "high", "low", "volume", "turnover"])
    klines["close"] = klines["close"].astype(float)
    return klines[::-1]  # invertimos para tener el más nuevo último

def get_signal(df):
    rsi = RSIIndicator(close=df["close"], window=14).rsi()
    ema = EMAIndicator(close=df["close"], window=20).ema_indicator()
    price = df["close"].iloc[-1]

    if rsi.iloc[-1] < 30 and price > ema.iloc[-1]:
        return "LONG"
    elif rsi.iloc[-1] > 70 and price < ema.iloc[-1]:
        return "SHORT"
    else:
        return "WAIT"

def send_telegram_message(message):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

send_telegram_message("Bot de señales BTC arrancó correctamente (KuCoin)")

while True:
    try:
        df = get_klines()
        signal = get_signal(df)

        price = df["close"].iloc[-1]
        global SIGNAL_STATE
        if signal != SIGNAL_STATE:
            SIGNAL_STATE = signal
            send_telegram_message(f"Señal actual: {signal} - Precio BTC: {price}")
        time.sleep(60)

    except Exception as e:
        send_telegram_message(f"Error general: {e}")
        time.sleep(60)
