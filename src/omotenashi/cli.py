"""
CLI Interface for Omotenashi Concierge
--------------------------------------
This module provides a command-line interface for interacting with the
Omotenashi luxury hospitality concierge agent. It handles user input,
displays formatted responses, and showcases the agent's reasoning.

The interface embodies the same Omotenashi principles as the agent,
providing a warm, welcoming experience even in a command-line format.
"""

import click
import sys
from typing import Optional
from colorama import init, Fore, Style
from datetime import datetime

# Import our ReAct agent
from .react_agent import OmotenaashiReActAgent as OmotenaashiAgent, AgentResponse


# Initialize colorama for cross-platform colored output
init(autoreset=True)


class OmotenaashiCLI:
    """
    Command-line interface for the Omotenashi concierge agent.
    Provides an elegant, user-friendly experience for interacting with the AI concierge.
    """
    
    def __init__(self, agent: OmotenaashiAgent):
        """
        Initialize the CLI with an agent instance.
        
        Args:
            agent: The OmotenaashiAgent instance to use for processing requests
        """
        self.agent = agent
        self.session_start = datetime.now()
        
    def display_welcome(self):
        """
        Display a warm welcome message embodying Omotenashi principles.
        Sets the tone for the entire interaction.
        """
        welcome_message = f"""
{Fore.CYAN}{'═' * 70}
{Fore.YELLOW}✨ Welcome to Your Luxury Resort ✨
{Fore.CYAN}{'═' * 70}

{Fore.WHITE}Konnichiwa and welcome, honored guest.

I am your personal concierge, dedicated to ensuring your stay exceeds 
every expectation. Drawing from the Japanese tradition of Omotenashi—
selfless hospitality—I am here to anticipate your needs and create 
unforgettable moments.

{Fore.GREEN}How may I create an exceptional experience for you today?

{Fore.CYAN}{'─' * 70}
{Fore.YELLOW}💡 Tips: 
{Fore.WHITE}  • Ask about dining, activities, spa services, or our amenities
  • I can make reservations and arrangements on your behalf  
  • Type 'help' for more options or 'exit' to end our conversation
{Fore.CYAN}{'═' * 70}
        """
        print(welcome_message)
    
    def display_response(self, response: AgentResponse):
        """
        Display the agent's response in a formatted, easy-to-read manner.
        Shows the message, tools used, and reasoning separately.
        
        Args:
            response: The AgentResponse object containing message, tools, and reasoning
        """
        # Display main response message (what the guest sees)
        print(f"\n{Fore.GREEN}🎌 Guest Response:")
        print(f"{Fore.WHITE}{'═' * 70}")
        print(f"{response.message}")
        print(f"{'═' * 70}")
        
        # Display thought process (if reasoning mode is enabled)
        if hasattr(self, 'show_reasoning') and self.show_reasoning:
            print(f"\n{Fore.CYAN}💭 Agent Thought Process:")
            print(f"{Fore.WHITE}{'-' * 70}")
            if response.reasoning:
                # Format the reasoning for better readability
                reasoning_lines = response.reasoning.split('\n')
                for line in reasoning_lines:
                    if line.strip():
                        print(f"{line}")
            else:
                print("Direct response - no complex reasoning required")
            print(f"{'-' * 70}")
        
        # Display detailed tool usage (if any)
        if hasattr(response, 'tool_details') and response.tool_details:
            print(f"\n{Fore.YELLOW}🔧 Tools Used:")
            print(f"{Fore.WHITE}{'-' * 70}")
            for i, tool_detail in enumerate(response.tool_details, 1):
                tool_name = tool_detail['tool'].replace('_', ' ').title()
                print(f"\n{i}. {Fore.YELLOW}{tool_name}")
                print(f"   {Fore.CYAN}Input: {Fore.WHITE}{tool_detail['input']}")
                # Format output for readability
                output_lines = tool_detail['output'].split('\n')
                print(f"   {Fore.CYAN}Output: {Fore.WHITE}{output_lines[0]}")
                for line in output_lines[1:5]:  # Show first few lines of output
                    if line.strip():
                        print(f"           {line}")
                if len(output_lines) > 5:
                    print(f"           ... (truncated)")
            print(f"{'-' * 70}")
        elif response.tools_used:
            # Fallback to simple tool list if detailed info not available
            print(f"\n{Fore.YELLOW}🔧 Services Utilized:")
            for tool in response.tools_used:
                tool_display = tool.replace('_', ' ').title()
                print(f"   • {tool_display}")
            
        print(f"\n{Fore.CYAN}{'─' * 70}\n")
    
    def display_help(self):
        """
        Display help information about available commands and features.
        """
        help_text = f"""
{Fore.YELLOW}📋 Available Commands:
{Fore.WHITE}
  • {Fore.GREEN}help{Fore.WHITE}     - Show this help message
  • {Fore.GREEN}clear{Fore.WHITE}    - Clear conversation history  
  • {Fore.GREEN}reasoning{Fore.WHITE} - Toggle display of agent's reasoning
  • {Fore.GREEN}examples{Fore.WHITE}  - Show example requests
  • {Fore.GREEN}exit{Fore.WHITE}     - End conversation

{Fore.YELLOW}💬 Example Requests:
{Fore.WHITE}
  • "I'd like to have dinner tonight"
  • "What spa treatments do you recommend?"
  • "Can you tell me about the resort amenities?"
  • "I need a late checkout tomorrow"
  • "Plan a romantic evening for us"
  • "What activities are available today?"
        """
        print(help_text)
    
    def display_examples(self):
        """
        Display detailed examples of how to interact with the concierge.
        """
        examples = f"""
{Fore.YELLOW}✨ Example Interactions:

{Fore.GREEN}For Dining:
{Fore.WHITE}  "I'd like Italian food tonight with a view"
  "Book me a table at your best restaurant"
  "We're celebrating an anniversary - any suggestions?"

{Fore.GREEN}For Activities:
{Fore.WHITE}  "What can we do this afternoon?"
  "I want an adventure experience"
  "Are there any cultural activities available?"

{Fore.GREEN}For Relaxation:
{Fore.WHITE}  "I need to unwind after my flight"
  "What's your most popular spa treatment?"
  "Book a couples massage for tomorrow"

{Fore.GREEN}For Special Requests:
{Fore.WHITE}  "Can I check in early tomorrow?"
  "Arrange a surprise for my partner"
  "I need a quiet place to work"
        """
        print(examples)
    
    def handle_command(self, user_input: str) -> bool:
        """
        Handle special commands (non-conversation inputs).
        
        Args:
            user_input: The user's input string
            
        Returns:
            bool: True if a command was handled, False otherwise
        """
        command = user_input.lower().strip()
        
        if command == 'help':
            self.display_help()
            return True
        elif command == 'clear':
            self.agent.reset_memory()
            click.clear()
            self.display_welcome()
            return True
        elif command == 'reasoning':
            self.show_reasoning = not getattr(self, 'show_reasoning', False)
            status = "enabled" if self.show_reasoning else "disabled"
            print(f"{Fore.YELLOW}Reasoning display {status}")
            return True
        elif command == 'examples':
            self.display_examples()
            return True
        elif command in ['exit', 'quit', 'bye', 'goodbye']:
            self.display_farewell()
            return True
            
        return False
    
    def display_farewell(self):
        """
        Display a gracious farewell message when the session ends.
        """
        session_duration = datetime.now() - self.session_start
        minutes = int(session_duration.total_seconds() / 60)
        
        farewell = f"""
{Fore.CYAN}{'═' * 70}
{Fore.YELLOW}🙏 Arigato Gozaimashita - Thank You

{Fore.WHITE}It has been my genuine pleasure to assist you today.
May your stay with us be filled with wonderful moments and cherished memories.

{Fore.GREEN}Please don't hesitate to call upon me anytime - I am always here for you.

{Fore.WHITE}Session duration: {minutes} minutes
{Fore.CYAN}{'═' * 70}

{Fore.YELLOW}Sayonara and sweet dreams ✨
        """
        print(farewell)
    
    def run(self):
        """
        Main conversation loop.
        Handles user input, processes through agent, and displays responses.
        """
        # Display welcome message
        self.display_welcome()
        
        # Initialize reasoning display preference
        self.show_reasoning = False
        
        # Main conversation loop
        while True:
            try:
                # Get user input with styled prompt
                user_input = click.prompt(
                    f"{Fore.BLUE}Guest",
                    prompt_suffix=f"{Fore.WHITE}: ",
                    type=str
                ).strip()
                
                # Check for empty input
                if not user_input:
                    continue
                
                # Handle special commands
                if self.handle_command(user_input):
                    if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                        break
                    continue
                
                # Process through agent
                try:
                    # Show thinking indicator
                    print(f"{Fore.YELLOW}🤔 Contemplating how best to assist you...", end='', flush=True)
                    
                    # Get response from agent
                    response = self.agent.process(user_input)
                    
                    # Clear thinking indicator
                    print('\r' + ' ' * 50 + '\r', end='', flush=True)
                    
                    # Display response
                    self.display_response(response)
                    
                except Exception as e:
                    # Handle any errors gracefully
                    print(f"\n{Fore.RED}I apologize, but I encountered an issue: {str(e)}")
                    print(f"{Fore.WHITE}Please try rephrasing your request, or type 'help' for assistance.")
                    
            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                print(f"\n\n{Fore.YELLOW}Interrupted... ending conversation gracefully.")
                self.display_farewell()
                break
            except EOFError:
                # Handle Ctrl+D gracefully
                print()
                self.display_farewell()
                break


