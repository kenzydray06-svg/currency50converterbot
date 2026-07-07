# Currency50 Converter Bot

A powerful Telegram bot for currency conversion with inline support.

## Features

- 💱 Real-time currency conversion
- 🌍 150+ currencies supported
- 📱 Inline mode for quick conversions
- 📊 Exchange rate display
- ⚡ Rate caching for speed
- 🎨 Clean, formatted responses

## Commands

- `/start` - Welcome message
- `/help` - Help guide
- `/convert [amount] [from] [to]` - Convert currency
- `/rates` - Show exchange rates
- `/list` - List all currencies
- `/about` - About the bot

## Deployment

### Prerequisites

- Python 3.8+
- Telegram Bot Token
- GitHub Account
- Railway Account

### Deploy on Railway

1. Fork this repository
2. Create bot on Telegram via @BotFather
3. Deploy on Railway
4. Set environment variables
5. Start the bot

## Environment Variables

| Variable | Description |
|----------|-------------|
| TELEGRAM_TOKEN | Your bot token from @BotFather |
| CURRENCY_API_URL | Currency API endpoint |
| CACHE_DURATION | Cache duration in seconds |
| LOG_LEVEL | Logging level |

## License

MIT License
