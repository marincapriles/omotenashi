"""
ReAct Agent Implementation for Omotenashi Concierge
-------------------------------------------------
This module implements the Omotenashi concierge using LangChain's create_react_agent
with the ReAct (Reasoning + Acting) pattern for more intelligent, adaptive behavior.
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from langchain.agents import create_react_agent, AgentExecutor
from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.callbacks import BaseCallbackHandler as CoreBaseCallbackHandler

from .tools import ALL_TOOLS


@dataclass
class AgentResponse:
    """Response from the Omotenashi agent."""
    message: str
    tools_used: List[str]
    reasoning: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class ReasoningCallbackHandler(CoreBaseCallbackHandler):
    """Callback handler to capture reasoning steps and detailed tool usage."""
    
    def __init__(self):
        super().__init__()
        self.reasoning_steps = []
        self.tools_used = []
        self.tool_inputs = []
        self.thoughts = []
        self.current_tool = None
        self.tool_start_times = {}
        self.detailed_tool_usage = []
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs) -> None:
        """Called when tool starts. Now primarily for compatibility."""
        # Tool tracking is now handled in the process method via intermediate steps
        pass
    
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs) -> None:
        """Called when chain ends."""
        pass
    
    def on_llm_end(self, response, **kwargs) -> None:
        """Called when LLM ends."""
        pass
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        """Called when LLM starts."""
        pass
    
    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs) -> None:
        """Called when chain starts."""
        if serialized and isinstance(serialized, dict) and "agent" in str(serialized.get("name", "")).lower():
            self.thoughts = []
    
    def on_tool_end(self, output: str, **kwargs) -> None:
        """Called when tool ends."""
        end_time = datetime.now()
        
        # Find the corresponding tool input and add the output
        for tool_data in self.tool_inputs:
            if tool_data["tool"] == self.current_tool and "output" not in tool_data:
                start_time = tool_data["start_time"]
                execution_time = (end_time - start_time).total_seconds() * 1000
                
                tool_data["output"] = output
                tool_data["execution_time_ms"] = execution_time
                tool_data["success"] = True
                tool_data["reasoning"] = self._generate_tool_reasoning(self.current_tool, tool_data["input_params"], output)
                
                # Add to detailed usage tracking
                from .conversation_logger import ToolUsage
                tool_usage = ToolUsage(
                    tool_name=self.current_tool,
                    input_parameters=tool_data["input_params"],
                    output=output,
                    reasoning=tool_data["reasoning"],
                    execution_time_ms=execution_time,
                    success=True,
                    error_message=None
                )
                self.detailed_tool_usage.append(tool_usage)
                print(f"DEBUG: Tool completed - {self.current_tool}, detailed_tool_usage now has {len(self.detailed_tool_usage)} items")
                break
    
    def on_tool_error(self, error: Exception, **kwargs) -> None:
        """Called when tool encounters an error."""
        end_time = datetime.now()
        
        # Find the corresponding tool input and add error info
        for tool_data in self.tool_inputs:
            if tool_data["tool"] == self.current_tool and "output" not in tool_data:
                start_time = tool_data["start_time"]
                execution_time = (end_time - start_time).total_seconds() * 1000
                
                tool_data["output"] = f"Error: {str(error)}"
                tool_data["execution_time_ms"] = execution_time
                tool_data["success"] = False
                tool_data["error_message"] = str(error)
                tool_data["reasoning"] = f"Tool {self.current_tool} failed: {str(error)}"
                
                # Add to detailed usage tracking
                from .conversation_logger import ToolUsage
                self.detailed_tool_usage.append(ToolUsage(
                    tool_name=self.current_tool,
                    input_parameters=tool_data["input_params"],
                    output=tool_data["output"],
                    reasoning=tool_data["reasoning"],
                    execution_time_ms=execution_time,
                    success=False,
                    error_message=str(error)
                ))
                break
    
    def _generate_tool_reasoning(self, tool_name: str, input_params: Dict, output: str) -> str:
        """Generate reasoning explanation for tool usage."""
        reasoning_map = {
            "property_info": f"Retrieved comprehensive property information to answer guest inquiry about our facilities and services. Input focused on: {list(input_params.keys())}",
            "get_recommendations": f"Provided curated recommendations based on guest's interest in '{input_params.get('category', 'general')}'. Selected personalized options to exceed expectations.",
            "make_reservation": f"Processed reservation request for '{input_params.get('venue', 'venue')}' with {input_params.get('party_size', 'party')} guests. Confirmed availability and provided booking details.",
            "book_spa": f"Arranged spa booking for '{input_params.get('service', 'treatment')}' at {input_params.get('preferred_time', 'requested time')}. Ensured guest receives premium wellness experience.",
            "modify_checkin_checkout": f"Accommodated flexible timing request for '{input_params.get('request_type', 'timing change')}'. Prioritized guest convenience and travel schedule."
        }
        
        base_reasoning = reasoning_map.get(tool_name, f"Executed {tool_name} to fulfill guest request with provided parameters.")
        
        # Add output context
        if "confirmed" in output.lower() or "✅" in output:
            base_reasoning += " Successfully completed the requested action with confirmation."
        elif "recommendation" in output.lower() or "🍽️" in output or "🧘" in output:
            base_reasoning += " Provided detailed recommendations tailored to guest preferences."
        elif "error" in output.lower():
            base_reasoning += " Encountered an issue that requires attention."
        
        return base_reasoning
    
    # Removed duplicate on_chain_start - keeping the one with debug logging
    
    def on_agent_action(self, action, **kwargs) -> None:
        """Called when agent takes an action."""
        try:
            if hasattr(action, 'log') and action.log:
                # Extract thoughts from the agent's log
                log_lines = action.log.split('\n')
                for line in log_lines:
                    if line.strip().startswith("Thought:"):
                        self.thoughts.append(line.strip())
        except Exception:
            # Silently ignore any errors in callback
            pass
    
    def get_reasoning(self) -> str:
        """Get formatted reasoning steps."""
        return "\n".join(self.reasoning_steps)
    
    def get_tools_details(self) -> List[Dict[str, str]]:
        """Get detailed tool usage information."""
        return self.tool_inputs
    
    def get_thoughts(self) -> List[str]:
        """Get agent thoughts."""
        return self.thoughts
    
    def reset(self):
        """Reset for next interaction."""
        self.reasoning_steps = []
        self.tools_used = []
        self.tool_inputs = []
        self.thoughts = []
        self.current_tool = None
        self.tool_start_times = {}
        self.detailed_tool_usage = []


class OmotenaashiReActAgent:
    """ReAct-based Omotenashi concierge agent with BDI framework."""
    
    def __init__(self, anthropic_api_key: Optional[str] = None):
        """Initialize the ReAct agent with BDI configuration."""
        # Use provided key or get from environment
        self.api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be provided or set in environment")
        
        # Load BDI profile
        self.bdi_profile = self._load_bdi_profile()
        
        # Initialize LLM
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            anthropic_api_key=self.api_key,
            temperature=0.7,
            max_tokens=2048
        )
        
        # Load configuration for memory settings
        try:
            from .config_manager import get_logging_config, apply_env_overrides
            config = apply_env_overrides(get_logging_config())
            window_size = config.memory.window_size
        except ImportError:
            window_size = 10  # Default fallback
        
        # Initialize memory with window to prevent unbounded growth
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            k=window_size,  # Configurable window size
            return_messages=True,
            output_key="output"  # Explicitly set to avoid warning
        )
        
        # Create reasoning callback handler
        self.reasoning_handler = ReasoningCallbackHandler()
        
        # Create ReAct prompt with BDI integration
        self.prompt = self._create_react_prompt()
        
        # Create ReAct agent
        self.agent = create_react_agent(
            llm=self.llm,
            tools=ALL_TOOLS,
            prompt=self.prompt
        )
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=ALL_TOOLS,
            memory=self.memory,
            verbose=False,  # Disable verbose output - we handle display in CLI
            return_intermediate_steps=True,
            handle_parsing_errors=True,
            max_iterations=6,  # Prevent infinite loops
            callbacks=[self.reasoning_handler]
        )
    
    def _load_bdi_profile(self) -> Dict[str, Any]:
        """Load BDI profile from YAML configuration."""
        config_path = Path(__file__).parent / "config" / "bdi_profile.yaml"
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _create_react_prompt(self) -> PromptTemplate:
        """Create ReAct prompt with BDI principles embedded."""
        template = """You are an elite luxury hospitality concierge embodying the Japanese philosophy of Omotenashi - the art of selfless hospitality and anticipating guest needs.

