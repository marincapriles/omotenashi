# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Running the Application
```bash
# Main CLI application
python main.py

# With reasoning display
python main.py --reasoning

# Telegram bot
python telegram_main.py

# Run individual modules for testing
python agent.py      # Test agent independently
python tools.py      # Test mock tools
python cli.py        # Test CLI interface
```

### Testing
```bash
# Run basic end-to-end tests (no API key required)
python test_omotenashi.py

# Test knowledge base functionality
python test_knowledge_base.py

# Run comprehensive E2E validation with scenarios
python e2e_validation.py

# Evaluate tool selection accuracy
python evaluate_tool_selection.py
```

### Conversation Auditing & Monitoring
```bash
# View recent conversations with detailed reasoning
python scripts/generate_audit_report.py recent --limit 10

# Generate usage statistics
python scripts/generate_audit_report.py stats --days 7

# Export conversations to CSV for analysis
python scripts/generate_audit_report.py export --days 30

# Generate comprehensive HTML audit report
python scripts/generate_audit_report.py daily

# Direct database queries for tool usage analysis
sqlite3 logs/conversations.db "SELECT tool_name, reasoning FROM tool_usage ORDER BY timestamp DESC LIMIT 5"
```

### Environment Setup
```bash
# Install dependencies (includes async database support)
pip install -r requirements.txt

# Set up API key (required for main application)
cp .env.example .env
# Then edit .env to add ANTHROPIC_API_KEY and TELEGRAM_BOT_TOKEN
```

## High-Level Architecture

### Core Components

1. **Agent System (react_agent.py)**
   - Implements BDI (Beliefs, Desires, Intentions) framework using ReAct pattern
   - Uses LangChain's create_react_agent for intelligent reasoning and tool selection
   - Integrates with Claude 3.5 Sonnet via Anthropic API
   - System prompt embeds Omotenashi principles from config/bdi_profile.yaml

2. **Tool System (tools.py)**
   - 5 mock tools simulate hotel services: property_info, recommendations, reservation, spa, checkin_checkout
   - Each tool returns realistic JSON responses from data/mock_data.json
   - Tools are mapped in agent.py and selected based on BDI reasoning

3. **CLI Interface (cli.py)**
   - Built with Click framework for professional command-line experience
   - Special commands: help, clear, reasoning, examples
   - Color-coded output shows tools used and reasoning (when enabled)
   - Maintains conversation state within session

4. **Telegram Bot Interface (telegram_bot.py)**
   - Uses python-telegram-bot library for Telegram integration
   - Manages per-chat agent instances for session isolation
   - Supports commands: /start, /help, /clear, /examples
   - Mobile-optimized formatting with HTML support
   - Async database logging with comprehensive conversation auditing

5. **Conversation Auditing System (conversation_logger.py)**
   - SQLite database with async operations (aiosqlite) for non-blocking logging
   - Captures complete conversation context: user messages, agent responses, reasoning
   - Detailed tool usage tracking with execution times and reasoning
   - Security features: file permissions, configurable data retention
   - Performance monitoring: processing times, error rates, rate limiting

6. **Configuration Management (config_manager.py)**
   - Centralized YAML-based configuration with environment variable overrides
   - Type-safe configuration classes for all system components
   - Configurable rate limits, session timeouts, database paths, export limits
   - Production-ready settings for deployment flexibility

7. **Configuration & Data**
   - config/bdi_profile.yaml: Defines agent's beliefs, desires, intentions, and tool usage patterns
   - config/logging_config.yaml: Centralized settings for auditing, rate limiting, security
   - data/mock_data.json: Contains all mock responses for tools
   - data/property_knowledge_base.json: Extended property information for richer responses

### Workflow Architecture

The agent processes requests through a ReAct (Reasoning + Acting) pattern:
1. **Thought**: Analyzes the request and reasons about what needs to be done
2. **Action**: Selects and executes appropriate tools based on reasoning
3. **Observation**: Processes tool results and determines if more actions are needed
4. **Response**: Synthesizes all information into a warm, comprehensive response

### Key Design Principles

- **Mock-First**: All external integrations are mocked for prototype stability
- **Configuration-Driven**: BDI principles and system settings defined in YAML, not hardcoded
- **Transparent Reasoning**: Every decision traceable to Omotenashi principles with full audit trail
- **Async-First**: Non-blocking operations for production scalability
- **Security-Conscious**: File permissions, data protection, configurable privacy settings
- **Monitoring-Ready**: Comprehensive logging with performance metrics and alerting thresholds

### Database Schema

The conversation auditing system uses SQLite with two main tables:

```sql
-- Main conversation records with complete context
CREATE TABLE conversations (
    conversation_id TEXT, message_id TEXT, timestamp TEXT,
    user_id INTEGER, username TEXT, first_name TEXT, last_name TEXT,
    user_message TEXT, agent_response TEXT, agent_reasoning TEXT,
    processing_time_ms REAL, rate_limited BOOLEAN, error_occurred BOOLEAN,
    session_message_count INTEGER, conversation_length_minutes REAL,
    tools_used_json TEXT, error_details TEXT
);

-- Detailed tool usage with individual reasoning
CREATE TABLE tool_usage (
    conversation_id TEXT, message_id TEXT, tool_name TEXT,
    input_parameters_json TEXT, output TEXT, reasoning TEXT,
    execution_time_ms REAL, success BOOLEAN, error_message TEXT, timestamp TEXT
);
```

### Production Monitoring

Key metrics to monitor in production:
- **Error Rate**: Should stay below 5% (configurable in logging_config.yaml)
- **Processing Time**: Target under 3000ms average response time
- **Rate Limiting**: Should affect less than 10% of conversations
- **Tool Performance**: Monitor slow-running tools and failure rates

### Testing Strategy

- test_omotenashi.py: Basic functionality tests without API requirements
- test_telegram_bot.py: Comprehensive tests for Telegram bot functionality
- e2e_validation.py: Comprehensive scenario testing with real agent interactions
- evaluate_tool_selection.py: Measures tool selection accuracy against expected choices

### Recent Enhancements (2025-07-29)

1. **Async Database Operations**: Implemented aiosqlite for non-blocking conversation logging
2. **Detailed Tool Usage Tracking**: Fixed extraction of per-tool reasoning from ReAct agent intermediate steps
3. **Configuration Management**: Added centralized YAML-based configuration with environment overrides
4. **Security Hardening**: Database file permissions, configurable data retention, secure logging
5. **Comprehensive Auditing**: Full conversation context, tool reasoning, performance metrics
6. **Production Readiness**: Rate limiting, session management, error handling, monitoring thresholds