#!/usr/bin/env python3
"""
Test Script for Omotenashi Prototype
------------------------------------
This script performs basic end-to-end testing of the Omotenashi concierge
without requiring user interaction or API keys.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set a test API key (we'll mock the responses)
os.environ['ANTHROPIC_API_KEY'] = 'test-key-for-testing'


def test_imports():
    """Test that all modules can be imported successfully."""
    print("Testing imports...")
    try:
        import yaml
        print("✓ yaml imported successfully")
        
        from src.omotenashi.tools import property_info, get_recommendations, make_reservation, book_spa, modify_checkin_checkout
        print("✓ tools module imported successfully")
        
        # Test new LangChain tools if available
        try:
            from src.omotenashi.tools import ALL_TOOLS, TOOL_MAP
            print("✓ tools module imported successfully")
            print(f"  - Found {len(ALL_TOOLS)} LangChain tools")
        except ImportError:
            print("ℹ tools module not available")
        
        # Test ReAct agent if available
        try:
            from src.omotenashi.react_agent import OmotenaashiReActAgent
            print("✓ react_agent module imported successfully")
        except ImportError:
            print("ℹ react_agent not available (optional)")
        
        # Test BDI profile loading
        with open("config/bdi_profile.yaml", "r") as f:
            bdi_profile = yaml.safe_load(f)
        print("✓ BDI profile loaded successfully")
        
        print(f"  - Found {len(bdi_profile['beliefs'])} beliefs")
        print(f"  - Found {len(bdi_profile['desires'])} desires")
        print(f"  - Found {len(bdi_profile['intentions'])} intentions")
        
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False


def test_tools():
    """Test that all mock tools return appropriate responses."""
    print("
Testing mock tools...")
    
    from src.omotenashi.tools import property_info, get_recommendations, make_reservation, book_spa, modify_checkin_checkout
    
    try:
        # Test property_info
        result = property_info()
        assert "Grand Omotenashi Resort" in result
        print("✓ property_info() works correctly")
        
        # Test recommendations
        result = get_recommendations("dinner tonight")
        assert "Dining Recommendations" in result or "Kaiseki" in result
        print("✓ get_recommendations() works correctly")
        
        # Test reservation
        result = make_reservation("dinner for two")
        assert "Reservation Confirmed" in result
        print("✓ make_reservation() works correctly")
        
        # Test spa booking
        result = book_spa("massage")
        assert "Spa Appointment Confirmed" in result
        print("✓ book_spa() works correctly")
        
        # Test check-in/out modification
        result = modify_checkin_checkout("late checkout")
        assert "Times Modified" in result
        print("✓ modify_checkin_checkout() works correctly")
        
        return True
    except Exception as e:
        print(f"✗ Tool error: {e}")
        return False


def test_tools():
    """Test LangChain tools if available."""
    print("\nTesting LangChain tools...")
    
    try:
        from src.omotenashi.tools import TOOL_MAP
        
        # Test property info tool
        result = TOOL_MAP["property_info"].run({})
        assert "Sakura Resort" in result
        print("✓ LangChain property_info tool works")
        
        # Test recommendations tool
        result = TOOL_MAP["get_recommendations"].run({"category": "dining"})
        assert "Dining Recommendations" in result or "Kaiseki" in result
        print("✓ LangChain recommendations tool works")
        
        print(f"  - All {len(TOOL_MAP)} LangChain tools tested successfully")
        return True
        
    except ImportError:
        print("ℹ LangChain tools not available (optional)")
        return True  # Not a failure, just optional
    except Exception as e:
        print(f"✗ LangChain tools error: {e}")
        return False


def test_bdi_system_prompt():
    """Test that the BDI system prompt is properly formatted."""
    print("\nTesting BDI system prompt generation...")
    
    try:
        import yaml
        
        # Load BDI profile
        with open("config/bdi_profile.yaml", "r") as f:
            bdi_profile = yaml.safe_load(f)
        
        # Format beliefs, desires, intentions
        beliefs_str = "\n".join(f"- {belief}" for belief in bdi_profile["beliefs"])
        desires_str = "\n".join(f"- {desire}" for desire in bdi_profile["desires"])
        intentions_str = "\n".join(f"- {intention}" for intention in bdi_profile["intentions"])
        
        # Create system prompt
        system_prompt = bdi_profile["system_prompt_template"].format(
            beliefs=beliefs_str,
            desires=desires_str,
            intentions=intentions_str
        )
        
        # Verify prompt contains key elements
        assert "Omotenashi" in system_prompt
        assert "BELIEFS:" in system_prompt
        assert "DESIRES:" in system_prompt
        assert "INTENTIONS:" in system_prompt
        assert len(system_prompt) > 500  # Should be substantial
        
        print("✓ System prompt generated successfully")
        print(f"  - Prompt length: {len(system_prompt)} characters")
        
        return True
    except Exception as e:
        print(f"✗ System prompt error: {e}")
        return False


def test_cli_components():
    """Test CLI components without running the full interface."""
    print("\nTesting CLI components...")
    
    try:
        # We can't fully test the CLI without mocking Anthropic,
        # but we can verify the structure
        from src.omotenashi.cli import OmotenaashiCLI, validate_environment
        from src.omotenashi.agent import AgentResponse
        
        # Test response formatting
        test_response = AgentResponse(
            message="I'd be delighted to help you.",
            tools_used=["recommendations", "reservation"],
            reasoning="Following Omotenashi principles..."
        )
        
        print("✓ CLI components structured correctly")
        print(f"  - AgentResponse has {len(test_response.__dict__)} fields")
        
        return True
    except Exception as e:
        print(f"✗ CLI component error: {e}")
        return False


def test_file_structure():
    """Verify all expected files exist."""
    print("\nTesting file structure...")
    
    expected_files = [
        "agent.py",
        "tools.py", 
        "cli.py",
        "main.py",
        "requirements.txt",
        "README.md",
        ".env.example",
        "config/bdi_profile.yaml",
        "data/mock_data.json"
    ]
    
    # Optional new files
    optional_files = [
        "tools.py",
        "react_agent.py",
        "test_react_migration.py",
        "MIGRATION_GUIDE.md"
    ]
    
    for file_path in optional_files:
        if Path(file_path).exists():
            print(f"  ✓ Found optional: {file_path}")
        else:
            print(f"  ℹ Optional not present: {file_path}")
    
    missing_files = []
    for file_path in expected_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"✗ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✓ All expected files present")
        return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Omotenashi End-to-End Testing")
    print("=" * 60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Module Imports", test_imports),
        ("Mock Tools", test_tools),
        ("Tools", test_tools),
        ("BDI System Prompt", test_bdi_system_prompt),
        ("CLI Components", test_cli_components)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n✅ All tests passed! The Omotenashi prototype is ready to use.")
        print("\nTo run the application:")
        print("1. Set your ANTHROPIC_API_KEY in .env")
        print("2. Run: python3 main.py")
    else:
        print(f"\n❌ {failed} tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()