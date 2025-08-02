#!/bin/bash
# Create all initial issues for Week 0-1

echo "Creating Track A issues..."

# Issue 2: DesireEngine
gh issue create --title "Build DesireEngine with BeliefNetwork Integration" \
  --label "track-a-core,p0-critical" \
  --body "- [ ] Create DesireEngine class
- [ ] Connect to BeliefNetwork
- [ ] Implement desire prioritization
- [ ] Test desire generation from beliefs
- [ ] Validate against 5 test scenarios

Success Criteria:
- Desires correctly derived from beliefs
- Priority ordering is logical
- Response relevance improved by 10%+"

# Issue 3: Tool Selection
gh issue create --title "Implement Tool Selection System with Affordances" \
  --label "track-a-core,tool-selection,innovation,p0-critical" \
  --body "- [ ] Create ToolAffordance embeddings
- [ ] Implement belief-aligned selection
- [ ] Add explainable reasoning
- [ ] Test with flagship scenarios
- [ ] Document selection algorithm

Success Criteria:
- Tool selection accuracy >90%
- Reasoning is human-readable
- Selection time <100ms"

echo "Creating Track B issues..."

# Issue 4: Pattern Library
gh issue create --title "Define Initial Pattern Library" \
  --label "track-b-patterns,pattern,p1-high" \
  --body "- [ ] Document 20 common hospitality patterns
- [ ] Create pattern template structure
- [ ] Map patterns to BDI components
- [ ] Implement Japanese Business pattern
- [ ] Implement Anniversary pattern

Success Criteria:
- Patterns have testable outcomes
- Confidence ranges defined
- Failover strategies specified"

# Issue 5: Pattern DSL
gh issue create --title "Create Pattern DSL and Engine" \
  --label "track-b-patterns,innovation,p1-high" \
  --body "- [ ] Design pattern specification language
- [ ] Build pattern compiler
- [ ] Create pattern executor
- [ ] Test with flagship patterns
- [ ] Document DSL syntax

Success Criteria:
- DSL is readable and expressive
- Patterns compile without errors
- Execution matches specification"

echo "Creating Track C issues..."

# Issue 6: Trace Logging
gh issue create --title "Set up Agent Trace Logging" \
  --label "track-c-platform,p0-critical" \
  --body "- [ ] Initialize trace database
- [ ] Implement decision logging
- [ ] Add belief update tracking
- [ ] Add tool selection tracking
- [ ] Create trace export functionality

Success Criteria:
- All decisions are logged
- Traces are queryable
- No performance impact (>5ms)"

# Issue 7: A/B Testing
gh issue create --title "Create A/B Testing Framework" \
  --label "track-c-platform,p0-critical" \
  --body "- [ ] Build comparison framework
- [ ] Set up metrics collection
- [ ] Create performance benchmarks
- [ ] Implement statistical analysis
- [ ] Build comparison dashboard

Success Criteria:
- Can run legacy vs new agent
- Metrics auto-collected
- Results statistically significant"

echo "Creating Week 0 preparation issues..."

# Issue 8: GitHub Project Setup
gh issue create --title "Complete GitHub Project Board Setup" \
  --label "track-c-platform,p0-critical" \
  --body "- [x] Create labels
- [ ] Set up Project Board
- [ ] Configure columns
- [ ] Add automation rules
- [ ] Link all issues to board
- [ ] Create first milestone

Success Criteria:
- Board shows all three tracks
- Automation working
- Team can track progress"

# Issue 9: Scenario Runner
gh issue create --title "Build Scenario Runner for Flagship Validation" \
  --label "track-c-platform,flagship-scenario,p0-critical" \
  --body "- [ ] Load flagship scenarios from YAML
- [ ] Create scenario execution engine
- [ ] Implement measurement collection
- [ ] Build comparison reports
- [ ] Set up automated daily runs

Success Criteria:
- Both flagship scenarios executable
- Measurements match expected format
- Reports show clear pass/fail"

echo "All issues created! Check them at:"
echo "https://github.com/marincapriles/omotenashi/issues"