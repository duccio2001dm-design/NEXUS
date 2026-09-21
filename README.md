# NEXUS 🤖

Personal Telegram assistant.

## Current MVP
- /start
- /stato
- /trade
- /chiudi
- /analisi

The bot is designed to run with Python and GitHub Actions. Secrets such as the Telegram bot token are never stored in the repository.

## Setup
1. Create a Telegram bot with BotFather.
2. Add the token as the GitHub Actions secret `TELEGRAM_BOT_TOKEN`.
3. Install dependencies with `pip install -r requirements.txt`.
4. Run `python bot.py`.

## Project structure
- `bot.py`: Telegram entry point
- `database.py`: SQLite storage
- `config.py`: environment configuration
- `.github/workflows/nexus.yml`: automation
