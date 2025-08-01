# Proprietary BDI-ToM Implementation Workplan

## Overview
This workplan details the step-by-step implementation of the proprietary BDI-ToM (Beliefs, Desires, Intentions + Theory of Mind) architecture for Omotenashi, transitioning from the current LangChain-based system to a custom hospitality-optimized AI engine.

## Timeline: 8-Week Implementation Plan

## Week 1-2: Foundation Phase
### Goal: Create proprietary BDI engine while maintaining current functionality

#### Day 1-2: Project Setup and Structure
- [ ] Create proprietary package structure
  ```bash
  mkdir -p src/omotenashi/proprietary
  mkdir -p src/omotenashi/proprietary/core
  mkdir -p src/omotenashi/proprietary/hospitality
  mkdir -p src/omotenashi/proprietary/integration
  mkdir -p src/omotenashi/legacy
  mkdir -p tests/proprietary
  ```

- [ ] Move current implementation to legacy
  ```bash
  mv src/omotenashi/react_agent.py src/omotenashi/legacy/
  ```

- [ ] Create base module files
  - `src/omotenashi/proprietary/__init__.py`
  - `src/omotenashi/proprietary/core/__init__.py`
  - `src/omotenashi/proprietary/core/bdi_engine.py`
  - `src/omotenashi/proprietary/core/belief_network.py`
  - `src/omotenashi/proprietary/core/desire_engine.py`
  - `src/omotenashi/proprietary/core/intention_planner.py`

#### Day 3-4: Belief Network Implementation
- [ ] Implement `BeliefNetwork` class
  ```python
  # Key features to implement:
  - Static belief loading from YAML
  - Dynamic belief updates during conversation
  - Confidence scoring system
  - Belief persistence across sessions
  - Belief conflict resolution
  ```

- [ ] Create belief update algorithms
  - Implement observation processing
  - Build confidence adjustment logic
  - Add temporal belief decay

- [ ] Write unit tests for BeliefNetwork
  - Test belief initialization
  - Test dynamic updates
  - Test confidence scoring
  - Test conflict resolution

#### Day 5-6: Desire Engine Implementation
- [ ] Implement `DesireEngine` class
  ```python
  # Key features:
  - Dynamic desire generation
  - Context-based prioritization
  - Hospitality-specific desire patterns
  - Desire satisfaction tracking
  ```

- [ ] Create desire prioritization algorithm
  - Urgency calculation
  - Guest satisfaction impact
  - Resource availability consideration

- [ ] Build hospitality desire templates
  - Anticipatory service desires
  - Problem resolution desires
  - Enhancement desires

#### Day 7-8: Intention Planning System
- [ ] Implement `IntentionPlanner` class
  ```python
  # Key features:
  - Multi-step plan generation
  - Resource allocation
  - Parallel action planning
  - Plan monitoring and adjustment
  ```

- [ ] Create planning algorithms
  - Goal decomposition
  - Action sequencing
  - Constraint satisfaction

#### Day 9-10: BDI Integration and Testing
- [ ] Create `ProprietaryBDIEngine` main class
  - Integrate all BDI components
  - Implement reasoning cycle
  - Add logging and debugging

- [ ] Build feature flag system
  ```python
  # In src/omotenashi/config.py
  FEATURES = {
      'use_proprietary_bdi': False,
      'use_theory_of_mind': False,
      'use_anticipation': False,
      'use_custom_workflow': False
  }
  ```

- [ ] Create comparison framework
  - Side-by-side response generation
  - Performance metrics collection
  - Quality assessment tools

## Week 3-4: Theory of Mind Integration
### Goal: Add guest mental state modeling

#### Day 11-12: Basic ToM Module
- [ ] Implement `TheoryOfMind` class
  ```python
  # Core components:
  - GuestMentalModel
  - EmotionalState tracker
  - ImplicitNeedsDetector
  - ExpectationManager
  ```

- [ ] Create emotional state inference
  - Sentiment analysis integration
  - Emotional trajectory tracking
  - Mood prediction

