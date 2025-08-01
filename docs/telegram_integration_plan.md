# Telegram Bot Integration Plan for Omotenashi

## Overview

This document outlines the plan to add Telegram bot functionality to the Omotenashi luxury hospitality AI concierge, allowing users to interact with the agent through their mobile phones.

## Current Architecture Analysis

### Existing Components
- **Main Entry Point**: `main.py` - Sets up environment and launches CLI
- **CLI Interface**: `src/omotenashi/cli.py` - Handles terminal interactions
- **Agent Core**: `src/omotenashi/agent.py` - BDI-based agent using LangGraph workflow
- **Tools**: Mock implementations for property info, recommendations, reservations, spa, check-in/out
- **Configuration**: BDI profile in `config/bdi_profile.yaml`

### Key Observations
1. The agent is well-separated from the interface layer
2. Agent has a clean API: `process_message(user_message) -> AgentResponse`
3. CLI manages session state and conversation history
4. Agent supports conversation reset functionality

## Proposed Telegram Integration

### Architecture Design

```
┌─────────────────┐     ┌─────────────────┐
│   Telegram      │     │      CLI        │
│   Interface     │     │   Interface     │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     │
              ┌──────▼──────┐
              │ Omotenashi  │
              │    Agent    │
              │   (Core)    │
              └──────┬──────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼────┐            ┌────▼────┐
    │  Tools  │            │   BDI   │
    │         │            │ Profile │
    └─────────┘            └─────────┘
```

### Implementation Components

#### 1. Telegram Bot Module (`src/omotenashi/telegram_bot.py`)

**Key Features:**
- Uses python-telegram-bot library
- Manages per-chat agent instances (session management)
- Handles Telegram-specific commands (/start, /help, /clear, /examples)
- Formats responses for mobile viewing with Markdown
- Shows typing indicators for better UX

**Core Methods:**
- `get_or_create_agent(chat_id)` - Session management
- `handle_message()` - Process user messages
- Command handlers for Telegram bot commands

#### 2. Telegram Launcher Script (`telegram_main.py`)

```python
#!/usr/bin/env python3
"""
Telegram Bot launcher for Omotenashi
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from src.omotenashi.telegram_bot import main as telegram_main

def setup_environment():
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)

if __name__ == "__main__":
    setup_environment()
    telegram_main()
```

#### 3. Environment Configuration Updates

Add to `.env.example`:
```
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your-bot-token-here
```

#### 4. Requirements Updates

Add to `requirements.txt`:
```
python-telegram-bot>=20.7
```

### Implementation Steps

1. **Create Telegram Bot Module**
   - Implement `OmotenaashiTelegramBot` class
   - Add command handlers and message processing
   - Implement session management by chat ID

2. **Create Launcher Script**
   - Simple entry point for running the Telegram bot
   - Environment setup and validation

3. **Update Documentation**
   - Add Telegram setup instructions to README
   - Update CLAUDE.md with Telegram commands

4. **Testing Approach**
   - Manual testing with a test bot token
   - Verify session isolation between users
   - Test all commands and error handling

### Key Design Decisions

1. **Parallel Interfaces**: Both CLI and Telegram can run simultaneously without interference

2. **Session Management**: Each Telegram chat gets its own agent instance to maintain conversation context

3. **Minimal Changes**: No modifications needed to existing agent or tool code

4. **Mobile-Optimized**: Responses formatted with Markdown for better mobile readability

5. **Error Handling**: Graceful error messages for API failures or processing errors

### Security Considerations

- Bot token and API key stored in environment variables
- No user data persistence (conversations only in memory)
- Each chat isolated with its own agent instance

### Future Enhancements

1. **Inline Keyboards**: Add buttons for common actions
2. **Rich Media**: Send images for property/dining recommendations
3. **Voice Messages**: Process voice notes through speech-to-text
4. **Persistent Sessions**: Optional Redis/database for conversation persistence
5. **Multi-language Support**: Detect user language and respond accordingly

## Setup Instructions for Users

1. **Create a Telegram Bot**
   - Message @BotFather on Telegram
   - Use `/newbot` command
   - Choose name and username
   - Copy the bot token

2. **Configure Environment**
   ```bash
   export TELEGRAM_BOT_TOKEN='your-bot-token'
   export ANTHROPIC_API_KEY='your-api-key'
   ```

3. **Install Dependencies**
   ```bash
   pip install python-telegram-bot>=20.7
   ```

4. **Run the Bot**
   ```bash
   python telegram_main.py
   ```

5. **Start Chatting**
   - Find your bot on Telegram by username
   - Send `/start` to begin
   - Ask questions naturally

## Benefits

- **Mobile Access**: Interact with Omotenashi anywhere
- **Natural Interface**: Familiar messaging experience
- **Always Available**: Bot runs 24/7 on a server
- **Multi-User**: Supports concurrent conversations
- **Rich Formatting**: Markdown support for elegant responses