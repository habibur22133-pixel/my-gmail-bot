import os
import re
import smtplib
import dns.resolver
from flask import Flask
import telebot
import threading
import time

# আপনার বটের টোকেন
TOKEN = "8881853485:AAFWkIjkrMaUbap5DoP2ntRpu1ilyt-fPeo"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Email SMTP Validator is running!"

EMAIL_REGEX = r'[a-zA-Z0-9-_.]+@[a-zA-Z0-9-_.]+\.[a-zA-Z]{2,}'

def verify_email_smtp(email):
    """SMTP সার্ভারে নক করে ইমেইল সচল কি না চেক করার ফাংশন"""
    try:
        domain = email.split('@')[1]
        # ডোমেইনের MX Record বা মেইল সার্ভার খুঁজে বের করা
        records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(records[0].exchange)
        
        # SMTP কানেকশন তৈরি করা
        server = smtplib.SMTP(timeout=10)
        server.set_debuglevel(0)
        server.connect(mx_record, 25)
        server.helo(server.local_hostname)
        server.mail('test@gmail.com') # একটি ডামি সেন্ডার অ্যাড্রেস
        
        # মূল ইমেইল চেক করা (RCPT TO)
        code, message = server.rcpt(str(email))
        server.quit()
        
        # SMTP Code 250 মানে ইমেইলটি একদম লাইভ এবং সচল আছে
        if code == 250:
            return "Live"
        else:
            return "Disabled/Invalid"
    except Exception:
        return "Disabled/Invalid"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 হ্যালো! আমি আপনার অ্যাডভান্সড বাল্ক জিমেইল ভেরিফায়ার বট।\n\n"
        "📩 আমাকে একসাথে অনেকগুলো ইমেইল টেক্সট আকারে পাঠান। "
        "আমি সরাসরি SMTP সার্ভার চেক করে Live এবং Disabled ইমেইল আলাদা করে দেব।"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def check_bulk_emails(message):
    text = message.text
    emails = list(set(re.findall(EMAIL_REGEX, text)))
    
    if not emails:
        bot.reply_to(message, "❌ আপনার মেসেজে কোনো ইমেইল অ্যাড্রেস খুঁজে পাওয়া যায়নি।")
        return
    
    status_msg = bot.reply_to(message, f"🔍 মোট {len(emails)}টি ইমেইল পাওয়া গেছে। SMTP সার্ভারে ভেরিফাই করা হচ্ছে, দয়া করে একটু অপেক্ষা করুন...")
    
    live_emails = []
    disabled_emails = []
    
    for email in emails:
        status = verify_email_smtp(email)
        if status == "Live":
            live_emails.append(email)
        else:
            disabled_emails.append(email)
            
    response = f"📊 **ইমেইল ভেরিফিকেশন রিপোর্ট**\n"
    response += f"━━━━━━━━━━━━━━━━━━\n"
    response += f"✅ **Live / Verified ({len(live_emails)}):**\n"
    response += "\n".join([f"`{e}`" for e in live_emails]) if live_emails else "_কোনো লাইভ ইমেইল পাওয়া যায়নি_\n"
        
    response += f"\n\n❌ **Disabled / Invalid ({len(disabled_emails)}):**\n"
    response += "\n".join([f"`{e}`" for e in disabled_emails]) if disabled_emails else "_কোনো ইনভ্যালিড ইমেইল পাওয়া যায়নি_\n"
        
    bot.edit_message_text(response, chat_id=message.chat.id, message_id=status_msg.message_id, parse_mode="Markdown")

def run_bot():
    while True:
        try:
            # Conflict এরর এড়াতে আগের যেকোনো পোলিং সেশন ক্লিন করে নেওয়া
            bot.delete_webhook(drop_pending_updates=True)
            print("Starting fresh bot polling...")
            bot.infinity_polling(none_stop=True, timeout=60, long_polling_timeout=30)
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(5)

bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
