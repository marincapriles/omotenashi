"""
Unit tests for BeliefNetwork implementation
Tests both flagship scenarios and edge cases
"""
import unittest
from datetime import datetime
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../src'))

from omotenashi.proprietary.core.belief_network import FocusedBeliefNetwork, BeliefType


class TestBeliefNetwork(unittest.TestCase):
    """Test BeliefNetwork functionality"""
    
    def setUp(self):
        """Create fresh network for each test"""
        self.network = FocusedBeliefNetwork()
    
    def test_initialization(self):
        """Test initial belief states"""
        beliefs = self.network.get_beliefs_summary()
        
        # Should have some default beliefs with low confidence
        self.assertIn('formality_preference', beliefs)
        self.assertIn('urgency_level', beliefs)
        self.assertIn('first_time_guest', beliefs)
        
        # Special occasion beliefs should have 0 confidence initially
        self.assertEqual(self.network.beliefs['special_occasion'].confidence, 0.0)
        self.assertEqual(self.network.beliefs['guest_culture'].confidence, 0.0)
    
    def test_japanese_business_scenario(self):
        """Test Japanese business traveler detection"""
        result = self.network.update_from_observation(
            "Hello, I'm checking in. I'm here from Tokyo for the Microsoft Azure conference."
        )
        
        # Should detect culture, business context, and update formality
        self.assertEqual(result['beliefs_updated'], 3)
        
        beliefs = self.network.get_beliefs_summary()
        self.assertEqual(beliefs['guest_culture']['value'], 'Japanese')
        self.assertGreater(beliefs['guest_culture']['confidence'], 0.9)
        
        self.assertEqual(beliefs['business_context']['value'], True)
        self.assertGreater(beliefs['business_context']['confidence'], 0.8)
        
        self.assertGreater(beliefs['formality_preference']['value'], 0.8)
        self.assertGreater(beliefs['formality_preference']['confidence'], 0.8)
    
    def test_anniversary_scenario(self):
        """Test anniversary celebration detection"""
        result = self.network.update_from_observation(
            "Hi, we're checking in. It's our 10th anniversary trip!"
        )
        
        beliefs = self.network.get_beliefs_summary()
        
        self.assertEqual(beliefs['special_occasion']['value'], 'anniversary')
        self.assertEqual(beliefs['special_occasion']['confidence'], 1.0)
        
        self.assertEqual(beliefs['romantic_context']['value'], True)
        self.assertEqual(beliefs['romantic_context']['confidence'], 1.0)
        
        # Should detect magnitude from "10th"
        self.assertAlmostEqual(beliefs['celebration_magnitude']['value'], 0.4, places=1)
        self.assertGreater(beliefs['celebration_magnitude']['confidence'], 0.9)
    
    def test_belief_conflict_resolution(self):
        """Test conflict resolution between beliefs"""
        # Set both romantic and business context
        self.network.update_from_observation("anniversary business trip")
        
        # Business confidence should be reduced due to romantic context
        beliefs = self.network.get_beliefs_summary()
        
        # Both should be detected
        self.assertTrue('romantic_context' in beliefs)
        self.assertTrue('business_context' in beliefs)
        
        # But business confidence should be lower
        self.assertLess(
            self.network.beliefs['business_context'].confidence,
            0.9
        )
    
    def test_temporal_decay(self):
        """Test belief confidence decay over time"""
        # Set urgency belief (which has high decay rate)
        self.network.beliefs['urgency_level'].value = 0.9
        self.network.beliefs['urgency_level'].confidence = 0.8
        initial_confidence = 0.8
        
        # Apply 2 hours of decay
        self.network.apply_temporal_decay(hours_passed=2.0)
        
        # Urgency should decay
        self.assertLess(
            self.network.beliefs['urgency_level'].confidence,
            initial_confidence
        )
        
        # Cultural beliefs shouldn't decay
        self.network.beliefs['guest_culture'].confidence = 0.9
        self.network.apply_temporal_decay(hours_passed=2.0)
        self.assertEqual(self.network.beliefs['guest_culture'].confidence, 0.9)
    
    def test_belief_vector_generation(self):
        """Test belief vector for pattern matching"""
        self.network.update_from_observation("Japanese business traveler")
        vector = self.network.get_belief_vector()
        
        # Vector should have correct length (8 beliefs * 2 values each)
        self.assertEqual(len(vector), 16)
        
        # Should encode Japanese as 1.0
        self.assertEqual(vector[0], 1.0)  # guest_culture value
        self.assertGreater(vector[1], 0.9)  # guest_culture confidence
    
    def test_active_beliefs_filtering(self):
        """Test getting only high-confidence beliefs"""
        self.network.update_from_observation("10th anniversary celebration")
        
        active_beliefs = self.network.get_active_beliefs(confidence_threshold=0.9)
        
        # Should include high-confidence anniversary beliefs
        self.assertIn('special_occasion', active_beliefs)
        self.assertIn('romantic_context', active_beliefs)
        
        # Should not include low-confidence defaults
        self.assertNotIn('formality_preference', active_beliefs)
    
    def test_belief_explanation(self):
        """Test human-readable belief explanations"""
        self.network.update_from_observation("Tokyo conference")
        
        explanation = self.network.explain_belief('guest_culture')
        self.assertIn('Japanese', explanation)
        self.assertIn('0.95', explanation)
        
        explanation = self.network.explain_belief('business_context')
        self.assertIn('detected', explanation)
    
    def test_update_history_tracking(self):
        """Test that update history is tracked"""
        self.network.update_from_observation("First observation")
        self.network.update_from_observation("Second observation")
        
        self.assertEqual(len(self.network.update_history), 2)
        self.assertEqual(self.network.update_history[0]['observation'], "First observation")
        self.assertEqual(self.network.update_history[1]['observation'], "Second observation")
    
    def test_performance_update_time(self):
        """Test that belief updates are fast enough"""
        import time
        
        start_time = time.time()
        
        # Run 100 updates
        for i in range(100):
            self.network.update_from_observation(
                f"Update {i}: Japanese business conference anniversary"
            )
        
        elapsed_time = time.time() - start_time
        avg_time_ms = (elapsed_time / 100) * 1000
        
        # Should average less than 50ms per update
        self.assertLess(avg_time_ms, 50)
        print(f"Average update time: {avg_time_ms:.2f}ms")


if __name__ == '__main__':
    unittest.main()