def validate_environment():
    """
    Validate that required environment variables are set.
    
    Returns:
        bool: True if environment is valid, False otherwise
    """
    import os
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print(f"{Fore.RED}Error: ANTHROPIC_API_KEY environment variable not set.")
        print(f"{Fore.YELLOW}Please set it using:")
        print(f"{Fore.WHITE}  export ANTHROPIC_API_KEY='your-api-key-here'")
        return False
    
    return True


# Main entry point when running the CLI directly
@click.command()
@click.option(
    '--reasoning',
    is_flag=True,
    help='Show agent reasoning by default'
)
@click.option(
    '--debug',
    is_flag=True,
    help='Enable debug mode with verbose output'
)
def main(reasoning: bool, debug: bool):
    """
    Omotenashi Luxury Concierge - Command Line Interface
    
    An AI-powered concierge embodying Japanese hospitality principles.
    """
    # Validate environment
    if not validate_environment():
        sys.exit(1)
    
    try:
        # Create agent
        import os
        agent = OmotenaashiAgent(os.getenv("ANTHROPIC_API_KEY"))
        
        # Create and configure CLI
        cli = OmotenaashiCLI(agent)
        cli.show_reasoning = reasoning
        
        # Run the CLI
        cli.run()
        
    except Exception as e:
        print(f"{Fore.RED}Failed to initialize: {str(e)}")
        if debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()