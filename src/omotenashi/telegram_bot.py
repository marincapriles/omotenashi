"""
Telegram Bot Interface for Omotenashi Concierge
----------------------------------------------
Provides a Telegram bot interface for the Omotenashi luxury hospitality
concierge agent, allowing guests to interact via mobile messaging.
"""

import os
import logging
import asyncio
from typing import Dict, List
from datetime import datetime, timedelta
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Import our ReAct agent and logging
from .react_agent import OmotenaashiReActAgent as OmotenaashiAgent
from .conversation_logger import get_conversation_logger, ConversationEntry, ToolUsage
from .config_manager import get_logging_config, apply_env_overrides


class OmotenaashiTelegramBot:
    """
    Telegram bot interface for the Omotenashi concierge agent.
    Manages user sessions and message routing.
    """
    
    def __init__(self, token: str):
        """
        Initialize the Telegram bot.
        
        Args:
            token: Telegram bot token from @BotFather
        """
        self.token = token
        
        # Load configuration
        self.config = apply_env_overrides(get_logging_config())
        
        # Store agent instances per chat for session management
        self.agents: Dict[int, OmotenaashiAgent] = {}
        self.agent_last_access: Dict[int, datetime] = {}
        self.session_timeout = timedelta(hours=self.config.session.timeout_hours)
        
        # Session tracking for conversation context
        self.session_start_times: Dict[int, datetime] = {}
        self.session_message_counts: Dict[int, int] = {}
        
        # Rate limiting: track message timestamps per user
        self.user_message_times: Dict[int, list] = {}
        self.rate_limit_messages = self.config.rate_limiting.messages_per_minute
        
        # Conversation logger
        self.conversation_logger = get_conversation_logger()
        
        # Configure logging
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        self.logger = logging.getLogger(__name__)
        
    def get_or_create_agent(self, chat_id: int) -> OmotenaashiAgent:
        """
        Get existing agent for chat or create new one.
        
        Args:
            chat_id: Telegram chat ID
            
        Returns:
            OmotenaashiAgent instance for this chat
        """
        # Clean up old sessions periodically
        if len(self.agents) > self.config.session.cleanup_threshold:
            self.cleanup_inactive_sessions()
        
        if chat_id not in self.agents:
            # Get API key from environment only when needed
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not configured")
            
            self.agents[chat_id] = OmotenaashiAgent(api_key)
            self.session_start_times[chat_id] = datetime.now()
            self.session_message_counts[chat_id] = 0
            self.logger.info(f"Created new agent for chat {chat_id}")
        
        # Update last access time
        self.agent_last_access[chat_id] = datetime.now()
        return self.agents[chat_id]
    
    def cleanup_inactive_sessions(self):
        """
        Remove inactive agent sessions to prevent memory leak.
        """
        current_time = datetime.now()
        inactive_chats = [
            chat_id for chat_id, last_access in self.agent_last_access.items()
            if current_time - last_access > self.session_timeout
        ]
        
        for chat_id in inactive_chats:
            if chat_id in self.agents:
                del self.agents[chat_id]
                del self.agent_last_access[chat_id]
                if chat_id in self.session_start_times:
                    del self.session_start_times[chat_id]
                if chat_id in self.session_message_counts:
                    del self.session_message_counts[chat_id]
                self.logger.info(f"Cleaned up inactive session for chat {chat_id}")
    
    def check_rate_limit(self, user_id: int) -> bool:
        """
        Check if user is within rate limits.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if within limits, False if rate limited
        """
        current_time = datetime.now()
        minute_ago = current_time - timedelta(minutes=1)
        
        # Initialize or clean old timestamps
        if user_id not in self.user_message_times:
            self.user_message_times[user_id] = []
        
        # Remove timestamps older than 1 minute
        self.user_message_times[user_id] = [
            t for t in self.user_message_times[user_id]
            if t > minute_ago
        ]
        
        # Check if within limit
        if len(self.user_message_times[user_id]) >= self.rate_limit_messages:
            return False
        
        # Add current timestamp
        self.user_message_times[user_id].append(current_time)
        return True
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /start command - send welcome message.
        """
        welcome_text = """
✨ <b>Welcome to Your Luxury Resort</b> ✨

Konnichiwa and welcome, honored guest.

I am your personal concierge, dedicated to ensuring your stay exceeds every expectation. Drawing from the Japanese tradition of Omotenashi—selfless hospitality—I am here to anticipate your needs and create unforgettable moments.

<b>How may I create an exceptional experience for you today?</b>

💡 <i>You can ask about:</i>
• Dining recommendations
• Spa services
• Activities and experiences  
• Room amenities
• Special arrangements

