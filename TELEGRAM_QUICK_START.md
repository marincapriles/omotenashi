# Telegram Bot Quick Start (macOS)

Since you're on macOS with Python 3.9.6, here are the exact commands to get started:

## 1. Install Dependencies

```bash
cd /Users/carlosmarin/Omotenashi
python3 -m pip install -r requirements.txt
```

If you get any permission errors, you might need to use:
```bash
python3 -m pip install --user -r requirements.txt
```

## 2. Create Your Telegram Bot

1. **On your phone**, open Telegram
2. Search for **@BotFather**
3. Send `/newbot`
4. Give it a name like "My Omotenashi Concierge"
5. Give it a username ending in 'bot' like "MyOmotenaashiBot"
6. **Copy the token** (looks like: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz)

## 3. Set Up Your Credentials

```bash
# Copy the example file
cp .env.example .env

# Open it in TextEdit or nano
open -e .env
# OR
nano .env
```

Add these lines (replace with your actual keys):
```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

## 4. Run the Bot

```bash
python3 telegram_main.py
```

## 5. Test on Telegram

1. Search for your bot on Telegram (use the username you chose)
2. Send `/start`
3. Try: "I'd like to have dinner tonight"

## If You Get Errors

### "No module named 'telegram'"
```bash
python3 -m pip install python-telegram-bot>=20.7
```

### Permission denied
```bash
python3 -m pip install --user python-telegram-bot>=20.7
```

### Still having issues?
Check what's installed:
```bash
python3 -m pip list | grep telegram
```

## Stop the Bot

Press `Ctrl+C` in the terminal.