#### Day 13-14: Guest Modeling
- [ ] Build `GuestMentalModel` class
  - Personality trait inference
  - Preference learning
  - Communication style adaptation

- [ ] Implement implicit need detection
  - Pattern recognition from queries
  - Context-based inference
  - Anticipatory need identification

#### Day 15-16: Cultural Adaptation Layer
- [ ] Create `CulturalAdapter` class
  - Cultural background detection
  - Communication style adjustment
  - Service expectation mapping

- [ ] Build cultural pattern library
  - Greeting preferences
  - Service style expectations
  - Communication norms

#### Day 17-18: BDI-ToM Integration
- [ ] Modify belief updates with ToM insights
  - Guest state influences beliefs
  - Emotional context in reasoning
  - Cultural factors in interpretation

- [ ] Enhance desire generation with ToM
  - Guest-specific desire creation
  - Empathy-driven prioritization
  - Cultural sensitivity in desires

#### Day 19-20: Integration Testing
- [ ] Create comprehensive test suite
  - ToM accuracy tests
  - Cultural adaptation tests
  - BDI-ToM interaction tests

## Week 5-6: Hospitality Optimization
### Goal: Build hospitality-specific components

#### Day 21-22: Anticipation Engine
- [ ] Implement `AnticipationEngine` class
  ```python
  # Features:
  - Pattern analysis from interactions
  - Need prediction algorithms
  - Proactive suggestion generation
  - Timing optimization
  ```

- [ ] Create prediction models
  - Sequential pattern mining
  - Context-based prediction
  - Confidence scoring

#### Day 23-24: Service Pattern Library
- [ ] Build `ServicePatternLibrary` class
  - Pattern definition framework
  - Pattern matching engine
  - Pattern composition system

- [ ] Codify Omotenashi patterns
  ```python
  # Example patterns:
  - Arrival sequences
  - Dining experiences
  - Problem resolution flows
  - Departure preparations
  ```

#### Day 25-26: Hospitality Workflow Templates
- [ ] Create workflow template system
  - Common scenario workflows
  - Customizable action sequences
  - Parallel action coordination

- [ ] Build template library
  - Check-in workflow
  - Concierge request workflow
  - Issue resolution workflow
  - Special occasion workflow

#### Day 27-28: Performance Optimization
- [ ] Optimize response generation
  - Caching frequently used patterns
  - Parallel processing implementation
  - Memory usage optimization

- [ ] Build monitoring system
  - Response time tracking
  - Pattern usage analytics
  - Success rate measurement

## Week 7-8: Custom Workflow Engine
### Goal: Replace LangGraph with proprietary system

#### Day 29-30: Workflow Engine Architecture
- [ ] Design `HospitalityWorkflow` class
  - State machine implementation
  - Transition management
  - Action execution framework

- [ ] Create workflow primitives
  - State definitions
  - Transition conditions
  - Action interfaces

#### Day 31-32: Workflow Execution Engine
- [ ] Implement execution engine
  - Sequential execution
  - Parallel action support
  - Error handling and recovery

- [ ] Build workflow monitoring
  - Execution tracking
  - Performance metrics
  - Debug capabilities

#### Day 33-34: Integration with BDI-ToM
- [ ] Connect workflow to BDI engine
  - BDI-driven state transitions
  - ToM-influenced decisions
  - Dynamic workflow adaptation

- [ ] Create feedback loops
  - Execution results to beliefs
  - Performance to desires
  - Outcomes to future planning

#### Day 35-36: Migration Tools
- [ ] Build migration utilities
  - LangGraph to proprietary converter
  - Compatibility layer
  - Rollback mechanisms

- [ ] Create migration testing
  - Behavior comparison tests
  - Performance benchmarks
  - Feature parity validation

#### Day 37-38: Full System Integration
- [ ] Complete system integration
  - All components connected
  - End-to-end testing
  - Performance optimization

