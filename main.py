import logging  
from telegram import Update  
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes  
# Enable logging  
logging.basicConfig(  
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  
    level=logging.INFO  
)  
logger = logging.getLogger(__name__)  
# Command handlers  
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  
    """Send a message when the command /start is issued."""  
    await update.message.reply_text(  
        "Welcome to HiuFai Monitor Bot! 🤖\n\n"  
        "Available commands:\n"  
        "/start - Show this message\n"  
        "/help - Get help\n"  
        "/latest - Get latest data\n"  
        "/sales - Get sales info\n"  
        "/rentals - Get rentals info"  
    )  
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  
    """Send a message when the command /help is issued."""  
    await update.message.reply_text(  
        "This bot monitors HiuFai data.\n\n"  
        "Use /latest, /sales, or /rentals to get information."  
    )  
async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  
    """Send latest data."""  
    await update.message.reply_text("📊 Latest data: [Your latest data here]")  
async def sales(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  
    """Send sales info."""  
    await update.message.reply_text("💰 Sales info: [Your sales data here]")  
async def rentals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  
    """Send rentals info."""  
    await update.message.reply_text("🏠 Rentals info: [Your rentals data here]")  
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  
    """Handle regular messages."""  
    await update.message.reply_text(  
        "I didn't understand that. Use /help to see available commands."  
    )  
def main() -> None:  
    """Start the bot."""  
    # Get token from environment  
    import os  
    token = os.getenv('BOT_TOKEN')  
      
    if not token:  
        logger.error("BOT_TOKEN environment variable not set!")  
        return  
      
    # Create the Application  
    application = Application.builder().token(token).build()  
    # Register command handlers  
    application.add_handler(CommandHandler("start", start))  
    application.add_handler(CommandHandler("help", help_command))  
    application.add_handler(CommandHandler("latest", latest))  
    application.add_handler(CommandHandler("sales", sales))  
    application.add_handler(CommandHandler("rentals", rentals))  
    # Register message handler for non-command messages  
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  
    # Start the bot  
    application.run_polling()  
if __name__ == '__main__':  
    main()  
