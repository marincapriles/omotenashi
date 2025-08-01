# Omotenashi Prototype v0.2 - Refined Implementation Proposal

## Executive Summary
This refined proposal streamlines the v0.2 implementation by focusing on the core PRD requirements: adding an Operations Manager agent that responds to specific triggers from the Concierge agent. The design emphasizes simplicity, clear agent separation, and maintainable code structure.

## Core Architecture

### Multi-Agent System Design
```
┌─────────────────┐    ┌────────────────────┐    ┌──────────────────┐
│   User Input    │───▶│ Agent Coordinator  │───▶│ Property Manager │
│     (CLI)       │    │                    │    │   (Notifications)│
└─────────────────┘    │ ┌────────────────┐ │    └──────────────────┘
         ▲             │ │ Concierge Agent │ │             ▲
         │             │ └────────┬───────┘ │             │
         │             │          │         │             │
         │             │          ▼         │             │
         │             │ ┌────────────────┐ │             │
         │             │ │   Trigger      │ │             │
         │             │ │   Manager      │ │             │
         │             │ └────────┬───────┘ │             │
         │             │          │         │             │
         │             │          ▼         │             │
         │             │ ┌────────────────┐ │             │
         └─────────────┤ │   Operations   │─┼─────────────┘
                       │ │   Manager      │ │
                       │ └────────────────┘ │
                       └────────────────────┘
```

## Implementation Components

### 1. Operations Manager Agent (`operations_agent.py`)

```python
"""
Operations Manager Agent
-----------------------
Handles escalations and operational communications triggered by Concierge Agent actions.
Embodies Omotenashi principles focused on seamless behind-the-scenes coordination.
"""

class OperationsAgent:
    def __init__(self):
        self.bdi_profile = self._load_operations_bdi_profile()
        self.system_prompt = self._create_operations_prompt()
        
    def handle_trigger(self, trigger: Dict[str, Any]) -> AgentResponse:
        """
        Process a trigger from the Concierge Agent.
        
        Args:
            trigger: Contains type, action, and context data
            
        Returns:
            AgentResponse with message, tools used, and reasoning
        """
        # Route to appropriate tool based on trigger action
        tool_function = self.tool_map[trigger['action']]
        result = tool_function(trigger['data'])
        
        return AgentResponse(
            message=result,
            tools_used=[trigger['action']],
            reasoning=self._generate_reasoning(trigger)
        )
```

### 2. Enhanced Concierge Agent Tools

Add to existing `tools.py`:

```python
def trigger_escalation(issue_description: str, severity: str = "high") -> Dict[str, str]:
    """
    Escalate complex guest issues to Operations Manager.
    
    Args:
        issue_description: Detailed description of the unresolvable issue
        severity: Issue severity level (high, medium, low)
        
    Returns:
        Confirmation of escalation with tracking details
    """
    escalation_id = f"ESC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return {
        "status": "escalated",
        "escalation_id": escalation_id,
        "message": f"🆘 Issue escalated to Operations Manager (ID: {escalation_id}). "
                  f"Our management team will address this immediately.",
        "details": issue_description,
        "severity": severity
    }
```

### 3. Trigger Manager (`trigger_manager.py`)

```python
"""
Trigger Manager
--------------
Detects when Concierge Agent actions should activate Operations Manager.
Implements the business rules for inter-agent communication.
"""

class TriggerManager:
    
    TRIGGER_RULES = {
        "checkin_checkout": {
            "trigger_type": "booking_modification",
            "operations_action": "communicate_booking_changes",
            "extract_data": lambda response: response.tool_results.get('checkin_checkout', {})
        },
        "trigger_escalation": {
            "trigger_type": "guest_escalation",
            "operations_action": "resolve_escalation",
            "extract_data": lambda response: response.tool_results.get('trigger_escalation', {})
        }
    }
    
    def detect_triggers(self, concierge_response: AgentResponse) -> List[Dict]:
        """
        Analyze Concierge response for trigger conditions.
        
        Returns:
            List of triggers to be processed by Operations Manager
        """
        triggers = []
        
        for tool_used in concierge_response.tools_used:
            if tool_used in self.TRIGGER_RULES:
                rule = self.TRIGGER_RULES[tool_used]
                triggers.append({
                    "type": rule["trigger_type"],
                    "action": rule["operations_action"],
                    "data": rule["extract_data"](concierge_response),
                    "timestamp": datetime.now().isoformat()
                })
        
        return triggers
```