- [ ] Production readiness
  - Error handling
  - Logging and monitoring
  - Documentation

#### Day 39-40: Final Testing and Documentation
- [ ] Comprehensive system testing
  - Load testing
  - Edge case handling
  - User acceptance testing

- [ ] Complete documentation
  - API documentation
  - Architecture guide
  - Deployment instructions

## Implementation Details

### File Structure
```
src/omotenashi/
├── proprietary/
│   ├── __init__.py
│   ├── config.py                    # Feature flags and settings
│   ├── core/
│   │   ├── __init__.py
│   │   ├── bdi_engine.py           # Main BDI engine
│   │   ├── belief_network.py       # Belief management
│   │   ├── desire_engine.py        # Desire generation
│   │   ├── intention_planner.py    # Planning system
│   │   └── theory_of_mind.py       # ToM implementation
│   ├── hospitality/
│   │   ├── __init__.py
│   │   ├── anticipation.py         # Anticipation engine
│   │   ├── cultural.py             # Cultural adaptation
│   │   ├── patterns.py             # Service patterns
│   │   └── workflows.py            # Hospitality workflows
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── agent_interface.py      # Unified agent interface
│   │   ├── tool_adapter.py         # Tool integration
│   │   └── migration.py            # Migration utilities
│   └── utils/
│       ├── __init__.py
│       ├── logging.py              # Custom logging
│       ├── metrics.py              # Performance metrics
│       └── comparison.py           # A/B testing tools
├── legacy/
│   ├── __init__.py
│   └── react_agent.py              # Current implementation
└── agent.py                        # Main entry point
```

### Testing Strategy
```
tests/proprietary/
├── unit/
│   ├── test_belief_network.py
│   ├── test_desire_engine.py
│   ├── test_intention_planner.py
│   ├── test_theory_of_mind.py
│   ├── test_anticipation.py
│   └── test_workflows.py
├── integration/
│   ├── test_bdi_integration.py
│   ├── test_tom_integration.py
│   └── test_full_system.py
├── performance/
│   ├── test_response_time.py
│   ├── test_memory_usage.py
│   └── test_scalability.py
└── comparison/
    ├── test_legacy_parity.py
    ├── test_quality_metrics.py
    └── test_ab_framework.py
```

### Development Guidelines

#### Code Standards
- Type hints for all functions
- Comprehensive docstrings
- Unit tests for each component
- Performance benchmarks

#### Git Workflow
- Feature branches for each component
- PR reviews required
- CI/CD integration
- Automated testing

#### Documentation Requirements
- API documentation for all public methods
- Architecture decision records (ADRs)
- Performance benchmarking results
- Migration guides

### Success Criteria

#### Technical Metrics
- Response time: < 2 seconds (current: ~3s)
- Tool selection accuracy: > 95% (current: ~85%)
- Anticipation success rate: > 70% (new capability)
- Memory usage: < 500MB per agent instance
- Concurrent users: > 1000

#### Quality Metrics
- Guest satisfaction improvement: > 20%
- Novel capability demonstrations: 5+
- Patent-eligible innovations: 3+
- Code coverage: > 90%

### Risk Mitigation

#### Technical Risks
- **Risk**: Integration complexity
  - **Mitigation**: Incremental migration with feature flags
  
- **Risk**: Performance regression
  - **Mitigation**: Continuous benchmarking and optimization

- **Risk**: Backwards compatibility
  - **Mitigation**: Comprehensive compatibility layer

#### Business Risks
- **Risk**: Development timeline overrun
  - **Mitigation**: Modular development, MVP approach

- **Risk**: User adoption challenges
  - **Mitigation**: A/B testing, gradual rollout

### Next Steps
1. Review and approve workplan
2. Set up development environment
3. Begin Week 1 implementation
4. Establish weekly progress reviews
5. Create project tracking dashboard

---

**Note**: This workplan is designed to be executed iteratively. Each component should be functional independently before integration. Regular reviews and adjustments are expected based on implementation learnings.