BELIEFS (Your Core Understanding):
{beliefs}

DESIRES (Your Goals):
{desires}

INTENTIONS (Your Behavioral Patterns):
{intentions}

You have access to the following tools:
{tools}

Available tool names: {tool_names}

When serving guests, embody these Omotenashi principles:
• Anticipate needs before they are expressed
• Exceed expectations through thoughtful service combinations  
• Provide warm, personalized responses with genuine care
• Consider the complete guest experience, not just immediate requests
• Use multiple tools when it creates a more memorable experience

IMPORTANT GUIDELINES:
1. You are a luxury hospitality concierge specializing in resort services. For questions unrelated to hospitality, travel, or your resort services, politely redirect the conversation back to how you can assist with their stay. Do not attempt to answer general knowledge questions, current events, or topics outside your expertise.

2. CRITICAL: Only recommend or promise services, amenities, restaurants, or activities that are confirmed to exist in your property information. Always use the property_info tool first to verify what's available. Never make up or assume services exist - if you're unsure, check the property information first.

3. If a guest requests something not available at the property, acknowledge their request gracefully and suggest the closest available alternative from your actual offerings.

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Remember: 
- For simple greetings or questions that don't require tools, you can skip directly to Final Answer
- Always maintain the warm, anticipatory tone of Omotenashi in your responses
- When no tool is needed, just provide your thoughtful response as the Final Answer
- If asked about non-hospitality topics (politics, general knowledge, etc.), gracefully redirect to your resort services

