# Proprietary BDI-ToM Architecture Proposal for Omotenashi

## Executive Summary

This proposal outlines the transition from our current LangChain/LangGraph-based implementation to a proprietary architecture that integrates BDI (Beliefs, Desires, Intentions) with Theory of Mind (ToM) capabilities, specifically optimized for luxury hospitality use cases.

## Current State Analysis

### What We Have
- Working ReAct agent with LangChain (`react_agent.py`)
- BDI framework implemented as YAML configuration
- 5 functional hospitality tools
- Strong Omotenashi principles in prompts
- Comprehensive knowledge base

### Limitations to Address
- Generic BDI implementation lacks sophistication
- No Theory of Mind capabilities
- Tool selection could be more anticipatory
- Limited cultural adaptation beyond prompts
- Framework constraints on hospitality-specific optimizations

## Proposed Architecture

### Core Innovation: BDI-ToM Integration

```python
# Conceptual structure for our proprietary system
class OmotenashiMind:
    """Proprietary hospitality AI mind combining BDI + ToM"""
    
    def __init__(self):
        # Core reasoning components
        self.belief_network = BeliefNetwork()      # What I know
        self.theory_of_mind = TheoryOfMind()       # What guest thinks/feels
        self.desire_engine = DesireEngine()        # What I want to achieve
        self.intention_planner = IntentionPlanner() # How I'll achieve it
        
        # Hospitality-specific components
        self.anticipation_engine = AnticipationEngine()
        self.cultural_adapter = CulturalAdapter()
        self.service_patterns = ServicePatternLibrary()
```

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
**Goal**: Create proprietary BDI engine while maintaining current functionality

#### Task 1.1: Extract and Enhance BDI System
```python
# Location: src/omotenashi/proprietary/bdi_engine.py
"""
TODO for Claude Code:
1. Create new directory: src/omotenashi/proprietary/
2. Extract BDI logic from current YAML config into dynamic system
3. Implement BeliefNetwork class that can update beliefs based on conversation
4. Keep existing agent working while building new system in parallel
"""

# Starting point - enhance current static BDI
class BeliefNetwork:
    def __init__(self, base_beliefs):
        self.static_beliefs = base_beliefs  # From YAML
        self.dynamic_beliefs = {}  # Updated during conversation
        self.confidence_scores = {}  # How certain we are
    
    def update(self, observation, context):
        # Proprietary belief update algorithm
        pass
```

#### Task 1.2: Create Modular Desire System
```python
# Location: src/omotenashi/proprietary/desire_engine.py
"""
TODO:
1. Move from static desires to dynamic desire generation
2. Implement desire prioritization based on context
3. Create hospitality-specific desire patterns
"""

class DesireEngine:
    def prioritize_desires(self, beliefs, guest_context):
        # Proprietary algorithm for desire ranking
        # Consider: urgency, guest satisfaction, anticipation
        pass
```

### Phase 2: Theory of Mind Integration (Week 3-4)
**Goal**: Add guest mental state modeling

#### Task 2.1: Basic ToM Module
```python
# Location: src/omotenashi/proprietary/theory_of_mind.py
"""
TODO:
1. Create guest mental state representation
2. Implement inference from conversation patterns
3. Track emotional states and implicit needs
"""

class GuestMentalModel:
    def __init__(self):
        self.emotional_state = EmotionalState()
        self.implicit_needs = []
        self.expectations = []
        self.cultural_background = None
```

#### Task 2.2: Integrate ToM with BDI
```python
# Location: src/omotenashi/proprietary/bdi_tom_integration.py
"""
TODO:
1. Modify belief updates to include ToM insights
2. Adjust desires based on guest mental state
3. Plan intentions considering guest expectations
"""
```

### Phase 3: Hospitality Optimization (Week 5-6)
**Goal**: Build hospitality-specific components

#### Task 3.1: Anticipation Engine
```python
# Location: src/omotenashi/proprietary/anticipation_engine.py
"""
TODO:
1. Analyze patterns from guest interactions
2. Predict likely next requests
3. Prepare proactive suggestions
"""

class AnticipationEngine:
    def predict_needs(self, current_context, guest_history):
        # Proprietary anticipation algorithms
        # Example: Guest asks about dinner → Anticipate transportation needs
        pass
```

#### Task 3.2: Service Pattern Library
```python
# Location: src/omotenashi/proprietary/service_patterns.py
"""
TODO:
1. Codify Omotenashi service patterns
2. Create reusable hospitality workflows
3. Build pattern matching system
"""

PATTERNS = {
    "arrival_greeting": {
        "triggers": ["check in", "just arrived"],
        "actions": ["warm_welcome", "offer_refreshment", "room_orientation"],
        "anticipate": ["luggage_help", "dinner_reservations", "spa_booking"]
    }
}
```

