import os
from flask import Flask
import telebot
import threading

# BotFather থেকে পাওয়া আপনার @Gchaker_bot এর আসল টোকেনটি নিচের লাইনে বসান
TOKEN = "8881853485:AAFWkIjkrMaUbap5DoP2ntRpu1ilyt-fPeo"
bot = telebot.TeleBot(TOKEN)

# রেন্ডার সার্ভারের জন্য ফ্লাস্ক অ্যাপ তৈরি
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# বটের মূল কাজ বা হ্যান্ডলার
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "হ্যালো! আপনার @Gchaker_bot এখন রেন্ডার সার্ভারে সম্পূর্ণ লাইভ আছে।")

# ব্যাকগ্রাউন্ডে বট চালু করার ট্রিকস
def run_bot():
    bot.infinity_polling(none_stop=True)

if __name__ == "__main__":
    # বটকে আলাদা থ্রেডে চালু করা হচ্ছে যেন ফ্লাস্ক সার্ভার ব্লক না হয়
    threading.Thread(target=run_bot).start()
    # রেন্ডার পোর্টের জন্য ফ্লাস্ক রান করা
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