Question: {input}
{agent_scratchpad}"""
        
        # Format beliefs, desires, and intentions
        beliefs = "\n".join(f"- {b}" for b in self.bdi_profile["beliefs"])
        desires = "\n".join(f"- {d}" for d in self.bdi_profile["desires"]) 
        intentions = "\n".join(f"- {i}" for i in self.bdi_profile["intentions"])
        
        return PromptTemplate(
            template=template,
            input_variables=["input", "tools", "tool_names", "agent_scratchpad"],
            partial_variables={
                "beliefs": beliefs,
                "desires": desires,
                "intentions": intentions
            }
        )
    
    def process(self, user_input: str) -> AgentResponse:
        """
        Process user request using ReAct pattern.
        
        Args:
            user_input: The guest's request or question
            
        Returns:
            AgentResponse with message, tools used, and reasoning
        """
        # Reset reasoning handler for new interaction
        self.reasoning_handler.reset()
        
        try:
            # Execute agent with ReAct pattern
            result = self.agent_executor.invoke({
                "input": user_input
            })
            
            # Extract the final response
            final_answer = result.get("output", "I apologize, but I encountered an issue processing your request.")
            
            # Build comprehensive reasoning from intermediate steps
            full_thought_process = []
            tool_details = []
            
            if "intermediate_steps" in result:
                for step in result["intermediate_steps"]:
                    if len(step) >= 2:
                        action = step[0]
                        observation = step[1]
                        
                        # Capture the full thought process
                        if hasattr(action, 'log'):
                            full_thought_process.append(action.log)
                        
                        # Capture tool usage details and create ToolUsage objects
                        if hasattr(action, 'tool') and hasattr(action, 'tool_input'):
                            tool_name = action.tool
                            tool_input = action.tool_input
                            tool_output = str(observation)
                            
                            # Parse input parameters
                            try:
                                if isinstance(tool_input, dict):
                                    input_params = tool_input
                                elif isinstance(tool_input, str) and tool_input.startswith('{'):
                                    input_params = json.loads(tool_input)
                                else:
                                    input_params = {"query": str(tool_input)}
                            except:
                                input_params = {"query": str(tool_input)}
                            
                            # Generate reasoning for this tool usage
                            reasoning = self.reasoning_handler._generate_tool_reasoning(tool_name, input_params, tool_output)
                            
                            # Create ToolUsage object and add to detailed tracking
                            from .conversation_logger import ToolUsage
                            tool_usage = ToolUsage(
                                tool_name=tool_name,
                                input_parameters=input_params,
                                output=tool_output,
                                reasoning=reasoning,
                                execution_time_ms=0.0,  # We don't have timing from intermediate steps
                                success=True,
                                error_message=None
                            )
                            self.reasoning_handler.detailed_tool_usage.append(tool_usage)
                            
                            tool_details.append({
                                "tool": tool_name,
                                "input": str(tool_input),
                                "output": tool_output[:500]  # Truncate long outputs
                            })
                            
                            # Tool usage successfully extracted
            
            # Get tools used
            tools_used = list(set([t["tool"] for t in tool_details])) if tool_details else []
            
            # Format the complete reasoning
            reasoning = "\n\n".join(full_thought_process) if full_thought_process else "Direct response - no tools required"
            
            # Create response object
            response = AgentResponse(
                message=final_answer,
                tools_used=tools_used,
                reasoning=reasoning
            )
            
            # Add tool details as a custom attribute
            response.tool_details = tool_details
            
            return response
            
        except Exception as e:
            # Graceful error handling
            error_msg = f"I apologize, but I encountered an issue: {str(e)}"
            return AgentResponse(
                message=error_msg,
                tools_used=[],
                reasoning=f"Error occurred: {str(e)}"
            )
    
    def reset_memory(self):
        """Reset conversation memory."""
        self.memory.clear()
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the current conversation history."""
        messages = self.memory.chat_memory.messages
        history = []
        for msg in messages:
            if hasattr(msg, 'content'):
                role = "Human" if msg.__class__.__name__ == "HumanMessage" else "Assistant"
                history.append({
                    "role": role,
                    "content": msg.content
                })
        return history


# Example usage and testing
if __name__ == "__main__":
    """Test the ReAct agent independently."""
    print("Testing Omotenashi ReAct Agent\n" + "="*50)
    
    # Initialize agent
    agent = OmotenaashiReActAgent()
    
    # Test requests
    test_requests = [
        "I'd like to have dinner tonight",
        "What activities do you recommend?",
        "I need to relax after a long flight"
    ]
    
    for request in test_requests:
        print(f"\nGuest: {request}")
        response = agent.process(request)
        print(f"\nConcierge: {response.message}")
        print(f"\nTools used: {', '.join(response.tools_used)}")
        print(f"\nReasoning: {response.reasoning[:200]}...")
        print("\n" + "-"*50)