### 4. Agent Coordinator (`agent_coordinator.py`)

```python
"""
Agent Coordinator
----------------
Orchestrates multi-agent interactions and manages the flow of information
between Concierge and Operations Manager agents.
"""

class AgentCoordinator:
    def __init__(self, anthropic_api_key: str):
        self.concierge = OmotenaashiAgent(anthropic_api_key)
        self.operations = OperationsAgent()
        self.trigger_manager = TriggerManager()
        self.interaction_log = []
        
    def process_request(self, user_input: str) -> Dict[str, Any]:
        """
        Process user request through the multi-agent system.
        
        Flow:
        1. Concierge processes user input
        2. Trigger Manager checks for operational triggers
        3. Operations Manager handles any triggers
        4. Combined response returned to user
        """
        # Step 1: Concierge handles user request
        concierge_response = self.concierge.process(user_input)
        
        # Step 2: Check for triggers
        triggers = self.trigger_manager.detect_triggers(concierge_response)
        
        # Step 3: Process triggers if any
        operations_responses = []
        for trigger in triggers:
            ops_response = self.operations.handle_trigger(trigger)
            operations_responses.append(ops_response)
        
        # Step 4: Log interaction
        self._log_interaction(user_input, concierge_response, operations_responses)
        
        return {
            "concierge": concierge_response,
            "operations": operations_responses,
            "triggers_activated": len(triggers) > 0
        }
```

### 5. Enhanced CLI Display (`cli.py`)

```python
def display_multi_agent_response(response: Dict[str, Any], show_reasoning: bool = False):
    """
    Display responses from both agents with clear visual separation.
    """
    # Always show Concierge response
    print("\n" + "═" * 70)
    print("🏨 CONCIERGE AGENT")
    print("─" * 70)
    print(f"{response['concierge'].message}")
    
    if show_reasoning:
        print(f"\n📋 Tools Used: {', '.join(response['concierge'].tools_used)}")
        print(f"💭 Reasoning: {response['concierge'].reasoning}")
    
    # Show Operations response if triggered
    if response['triggers_activated'] and response['operations']:
        for ops_response in response['operations']:
            print("\n" + "═" * 70)
            print("⚙️  OPERATIONS MANAGER")
            print("─" * 70)
            print(f"{ops_response.message}")
            
            if show_reasoning:
                print(f"\n📋 Action Taken: {', '.join(ops_response.tools_used)}")
                print(f"💭 Reasoning: {ops_response.reasoning}")
    
    print("═" * 70 + "\n")
```

## Operations Manager BDI Profile

`config/operations_bdi_profile.yaml`:

```yaml
# Operations Manager BDI Profile
# Focused on behind-the-scenes coordination and escalation management

beliefs:
  - "Proactive communication prevents service disruptions"
  - "Swift escalation resolution maintains guest satisfaction"
  - "Operational excellence enables exceptional hospitality"
  - "Transparency with property management ensures smooth operations"
  - "Omotenashi requires invisible yet impeccable coordination"

desires:
  - "Maintain seamless property operations"
  - "Resolve guest issues before they impact experience"
  - "Keep property manager informed of critical changes"
  - "Support front-line staff in delivering exceptional service"
  - "Anticipate and prevent operational challenges"

intentions:
  - "Respond immediately to booking modifications"
  - "Escalate and resolve issues with appropriate urgency"
  - "Provide clear, actionable updates to property management"
  - "Coordinate resources to support guest needs"
  - "Document patterns for continuous improvement"

system_prompt_template: |
  You are the Operations Manager for a luxury hospitality property, working behind 
  the scenes to ensure flawless guest experiences through the principle of Omotenashi.
  
  Your role is to handle escalations and operational communications triggered by 
  the Concierge Agent's interactions with guests.
  
  BELIEFS: {beliefs}
  DESIRES: {desires}
  INTENTIONS: {intentions}
  
  When responding to triggers:
  1. Address the operational need immediately
  2. Communicate clearly with the property manager
  3. Ensure follow-through on all commitments
  4. Maintain the seamless experience guests expect
```

