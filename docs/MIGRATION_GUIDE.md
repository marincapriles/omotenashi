# Migration Guide: LangGraph to ReAct Agent

## Overview

This guide documents the migration from the custom LangGraph implementation to the LangChain ReAct agent pattern, completed on [current date].

## Key Changes

### 1. Architecture Simplification

**Before (LangGraph):**
- 4 sequential nodes: analyze → select_tools → execute → respond
- Manual tool selection and execution
- Custom state management with TypedDict
- ~400 lines of complex workflow code

**After (ReAct):**
- Single ReAct agent with iterative reasoning
- Automatic tool selection and execution
- Built-in conversation memory
- ~200 lines of cleaner code

### 2. Tool Implementation

**Before:**
```python
# Manual tool mapping and execution
def _execute_tools(self, state):
    for tool_name in state["selected_tools"]:
        if tool_name in self.tool_map:
            # Complex parameter extraction
```

**After:**
```python
# Structured tools with automatic validation
recommendations_tool = StructuredTool.from_function(
    func=get_recommendations_wrapper,
    name="get_recommendations",
    description="...",
    args_schema=RecommendationInput
)
```

### 3. Agent Reasoning

**Before:**
- Fixed linear flow
- No ability to adapt based on tool results
- Manual reasoning extraction

**After:**
- Iterative ReAct pattern: Thought → Action → Observation → repeat
- Dynamic adaptation based on observations
- Built-in reasoning capture

## Benefits of Migration

### 1. **Better Guest Experience**
- More intelligent responses that adapt to tool results
- Ability to try alternative approaches if first attempt doesn't satisfy
- Natural conversation flow with memory

### 2. **Cleaner Codebase**
- Removed 200+ lines of manual tool handling
- Leverages battle-tested LangChain components
- Easier to maintain and extend

### 3. **Enhanced Capabilities**
- Automatic error recovery
- Streaming support (can be enabled)
- Better debugging with verbose mode
- Conversation memory management

### 4. **Future-Ready**
- Easy to add new tools
- Compatible with LangChain ecosystem
- Ready for multi-agent scenarios

## Usage

The system automatically uses the ReAct agent if available. The CLI seamlessly handles both implementations:

```bash
# Run with ReAct agent (if dependencies installed)
python main.py

# Show reasoning
python main.py --reasoning
```

## File Structure

```
New files:
├── langchain_tools.py      # LangChain tool definitions
├── react_agent.py          # ReAct agent implementation
├── test_react_migration.py # Migration test script
└── MIGRATION_GUIDE.md      # This file

Modified files:
├── cli.py                  # Updated to support both agents
├── main.py                 # Updated dependency checking
└── requirements.txt        # Added LangChain dependencies
```

## Testing

Run the migration test:
```bash
python test_react_migration.py
```

## Rollback

If needed, the original LangGraph agent is still available. The CLI will automatically fall back if ReAct dependencies are not installed.

## Next Steps

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Test the migration**: `python test_react_migration.py`
3. **Run the application**: `python main.py`

The ReAct agent provides a more intelligent, maintainable, and scalable foundation for the Omotenashi concierge system.