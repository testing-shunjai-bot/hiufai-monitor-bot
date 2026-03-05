import requests
from bs4 import BeautifulSoup
import telegram
from telegram.ext import Updater
import schedule
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot設定
BOT_TOKEN = os.getenv('BOT_TOKEN')  # 從.env檔案讀取你的Token
CHANNEL_ID = '@your_channel'  # 替換成你的頻道ID

bot = telegram.Bot(token=BOT_TOKEN)

# 上次抓取的盤源（用來檢查新盤）
last_sales = set()
last_rentals = set()

def fetch_listings(url, is_sale=True):
    headers = {'User-Agent': 'Mozilla/5.0'}  # 模擬瀏覽器，避免被擋
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    listings = []
    
    # 從28Hse頁面抓取結構（基於你的網站結構）
    for item in soup.find_all('div', class_='buy-item'):  # 調整class根據實際HTML檢查
        title = item.find('a', class_='buy-title').text.strip() if item.find('a', class_='buy-title') else '無標題'
        price = item.find('span', class_='price').text.strip() if item.find('span', class_='price') else '無價格'
        area = item.find('span', class_='area').text.strip() if item.find('span', class_='area') else '無面積'
        rooms = item.find('span', class_='rooms').text.strip() if item.find('span', class_='rooms') else '無房間資訊'
        link = 'https://www.28hse.com' + item.find('a')['href'] if item.find('a') else '無連結'
        
        listing = f"{title}\n價格: {price}\n面積: {area}\n房間: {rooms}\n連結: {link}"
        listings.append(listing)
    
    return listings

def check_and_report():
    global last_sales, last_rentals
    
    # 賣盤URL (從28Hse)
    sales_url = 'https://www.28hse.com/buy/a2/dg122/c2052'
    sales_listings = fetch_listings(sales_url, is_sale=True)
    new_sales = set(sales_listings) - last_sales
    if new_sales:
        message = "新賣盤:\n" + "\n\n".join(new_sales)
        bot.send_message(chat_id=CHANNEL_ID, text=message)
        last_sales.update(new_sales)
    
    # 租盤URL (從28Hse)
    rentals_url = 'https://www.28hse.com/rent/a2/dg122/c2052'
    rentals_listings = fetch_listings(rentals_url, is_sale=False)
    new_rentals = set(rentals_listings) - last_rentals
    if new_rentals:
        message = "新租盤:\n" + "\n\n".join(new_rentals)
        bot.send_message(chat_id=CHANNEL_ID, text=message)
        last_rentals.update(new_rentals)

# 定時任務：每小時檢查一次
schedule.every(1).hours.do(check_and_report)

# 首次運行抓取初始數據
check_and_report()

while True:
    schedule.run_pending()
    time.sleep(1)
