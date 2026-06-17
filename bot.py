import telebot
from playwright.sync_api import sync_playwright
import sqlite3
from datetime import datetime

# Ботты іске қосу
bot = telebot.TeleBot("8618325710:AAFNWTU5sx7s95-jkopIeLorLyPz4Z3IMzk")

# Дерекқорды дайындау
conn = sqlite3.connect('sales.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS sales (id INTEGER PRIMARY KEY, profit REAL, date TEXT)''')
conn.commit()

# 1. Kaspi жеткізу құнын анықтау (Кесте бойынша)
def get_kaspi_delivery(price):
    if price < 1000: return 57
    if 1000 <= price < 3000: return 173
    if 3000 <= price < 5000: return 231
    if 5000 <= price < 10000: return 811
    return 1275

# 2. Kaspi сілтемесін өңдеу
@bot.message_handler(func=lambda message: 'kaspi.kz' in message.text)
def handle_kaspi(message):
    bot.reply_to(message, "⏳ Kaspi бағасын және жеткізуді есептеп жатырмын...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(message.text)
            page.wait_for_selector('.item__price-once', timeout=15000)
            
            raw_price = page.locator('.item__price-once').first.inner_text()
            price = float(''.join(filter(str.isdigit, raw_price)))
            browser.close()
            
            delivery = get_kaspi_delivery(price)
            
            msg = bot.reply_to(message, f"💰 Kaspi бағасы: {price:,.0f} ₸\n🚚 Kaspi жеткізуі: {delivery} ₸\nСебестоимостьты жаз (Қытай бағасы + Қытай жеткізуі):")
            bot.register_next_step_handler(msg, process_profit, price, delivery)
    except Exception as e:
        bot.reply_to(message, f"❌ Қате: Бағаны таба алмадым.")

# 3. Барлық шығынды есептеу
def process_profit(message, kaspi_price, kaspi_delivery):
    try:
        total_cost = float(''.join(filter(str.isdigit, message.text)))
        
        commission = kaspi_price * 0.125
        tax = kaspi_price * 0.03
        
        # Барлық шығын қосындысы
        total_expense = total_cost + commission + tax + kaspi_delivery
        profit = kaspi_price - total_expense
        
        cursor.execute("INSERT INTO sales (profit, date) VALUES (?, ?)", 
                       (profit, datetime.now().strftime("%Y-%m-%d")))
        conn.commit()
        
        response = (
            f"💰 **Kaspi бағасы:** {kaspi_price:,.0f} ₸\n"
            f"➖➖➖➖➖➖➖➖\n"
            f"📦 **Шығындар:**\n"
            f"— 🏷 Себестоимость: {total_cost:,.0f} ₸\n"
            f"— 💼 Комиссия (12.5%): {commission:,.0f} ₸\n"
            f"— 🏦 Салық (3%): {tax:,.0f} ₸\n"
            f"— 🚚 Kaspi жеткізуі: {kaspi_delivery} ₸\n"
            f"➖➖➖➖➖➖➖➖\n"
            f"✅ **Таза пайда:** {profit:,.0f} ₸\n"
        )
        bot.reply_to(message, response)
    except:
        bot.reply_to(message, "⚠️ Қате: тек санды жаз.")

# 4. Ботты іске қосу
if __name__ == '__main__':
    print("✅ Бот сәтті іске қосылды! Telegram-ға өтіп, сілтеме жібер.")
    bot.infinity_polling()
