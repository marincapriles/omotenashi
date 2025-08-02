# GitHub Project Board Setup Guide

## Manual Setup Instructions

### 1. Create the Project Board

1. Go to: https://github.com/marincapriles/omotenashi
2. Click "Projects" tab
3. Click "New project" → Select "Board" template
4. Name: "Omotenashi BDI-ToM Implementation"
5. Description: "Proprietary BDI-ToM architecture implementation tracking"

### 2. Configure Columns

Create these columns in order:
- **Backlog** - All future work items
- **Planning** - Items being specified/designed  
- **In Progress** - Active development (limit: 3 items per track)
- **Testing** - Items in validation/testing
- **Done** - Completed items

### 3. Create Labels

Go to Issues → Labels and create:

**Track Labels** (color: blue):
- `track-a-core` - Core BDI Development
- `track-b-patterns` - Hospitality Patterns Team
- `track-c-platform` - Testing Infrastructure Team

**Type Labels** (color: purple):
- `innovation` - Novel algorithm/approach
- `flagship-scenario` - Related to flagship scenarios
- `tool-selection` - Tool selection system
- `pattern` - Pattern implementation

**Status Labels** (color: yellow):
- `blocked` - Blocked by dependency
- `needs-review` - Needs code/design review
- `regression` - Performance/quality regression

**Priority Labels** (color: red):
- `p0-critical` - Must complete this week
- `p1-high` - Should complete this week
- `p2-medium` - Nice to have this week

### 4. Add Initial Issues

Create these Week 0-1 issues:

#### Track A: Core BDI Development
```
Title: Implement Minimal Viable BeliefNetwork
Labels: track-a-core, flagship-scenario, p0-critical
Body:
- [ ] Create BeliefNetwork class with flagship scenario beliefs
- [ ] Implement belief update mechanism
- [ ] Add confidence scoring
- [ ] Test with Cultural Adaptation scenario
- [ ] Test with Anniversary scenario
- [ ] Document belief update algorithm

Success Criteria:
- Both flagship scenarios show belief updates
- Confidence scores are meaningful (0.0-1.0)
- Update time < 50ms
```

```
Title: Build DesireEngine with BeliefNetwork Integration
Labels: track-a-core, p0-critical
Body:
- [ ] Create DesireEngine class
- [ ] Connect to BeliefNetwork
- [ ] Implement desire prioritization
- [ ] Test desire generation from beliefs
- [ ] Validate against 5 test scenarios

Success Criteria:
- Desires correctly derived from beliefs
- Priority ordering is logical
- Response relevance improved by 10%+
```

```
Title: Implement Tool Selection System with Affordances
Labels: track-a-core, tool-selection, innovation, p0-critical
Body:
- [ ] Create ToolAffordance embeddings
- [ ] Implement belief-aligned selection
- [ ] Add explainable reasoning
- [ ] Test with flagship scenarios
- [ ] Document selection algorithm

Success Criteria:
- Tool selection accuracy >90%
- Reasoning is human-readable
- Selection time <100ms
```

#### Track B: Hospitality Patterns
```
Title: Define Initial Pattern Library
Labels: track-b-patterns, pattern, p1-high
Body:
- [ ] Document 20 common hospitality patterns
- [ ] Create pattern template structure
- [ ] Map patterns to BDI components
- [ ] Implement Japanese Business pattern
- [ ] Implement Anniversary pattern

Success Criteria:
- Patterns have testable outcomes
- Confidence ranges defined
- Failover strategies specified
```

```
Title: Create Pattern DSL and Engine
Labels: track-b-patterns, innovation, p1-high
Body:
- [ ] Design pattern specification language
- [ ] Build pattern compiler
- [ ] Create pattern executor
- [ ] Test with flagship patterns
- [ ] Document DSL syntax

Success Criteria:
- DSL is readable and expressive
- Patterns compile without errors
- Execution matches specification
```

#### Track C: Testing Infrastructure
```
Title: Set up Agent Trace Logging
Labels: track-c-platform, p0-critical
Body:
- [ ] Initialize trace database
- [ ] Implement decision logging
- [ ] Add belief update tracking
- [ ] Add tool selection tracking
- [ ] Create trace export functionality

Success Criteria:
- All decisions are logged
- Traces are queryable
- No performance impact (>5ms)
```

```
Title: Create A/B Testing Framework
Labels: track-c-platform, p0-critical
Body:
- [ ] Build comparison framework
- [ ] Set up metrics collection
- [ ] Create performance benchmarks
- [ ] Implement statistical analysis
- [ ] Build comparison dashboard

Success Criteria:
- Can run legacy vs new agent
- Metrics auto-collected
- Results statistically significant
```

### 5. Set Up Automation Rules

In Project settings → Manage → Workflows:

1. **Auto-move to "In Progress"**
   - When: Issue assigned
   - Action: Move to "In Progress"

2. **Auto-move to "Testing"**
   - When: Pull request created
   - Action: Move to "Testing"

3. **Auto-move to "Done"**
   - When: Issue closed
   - Action: Move to "Done"

4. **Auto-label regressions**
   - When: Issue title contains "regression" or "performance degradation"
   - Action: Add label "regression"

### 6. Create Milestone

Create milestone "Week 1-2: Foundation Phase"
- Due date: 2 weeks from today
- Description: Core BDI with flagship validation

### 7. Project Board View Options

Configure view:
- Group by: Track (using labels)
- Sort by: Priority
- Show fields: Assignee, Labels, Milestone

## Quick Setup Script

If you have GitHub CLI with project permissions:

```bash
# Create labels
gh label create "track-a-core" --color 0052CC --description "Core BDI Development"
gh label create "track-b-patterns" --color 0052CC --description "Hospitality Patterns Team"
gh label create "track-c-platform" --color 0052CC --description "Testing Infrastructure Team"

gh label create "innovation" --color 5319E7 --description "Novel algorithm/approach"
gh label create "flagship-scenario" --color 5319E7 --description "Related to flagship scenarios"
gh label create "tool-selection" --color 5319E7 --description "Tool selection system"
gh label create "pattern" --color 5319E7 --description "Pattern implementation"

gh label create "p0-critical" --color B60205 --description "Must complete this week"
gh label create "p1-high" --color D93F0B --description "Should complete this week"
gh label create "p2-medium" --color E99695 --description "Nice to have this week"

# Create milestone
gh api repos/marincapriles/omotenashi/milestones \
  --method POST \
  -f title="Week 1-2: Foundation Phase" \
  -f description="Core BDI with flagship validation" \
  -f due_on="2025-08-16T00:00:00Z"

# Create issues
gh issue create --title "Implement Minimal Viable BeliefNetwork" \
  --label "track-a-core,flagship-scenario,p0-critical" \
  --body-file - << 'EOF'
- [ ] Create BeliefNetwork class with flagship scenario beliefs
- [ ] Implement belief update mechanism
- [ ] Add confidence scoring
- [ ] Test with Cultural Adaptation scenario
- [ ] Test with Anniversary scenario
- [ ] Document belief update algorithm

Success Criteria:
- Both flagship scenarios show belief updates
- Confidence scores are meaningful (0.0-1.0)
- Update time < 50ms
EOF
```

## Daily Board Management

1. **Morning Standup Review**:
   - Check "In Progress" items per track
   - Move completed items to "Testing"
   - Pull new items from "Planning" to "In Progress"

2. **End of Day**:
   - Update issue progress (check boxes)
   - Add comments on blockers
   - Move tested items to "Done"

3. **Weekly Planning**:
   - Review velocity (items completed)
   - Adjust priorities
   - Add new items to backlog