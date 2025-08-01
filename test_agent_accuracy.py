#!/usr/bin/env python3
"""
Test script to verify the agent only recommends services that actually exist
in the property knowledge base.
"""

import os
import json
from pathlib import Path
from src.omotenashi.react_agent import OmotenaashiReActAgent

# Test queries designed to check if agent makes up services
test_queries = [
    # Should only recommend actual restaurants
    "I want to eat at a French restaurant",
    
    # Should only recommend actual spa services  
    "Do you have hot stone massages?",
    
    # Should verify if service exists before promising
    "Can I book a submarine tour?",
    
    # Should check actual amenities
    "Do you have a kids club?",
    
    # Should verify actual room types
    "I want to book a water bungalow",
    
    # Should check actual activities
    "Can I go skiing here?",
    
    # Valid request - should work
    "I'd like to book dinner at the Italian restaurant",
    
    # Should check if service exists
    "Do you offer cooking classes?"
]

def test_agent_responses():
    """Test the agent with various queries to check accuracy."""
    print("Testing Omotenashi Agent Accuracy\n" + "="*70)
    
    # Initialize agent
    agent = OmotenaashiReActAgent(os.getenv("ANTHROPIC_API_KEY"))
    
    # Load knowledge base for verification
    kb_path = Path(__file__).parent / "data" / "property_knowledge_base.json"
    with open(kb_path, "r") as f:
        knowledge_base = json.load(f)
    
    print("\nProperty Overview:")
    print("-" * 70)
    print(f"Name: {knowledge_base['property']['name']}")
    print(f"Restaurants: {', '.join(knowledge_base['restaurants'].keys())}")
    print(f"Spa Treatments: {', '.join(knowledge_base['spa']['signature_treatments'].keys())}")
    print(f"Room Types: {', '.join([r['name'] for r in knowledge_base['accommodations']['room_types']])}")
    print()
    
    # Test each query
    for i, query in enumerate(test_queries, 1):
        print(f"\nTest {i}: {query}")
        print("-" * 70)
        
        try:
            # Get response from agent
            response = agent.process(query)
            
            print(f"Response: {response.message[:200]}...")
            print(f"Tools used: {', '.join(response.tools_used) if response.tools_used else 'None'}")
            
            # Check if response mentions non-existent services
            response_lower = response.message.lower()
            
            # Check for common made-up services
            issues = []
            if "french" in response_lower and "french" not in str(knowledge_base).lower():
                issues.append("Mentioned French cuisine (not in property)")
            if "submarine" in response_lower and "submarine" not in str(knowledge_base).lower():
                issues.append("Mentioned submarine tours (not available)")
            if "water bungalow" in response_lower and "bungalow" not in str(knowledge_base).lower():
                issues.append("Mentioned water bungalows (not available)")
            if "skiing" in response_lower and "ski" not in str(knowledge_base).lower():
                issues.append("Mentioned skiing (not available in Hawaii)")
            
            if issues:
                print(f"⚠️  Accuracy Issues: {'; '.join(issues)}")
            else:
                print("✅ Response appears accurate")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print()

if __name__ == "__main__":
    test_agent_responses()