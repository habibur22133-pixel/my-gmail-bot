import os
import re
from flask import Flask
import telebot
import threading
import time
from email_validator import validate_email, EmailNotValidError

# আপনার বটের টোকেন
TOKEN = "8881853485:AAFWkIjkrMaUbap5DoP2ntRpu1ilyt-fPeo"
bot = telebot.TeleBot(TOKEN)

# রেন্ডার সার্ভারের জন্য ফ্লাস্ক অ্যাপ তৈরি
app = Flask(__name__)

@app.route('/')
def home():
    return "Email Validator Bot is running!"

# টেক্সট থেকে ইমেইল খুঁজে বের করার রেগুলার এক্সপ্রেশন
EMAIL_REGEX = r'[a-zA-Z0-9-_.]+@[a-zA-Z0-9-_.]+\.[a-zA-Z]{2,}'

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 হ্যালো! আমি আপনার বাল্ক ইমেইল ভেরিফায়ার বট।\n\n"
        "📩 আমাকে একসাথে অনেকগুলো ইমেইল টেক্সট আকারে পাঠান। "
        "আমি সেগুলোকে চেক করে Live (Valid) এবং Disabled (Invalid) ইমেইল আলাদা করে দেব।"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def check_bulk_emails(message):
    text = message.text
    # টেক্সট থেকে সব ইমেইল এক্সট্রাক্ট করা
    emails = list(set(re.findall(EMAIL_REGEX, text)))
    
    if not emails:
        bot.reply_to(message, "❌ আপনার মেসেজে কোনো বৈধ ইমেইল অ্যাড্রেস খুঁজে পাওয়া যায়নি। দয়া করে সঠিক ফরম্যাটে ইমেইল পাঠান।")
        return
    
    status_msg = bot.reply_to(message, f"🔍 মোট {len(emails)}টি ইমেইল পাওয়া গেছে। ভেরিফাই করা হচ্ছে, দয়া করে একটু অপেক্ষা করুন...")
    
    live_emails = []
    disabled_emails = []
    
    for email in emails:
        try:
            # ইমেইলের ডোমেইন এবং সিনট্যাক্স লাইভ কি না চেক করা
            validate_email(email, check_deliverability=True)
            live_emails.append(email)
        except EmailNotValidError:
            disabled_emails.append(email)
            
    # ফলাফল তৈরি করা
    response = f"📊 **ইমেইল ভেরিফিকেশন রিপোর্ট**\n"
    response += f"━━━━━━━━━━━━━━━━━━\n"
    response += f"✅ **Live / Verified ({len(live_emails)}):**\n"
    if live_emails:
        response += "\n".join([f"`{e}`" for e in live_emails])
    else:
        response += "_কোনো লাইভ ইমেইল পাওয়া যায়নি_\n"
        
    response += f"\n\n❌ **Disabled / Invalid ({len(disabled_emails)}):**\n"
    if disabled_emails:
        response += "\n".join([f"`{e}`" for e in disabled_emails])
    else:
        response += "_কোনo ইনভ্যালিড ইমেইল পাওয়া যায়নি_\n"
        
    # ফলাফল টেলিগ্রামে পাঠানো
    bot.edit_message_text(response, chat_id=message.chat.id, message_id=status_msg.message_id, parse_mode="Markdown")

# バックグラウンド পোলিং চালু
def run_bot():
    while True:
        try:
            bot.infinity_polling(none_stop=True, timeout=60, long_polling_timeout=30)
        except Exception as e:
            time.sleep(5)

bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
