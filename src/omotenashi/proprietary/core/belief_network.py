"""
Minimal Viable BeliefNetwork for Omotenashi
Focused on two flagship scenarios: Japanese Business Traveler & Anniversary Celebration
"""
from typing import Dict, Any, Tuple, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
from enum import Enum


class BeliefType(Enum):
    """Types of beliefs in the system"""
    CULTURAL = "cultural"
    CONTEXTUAL = "contextual"
    EMOTIONAL = "emotional"
    PREFERENCE = "preference"
    TEMPORAL = "temporal"


@dataclass
class Belief:
    """Represents a single belief with confidence"""
    name: str
    value: Any
    confidence: float
    belief_type: BeliefType
    last_updated: datetime = field(default_factory=datetime.now)
    source: str = "observation"
    decay_rate: float = 0.0  # How fast confidence decays over time
    
    def decay_confidence(self, hours_passed: float):
        """Apply temporal decay to confidence"""
        if self.decay_rate > 0:
            self.confidence *= (1 - self.decay_rate * hours_passed)
            self.confidence = max(0.1, self.confidence)  # Minimum confidence
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'value': self.value,
            'confidence': self.confidence,
            'type': self.belief_type.value,
            'last_updated': self.last_updated.isoformat(),
            'source': self.source
        }


