import os
import logging
import sys
from datetime import datetime
from typing import Optional, Dict, Any

from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import (
    Application,
    CommandHandler,
    InlineQueryHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from config import Config
from utils import CurrencyConverter, format_amount, get_currency_symbol

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class CurrencyBot:
    """Main bot class for currency conversion"""
    
    def __init__(self):
        """Initialize the bot with configuration"""
        self.config = Config()
        self.converter = CurrencyConverter()
        self.application = None
        
        # Validate token
        if not self.config.TELEGRAM_TOKEN:
            logger.error("TELEGRAM_TOKEN not set in environment variables")
            raise ValueError("TELEGRAM_TOKEN is required")
        
        logger.info("Currency Bot initialized successfully")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        welcome_text = f"""
🌟 **Welcome to Currency50 Converter Bot!** 🌟

Hello {user.first_name}! I'm your reliable currency converter.

**📊 Available Commands:**
• `/start` - Show this welcome message
• `/help` - Get detailed help and usage guide
• `/convert` - Convert currency (format: `/convert 100 USD EUR`)
• `/rates` - Show current exchange rates
• `/list` - List all supported currencies
• `/about` - About this bot

**💡 Examples:**
• `/convert 50 USD EUR` - Convert 50 USD to EUR
• `/convert 1000 JPY GBP` - Convert 1000 JPY to GBP
• `@currency50converterbot 100 USD INR` - Use inline mode

**🔄 Features:**
• Real-time exchange rates
• 150+ currencies supported
• Inline mode support
• Rate caching for speed
• Clean, formatted responses

*Powered by ExchangeRate-API.com*
        """
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
        logger.info(f"User {user.id} started the bot")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
📖 **Currency50 Converter Bot - Help Guide**

**🔹 Quick Conversion**
Format: `/convert [amount] [from_currency] [to_currency]`
Example: `/convert 100 USD EUR`

**🔹 View Exchange Rates**
Format: `/rates` or `/rates [currency]`
Example: `/rates USD` shows rates for USD

**🔹 List Currencies**
Format: `/list` - Shows all supported currencies

**🔹 About Bot**
Format: `/about` - Bot information

**🔹 Inline Mode**
Type `@currency50converterbot 100 USD EUR` in any chat

**📝 Important Notes:**
• Use standard 3-letter currency codes (USD, EUR, GBP, etc.)
• Amount can be decimal (e.g., 15.50, 100.25)
• Rates update automatically every hour
• Case insensitive (usd = USD)

**❓ Need more help?**
Contact: [Bot Support](https://t.me/YourSupportChannel)
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def convert_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /convert command"""
        try:
            args = context.args
            
            # Validate arguments
            if len(args) != 3:
                await update.message.reply_text(
                    "❌ **Invalid format!**\n\n"
                    "Please use: `/convert [amount] [from] [to]`\n\n"
                    "Example: `/convert 100 USD EUR`\n"
                    "Example: `/convert 50.5 GBP JPY`",
                    parse_mode='Markdown'
                )
                return
            
            # Parse arguments
            try:
                amount = float(args[0])
            except ValueError:
                await update.message.reply_text(
                    "❌ **Invalid amount!**\n\n"
                    f"'{args[0]}' is not a valid number.\n"
                    "Please use a valid number (e.g., 100 or 50.5)",
                    parse_mode='Markdown'
                )
                return
            
            from_currency = args[1].upper()
            to_currency = args[2].upper()
            
            # Validate currency codes
            if not self.converter.is_valid_currency(from_currency):
                await update.message.reply_text(
                    f"❌ **Invalid currency code!**\n\n"
                    f"'{from_currency}' is not supported.\n"
                    "Use `/list` to see all supported currencies.",
                    parse_mode='Markdown'
                )
                return
            
            if not self.converter.is_valid_currency(to_currency):
                await update.message.reply_text(
                    f"❌ **Invalid currency code!**\n\n"
                    f"'{to_currency}' is not supported.\n"
                    "Use `/list` to see all supported currencies.",
                    parse_mode='Markdown'
                )
                return
            
            # Perform conversion
            result = self.converter.convert(amount, from_currency, to_currency)
            
            if result is None:
                await update.message.reply_text(
                    "❌ **Conversion failed!**\n\n"
                    "Unable to fetch exchange rates. Please try again later.",
                    parse_mode='Markdown'
                )
                return
            
            # Get currency symbols
            from_symbol = get_currency_symbol(from_currency) or from_currency
            to_symbol = get_currency_symbol(to_currency) or to_currency
            
            # Format response
            rate = result / amount
            response = f"""
💱 **Conversion Result**

**{format_amount(amount)}** {from_symbol} = **{format_amount(result)}** {to_symbol}

📊 **Exchange Rate:** 1 {from_currency} = {format_amount(rate)} {to_currency}
🕐 **Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            await update.message.reply_text(response, parse_mode='Markdown')
            logger.info(f"Converted {amount} {from_currency} to {to_currency} = {result}")
            
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            await update.message.reply_text(
                "❌ **An error occurred!**\n\n"
                "Please try again later or use `/help` for guidance.",
                parse_mode='Markdown'
            )
    
    async def rates_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /rates command"""
        try:
            # Check if specific currency requested
            base_currency = 'USD'
            if context.args and len(context.args) > 0:
                base_currency = context.args[0].upper()
                if not self.converter.is_valid_currency(base_currency):
                    await update.message.reply_text(
                        f"❌ **Invalid currency!**\n\n"
                        f"'{base_currency}' is not supported.\n"
                        "Use `/list` to see all supported currencies.",
                        parse_mode='Markdown'
                    )
                    return
            
            rates_data = self.converter.get_rates(base_currency)
            
            if not rates_data:
                await update.message.reply_text(
                    "❌ **Unable to fetch rates!**\n\n"
                    "Please try again later.",
                    parse_mode='Markdown'
                )
                return
            
            # Get rates for major currencies
            major_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CNY', 'INR', 'CAD', 'AUD', 'CHF', 'NZD']
            
            response = f"📈 **Exchange Rates (Base: {base_currency})**\n\n"
            
            for currency in major_currencies:
                if currency in rates_data:
                    rate = rates_data[currency]
                    symbol = get_currency_symbol(currency) or currency
                    response += f"• **{symbol}** ({currency}): {format_amount(rate)}\n"
            
            response += f"\n🕐 **Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Rates command error: {e}")
            await update.message.reply_text(
                "❌ **An error occurred!**\n\n"
                "Please try again later.",
                parse_mode='Markdown'
            )
    
    async def list_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /list command"""
        try:
            currencies = self.converter.get_all_currencies()
            
            if not currencies:
                await update.message.reply_text(
                    "❌ **Unable to fetch currencies!**\n\n"
                    "Please try again later.",
                    parse_mode='Markdown'
                )
                return
            
            # Group currencies alphabetically
            currencies.sort()
            
            # Split into chunks for better display
            chunks = [currencies[i:i+15] for i in range(0, len(currencies), 15)]
            
            response = "📋 **Supported Currencies**\n\n"
            response += f"Total: {len(currencies)} currencies\n\n"
            
            for chunk in chunks[:5]:  # Show first 5 chunks (75 currencies)
                response += "• " + "\n• ".join(chunk) + "\n\n"
            
            if len(chunks) > 5:
                response += f"... and {len(currencies) - 75} more currencies\n\n"
            
            response += "💡 **Tip:** Use `/convert 100 USD EUR` to convert"
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"List command error: {e}")
            await update.message.reply_text(
                "❌ **An error occurred!**\n\n"
                "Please try again later.",
                parse_mode='Markdown'
            )
    
    async def about_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /about command"""
        about_text = """
ℹ️ **About Currency50 Converter Bot**

**Version:** 1.0.0
**Creator:** Currency50 Project
**Status:** 🟢 Active

**Features:**
• Real-time currency conversion
• 150+ currencies supported
• Inline mode for quick conversions
• Exchange rate history
• Clean, user-friendly interface

**Technologies:**
• Python 3.11
• python-telegram-bot v20.7
• ExchangeRate-API.com
• Deployed on Railway

**Privacy Policy:**
We don't store any user data. All conversions are processed in real-time.

**🔗 Links:**
• [GitHub Repository](https://github.com/yourusername/currency50converterbot)
• [Report Issue](https://github.com/yourusername/currency50converterbot/issues)

*Made with ❤️ by Currency50 Team*
        """
        await update.message.reply_text(about_text, parse_mode='Markdown')
    
    async def inline_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline queries"""
        query = update.inline_query.query.strip()
        
        if not query:
            # Show help for empty query
            results = [
                InlineQueryResultArticle(
                    id="1",
                    title="💱 Quick Currency Converter",
                    description="Type: 100 USD EUR",
                    input_message_content=InputTextMessageContent(
                        "📝 **Usage:**\n"
                        "Type `100 USD EUR` to convert\n"
                        "Example: `50 GBP JPY`",
                        parse_mode='Markdown'
                    )
                )
            ]
            await update.inline_query.answer(results)
            return
        
        parts = query.split()
        
        if len(parts) != 3:
            results = [
                InlineQueryResultArticle(
                    id="1",
                    title="❌ Invalid format",
                    description="Use: [amount] [from] [to]",
                    input_message_content=InputTextMessageContent(
                        "❌ **Invalid format!**\n\n"
                        "Please use: `[amount] [from] [to]`\n"
                        "Example: `100 USD EUR`",
                        parse_mode='Markdown'
                    )
                )
            ]
            await update.inline_query.answer(results)
            return
        
        try:
            amount = float(parts[0])
            from_currency = parts[1].upper()
            to_currency = parts[2].upper()
            
            # Validate currencies
            if not (self.converter.is_valid_currency(from_currency) and 
                   self.converter.is_valid_currency(to_currency)):
                results = [
                    InlineQueryResultArticle(
                        id="1",
                        title="❌ Invalid currency",
                        description="Please check currency codes",
                        input_message_content=InputTextMessageContent(
                            "❌ **Invalid currency code!**\n\n"
                            "Please use valid 3-letter currency codes.",
                            parse_mode='Markdown'
                        )
                    )
                ]
                await update.inline_query.answer(results)
                return
            
            # Perform conversion
            result = self.converter.convert(amount, from_currency, to_currency)
            
            if result is None:
                return
            
            # Create inline result
            from_symbol = get_currency_symbol(from_currency) or from_currency
            to_symbol = get_currency_symbol(to_currency) or to_currency
            
            result_text = f"💱 {format_amount(amount)} {from_symbol} = {format_amount(result)} {to_symbol}"
            
            results = [
                InlineQueryResultArticle(
                    id="1",
                    title=result_text,
                    description=f"Rate: 1 {from_currency} = {format_amount(result/amount)} {to_currency}",
                    input_message_content=InputTextMessageContent(
                        f"{result_text}\n\n"
                        f"📊 Rate: 1 {from_currency} = {format_amount(result/amount)} {to_currency}\n"
                        f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                )
            ]
            
            await update.inline_query.answer(results)
            logger.info(f"Inline conversion: {amount} {from_currency} to {to_currency}")
            
        except ValueError:
            results = [
                InlineQueryResultArticle(
                    id="1",
                    title="❌ Invalid amount",
                    description="Please enter a valid number",
                    input_message_content=InputTextMessageContent(
                        "❌ **Invalid amount!**\n\n"
                        "Please enter a valid number.\n"
                        "Example: `100 USD EUR`",
                        parse_mode='Markdown'
                    )
                )
            ]
            await update.inline_query.answer(results)
        except Exception as e:
            logger.error(f"Inline query error: {e}")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        # Send error message to user if possible
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ **An error occurred!**\n\n"
                "Please try again later or contact support.",
                parse_mode='Markdown'
            )
    
    def setup_handlers(self):
        """Setup all command handlers"""
        self.application = Application.builder().token(self.config.TELEGRAM_TOKEN).build()
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("convert", self.convert_command))
        self.application.add_handler(CommandHandler("rates", self.rates_command))
        self.application.add_handler(CommandHandler("list", self.list_command))
        self.application.add_handler(CommandHandler("about", self.about_command))
        
        # Inline query handler
        self.application.add_handler(InlineQueryHandler(self.inline_query))
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
        
        logger.info("Handlers setup completed")
    
    def run(self):
        """Start the bot"""
        self.setup_handlers()
        
        logger.info("Starting Currency Bot...")
        logger.info(f"Bot username: @currency50converterbot")
        
        # Start the bot with long polling
        self.application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )

def main():
    """Main entry point"""
    try:
        bot = CurrencyBot()
        bot.run()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
