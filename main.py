#!/usr/bin/env python3
"""
Omotenashi - Luxury Hospitality AI Concierge
============================================

Main entry point for the Omotenashi prototype v0.1.

This application demonstrates an AI-powered luxury concierge that embodies
the Japanese principle of Omotenashi (selfless hospitality) using:
- Anthropic's Claude 3.5 Sonnet for natural language understanding
- LangGraph for structured workflow orchestration  
- BDI (Beliefs, Desires, Intentions) framework for principled behavior

Usage:
    python main.py              # Run with default settings
    python main.py --reasoning  # Show agent reasoning by default
    python main.py --help       # Show all options

Environment:
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

# Import our CLI from the new package structure
from src.omotenashi.cli import main as cli_main


def setup_environment():
    """
    Set up the environment by loading .env file if it exists.
    This allows users to store their API key in a .env file for convenience.
    """
    # Load .env file if it exists
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print("Loaded environment from .env file")
    
    # Create .env.example if it doesn't exist
    example_path = Path(__file__).parent / '.env.example'
    if not example_path.exists():
        with open(example_path, 'w') as f:
            f.write("""# Omotenashi Environment Configuration
# Copy this file to .env and add your actual API key

# Required: Your Anthropic API key for Claude 3.5 Sonnet
ANTHROPIC_API_KEY=your-api-key-here

# Optional: Additional configuration
# LOG_LEVEL=INFO
# DEBUG_MODE=false
""")
        print(f"Created .env.example file for reference")


def check_dependencies():
    """
    Verify that all required dependencies are installed.
    Provides helpful error messages if dependencies are missing.
    """
    required_packages = {
        'anthropic': 'Anthropic API client',
        'click': 'CLI framework',
        'yaml': 'Configuration parsing',
        'colorama': 'Terminal colors'
    }
    
    # Optional packages for different agent implementations
    optional_packages = {
        'langchain': 'LangChain framework for ReAct agent',
        'langchain_anthropic': 'LangChain Anthropic integration',
        'langgraph': 'Workflow orchestration (original agent)'
    }
    
    missing_packages = []
    
    for package, description in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(f"{package} ({description})")
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Please install dependencies with:")
        print("   pip install -r requirements.txt")
        return False
    
    # Check optional packages and provide information
    missing_optional = []
    for package, description in optional_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing_optional.append(f"{package} ({description})")
    
    if missing_optional:
        print("\n⚠️  Optional packages not installed:")
        for package in missing_optional:
            print(f"   - {package}")
        print("\n   The application will use available implementations.")
    
    return True


def display_banner():
    """
    Display a beautiful ASCII banner for the application.
    Sets the tone for the luxury experience.
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
    ║              ♨ LUXURY HOSPITALITY AI CONCIERGE ♨              ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    
                  Embodying the Art of Japanese Hospitality
                              Version 0.1.0
    """
    print(banner)


def main():
    """
    Main entry point for the Omotenashi application.
    Handles setup, validation, and launches the CLI.
    """
    # Display banner
    display_banner()
    
    # Set up environment
    setup_environment()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Verify API key is available
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n❌ ANTHROPIC_API_KEY not found in environment")
        print("\n🔧 To set up:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your Anthropic API key to .env")
        print("   3. Run the application again")
        print("\n📚 Get your API key at: https://console.anthropic.com/")
        sys.exit(1)
    
    # Everything is ready - launch the CLI
    print("\n✅ All systems ready. Launching Omotenashi...\n")
    
    try:
        # Hand off to the CLI
        cli_main()
    except KeyboardInterrupt:
        print("\n\n👋 Sayonara! Thank you for visiting.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        print("Please check your configuration and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()