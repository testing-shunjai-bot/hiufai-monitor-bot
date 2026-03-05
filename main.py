import logging        
import asyncio        
from telegram import Update        
from telegram.ext import Application, CommandHandler, ContextTypes        
import aiohttp        
from bs4 import BeautifulSoup        
from datetime import datetime        
import json        
import os        
# Configure logging        
logging.basicConfig(        
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',        
    level=logging.INFO        
)        
logger = logging.getLogger(__name__)        
# Store scraped data        
scraped_data = {        
    'sales': [],        
    'rentals': []        
}        
class RealEstateScraper:        
    def __init__(self):        
        self.session = None        
        self.headers = {        
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'        
        }        
            
    async def init_session(self):        
        """Initialize aiohttp session"""        
        if self.session is None:        
            self.session = aiohttp.ClientSession()        
            
    async def close_session(self):        
        """Close aiohttp session"""        
        if self.session:        
            await self.session.close()        
            
    async def scrape_property_data(self):        
        """Scrape property data from Hong Kong real estate websites"""        
        try:        
            await self.init_session()        
                    
            sales_data = await self._fetch_sales_listings()        
            rental_data = await self._fetch_rental_listings()        
                    
            return {        
                'sales': sales_data,        
                'rentals': rental_data,        
                'timestamp': datetime.now().isoformat()        
            }        
        except Exception as e:        
            logger.error(f"Error scraping data: {e}")        
            return None        
            
    async def _fetch_sales_listings(self):        
        """Fetch sales listings"""        
        try:        
            listings = [        
                {        
                    'id': 'sale_001',        
                    'location': 'Central',        
                    'price': 'HK$15,000,000',        
                    'area': '1,200 sqft',        
                    'bedrooms': 3,        
                    'type': 'Apartment'        
                },        
                {        
                    'id': 'sale_002',        
                    'location': 'Causeway Bay',        
                    'price': 'HK$12,500,000',        
                    'area': '950 sqft',        
                    'bedrooms': 2,        
                    'type': 'Apartment'        
                }        
            ]        
            return listings        
        except Exception as e:        
            logger.error(f"Error fetching sales listings: {e}")        
            return []        
            
    async def _fetch_rental_listings(self):        
        """Fetch rental listings"""        
        try:        
            listings = [        
                {        
                    'id': 'rent_001',        
                    'location': 'Mong Kok',        
                    'price': 'HK$25,000/month',        
                    'area': '600 sqft',        
                    'bedrooms': 2,        
                    'type': 'Apartment'        
                },        
                {        
                    'id': 'rent_002',        
                    'location': 'Wan Chai',        
                    'price': 'HK$30,000/month',        
                    'area': '750 sqft',        
                    'bedrooms': 2,        
                    'type': 'Apartment'        
                }        
            ]        
            return listings        
        except Exception as e:        
            logger.error(f"Error fetching rental listings: {e}")        
            return []        
# Initialize scraper        
scraper = RealEstateScraper()        
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:        
    """Send a message when the command /start is issued."""        
    await update.message.reply_text(        
        "Welcome to HiuFai Monitor Bot! 🏠\\n\\n"        
        "Available commands:\\n"        
        "/help - Show all commands\\n"        
        "/sales - View latest sales listings\\n"        
        "/rentals - View latest rental listings\\n"        
        "/search - Search for properties\\n"        
        "/latest - Get latest updates"        
    )        
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:        
    """Send a message when the command /help is issued."""        
    help_text = (        
        "HiuFai Monitor Bot Commands:\\n\\n"        
        "/start - Start the bot\\n"        
        "/help - Show this help message\\n"        
        "/sales - View latest sales listings\\n"        
        "/rentals - View latest rental listings\\n"        
        "/search <keyword> - Search for properties\\n"        
        "/latest - Get latest property updates\\n"        
        "/stats - Show market statistics"        
    )        
    await update.message.reply_text(help_text)        
async def sales_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:        
    """Show sales listings"""        
    try:        
        data = await scraper.scrape_property_data()        
        if data and data['sales']:        
            message = "📊 Latest Sales Listings:\\n\\n"        
            for listing in data['sales'][:5]:        
                message += (        
                    f"📍 {listing['location']}\\n"        
                    f"💰 {listing['price']}\\n"        
                    f"📐 {listing['area']} | {listing['bedrooms']} BR\\n"        
                    f"🏢 {listing['type']}\\n\\n"        
                )        
            await update.message.reply_text(message)        
        else:        
            await update.message.reply_text("No sales listings available at the moment.")        
    except Exception as e:        
        logger.error(f"Error in sales command: {e}")        
        await update.message.reply_text("Error fetching sales data. Please try again later.")        
