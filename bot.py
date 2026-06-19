import os
from flask import Flask
import telebot
import threading
import time

# আপনার বটের টোকেন
TOKEN = "8881853485:AAFWkIjkrMaUbap5DoP2ntRpu1ilyt-fPeo"
bot = telebot.TeleBot(TOKEN)

# রেন্ডার সার্ভারের জন্য ফ্লাস্ক অ্যাপ তৈরি
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# বটের মূল কমান্ড হ্যান্ডলার
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        bot.reply_to(message, "হ্যালো! আপনার @Gchaker_bot এখন সম্পূর্ণ সচল এবং লাইভ আছে।")
    except Exception as e:
        print(f"Error sending message: {e}")

# ব্যাকগ্রাউন্ডে বট পোলিং চালু করার ফাংশন
def run_bot():
    while True:
        try:
            print("Starting bot polling...")
            bot.infinity_polling(none_stop=True, timeout=60, long_polling_timeout=30)
        except Exception as e:
            print(f"Bot polling crashed, restarting in 5 seconds... Error: {e}")
            time.sleep(5)

# বটটিকে আলাদা থ্রেডে ব্যাকগ্রাউন্ডে রান করানো
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()

if __name__ == "__main__":
    # রেন্ডার পোর্টের জন্য ফ্লাস্ক রান করা
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
