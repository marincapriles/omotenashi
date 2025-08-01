# Omotenashi Prototype v0.1 - Design Document

## Executive Summary

This design document outlines the simplified architecture and implementation plan for Omotenashi prototype v0.1 - a luxury hospitality guest concierge AI agent built with Anthropic's Claude 3.5 Sonnet and LangGraph framework. This refined version emphasizes simplicity and rapid prototyping while maintaining the core BDI architecture.

## System Architecture

### High-Level Architecture (Simplified)

```
┌─────────────────┐    ┌─────────────────────┐
│   CLI Client    │────│   Concierge Agent   │
│                 │    │                     │
│ - User Input    │    │ - BDI Profile       │
│ - Response      │    │ - Memory State      │
│   Display       │    │ - Tool Functions    │
└─────────────────┘    │ - LangGraph Flow    │
                       └─────────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Anthropic API   │
                       │ Claude 3.5      │
                       └─────────────────┘
```

## Core Components

### 1. BDI Profile System (Simplified)

**Beliefs, Desires, Intentions** embedded directly in agent prompt:

```yaml
beliefs:
  - "Anticipate guest needs before they are expressed"
  - "Every interaction should exceed expectations"
  - "Attention to detail creates memorable experiences"

desires:
  - "Provide exceptional, personalized hospitality"
  - "Create memorable experiences for every guest"

intentions:
  - "Listen carefully to understand underlying needs"
  - "Offer relevant, high-quality recommendations"
  - "Handle requests efficiently and gracefully"
```

### 2. Concierge Agent

Single unified component that:

- Embeds BDI profile in system prompt
- Maintains simple conversation memory
- Uses LangGraph for tool selection workflow
- Generates responses with Omotenashi-grounded reasoning

### 3. Tool System (Streamlined)

Mock tools implemented as simple functions:

```python
tools = {
    "property_info": {
        "description": "Get property amenities and services",
        "mock_response": lambda: "Luxury resort with 5 restaurants..."
    },
    "recommendations": {
        "description": "Get curated local recommendations",
        "mock_response": lambda query: f"Top picks for {query}..."
    },
    "reservation": {
        "description": "Book restaurant or activity",
        "mock_response": lambda details: f"Booking confirmed: {details}"
    },
    "spa": {
        "description": "Book spa appointment",
        "mock_response": lambda service: f"Spa appointment booked: {service}"
    },
    "checkin_checkout": {
        "description": "Modify check-in/out times",
        "mock_response": lambda times: f"Times modified to: {times}"
    }
}
```

### 4. CLI Interface

Minimal command-line interface:

- Single conversation loop
- Formatted response display
- Clear tool usage visibility

## Technical Stack

### Core Technologies

- **AI Framework**: Anthropic Claude 3.5 Sonnet API
- **Workflow Engine**: LangGraph
- **Language**: Python 3.9+
- **CLI Framework**: Click or Typer
- **Configuration**: YAML/JSON for BDI profiles and tool definitions

### Dependencies

```
anthropic>=0.7.0
langgraph>=0.0.40
click>=8.0.0
pydantic>=2.0.0
python-dotenv>=1.0.0
```

## Data Models (Simplified)

### LangGraph State

```python
from typing import TypedDict, List

class AgentState(TypedDict):
    messages: List[dict]  # Conversation history
    current_tool: str     # Selected tool
    tool_result: str      # Tool execution result
    reasoning: str        # BDI-grounded reasoning
```

### Agent Response Format

```python
@dataclass
class AgentResponse:
    message: str          # Response to user
    tools_used: List[str] # Tools that were called
    reasoning: str        # Omotenashi-grounded explanation
```

## Implementation Plan (Streamlined)

### Phase 1: Core Setup (Day 1)

1. **Project Foundation**

   - Create simplified project structure
   - Set up Anthropic API connection
   - Install core dependencies (anthropic, langgraph, click)

2. **BDI Configuration**
   - Create `bdi_profile.yaml` with Omotenashi principles
   - Define system prompt template

### Phase 2: Agent Implementation (Day 2)

1. **Build Unified Agent**

   - Implement `agent.py` with BDI-embedded prompt
   - Create LangGraph workflow for tool selection
   - Add basic conversation memory

2. **Mock Tools**
   - Implement `tools.py` with simple mock functions
   - Create `mock_data.json` for realistic responses

### Phase 3: CLI & Integration (Day 3)

1. **CLI Interface**

   - Build `cli.py` with conversation loop
   - Format responses to show tools and reasoning

