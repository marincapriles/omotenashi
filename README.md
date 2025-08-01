# Omotenashi - Luxury Hospitality AI Concierge

## Overview

Omotenashi is an AI-powered luxury hospitality concierge that embodies the Japanese principle of selfless hospitality. Built with Anthropic's Claude 3.5 Sonnet and LangGraph, it provides exceptional, anticipatory service through a Beliefs, Desires, and Intentions (BDI) framework.

## Features

- **BDI-Driven Behavior**: Agent operates based on Omotenashi principles
- **5 Specialized Tools**: Property info, recommendations, reservations, spa booking, and check-in/out modifications
- **LangGraph Workflow**: Structured decision-making and tool selection
- **Elegant CLI**: Warm, welcoming command-line interface
- **Telegram Bot**: Interact with the concierge via Telegram on your phone
- **Transparent Reasoning**: Understand how the agent makes decisions

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Key

Create a `.env` file with your Anthropic API key:

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 3. Run the Application

#### CLI Interface

```bash
python main.py
```

**Optional Flags:**
- `--reasoning`: Show agent's decision-making process
- `--help`: Display all available options

#### Telegram Bot

1. Create a bot with @BotFather on Telegram
2. Add your bot token to `.env`:
   ```
   TELEGRAM_BOT_TOKEN=your-telegram-bot-token
   ```
3. Run the bot:
   ```bash
   python telegram_main.py
   ```
4. Find your bot on Telegram and send `/start`

## Usage Examples

Once running, try these interactions:

- "I'd like to have dinner tonight"
- "What spa treatments do you recommend?"
- "Tell me about the resort amenities"
- "Can I have a late checkout?"
- "Plan a romantic evening for us"

## Project Structure

```
omotenashi/
├── main.py                    # Entry point and application setup
├── telegram_main.py           # Telegram bot entry point
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── src/
│   └── omotenashi/           # Core application package
│       ├── __init__.py       # Package initialization
│       ├── agent.py          # Core AI agent with BDI framework
│       ├── react_agent.py    # ReAct agent implementation
│       ├── tools.py          # Mock tool implementations
│       ├── langchain_tools.py # LangChain tool wrappers
│       ├── cli.py            # Command-line interface
│       └── telegram_bot.py   # Telegram bot interface
├── tests/                    # All test files
│   ├── __init__.py          # Test package initialization
│   ├── test_omotenashi.py   # Main functionality tests
│   ├── test_knowledge_base.py # Knowledge base tests
│   ├── test_react_migration.py # ReAct agent tests
│   └── test_simplified_prompt.py # Prompt optimization tests
├── scripts/                  # Analysis and validation scripts
│   ├── e2e_validation.py    # End-to-end validation
│   ├── e2e_react_validation.py # ReAct agent validation
│   └── evaluate_tool_selection.py # Tool selection analysis
├── analysis/                 # Analysis results and outputs
│   ├── e2e_validation_analysis.md
│   ├── e2e_validation_results_*.json
│   ├── react_validation_results.json
│   └── FINAL_E2E_VALIDATION_RESULTS.txt
├── config/
│   └── bdi_profile.yaml     # Omotenashi principles configuration
├── data/
│   ├── mock_data.json       # Mock property and service data
│   ├── evaluation_samples.json
│   ├── e2e_test_scenarios.json
│   └── property_knowledge_base.json
└── docs/                     # Documentation
    ├── design_decisions.md
    ├── design_document.md
    ├── MIGRATION_GUIDE.md
    ├── operations_manager_enhancements.md
    ├── prototype_v0.2_implementation_proposal.txt
    ├── prototype_v0.2_implementation_proposal_refined.md
    ├── react_agent_comparison.md
    ├── CLAUDE.md
    └── # Omotenashi PRD.md
```

## Key Components

### Agent (src/omotenashi/agent.py)

- Embeds BDI principles in system prompt
- Uses LangGraph for workflow orchestration
- Processes requests through 4 nodes: analyze → select tools → execute → respond

### Tools (src/omotenashi/tools.py)

- 5 mock tools simulating real hotel services
- Returns realistic responses for prototype demonstration

### CLI (src/omotenashi/cli.py)

- Elegant interface with color-coded responses
- Shows tools used and reasoning (optional)
- Special commands: help, clear, reasoning, examples

## Development Principles

This prototype follows these principles:

- **Simplicity**: Clean, well-commented code
- **Iterative**: Built to evolve with new features
- **User-focused**: Every interaction embodies Omotenashi

## Future Enhancements

- Multi-agent team coordination
- Real API integrations
- Web interface
- Guest preference learning
- Production deployment

## License

This is a research prototype for demonstration purposes.