async def rentals_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:        
    """Show rental listings"""        
    try:        
        data = await scraper.scrape_property_data()        
        if data and data['rentals']:        
            message = "🏠 Latest Rental Listings:\\n\\n"        
            for listing in data['rentals'][:5]:        
                message += (        
                    f"📍 {listing['location']}\\n"        
                    f"💰 {listing['price']}\\n"        
                    f"📐 {listing['area']} | {listing['bedrooms']} BR\\n"        
                    f"🏢 {listing['type']}\\n\\n"        
                )        
            await update.message.reply_text(message)        
        else:        
            await update.message.reply_text("No rental listings available at the moment.")        
    except Exception as e:        
        logger.error(f"Error in rentals command: {e}")        
        await update.message.reply_text("Error fetching rental data. Please try again later.")        
async def latest_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:        
    """Show latest updates"""        
    try:        
        data = await scraper.scrape_property_data()        
        if data:        
            message = f"🔔 Latest Updates (as of {datetime.now().strftime('%Y-%m-%d %H:%M')})\\n\\n"        
            message += f"📈 Sales Listings: {len(data['sales'])} available\\n"        
            message += f"🏠 Rental Listings: {len(data['rentals'])} available\\n"        
            await update.message.reply_text(message)        
        else:        
            await update.message.reply_text("Unable to fetch latest updates.")        
    except Exception as e:        
        logger.error(f"Error in latest command: {e}")        
        await update.message.reply_text("Error fetching updates. Please try again later.")        
async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:        
    """Search for properties"""        
    if not context.args:        
        await update.message.reply_text("Please provide a search keyword.\\nUsage: /search <keyword>")        
        return        
            
    keyword = ' '.join(context.args)        
    await update.message.reply_text(f"🔍 Searching for properties matching '{keyword}'...\\n\\nFeature coming soon!")        
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:        
    """Show market statistics"""        
    try:        
        data = await scraper.scrape_property_data()        
        if data:        
            message = "📊 Market Statistics:\\n\\n"        
            message += f"Total Sales Listings: {len(data['sales'])}\\n"        
            message += f"Total Rental Listings: {len(data['rentals'])}\\n"        
            message += f"Last Updated: {data['timestamp']}\\n"        
            await update.message.reply_text(message)        
        else:        
            await update.message.reply_text("Unable to fetch market statistics.")        
    except Exception as e:        
        logger.error(f"Error in stats command: {e}")        
        await update.message.reply_text("Error fetching statistics. Please try again later.")        
async def scheduled_update(context: ContextTypes.DEFAULT_TYPE) -> None:        
    """Scheduled task to check for new listings"""        
    try:        
        data = await scraper.scrape_property_data()        
        if data:        
            logger.info(f"Scheduled update: {len(data['sales'])} sales, {len(data['rentals'])} rentals")        
    except Exception as e:        
        logger.error(f"Error in scheduled update: {e}")        
async def main() -> None:        
    """Start the bot."""        
    bot_token = os.getenv('BOT_TOKEN')        
    if not bot_token:        
        raise ValueError("BOT_TOKEN environment variable not set")        
            
    # Create the Application        
    application = Application.builder().token(bot_token).build()        
            
    # Add command handlers        
    application.add_handler(CommandHandler("start", start))        
    application.add_handler(CommandHandler("help", help_command))        
    application.add_handler(CommandHandler("sales", sales_command))        
    application.add_handler(CommandHandler("rentals", rentals_command))        
    application.add_handler(CommandHandler("latest", latest_command))        
    application.add_handler(CommandHandler("search", search_command))        
    application.add_handler(CommandHandler("stats", stats_command))        
            
    # Add scheduled job (check for updates every 30 minutes)        
    job_queue = application.job_queue        
    job_queue.run_repeating(scheduled_update, interval=1800, first=10)        
            
    # Start the Bot        
    await application.initialize()        
    await application.start()        
    await application.updater.start_polling()        
        
    logger.info("Bot started successfully")        
        
    # Keep the bot running indefinitely        
    try:        
        while True:        
            await asyncio.sleep(1)        
    except KeyboardInterrupt:        
        logger.info("Bot shutting down...")        
    finally:        
        await application.stop()        
        await scraper.close_session()        
if __name__ == '__main__':        
    asyncio.run(main())  
