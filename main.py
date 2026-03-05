import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import schedule
import time
import os
from dotenv import load_dotenv
import asyncio
from threading import Thread

load_dotenv()

# Telegram Bot設定
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = '@your_channel'  # 替換成你的頻道ID

# 上次抓取的盤源（用來檢查新盤）
last_sales = set()
last_rentals = set()

def fetch_listings(url, is_sale=True):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        listings = []
        
        for item in soup.find_all('div', class_='buy-item'):
            title = item.find('a', class_='buy-title').text.strip() if item.find('a', class_='buy-title') else '無標題'
            price = item.find('span', class_='price').text.strip() if item.find('span', class_='price') else '無價格'
            area = item.find('span', class_='area').text.strip() if item.find('span', class_='area') else '無面積'
            rooms = item.find('span', class_='rooms').text.strip() if item.find('span', class_='rooms') else '無房間資訊'
            link = 'https://www.28hse.com' + item.find('a')['href'] if item.find('a') else '無連結'
            
            listing = f"{title}\n價格: {price}\n面積: {area}\n房間: {rooms}\n連結: {link}"
            listings.append(listing)
        
        return listings
    except Exception as e:
        print(f"Error fetching listings: {e}")
        return []

def check_and_report():
    global last_sales, last_rentals
    
    try:
        # 賣盤URL
        sales_url = 'https://www.28hse.com/buy/a2/dg122/c2052'
        sales_listings = fetch_listings(sales_url, is_sale=True)
        new_sales = set(sales_listings) - last_sales
        if new_sales:
            message = "新賣盤:\n" + "\n\n".join(new_sales)
            # Note: This requires async context, will be handled in scheduler
            last_sales.update(new_sales)
        
        # 租盤URL
        rentals_url = 'https://www.28hse.com/rent/a2/dg122/c2052'
        rentals_listings = fetch_listings(rentals_url, is_sale=False)
        new_rentals = set(rentals_listings) - last_rentals
        if new_rentals:
            message = "新租盤:\n" + "\n\n".join(new_rentals)
            last_rentals.update(new_rentals)
    except Exception as e:
        print(f"Error in check_and_report: {e}")

# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "歡迎使用房產監控機器人！\n\n"
        "可用命令:\n"
        "/help - 顯示幫助\n"
        "/latest - 顯示最新盤源\n"
        "/sales - 顯示最新賣盤\n"
        "/rentals - 顯示最新租盤\n\n"
        "或直接輸入訊息與我聊天！"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await update.message.reply_text(
        "房產監控機器人幫助\n\n"
        "命令列表:\n"
        "/start - 開始\n"
        "/help - 顯示此幫助\n"
        "/latest - 顯示最新盤源\n"
        "/sales - 顯示最新賣盤\n"
        "/rentals - 顯示最新租盤\n\n"
        "功能:\n"
        "• 自動監控房產網站\n"
        "• 實時推送新盤源\n"
        "• 支持交互式查詢"
    )

async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /latest command"""
    sales_url = 'https://www.28hse.com/buy/a2/dg122/c2052'
    sales = fetch_listings(sales_url, is_sale=True)
    
    if sales:
        message = "最新賣盤 (前5個):\n\n" + "\n\n".join(sales[:5])
    else:
        message = "暫無最新賣盤"
    
    await update.message.reply_text(message)

async def sales(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /sales command"""
    sales_url = 'https://www.28hse.com/buy/a2/dg122/c2052'
    sales_listings = fetch_listings(sales_url, is_sale=True)
    
    if sales_listings:
        message = "最新賣盤:\n\n" + "\n\n".join(sales_listings[:3])
    else:
        message = "暫無賣盤信息"
    
    await update.message.reply_text(message)

async def rentals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /rentals command"""
    rentals_url = 'https://www.28hse.com/rent/a2/dg122/c2052'
    rentals_listings = fetch_listings(rentals_url, is_sale=False)
    
    if rentals_listings:
        message = "最新租盤:\n\n" + "\n\n".join(rentals_listings[:3])
    else:
        message = "暫無租盤信息"
    
    await update.message.reply_text(message)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages"""
    user_message = update.message.text.lower()
    
    if '賣盤' in user_message or '買' in user_message:
        await sales(update, context)
    elif '租' in user_message or '租盤' in user_message:
        await rentals(update, context)
    elif '幫助' in user_message or '命令' in user_message:
        await help_command(update, context)
    else:
        await update.message.reply_text(
            f"你說: {update.message.text}\n\n"
            "我是房產監控機器人。\n"
            "輸入 /help 查看可用命令。"
        )

def run_scheduler():
    """Run the scheduler in a separate thread"""
    schedule.every(1).hours.do(check_and_report)
    check_and_report()  # Initial run
    
    while True:
        schedule.run_pending()
        time.sleep(60)

async def main():
    """Start the bot"""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("latest", latest))
    application.add_handler(CommandHandler("sales", sales))
    application.add_handler(CommandHandler("rentals", rentals))
    
    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start scheduler in background thread
    scheduler_thread = Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    # Start the bot
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
