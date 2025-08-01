#!/usr/bin/env python3
"""
Knowledge Base Integration Test
------------------------------
This script tests that the tools are now properly grounded in the 
property knowledge base and return accurate, consistent information.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set a test API key
os.environ['ANTHROPIC_API_KEY'] = 'test-key-for-testing'

def test_knowledge_base_structure():
    """Test that the knowledge base has the expected structure."""
    print("Testing knowledge base structure...")
    
    try:
        from src.omotenashi.tools import KNOWLEDGE_BASE
        
        # Verify key sections exist
        assert "property" in KNOWLEDGE_BASE
        assert "restaurants" in KNOWLEDGE_BASE
        assert "spa" in KNOWLEDGE_BASE
        assert "activities" in KNOWLEDGE_BASE
        assert "policies" in KNOWLEDGE_BASE
        
        # Verify specific data
        assert KNOWLEDGE_BASE["property"]["name"] == "The Grand Omotenashi Resort & Spa"
        assert len(KNOWLEDGE_BASE["restaurants"]) == 5  # 4 restaurants + in-room dining
        assert "kaiseki" in KNOWLEDGE_BASE["restaurants"]
        assert "Michelin 2-star" in KNOWLEDGE_BASE["restaurants"]["kaiseki"]["rating"]
        
        print("✓ Knowledge base loaded successfully")
        print(f"  - Property: {KNOWLEDGE_BASE['property']['name']}")
        print(f"  - Restaurants: {len(KNOWLEDGE_BASE['restaurants'])} venues")
        print(f"  - Spa treatments: {len(KNOWLEDGE_BASE['spa']['signature_treatments'])} signature treatments")
        
        return True
    except Exception as e:
        print(f"✗ Knowledge base loading error: {e}")
        return False


def test_property_info_accuracy():
    """Test that property_info returns accurate data from knowledge base."""
    print("\nTesting property info accuracy...")
    
    try:
        from src.omotenashi.tools import property_info, KNOWLEDGE_BASE
        
        result = property_info()
        kb = KNOWLEDGE_BASE
        
        # Verify key information is included
        assert kb["property"]["name"] in result
        assert str(kb["property"]["overview"]["total_rooms"]) in result
        assert kb["restaurants"]["kaiseki"]["rating"] in result
        assert kb["spa"]["name"] in result
        
        print("✓ Property info contains accurate knowledge base data")
        print(f"  - Mentions {kb['property']['name']}")
        print(f"  - Includes {kb['property']['overview']['total_rooms']} rooms")
        print(f"  - References {kb['restaurants']['kaiseki']['rating']} restaurant")
        
        return True
    except Exception as e:
        print(f"✗ Property info accuracy error: {e}")
        return False


def test_dining_recommendations_accuracy():
    """Test that dining recommendations use real restaurant data."""
    print("\nTesting dining recommendations accuracy...")
    
    try:
        from src.omotenashi.tools import get_recommendations, KNOWLEDGE_BASE
        
        result = get_recommendations("dinner tonight")
        kb = KNOWLEDGE_BASE
        
        # Verify real restaurant names and details
        assert kb["restaurants"]["kaiseki"]["name"] in result
        assert kb["restaurants"]["il_cielo"]["name"] in result
        assert kb["restaurants"]["kaiseki"]["rating"] in result
        assert "295" in result  # Price from knowledge base
        
        print("✓ Dining recommendations use accurate restaurant data")
        print(f"  - Includes {kb['restaurants']['kaiseki']['name']}")
        print(f"  - Shows correct pricing and hours")
        print(f"  - References {kb['restaurants']['kaiseki']['rating']} rating")
        
        return True
    except Exception as e:
        print(f"✗ Dining recommendations accuracy error: {e}")
        return False


def test_spa_booking_accuracy():
    """Test that spa bookings use real treatment data."""
    print("\nTesting spa booking accuracy...")
    
    try:
        from src.omotenashi.tools import book_spa, KNOWLEDGE_BASE
        
        result = book_spa("signature treatment")
        kb = KNOWLEDGE_BASE
        
        # Verify real spa data
        spa_data = kb["spa"]
        signature_treatment = spa_data["signature_treatments"]["omotenashi_journey"]
        
        assert signature_treatment["name"] in result
        assert signature_treatment["duration"] in result
        assert signature_treatment["price"] in result
        assert spa_data["name"] in result
        
        print("✓ Spa booking uses accurate treatment data")
        print(f"  - Treatment: {signature_treatment['name']}")
        print(f"  - Correct price: {signature_treatment['price']}")
        print(f"  - Proper duration: {signature_treatment['duration']}")
        
        return True
    except Exception as e:
        print(f"✗ Spa booking accuracy error: {e}")
        return False


def test_reservation_accuracy():
    """Test that reservations use real restaurant policies."""
    print("\nTesting reservation accuracy...")
    
    try:
        from src.omotenashi.tools import make_reservation, KNOWLEDGE_BASE
        
        result = make_reservation("dinner at kaiseki")
        kb = KNOWLEDGE_BASE
        
        # Verify real restaurant data
        kaiseki = kb["restaurants"]["kaiseki"]
        
        assert kaiseki["name"] in result
        assert kaiseki["type"] in result
        assert kaiseki["dress_code"] in result
        
        print("✓ Reservations use accurate restaurant policies")
        print(f"  - Restaurant: {kaiseki['name']}")
        print(f"  - Correct dress code: {kaiseki['dress_code']}")
        print(f"  - Proper cuisine type: {kaiseki['type']}")
        
        return True
    except Exception as e:
        print(f"✗ Reservation accuracy error: {e}")
        return False


def test_checkin_policies():
    """Test that check-in modifications use real policies."""
    print("\nTesting check-in policy accuracy...")
    
    try:
        from src.omotenashi.tools import modify_checkin_checkout, KNOWLEDGE_BASE
        
        result = modify_checkin_checkout("early check-in")
        kb = KNOWLEDGE_BASE
        
        # Verify real policy data
        policies = kb["policies"]["check_in_out"]
        
        assert policies["standard_check_in"] in result
        assert "Subject to availability" in result  # From policy
        assert "$100 fee" in result  # From policy
        
        print("✓ Check-in modifications use accurate policies")
        print(f"  - Standard time: {policies['standard_check_in']}")
        print(f"  - Includes policy details and fees")
        
        return True
    except Exception as e:
        print(f"✗ Check-in policy accuracy error: {e}")
        return False


def main():
    """Run all knowledge base integration tests."""
    print("=" * 60)
    print("Knowledge Base Integration Testing")
    print("=" * 60)
    
    tests = [
        ("Knowledge Base Loading", test_knowledge_base_structure),
        ("Property Info Accuracy", test_property_info_accuracy),
        ("Dining Recommendations", test_dining_recommendations_accuracy),
        ("Spa Booking Accuracy", test_spa_booking_accuracy),
        ("Reservation Accuracy", test_reservation_accuracy),
        ("Check-in Policies", test_checkin_policies)
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
    print(f"Knowledge Base Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n✅ All tests passed! The agent is now grounded in accurate property data.")
        print("\nKey improvements:")
        print("- Real restaurant names, prices, and policies")
        print("- Accurate spa treatments and pricing")
        print("- Consistent property information")
        print("- Actual check-in/out policies and fees")
    else:
        print(f"\n❌ {failed} tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()