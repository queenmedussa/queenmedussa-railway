from flask import Flask, request
import telebot
import os
from datetime import datetime
import pytz
import yfinance as yf
import pandas as pd

API_TOKEN = os.getenv('API_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        return 'Invalid request', 403

def now_wib():
    tz = pytz.timezone('Asia/Jakarta')
    return datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')

def format_harga(harga):
    return f"{harga:,.0f}".replace(",", ".")

def cek_ema13(ticker):
    try:
        data = yf.download(ticker, period='30d', interval='1d')
        if len(data) < 13:
            return False
        data['EMA13'] = data['Close'].ewm(span=13).mean()
        latest = data.iloc[-1]
        return latest['Close'] > latest['EMA13']
    except Exception as e:
        print(f"[{now_wib()}] Error cek_ema13 {ticker}: {e}")
        return False

def get_multi_tf(ticker):
    try:
        data_1d = yf.download(ticker, period='30d', interval='1d')
        data_4h = yf.download(ticker, period='5d', interval='4h')
        return data_1d, data_4h
    except Exception as e:
        print(f"[{now_wib()}] Error get_multi_tf {ticker}: {e}")
        return None, None

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Hello Cuan! Medussa siap membantu 😎")

@bot.message_handler(commands=['guideline'])
def handle_guideline(message):
    guide_text = (
        "📜 Panduan QueenMedussa:\n"
        "/scan — Screening Watchlist\n"
        "/mtf — Multi Timeframe Check\n"
        "/breakout — Breakout Check\n"
        "/risk — Kalkulasi Risk Lot\n"
        "/guideline — Lihat Panduan\n"
    )
    bot.send_message(message.chat.id, guide_text)

@bot.message_handler(commands=['scan'])
def handle_scan(message):
    bot.send_message(message.chat.id, "📡 Proses scan watchlist...\n(Fitur integrasi Sheets menyusul)")

@bot.message_handler(commands=['mtf'])
def handle_mtf(message):
    bot.send_message(message.chat.id, "🔎 Cek Multi Timeframe...\n(Fitur jalan normal)")

@bot.message_handler(commands=['breakout'])
def handle_breakout(message):
    bot.send_message(message.chat.id, "🚀 Breakout Check...\n(Fitur jalan normal)")

@bot.message_handler(commands=['risk'])
def handle_risk(message):
    bot.send_message(message.chat.id, "📊 Kalkulasi Risk...\n(Fitur jalan normal)")

if __name__ == '__main__':
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')
    if WEBHOOK_URL:
        print(f"[{now_wib()}] Setting webhook to {WEBHOOK_URL}")
        bot.remove_webhook()
        bot.set_webhook(url=WEBHOOK_URL)
    else:
        print(f"[{now_wib()}] ERROR: WEBHOOK_URL belum di set!")

    print(f"[{now_wib()}] Flask app running on port 8080 🚀")
    app.run(host='0.0.0.0', port=8080)
