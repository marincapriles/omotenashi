# Telegram Bot Setup & Testing Guide

This guide will walk you through setting up and testing the Omotenashi Telegram bot on your phone.

## Prerequisites

- Python 3.8 or higher installed
- An Anthropic API key (get one at https://console.anthropic.com/)
- A Telegram account on your phone

## Step 1: Install Dependencies

First, make sure you have all the required packages:

```bash
cd /Users/carlosmarin/Omotenashi
pip install -r requirements.txt
```

If you get any errors, you may need to specifically install the Telegram package:

```bash
pip install python-telegram-bot>=20.7
```

## Step 2: Create Your Telegram Bot

1. **Open Telegram on your phone**
2. **Search for @BotFather** (it will have a blue checkmark)
3. **Start a chat** and send `/start`
4. **Create a new bot** by sending `/newbot`
5. **Choose a name** for your bot (e.g., "My Omotenashi Concierge")
6. **Choose a username** ending in 'bot' (e.g., "MyOmotenaashiBot")
7. **Copy the token** that BotFather gives you - it looks like:
   ```
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567890
   ```

## Step 3: Set Up Environment Variables

### Option A: Using .env file (Recommended)

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the .env file:
   ```bash
   nano .env  # or use your favorite editor
   ```

3. Add your credentials:
   ```
   ANTHROPIC_API_KEY=your-anthropic-api-key-here
   TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
   ```

### Option B: Export directly (Temporary)

```bash
export ANTHROPIC_API_KEY='your-anthropic-api-key-here'
export TELEGRAM_BOT_TOKEN='your-telegram-bot-token-here'
```

## Step 4: Run the Bot

```bash
python telegram_main.py
```

You should see:
```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     ██████  ███    ███  ██████  ████████ ███████ ███    ██   ║
║    ██    ██ ████  ████ ██    ██    ██    ██      ████   ██   ║
║    ██    ██ ██ ████ ██ ██    ██    ██    █████   ██ ██  ██   ║
║    ██    ██ ██  ██  ██ ██    ██    ██    ██      ██  ██ ██   ║
║     ██████  ██      ██  ██████     ██    ███████ ██   ████   ║
║                                                               ║
║            📱 TELEGRAM BOT - LUXURY AI CONCIERGE 📱           ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

✅ All systems ready. Launching Telegram bot...
📱 Once started, find your bot on Telegram and send /start
🛑 Press Ctrl+C to stop the bot

Starting Omotenashi Telegram bot...
```

## Step 5: Test Your Bot

### Find Your Bot
1. **On Telegram**, search for your bot username (e.g., @MyOmotenaashiBot)
2. **Start a chat** with your bot
3. **Send** `/start`

### Test Commands

Try these commands to test different features:

#### Basic Commands
- `/start` - Welcome message
- `/help` - Show available commands
- `/examples` - See example requests
- `/clear` - Reset your conversation

#### Test Conversations

**Simple Requests:**
```
You: Hi, I just arrived at the hotel
Bot: [Warm welcome and offers assistance]

You: What time is breakfast?
Bot: [Provides breakfast information from property_info tool]
```

**Dining Recommendations:**
```
You: I'd like to have Italian food tonight
Bot: [Provides restaurant recommendations with details]

You: Can you book a table for 2 at 7pm?
Bot: [Confirms reservation using the reservation tool]
```

**Spa Services:**
```
You: I need to relax after my flight
Bot: [Suggests spa treatments]

You: Book me a massage tomorrow at 3pm
Bot: [Confirms spa booking]
```

**Special Requests:**
```
You: Can I have a late checkout tomorrow?
Bot: [Handles check-out modification]

You: I'm celebrating my anniversary
Bot: [Offers special arrangements and suggestions]
```

### Test Error Handling

**Rate Limiting:**
- Send 10+ messages rapidly
- You should see: "⚠️ You're sending messages too quickly..."

**Long Messages:**
- Send a message with 1000+ characters
- You should see: "Your message is too long..."

**Empty Messages:**
- Send just spaces
- You should see: "Please send a message with your request."

## Step 6: Monitor the Bot

While the bot is running, you'll see logs in your terminal:

```
2024-01-15 10:30:45,123 - __main__ - INFO - Created new agent for chat 12345678
2024-01-15 10:31:02,456 - __main__ - INFO - Cleaned up inactive session for chat 87654321
```

## Troubleshooting

### Bot doesn't respond
1. Check the terminal for error messages
2. Verify your bot token is correct
3. Make sure you're messaging the right bot

### "Service configuration error"
- Your Anthropic API key might be incorrect or missing
- Check your .env file or environment variables

### "Service temporarily unavailable"
- There might be an issue with the agent module
- Check that all dependencies are installed

### Connection errors
- Check your internet connection
- Telegram might be blocked on your network

## Advanced Testing

### Multiple Users
Have friends or family members message your bot to test:
- Session isolation (each user has their own conversation)
- Concurrent message handling
- Rate limiting per user

### Long Running Test
Leave the bot running for several hours to test:
- Memory usage (check Activity Monitor or Task Manager)
- Session cleanup (inactive sessions removed after 2 hours)
- Stability over time

### Stress Testing
1. Send various types of requests rapidly
2. Use special characters in messages: `*test* _message_ [link]`
3. Send very long responses to test message splitting

## Stopping the Bot

Press `Ctrl+C` in the terminal to gracefully stop the bot.

## Next Steps

Once testing is complete, you can:
1. Deploy the bot to a cloud server for 24/7 availability
2. Add more features like inline keyboards or voice message support
3. Customize the responses and personality
4. Add persistent storage for conversation history

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Module not found" error | Run `pip install -r requirements.txt` |
| Bot created but not responding | Double-check the bot token |
| API key errors | Verify your Anthropic API key is valid |
| Markdown formatting broken | The bot now escapes special characters automatically |
| Messages too long | Bot automatically splits long messages |

Happy testing! 🎌