Type /help for more commands or simply tell me what you need.
"""
        await update.message.reply_text(
            welcome_text,
            parse_mode='HTML'
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /help command - show available commands.
        """
        help_text = """
📋 <b>Available Commands:</b>

/start - Welcome message
/help - Show this help
/clear - Start fresh conversation
/examples - Show example requests

Or simply send me a message with your request!

<b>Example requests:</b>
• "I'd like to have dinner tonight"
• "What spa treatments do you recommend?"
• "Can you tell me about the resort amenities?"
• "I need a late checkout tomorrow"
"""
        await update.message.reply_text(
            help_text,
            parse_mode='HTML'
        )
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /clear command - reset conversation.
        """
        chat_id = update.effective_chat.id
        if chat_id in self.agents:
            del self.agents[chat_id]
        
        await update.message.reply_text(
            "🔄 Conversation cleared. How may I assist you with a fresh start?",
            parse_mode='HTML'
        )
    
    async def examples_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /examples command - show example interactions.
        """
        examples_text = """
✨ <b>Example Interactions:</b>

<b>For Dining:</b>
• "I'd like Italian food tonight with a view"
• "Book me a table at your best restaurant"
• "We're celebrating an anniversary"

<b>For Activities:</b>
• "What can we do this afternoon?"
• "I want an adventure experience"
• "Any cultural activities available?"

<b>For Relaxation:</b>
• "I need to unwind after my flight"
• "What's your most popular spa treatment?"
• "Book a couples massage for tomorrow"

<b>For Special Requests:</b>
• "Can I check in early?"
• "Arrange a surprise for my partner"
• "I need a quiet place to work"
"""
        await update.message.reply_text(
            examples_text,
            parse_mode='HTML'
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle regular text messages from users with comprehensive logging.
        """
        start_time = datetime.now()
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        user_message = update.message.text
        
        # Initialize logging variables
        rate_limited = False
        error_occurred = False
        error_details = None
        agent_response = ""
        agent_reasoning = ""
        tools_used = []
        
        # Check rate limit
        if not self.check_rate_limit(user_id):
            rate_limited = True
            await update.message.reply_text(
                "⚠️ You're sending messages too quickly. Please wait a moment before trying again."
            )
            # Log rate limiting incident
            await self._log_conversation(
                update, user_message, "Rate limit exceeded", "User exceeded message rate limit",
                [], start_time, rate_limited, True, "Rate limit exceeded"
            )
            return
        
        # Validate input
        if not user_message or len(user_message.strip()) == 0:
            await update.message.reply_text(
                "Please send a message with your request."
            )
            return
        
        if len(user_message) > 1000:
            await update.message.reply_text(
                "Your message is too long. Please keep requests under 1000 characters."
            )
            return
        
        # Show typing indicator
        await context.bot.send_chat_action(
            chat_id=chat_id,
            action="typing"
        )
        
        try:
            # Get or create agent for this chat
            agent = self.get_or_create_agent(chat_id)
            
            # Increment message count for session tracking
            self.session_message_counts[chat_id] = self.session_message_counts.get(chat_id, 0) + 1
            
            # Process message through agent asynchronously
            # Run blocking operation in thread pool to avoid blocking event loop
            response = await asyncio.to_thread(agent.process, user_message)
            
            # Extract detailed reasoning and tool usage from agent callback
            callback_handler = None
            if hasattr(agent, 'agent_executor') and hasattr(agent.agent_executor, 'callbacks'):
                for callback in agent.agent_executor.callbacks or []:
                    if hasattr(callback, 'detailed_tool_usage'):
                        callback_handler = callback
                        break
            
            # Get detailed tool usage from callback handler
            if callback_handler:
                tools_used = callback_handler.detailed_tool_usage
            else:
                # Fallback: try to get from reasoning_handler directly
                if hasattr(agent, 'reasoning_handler') and hasattr(agent.reasoning_handler, 'detailed_tool_usage'):
                    tools_used = agent.reasoning_handler.detailed_tool_usage
            
            # Format response using HTML instead of Markdown for better reliability
            message_text = f"🎌 <b>Concierge Response:</b>\n\n{response.message}"
            
            # Add tools used if any
            if response.tools_used:
                tools_text = "\n\n🔧 <i>Services utilized: " + ", ".join(
                    tool.replace('_', ' ').title() for tool in response.tools_used
                ) + "</i>"
                message_text += tools_text
            
            agent_response = response.message
            agent_reasoning = response.reasoning
            
            # Handle long messages (Telegram limit is 4096 characters)
            if len(message_text) > 4000:
                # Split into multiple messages
                chunks = self._split_message(message_text, 4000)
                for chunk in chunks:
                    await update.message.reply_text(
                        chunk,
                        parse_mode='HTML'
                    )
            else:
                await update.message.reply_text(
                    message_text,
                    parse_mode='HTML'
                )
            
        except ValueError as e:
            error_occurred = True
            error_details = f"Configuration error: {str(e)}"
            agent_response = "Service configuration error. Please contact support."
            agent_reasoning = "Failed to process request due to configuration issue"
            
            self.logger.error(f"Configuration error: {e}")
            await update.message.reply_text(
                "⚠️ Service configuration error. Please contact support."
            )
            
        except ImportError as e:
            error_occurred = True
            error_details = f"Module import error: {str(e)}"
            agent_response = "Service temporarily unavailable. Please try again later."
            agent_reasoning = "Failed to process request due to missing module"
            
            self.logger.error(f"Module import error: {e}")
            await update.message.reply_text(
                "⚠️ Service temporarily unavailable. Please try again later."
            )
            
        except Exception as e:
            error_occurred = True
            error_details = f"Unexpected error: {str(e)}"
            agent_response = "I encountered an unexpected issue. Please try again."
            agent_reasoning = "Failed to process request due to unexpected error"
            
            self.logger.error(f"Unexpected error processing message: {e}", exc_info=True)
            await update.message.reply_text(
                "I apologize, but I encountered an unexpected issue. "
                "Please try again or rephrase your question."
            )
        
        finally:
            # Log the complete conversation regardless of outcome
            await self._log_conversation(
                update, user_message, agent_response, agent_reasoning,
                tools_used, start_time, rate_limited, error_occurred, error_details
            )
    
    def _escape_markdown(self, text: str) -> str:
        """
        Escape special Markdown characters to prevent formatting issues.
        """
        # Only escape the most problematic characters that break Telegram's markdown
        # Don't escape common punctuation like periods, commas, exclamation marks
        special_chars = ['*', '_', '[', ']', '`', '~']
        
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        
        return text
    
    def _split_message(self, text: str, max_length: int) -> list:
        """
        Split long messages into chunks.
        """
        chunks = []
        current_chunk = ""
        
        lines = text.split('\n')
        for line in lines:
            if len(current_chunk) + len(line) + 1 <= max_length:
                current_chunk += line + '\n'
            else:
                if current_chunk:
                    chunks.append(current_chunk.rstrip())
                current_chunk = line + '\n'
        
        if current_chunk:
            chunks.append(current_chunk.rstrip())
        
        return chunks
    
    async def _log_conversation(self, update: Update, user_message: str, agent_response: str, 
                         agent_reasoning: str, tools_used: List[ToolUsage], start_time: datetime,
                         rate_limited: bool, error_occurred: bool, error_details: str = None):
        """
        Log conversation entry to the audit database asynchronously.
        """
        try:
            end_time = datetime.now()
            processing_time_ms = (end_time - start_time).total_seconds() * 1000
            
            # Calculate session context
            chat_id = update.effective_chat.id
            session_start = self.session_start_times.get(chat_id, start_time)
            conversation_length_minutes = (end_time - session_start).total_seconds() / 60
            session_message_count = self.session_message_counts.get(chat_id, 1)
            
            # Create conversation entry
            entry = ConversationEntry(
                conversation_id=f"telegram_chat_{chat_id}",
                message_id=f"msg_{update.message.message_id}",
                timestamp=start_time,
                user_id=update.effective_user.id,
                username=update.effective_user.username,
                first_name=update.effective_user.first_name,
                last_name=update.effective_user.last_name,
                user_message=user_message,
                agent_response=agent_response,
                agent_reasoning=agent_reasoning,
                tools_used=tools_used or [],
                processing_time_ms=processing_time_ms,
                rate_limited=rate_limited,
                error_occurred=error_occurred,
                error_details=error_details,
                session_message_count=session_message_count,
                conversation_length_minutes=conversation_length_minutes
            )
            
            # Log to database asynchronously
            await self.conversation_logger.log_conversation(entry)
            
        except Exception as e:
            # Don't let logging errors break the main flow
            self.logger.error(f"Failed to log conversation: {e}", exc_info=True)
    
    def run(self):
        """
        Start the Telegram bot and begin polling for messages.
        """
        # Create application
        application = Application.builder().token(self.token).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("clear", self.clear_command))
        application.add_handler(CommandHandler("examples", self.examples_command))
        
        # Add message handler for regular text
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_message
        ))
        
        # Start bot
        self.logger.info("Starting Omotenashi Telegram bot...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """
    Main entry point for running the Telegram bot.
    """
    # Get credentials from environment
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not telegram_token:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment")
        print("\n🔧 To set up:")
        print("   1. Create a bot with @BotFather on Telegram")
        print("   2. Copy the bot token")
        print("   3. Set environment variable:")
        print("      export TELEGRAM_BOT_TOKEN='your-bot-token'")
        return
    
    if not anthropic_key:
        print("❌ ANTHROPIC_API_KEY not found in environment")
        print("\n🔧 To set up:")
        print("   1. Get your API key from https://console.anthropic.com/")
        print("   2. Set environment variable:")
        print("      export ANTHROPIC_API_KEY='your-api-key'")
        return
    
    # Create and run bot (no longer passing API key to constructor)
    bot = OmotenaashiTelegramBot(telegram_token)
    bot.run()


if __name__ == "__main__":
    main()