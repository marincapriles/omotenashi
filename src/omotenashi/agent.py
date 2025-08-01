"""
Omotenashi Concierge Agent
-------------------------
This module now provides the ReAct-based implementation as the primary agent.
The original LangGraph implementation has been retired in favor of the more
capable ReAct agent with better reasoning and tool selection.
"""

# Import the ReAct agent as the primary implementation
from .react_agent import OmotenaashiReActAgent as OmotenaashiAgent, AgentResponse

# For backward compatibility, export the main agent class
__all__ = ['OmotenaashiAgent', 'AgentResponse']