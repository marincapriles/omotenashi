"""
Tests for Telegram Bot Interface
---------------------------------
Unit tests for the Omotenashi Telegram bot implementation.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from telegram import Update, Chat, Message, User

# Import the bot class
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.omotenashi.telegram_bot import OmotenaashiTelegramBot


class TestTelegramBot:
    """Test suite for OmotenaashiTelegramBot."""
    
    @pytest.fixture
    def bot(self):
        """Create bot instance for testing."""
        return OmotenaashiTelegramBot("test_token")
    
    @pytest.fixture
    def mock_update(self):
        """Create mock Update object."""
        update = Mock(spec=Update)
        update.effective_chat = Mock(spec=Chat)
        update.effective_chat.id = 12345
        update.effective_user = Mock(spec=User)
        update.effective_user.id = 67890
        update.message = Mock(spec=Message)
        update.message.text = "Test message"
        update.message.reply_text = AsyncMock()
        return update
    
    @pytest.fixture
    def mock_context(self):
        """Create mock context."""
        context = Mock()
        context.bot = Mock()
        context.bot.send_chat_action = AsyncMock()
        return context
    
    def test_initialization(self, bot):
        """Test bot initialization."""
        assert bot.token == "test_token"
        assert bot.agents == {}
        assert bot.agent_last_access == {}
        assert bot.session_timeout == timedelta(hours=2)
        assert bot.rate_limit_messages == 10
    
    def test_get_or_create_agent_new(self, bot):
        """Test creating new agent for chat."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'}):
            with patch('src.omotenashi.telegram_bot.OmotenaashiAgent') as mock_agent:
                agent = bot.get_or_create_agent(123)
                
                # Should create new agent
                mock_agent.assert_called_once_with('test_key')
                assert 123 in bot.agents
                assert 123 in bot.agent_last_access
    
    def test_get_or_create_agent_existing(self, bot):
        """Test getting existing agent for chat."""
        # Pre-create agent
        mock_agent = Mock()
        bot.agents[123] = mock_agent
        bot.agent_last_access[123] = datetime.now()
        
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'}):
            agent = bot.get_or_create_agent(123)
            
            # Should return existing agent
            assert agent is mock_agent
    
    def test_get_or_create_agent_no_api_key(self, bot):
        """Test error when API key not configured."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY not configured"):
                bot.get_or_create_agent(123)
    
    def test_cleanup_inactive_sessions(self, bot):
        """Test cleanup of inactive sessions."""
        # Create sessions with different last access times
        current_time = datetime.now()
        
        # Active session (1 hour ago)
        bot.agents[1] = Mock()
        bot.agent_last_access[1] = current_time - timedelta(hours=1)
        
        # Inactive session (3 hours ago)
        bot.agents[2] = Mock()
        bot.agent_last_access[2] = current_time - timedelta(hours=3)
        
        # Run cleanup
        bot.cleanup_inactive_sessions()
        
        # Active session should remain
        assert 1 in bot.agents
        assert 1 in bot.agent_last_access
        
        # Inactive session should be removed
        assert 2 not in bot.agents
        assert 2 not in bot.agent_last_access
    
    def test_rate_limit_check_within_limit(self, bot):
        """Test rate limiting allows messages within limit."""
        user_id = 123
        
        # Send messages within limit
        for i in range(5):
            assert bot.check_rate_limit(user_id) is True
        
        # Should have 5 timestamps
        assert len(bot.user_message_times[user_id]) == 5
    
    def test_rate_limit_check_exceeds_limit(self, bot):
        """Test rate limiting blocks excessive messages."""
        user_id = 123
        
        # Send messages up to limit
        for i in range(10):
            bot.check_rate_limit(user_id)
        
        # Next message should be blocked
        assert bot.check_rate_limit(user_id) is False
    
    def test_rate_limit_cleanup_old_timestamps(self, bot):
        """Test rate limiter cleans up old timestamps."""
        user_id = 123
        current_time = datetime.now()
        
        # Add old timestamps
        bot.user_message_times[user_id] = [
            current_time - timedelta(minutes=2),  # Old
            current_time - timedelta(seconds=30)  # Recent
        ]
        
        # Check rate limit should clean old timestamps
        assert bot.check_rate_limit(user_id) is True
        
        # Should have 2 timestamps (1 old removed, 1 kept, 1 new)
        assert len(bot.user_message_times[user_id]) == 2
    
    @pytest.mark.asyncio
    async def test_start_command(self, bot, mock_update, mock_context):
        """Test /start command sends welcome message."""
        await bot.start_command(mock_update, mock_context)
        
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "Welcome to The Grand Omotenashi Resort" in call_args[0][0]
        assert call_args[1]['parse_mode'] == 'Markdown'
    
    @pytest.mark.asyncio
    async def test_help_command(self, bot, mock_update, mock_context):
        """Test /help command."""
        await bot.help_command(mock_update, mock_context)
        
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "Available Commands" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_clear_command(self, bot, mock_update, mock_context):
        """Test /clear command removes agent."""
        # Add agent to cache
        chat_id = mock_update.effective_chat.id
        bot.agents[chat_id] = Mock()
        
        await bot.clear_command(mock_update, mock_context)
        
        # Agent should be removed
        assert chat_id not in bot.agents
        mock_update.message.reply_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_message_rate_limited(self, bot, mock_update, mock_context):
        """Test message handling when rate limited."""
        # Mock rate limit to return False
        bot.check_rate_limit = Mock(return_value=False)
        
        await bot.handle_message(mock_update, mock_context)
        
        # Should send rate limit message
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "too quickly" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_handle_message_empty(self, bot, mock_update, mock_context):
        """Test handling empty message."""
        mock_update.message.text = "   "  # Whitespace only
        
        await bot.handle_message(mock_update, mock_context)
        
        # Should ask for message
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "Please send a message" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_handle_message_too_long(self, bot, mock_update, mock_context):
        """Test handling message that's too long."""
        mock_update.message.text = "x" * 1001  # Over 1000 chars
        
        await bot.handle_message(mock_update, mock_context)
        
        # Should reject long message
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "too long" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_handle_message_success(self, bot, mock_update, mock_context):
        """Test successful message handling."""
        # Mock agent and response
        mock_agent = Mock()
        mock_response = Mock(
            message="Welcome to our resort!",
            tools_used=["recommendations"],
            reasoning="Guest needs assistance"
        )
        mock_agent.process_message = Mock(return_value=mock_response)
        
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'}):
            with patch.object(bot, 'get_or_create_agent', return_value=mock_agent):
                with patch('asyncio.to_thread', new_callable=AsyncMock) as mock_thread:
                    mock_thread.return_value = mock_response
                    
                    await bot.handle_message(mock_update, mock_context)
        
        # Should show typing indicator
        mock_context.bot.send_chat_action.assert_called_once()
        
        # Should process message
        mock_thread.assert_called_once()
        
        # Should send response
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "Concierge Response" in call_args[0][0]
        assert "Welcome to our resort" in call_args[0][0]
        assert "recommendations" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_handle_message_error(self, bot, mock_update, mock_context):
        """Test error handling in message processing."""
        with patch.object(bot, 'get_or_create_agent', side_effect=Exception("Test error")):
            await bot.handle_message(mock_update, mock_context)
        
        # Should send error message
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "unexpected issue" in call_args[0][0]
    
    def test_escape_markdown(self, bot):
        """Test Markdown escaping."""
        text = "Hello *world* with _emphasis_ and [link](url)"
        escaped = bot._escape_markdown(text)
        
        assert escaped == "Hello \\*world\\* with \\_emphasis\\_ and \\[link\\]\\(url\\)"
    
    def test_split_message(self, bot):
        """Test message splitting for long messages."""
        # Create long message
        long_text = "Line 1\n" + ("x" * 100 + "\n") * 50  # ~5000 chars
        
        chunks = bot._split_message(long_text, 1000)
        
        # Should split into multiple chunks
        assert len(chunks) > 1
        
        # Each chunk should be under limit
        for chunk in chunks:
            assert len(chunk) <= 1000
        
        # Combined chunks should preserve content
        combined = "\n".join(chunks)
        assert long_text.strip() == combined


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])