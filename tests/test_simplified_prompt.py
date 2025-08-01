#!/usr/bin/env python3
"""
Quick test of simplified ReAct agent prompt
-------------------------------------------
Tests a few key scenarios to ensure the simplified prompt
maintains the same quality and tool selection behavior.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_simplified_prompt():
    """Test the simplified prompt with key scenarios."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found. Cannot test with real API.")
        return False
    
    try:
        from src.omotenashi.react_agent import OmotenaashiReActAgent
        
        print("🧪 Testing Simplified Prompt Performance")
        print("=" * 50)
        
        agent = OmotenaashiReActAgent(api_key)
        
        # Key test scenarios
        test_cases = [
            {
                "input": "I'd like dinner tonight",
                "expected_tools": {"get_recommendations", "make_reservation"},
                "description": "Simple dining request"
            },
            {
                "input": "We're celebrating our anniversary",
                "expected_tools": {"get_recommendations", "make_reservation", "book_spa"},
                "description": "Special occasion requiring anticipatory service"
            },
            {
                "input": "What can we do this afternoon?",
                "expected_tools": {"get_recommendations", "property_info"},
                "description": "Open-ended activity request"
            }
        ]
        
        all_passed = True
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}: {test_case['description']}")
            print(f"Input: {test_case['input']}")
            
            try:
                response = agent.process(test_case['input'])
                actual_tools = set(response.tools_used)
                expected_tools = test_case['expected_tools']
                
                # Calculate basic metrics
                correct_tools = expected_tools.intersection(actual_tools)
                precision = len(correct_tools) / len(actual_tools) if actual_tools else 0
                recall = len(correct_tools) / len(expected_tools) if expected_tools else 1
                
                print(f"Expected tools: {expected_tools}")
                print(f"Actual tools: {actual_tools}")
                print(f"Precision: {precision:.2f}, Recall: {recall:.2f}")
                
                # Check if response embodies Omotenashi
                response_lower = response.message.lower()
                omotenashi_indicators = [
                    "delighted", "pleasure", "exceptional", "memorable", 
                    "personalized", "anticipate", "experience"
                ]
                found_indicators = [ind for ind in omotenashi_indicators if ind in response_lower]
                
                print(f"Omotenashi indicators found: {found_indicators}")
                
                if recall >= 0.5 and len(found_indicators) >= 1:
                    print("✅ PASSED")
                else:
                    print("❌ FAILED")
                    all_passed = False
                    
                # Reset for next test
                agent.reset_memory()
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                all_passed = False
        
        print("\n" + "=" * 50)
        if all_passed:
            print("🎉 All tests passed! Simplified prompt maintains performance.")
        else:
            print("⚠️  Some tests failed. Review prompt changes.")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Failed to test: {str(e)}")
        return False

if __name__ == "__main__":
    test_simplified_prompt()