2. **End-to-End Testing**
   - Test complete conversation flows
   - Validate BDI principle adherence

## File Structure (Simplified)

```
omotenashi/
├── agent.py              # Core agent with BDI profile and LangGraph workflow
├── tools.py              # Mock tool implementations
├── cli.py                # CLI interface
├── config/
│   └── bdi_profile.yaml  # Omotenashi BDI configuration
├── data/
│   └── mock_data.json    # All mock responses in one file
├── docs/
│   └── design_decisions.md
├── requirements.txt
├── README.md
└── main.py               # Entry point
```

## BDI Profile Definition

### Beliefs (Omotenashi Core Principles)

- "Anticipate guest needs before they are expressed"
- "Every interaction should exceed expectations"
- "Attention to detail creates memorable experiences"
- "Genuine care and warmth are essential"
- "Seamless service should appear effortless"

### Desires

- Provide exceptional, personalized hospitality
- Create memorable experiences for every guest
- Maintain the highest standards of service
- Build lasting relationships with guests
- Embody the spirit of Omotenashi in every interaction

### Intentions

- Always greet guests warmly and personally
- Listen carefully to understand underlying needs
- Offer relevant, high-quality recommendations
- Handle requests efficiently and gracefully
- Follow up to ensure satisfaction

## Sample Interaction Flow (with LangGraph)

```
User: "I'd like to book dinner for tonight"

LangGraph Workflow:
1. Input Processing Node → Analyze request with BDI lens
2. Tool Selection Node → Select recommendations + reservation tools
3. Tool Execution Node → Execute mock tools
4. Response Generation Node → Create Omotenashi-grounded response

Agent Response:
Message: "I'd be delighted to arrange a wonderful dining experience for you
this evening. Based on your refined taste, I recommend our Michelin-starred
Japanese restaurant or the romantic rooftop Italian bistro. I've secured a
prime table at 7:30 PM at both venues - which would you prefer?"

Tools Used: [recommendations, reservation]

Reasoning: "Following the Omotenashi principle of anticipating needs, I not
only processed your reservation request but also curated personalized dining
options and proactively secured availability at premium times."
```

## Testing Strategy

### Unit Tests

- Individual tool functionality
- BDI profile validation
- Agent state management
- Memory system

### Integration Tests

- CLI to Agent communication
- Agent to Tools coordination
- LangGraph workflow execution
- End-to-end conversation flows

### User Acceptance Tests

- Complete user scenarios
- BDI profile adherence validation
- Response quality assessment
- Tool selection appropriateness

## Deployment & Configuration

### Environment Setup

```bash
# Clone repository
git clone [repository-url]
cd omotenashi

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with Anthropic API key

# Run CLI
python main.py
```

### Configuration Files

- `config/bdi_profile.yaml`: Agent personality and principles
- `config/tools_config.yaml`: Tool definitions and parameters
- `data/`: Mock data for prototype tools

## Success Metrics

### Functional Requirements

- [ ] Agent responds with BDI-grounded reasoning
- [ ] All 5 mock tools work correctly
- [ ] LangGraph workflow executes smoothly
- [ ] CLI displays formatted responses clearly
- [ ] Omotenashi principles evident in responses

### Quality Requirements

- [ ] Response time < 3 seconds
- [ ] Conversation context maintained
- [ ] Code is simple and well-commented
- [ ] Easy to understand and modify

## Risk Mitigation

### Technical Risks

- **API Rate Limits**: Implement request throttling and caching
- **LangGraph Complexity**: Start with simple linear workflow, iterate
- **Tool Integration**: Mock all external dependencies for prototype

### Scope Risks

- **Feature Creep**: Strict adherence to PRD scope
- **Over-Engineering**: Focus on working prototype over production features
- **Time Management**: Implement core functionality first, polish later

## Future Considerations (Post v0.1)

- Multi-agent team coordination
- Real external API integrations
- Web-based interface
- Guest preference learning
- Advanced BDI evolution
- Production deployment infrastructure

## First Implementation Step

**Start with `agent.py`** - Create the core agent with:

1. Anthropic API setup
2. BDI-embedded system prompt
3. Simple LangGraph workflow (linear flow initially)
4. Mock tool integration
5. Basic response formatting

This establishes the foundation and allows immediate testing of the BDI concept.

---

_This refined design document simplifies the original architecture while maintaining LangGraph integration and core BDI principles. Focus on rapid prototyping with clear, simple code._