class FocusedBeliefNetwork:
    """Minimal BeliefNetwork for flagship scenarios"""
    
    def __init__(self):
        """Initialize with beliefs needed for flagship scenarios"""
        self.beliefs: Dict[str, Belief] = {}
        self._initialize_flagship_beliefs()
        self.update_history: List[Dict[str, Any]] = []
        
    def _initialize_flagship_beliefs(self):
        """Initialize beliefs for Japanese Business & Anniversary scenarios"""
        
        # Cultural Adaptation beliefs
        self.beliefs['guest_culture'] = Belief(
            name='guest_culture',
            value='unknown',
            confidence=0.0,
            belief_type=BeliefType.CULTURAL,
            decay_rate=0.0  # Culture doesn't decay
        )
        
        self.beliefs['formality_preference'] = Belief(
            name='formality_preference',
            value=0.5,  # 0=casual, 1=formal
            confidence=0.3,
            belief_type=BeliefType.PREFERENCE,
            decay_rate=0.01  # Slowly decays
        )
        
        self.beliefs['business_context'] = Belief(
            name='business_context',
            value=False,
            confidence=0.0,
            belief_type=BeliefType.CONTEXTUAL,
            decay_rate=0.02  # Context can change
        )
        
        # Anniversary/Special Occasion beliefs
        self.beliefs['special_occasion'] = Belief(
            name='special_occasion',
            value=None,
            confidence=0.0,
            belief_type=BeliefType.CONTEXTUAL,
            decay_rate=0.0  # Occasion doesn't decay during stay
        )
        
        self.beliefs['celebration_magnitude'] = Belief(
            name='celebration_magnitude',
            value=0.0,  # 0=none, 1=major celebration
            confidence=0.0,
            belief_type=BeliefType.EMOTIONAL,
            decay_rate=0.01
        )
        
        self.beliefs['romantic_context'] = Belief(
            name='romantic_context',
            value=False,
            confidence=0.0,
            belief_type=BeliefType.CONTEXTUAL,
            decay_rate=0.0
        )
        
        # Shared beliefs
        self.beliefs['urgency_level'] = Belief(
            name='urgency_level',
            value=0.5,
            confidence=0.5,
            belief_type=BeliefType.TEMPORAL,
            decay_rate=0.05  # Urgency decays quickly
        )
        
        self.beliefs['first_time_guest'] = Belief(
            name='first_time_guest',
            value=True,
            confidence=0.7,
            belief_type=BeliefType.CONTEXTUAL,
            decay_rate=0.0
        )
    
    def update_from_observation(self, observation: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Update beliefs based on observation with pattern matching"""
        
        updates = []
        observation_lower = observation.lower()
        
        # Pattern matching for Japanese Business scenario
        if any(indicator in observation_lower for indicator in ['tokyo', 'japan', 'japanese']):
            old_culture = self.beliefs['guest_culture'].value
            self.beliefs['guest_culture'].value = 'Japanese'
            self.beliefs['guest_culture'].confidence = 0.95
            self.beliefs['guest_culture'].source = 'explicit_mention'
            updates.append(('guest_culture', old_culture, 'Japanese', 0.95))
            
            # Cultural inference cascade
            self.beliefs['formality_preference'].value = 0.9
            self.beliefs['formality_preference'].confidence = 0.85
            updates.append(('formality_preference', 0.5, 0.9, 0.85))
            
        if any(indicator in observation_lower for indicator in ['business', 'conference', 'meeting', 'microsoft', 'work']):
            self.beliefs['business_context'].value = True
            self.beliefs['business_context'].confidence = 0.9
            self.beliefs['business_context'].source = 'keyword_match'
            updates.append(('business_context', False, True, 0.9))
            
            # Business context affects urgency
            self.beliefs['urgency_level'].value = 0.7
            self.beliefs['urgency_level'].confidence = 0.6
            
        # Pattern matching for Anniversary scenario
        if any(indicator in observation_lower for indicator in ['anniversary', 'celebrating', 'years together']):
            self.beliefs['special_occasion'].value = 'anniversary'
            self.beliefs['special_occasion'].confidence = 1.0
            self.beliefs['special_occasion'].source = 'explicit_mention'
            updates.append(('special_occasion', None, 'anniversary', 1.0))
            
            self.beliefs['romantic_context'].value = True
            self.beliefs['romantic_context'].confidence = 1.0
            updates.append(('romantic_context', False, True, 1.0))
            
            # Extract magnitude if mentioned (e.g., "10th anniversary")
            import re
            magnitude_match = re.search(r'(\d+)(?:st|nd|rd|th)?\s*(?:year|anniversary)', observation_lower)
            if magnitude_match:
                years = int(magnitude_match.group(1))
                magnitude = min(years / 25.0, 1.0)  # 25th anniversary = max magnitude
                self.beliefs['celebration_magnitude'].value = magnitude
                self.beliefs['celebration_magnitude'].confidence = 0.95
                updates.append(('celebration_magnitude', 0.0, magnitude, 0.95))
        
        # Pattern matching for emotional indicators
        if any(indicator in observation_lower for indicator in ['special', 'celebrate', 'romantic', 'surprise']):
            current_magnitude = self.beliefs['celebration_magnitude'].value
            if current_magnitude < 0.5:
                self.beliefs['celebration_magnitude'].value = 0.7
                self.beliefs['celebration_magnitude'].confidence = 0.7
                
        # Check for first-time guest indicators
        if any(indicator in observation_lower for indicator in ['first time', 'never been', 'new to']):
            self.beliefs['first_time_guest'].value = True
            self.beliefs['first_time_guest'].confidence = 0.95
        elif any(indicator in observation_lower for indicator in ['returning', 'back again', 'last time']):
            self.beliefs['first_time_guest'].value = False
            self.beliefs['first_time_guest'].confidence = 0.95
            
        # Log update
        self.update_history.append({
            'timestamp': datetime.now(),
            'observation': observation,
            'updates': updates,
            'context': context
        })
        
        # Apply belief conflict resolution
        self._resolve_conflicts()
        
        return {
            'beliefs_updated': len(updates),
            'updates': updates,
            'current_beliefs': self.get_beliefs_summary()
        }
    
    def _resolve_conflicts(self):
        """Resolve conflicts between beliefs"""
        
        # If romantic context is high, business context should be lower
        if (self.beliefs['romantic_context'].value and 
            self.beliefs['romantic_context'].confidence > 0.8 and
            self.beliefs['business_context'].value):
            
            self.beliefs['business_context'].confidence *= 0.7
            
        # High celebration magnitude reduces formality preference
        if (self.beliefs['celebration_magnitude'].value > 0.7 and
            self.beliefs['celebration_magnitude'].confidence > 0.7):
            
            self.beliefs['formality_preference'].value = min(
                self.beliefs['formality_preference'].value, 0.6
            )
    
    def get_beliefs_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get current beliefs as dictionary"""
        return {
            name: belief.to_dict() 
            for name, belief in self.beliefs.items()
            if belief.confidence > 0.1  # Only return beliefs with meaningful confidence
        }
    
    def get_active_beliefs(self, confidence_threshold: float = 0.5) -> Dict[str, Belief]:
        """Get beliefs above confidence threshold"""
        return {
            name: belief 
            for name, belief in self.beliefs.items()
            if belief.confidence >= confidence_threshold
        }
    
    def apply_temporal_decay(self, hours_passed: float = 1.0):
        """Apply temporal decay to all beliefs"""
        for belief in self.beliefs.values():
            belief.decay_confidence(hours_passed)
    
    def get_belief_vector(self) -> List[float]:
        """Get belief state as vector for pattern matching"""
        # Fixed order for consistent vectors
        belief_names = [
            'guest_culture', 'formality_preference', 'business_context',
            'special_occasion', 'celebration_magnitude', 'romantic_context',
            'urgency_level', 'first_time_guest'
        ]
        
        vector = []
        for name in belief_names:
            belief = self.beliefs.get(name)
            if belief:
                # Encode value and confidence
                if isinstance(belief.value, bool):
                    value_encoded = 1.0 if belief.value else 0.0
                elif isinstance(belief.value, (int, float)):
                    value_encoded = float(belief.value)
                elif belief.value == 'Japanese':
                    value_encoded = 1.0
                elif belief.value == 'anniversary':
                    value_encoded = 1.0
                else:
                    value_encoded = 0.0
                    
                vector.extend([value_encoded, belief.confidence])
            else:
                vector.extend([0.0, 0.0])
                
        return vector
    
    def explain_belief(self, belief_name: str) -> str:
        """Generate human-readable explanation for a belief"""
        if belief_name not in self.beliefs:
            return f"No belief found for '{belief_name}'"
            
        belief = self.beliefs[belief_name]
        
        # Handle different belief types
        if belief_name == 'guest_culture':
            if belief.value == 'Japanese':
                return f"Guest is Japanese (confidence: {belief.confidence:.2f}) based on {belief.source}"
            else:
                return "Guest culture is unknown"
        elif belief_name == 'formality_preference':
            return f"Formality preference is {belief.value:.1f} (0=casual, 1=formal) with confidence {belief.confidence:.2f}"
        elif belief_name == 'business_context':
            return f"Business context is {'detected' if belief.value else 'not detected'} (confidence: {belief.confidence:.2f})"
        elif belief_name == 'special_occasion':
            if belief.value == 'anniversary':
                return f"Anniversary celebration detected (confidence: {belief.confidence:.2f})"
            else:
                return "No special occasion detected"
        elif belief_name == 'celebration_magnitude':
            return f"Celebration magnitude is {belief.value:.1f} (confidence: {belief.confidence:.2f})"
        elif belief_name == 'romantic_context':
            return f"Romantic context is {'detected' if belief.value else 'not detected'} (confidence: {belief.confidence:.2f})"
        else:
            return f"{belief_name}: {belief.value} (confidence: {belief.confidence:.2f})"


# Quick test
if __name__ == "__main__":
    # Test Japanese Business scenario
    network = FocusedBeliefNetwork()
    
    print("=== Testing Japanese Business Scenario ===")
    result1 = network.update_from_observation(
        "Hello, I'm checking in. I'm here from Tokyo for the Microsoft Azure conference."
    )
    print(f"Updates: {result1['beliefs_updated']}")
    print("Current beliefs:")
    for belief_name, belief_data in result1['current_beliefs'].items():
        print(f"  {belief_name}: {belief_data['value']} (confidence: {belief_data['confidence']:.2f})")
    
    print("\n=== Testing Anniversary Scenario ===")
    network2 = FocusedBeliefNetwork()
    result2 = network2.update_from_observation(
        "Hi, we're checking in. It's our 10th anniversary trip!"
    )
    print(f"Updates: {result2['beliefs_updated']}")
    print("Current beliefs:")
    for belief_name, belief_data in result2['current_beliefs'].items():
        print(f"  {belief_name}: {belief_data['value']} (confidence: {belief_data['confidence']:.2f})")