## Implementation Roadmap

### Phase 1: Foundation (Day 1)
- [ ] Create `operations_agent.py` with BDI integration
- [ ] Implement 5 Operations Manager tools
- [ ] Add `trigger_escalation` to Concierge tools
- [ ] Create `operations_bdi_profile.yaml`
- [ ] Unit test all new components

### Phase 2: Integration (Day 2)
- [ ] Implement `trigger_manager.py` with detection rules
- [ ] Create `agent_coordinator.py` for orchestration
- [ ] Add interaction logging for debugging
- [ ] Integration test trigger scenarios
- [ ] Verify proper data flow between agents

### Phase 3: Interface & Testing (Day 3)
- [ ] Enhance CLI for dual-agent display
- [ ] Add visual indicators for trigger activation
- [ ] Create comprehensive test scenarios
- [ ] Update documentation and CLAUDE.md
- [ ] End-to-end validation of all workflows

## Key Design Improvements

### 1. Simplified Trigger Detection
- Rule-based system with clear mappings
- Extensible for future trigger types
- Easy to debug and modify

### 2. Clear Agent Separation
- Concierge: Guest-facing interactions
- Operations: Backend coordination
- No direct guest interaction for Operations Manager

### 3. Structured Data Flow
- Explicit trigger objects with metadata
- Traceable interaction logging
- Clear response formatting

### 4. Maintainable Architecture
- Each component has single responsibility
- Minimal coupling between agents
- Easy to add new triggers or tools

## Testing Strategy

### Unit Tests
```python
def test_trigger_escalation_tool():
    """Verify escalation tool creates proper trigger data."""
    result = trigger_escalation("AC broken in room 305", "high")
    assert result["status"] == "escalated"
    assert "escalation_id" in result
    assert result["severity"] == "high"

def test_trigger_detection():
    """Verify trigger manager detects correct conditions."""
    mock_response = AgentResponse(
        message="Updated checkout time",
        tools_used=["checkin_checkout"],
        reasoning="Guest requested later checkout"
    )
    triggers = TriggerManager().detect_triggers(mock_response)
    assert len(triggers) == 1
    assert triggers[0]["type"] == "booking_modification"
```

### Integration Tests
```python
def test_escalation_flow():
    """Test complete escalation from Concierge to Operations."""
    coordinator = AgentCoordinator(test_api_key)
    response = coordinator.process_request(
        "The AC in my room is broken and I have a meeting in 1 hour!"
    )
    
    assert response["triggers_activated"] == True
    assert len(response["operations"]) == 1
    assert "resolve_escalation" in response["operations"][0].tools_used
```

## Success Criteria

### Functional Requirements ✓
- Operations Manager responds to booking changes
- Escalations trigger appropriate resolution
- Property Manager receives clear notifications
- Both agents maintain Omotenashi principles
- CLI shows coordinated responses clearly

### Non-Functional Requirements ✓
- Response time < 3 seconds for dual-agent scenarios
- Code remains simple and well-documented
- System handles edge cases gracefully
- Easy to extend with new triggers
- Clear separation of concerns

## Risk Mitigation

### Simplified Architecture
- Linear processing flow (no complex async)
- Clear trigger rules (no ML/inference needed)
- Mock all external systems

### Focused Scope
- Only implement PRD-specified features
- Resist adding "nice-to-have" functionality
- Keep tools simple with mock responses

### Robust Testing
- Test each component in isolation
- Validate all trigger scenarios
- Ensure graceful handling of edge cases

## Conclusion

This refined proposal maintains the simplicity principle while delivering a robust multi-agent system. The architecture is clean, extensible, and focused on the core PRD requirements. By emphasizing clear separation of concerns and straightforward trigger detection, we create a system that's both powerful and maintainable.