### Phase 4: Custom Workflow Engine (Week 7-8)
**Goal**: Replace LangGraph with proprietary workflow system

#### Task 4.1: Hospitality Workflow Engine
```python
# Location: src/omotenashi/proprietary/workflow_engine.py
"""
TODO:
1. Create state machine optimized for hospitality flows
2. Implement parallel action execution
3. Add workflow templates for common scenarios
"""

class HospitalityWorkflow:
    def __init__(self):
        self.states = {}
        self.transitions = {}
        self.parallel_actions = []
```

## Migration Strategy

### Step 1: Parallel Development
```python
# In react_agent.py, add feature flag
USE_PROPRIETARY_BDI = False  # Toggle as we develop

if USE_PROPRIETARY_BDI:
    from .proprietary.bdi_engine import ProprietaryBDIEngine
    reasoning_engine = ProprietaryBDIEngine()
else:
    # Use existing implementation
```

### Step 2: Component-by-Component Migration
1. Start with BDI engine (lowest risk)
2. Add ToM capabilities (new functionality)
3. Integrate anticipation (enhancement)
4. Replace workflow engine (highest risk)

### Step 3: A/B Testing
```python
# Create comparison framework
class AgentComparison:
    def __init__(self):
        self.current_agent = ReActAgent()
        self.proprietary_agent = ProprietaryAgent()
    
    def compare_responses(self, user_input):
        # Compare quality, speed, tool selection
        pass
```

## Development Priorities

### Immediate (This Week)
1. **Set up proprietary package structure**
   ```bash
   mkdir -p src/omotenashi/proprietary
   touch src/omotenashi/proprietary/__init__.py
   ```

2. **Create base classes with interfaces**
   - Start with `bdi_engine.py`
   - Define interfaces for all components
   - Ensure backward compatibility

3. **Build first working prototype**
   - Focus on BeliefNetwork
   - Test with existing agent

### Next Sprint
1. Implement basic ToM
2. Create anticipation patterns
3. Start measuring improvements

### Future Sprints
1. Full workflow replacement
2. Advanced cultural adaptation
3. Performance optimization

## Success Metrics

### Technical Metrics
- Response time: < 2s (current: ~3s)
- Tool selection accuracy: > 90%
- Anticipation success rate: > 70%

### Business Metrics
- Guest satisfaction scores
- Unique capabilities vs competitors
- Patent-eligible innovations

## Code Organization

```
src/omotenashi/
├── proprietary/              # New IP components
│   ├── __init__.py
│   ├── bdi_engine.py        # Core BDI reasoning
│   ├── theory_of_mind.py    # ToM implementation
│   ├── anticipation.py      # Predictive systems
│   ├── cultural.py          # Cultural adaptation
│   ├── workflow.py          # Custom workflows
│   └── integration.py       # Ties everything together
├── legacy/                  # Move current implementation here
│   └── react_agent.py       # Current ReAct agent
└── agent.py                 # New unified interface
```

## Testing Strategy

### Unit Tests for Each Component
```python
# tests/test_proprietary_bdi.py
def test_belief_update():
    """Test that beliefs update correctly with new information"""
    pass

def test_desire_prioritization():
    """Test desire ranking algorithm"""
    pass
```

### Integration Tests
```python
# tests/test_bdi_tom_integration.py
def test_tom_influences_beliefs():
    """Test that ToM insights affect belief updates"""
    pass
```

### Comparison Tests
```python
# tests/test_agent_comparison.py
def test_proprietary_vs_current():
    """Compare responses between implementations"""
    pass
```

## Getting Started

### For Claude Code:

1. **Create the proprietary package structure** (as shown above)

2. **Start with `bdi_engine.py`**:
   ```python
   # Skeleton to get started
   class ProprietaryBDIEngine:
       def __init__(self, config_path):
           self.load_base_config(config_path)
           self.belief_network = BeliefNetwork()
           
       def reason(self, input_text, context):
           # Start simple, enhance iteratively
           pass
   ```

3. **Create a feature flag system** in `config.py`:
   ```python
   FEATURES = {
       'use_proprietary_bdi': False,
       'use_theory_of_mind': False,
       'use_anticipation': False,
       'use_custom_workflow': False
   }
   ```

4. **Build comparison tooling** early to measure improvements

5. **Document innovations** as you build them (for IP protection)

## Questions for Implementation

1. Should we start with a specific guest scenario to optimize for?
2. What level of explainability do we need in the proprietary system?
3. How much backward compatibility should we maintain?
4. What's our patent strategy for the innovations?

## Next Steps

1. Review and refine this proposal
2. Set up the proprietary package structure
3. Implement the first BeliefNetwork prototype
4. Create comparison metrics
5. Begin iterative development

---

**Note for Claude Code**: This is a living document. As you implement each component, please update this file with learnings, challenges, and refinements to the architecture. The goal is to build incrementally while maintaining a working system throughout the transition.