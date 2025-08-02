# Omotenashi - Agentic Infrastructure for Next-Generation Hospitality

## Overview

Omotenashi is pioneering the future of hospitality through an agentic AI platform that embodies the Japanese principle of anticipatory, wholehearted service. We're building a proprietary BDI-ToM (Beliefs, Desires, Intentions + Theory of Mind) architecture that serves as the essential hospitality intelligence layer between general-purpose AI assistants and hotel systems.

## 🎯 Vision

To become the indispensable hospitality intelligence that every AI assistant relies on when users need hotel services - from ChatGPT to Claude to Alexa and beyond.

## 🏗️ Architecture Evolution

### Current: ReAct Agent with LangChain
- Claude 3.5 Sonnet-powered concierge
- 5 specialized hospitality tools
- BDI principles embedded in prompts

### In Development: Proprietary BDI-ToM Architecture
- **Belief Network**: Dynamic guest understanding with cultural awareness
- **Desire Engine**: Hospitality-specific goal prioritization  
- **Intention Planner**: Multi-step service orchestration
- **Theory of Mind**: Guest mental state modeling for anticipatory service
- **Tool Selection System**: Explainable, belief-aligned tool choices

## 🚀 Implementation Roadmap (9 Weeks)

### Phase 1: Foundation (Weeks 1-2)
- ✅ Minimal Viable BeliefNetwork for 2 flagship scenarios
- 🔄 DesireEngine with belief integration
- 🔄 Tool selection with affordance embeddings

### Phase 2: Intelligence Layer (Weeks 3-4)
- Theory of Mind integration
- Enhanced tool selection with guest mental models
- Pattern library for hospitality scenarios

### Phase 3: Anticipation Engine (Weeks 5-6)
- Pattern composition system
- Anticipatory service capabilities
- Expand from 2 to 10 scenarios

### Phase 4: Production Platform (Weeks 7-9)
- Custom workflow engine replacing LangGraph
- Production monitoring and SDK packaging
- Performance optimization (<2s responses)

## 🎭 Flagship Scenarios

### 1. Cultural Adaptation Concierge
**Japanese Business Traveler at Microsoft Conference**
- Formal communication style (keigo patterns)
- Business amenity prioritization
- Cultural dietary considerations
- Anticipatory business services

### 2. Anniversary Anticipation Service
**Couple's 10th Anniversary Celebration**
- Romantic atmosphere coordination
- Special moment orchestration
- Surprise element management
- Emotional resonance optimization

## Features

### Current Capabilities
- **BDI-Driven Behavior**: Agent operates based on Omotenashi principles
- **5 Specialized Tools**: Property info, recommendations, reservations, spa booking, check-in/out
- **Multi-Interface**: CLI and Telegram bot
- **Transparent Reasoning**: Explainable decision-making
- **Conversation Auditing**: Comprehensive logging and analytics

### Coming Soon
- **Belief-Based Personalization**: Dynamic guest preference learning
- **Anticipatory Service**: Predict needs before they're expressed
- **Cultural Intelligence**: Adapt communication and service style
- **Multi-Property Network Effects**: Learn from millions of interactions
- **Tool Effectiveness Learning**: Continuously improve selections

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
├── main.py                    # Entry point (current system)
├── telegram_main.py           # Telegram bot entry point
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── CLAUDE.md                  # Development guidance
├── src/
│   └── omotenashi/
│       ├── __init__.py
│       ├── agent.py          # Current ReAct agent
│       ├── react_agent.py    
│       ├── tools.py          
│       ├── cli.py            
│       ├── telegram_bot.py   
│       └── proprietary/      # New BDI-ToM architecture
│           ├── core/
│           │   ├── belief_network.py    # ✅ Implemented
│           │   ├── desire_engine.py     # 🔄 In Progress
│           │   ├── intention_planner.py # 📋 Planned
│           │   ├── theory_of_mind.py    # 📋 Planned
│           │   └── tool_selection.py    # ✅ Implemented
│           ├── hospitality/
│           │   ├── patterns.py          # 🔄 In Progress
│           │   ├── anticipation.py      # 📋 Planned
│           │   └── cultural_adapter.py  # 📋 Planned
│           ├── testing/
│           │   └── flagship_scenarios.yaml # ✅ Implemented
│           └── utils/
│               ├── pattern_testing.py   # ✅ Implemented
│               └── trace_logger.py      # ✅ Implemented
├── tests/
│   ├── proprietary/
│   │   └── unit/
│   │       └── test_belief_network.py  # ✅ Implemented
│   └── [existing tests]
├── scripts/
│   ├── setup_project_board.md          # Project management
│   └── create_all_issues.sh            # GitHub automation
├── docs/
│   └── platform/
│       ├── proprietary-bdi-implementation-workplan-v3.md  # Current plan
│       └── [product memos and feedback]
└── [existing folders]
```

## Key Components

### Current System (LangChain/ReAct)
- **Agent**: ReAct pattern with BDI principles in prompts
- **Tools**: 5 mock hotel service tools
- **Interfaces**: CLI and Telegram bot

### Proprietary BDI-ToM Architecture (In Development)

#### BeliefNetwork (✅ Implemented)
- Dynamic belief updates from observations
- Confidence scoring and temporal decay
- Cultural and contextual understanding
- Pattern-based inference

#### Tool Selection System (✅ Implemented)
- Tool affordance embeddings
- Belief-aligned selection
- Explainable reasoning
- Effectiveness tracking

#### Pattern Testing Framework (✅ Implemented)
- Testable hospitality patterns
- Measurable outcomes
- Failover strategies
- Confidence adjustments

## Development Approach

### Three Parallel Tracks
- **Track A**: Core BDI Development
- **Track B**: Hospitality Patterns
- **Track C**: Platform Infrastructure

### Validation Gates
- Daily testing against flagship scenarios
- A/B testing current vs new system
- Performance benchmarks (<2s response)
- User satisfaction metrics

### Innovation Focus
- Tool selection reasoning algorithms
- Pattern composition system
- Anticipatory service engine
- Cultural adaptation models

## Contributing

We're building the future of hospitality AI. Key areas:

1. **BDI Components**: Help implement DesireEngine and IntentionPlanner
2. **Hospitality Patterns**: Define new service patterns
3. **Testing**: Expand test scenarios beyond flagship ones
4. **Performance**: Optimize for <2s responses

See [GitHub Issues](https://github.com/marincapriles/omotenashi/issues) for current tasks.

## License

This is a research prototype for demonstration purposes.
