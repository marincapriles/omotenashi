#!/usr/bin/env python3
"""
Telegram Bot launcher for Omotenashi Luxury Hospitality AI Concierge
====================================================================

This is the main entry point for running the Omotenashi concierge
as a Telegram bot, allowing guests to interact via mobile messaging.

Usage:
    python telegram_main.py

Environment:
    TELEGRAM_BOT_TOKEN: Required bot token from @BotFather
    ANTHROPIC_API_KEY: Required API key for Claude 3.5 Sonnet

Author: Omotenashi Development Team
Version: 0.1.0
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

# Import our Telegram bot
from src.omotenashi.telegram_bot import main as telegram_main


def setup_environment():
    """
    Set up the environment by loading .env file if it exists.
    This allows users to store their credentials in a .env file.
    """
    # Load .env file if it exists
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print("Loaded environment from .env file")


def display_banner():
    """
    Display a banner for the Telegram bot.
    """
    banner = """
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
    
                  Bringing Omotenashi to Your Mobile Device
                              Version 0.1.0
    """
    print(banner)


def validate_environment():
    """
    Validate that all required environment variables are set.
    
    Returns:
        bool: True if environment is valid, False otherwise
    """
    missing_vars = []
    
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        missing_vars.append("TELEGRAM_BOT_TOKEN")
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        missing_vars.append("ANTHROPIC_API_KEY")
    
    if missing_vars:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("\n🔧 To set up:")
        
        if "TELEGRAM_BOT_TOKEN" in missing_vars:
            print("\n   For Telegram Bot Token:")
            print("   1. Open Telegram and search for @BotFather")
            print("   2. Send /newbot and follow the instructions")
            print("   3. Copy the bot token")
            print("   4. Set: export TELEGRAM_BOT_TOKEN='your-bot-token'")
        
        if "ANTHROPIC_API_KEY" in missing_vars:
            print("\n   For Anthropic API Key:")
            print("   1. Visit https://console.anthropic.com/")
            print("   2. Create or copy your API key")
            print("   3. Set: export ANTHROPIC_API_KEY='your-api-key'")
        
        print("\n💡 Tip: Add these to your .env file for persistence")
        return False
    
    return True


def main():
    """
    Main entry point for the Telegram bot.
    """
    # Display banner
    display_banner()
    
    # Set up environment
    setup_environment()
    
    # Validate environment
    if not validate_environment():
        sys.exit(1)
    
    print("\n✅ All systems ready. Launching Telegram bot...")
    print("📱 Once started, find your bot on Telegram and send /start")
    print("🛑 Press Ctrl+C to stop the bot\n")
    
    try:
        # Launch the Telegram bot
        telegram_main()
    except KeyboardInterrupt:
        print("\n\n👋 Telegram bot stopped. Sayonara!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("Please check your configuration and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()