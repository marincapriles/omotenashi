"""
Tool Selection System with Affordance Embeddings
Implements robust tool selection with belief alignment and explainable reasoning
"""
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from abc import ABC, abstractmethod


@dataclass
class ToolSelectionResult:
    """Result of tool selection with full explainability"""
    tool_name: str
    confidence: float
    reasoning: str
    belief_support: Dict[str, float]
    alignment_score: float
    alternative_tools: List[Tuple[str, float, str]]  # (tool, score, why_not)


@dataclass
class ToolUsageOutcome:
    """Outcome of tool usage for effectiveness tracking"""
    tool_name: str
    intention_type: str
    success: bool
    execution_time_ms: float
    guest_satisfaction: Optional[float]
    belief_impacts: Dict[str, float]


class ToolAffordance:
    """Represents what a tool can do and when it's appropriate"""
    
    def __init__(self, tool_name: str, capabilities: Dict[str, float]):
        self.tool_name = tool_name
        self.capabilities = capabilities
        self.problem_space_embedding = self._generate_embedding()
        self.confidence_history = []
        self.belief_alignment_scores = {}
        
    def _generate_embedding(self) -> np.ndarray:
        """Generate embedding representing tool's problem-solving space"""
        # In production, this would use a more sophisticated embedding
        # For now, we'll use a simple vector based on capabilities
        capability_vector = []
        
        # Standard capability dimensions for hospitality tools
        dimensions = [
            'information_retrieval', 'reservation_making', 'recommendation',
            'guest_preference_learning', 'service_coordination', 'problem_resolution',
            'cultural_adaptation', 'anticipatory_service', 'emotional_support'
        ]
        
        for dim in dimensions:
            capability_vector.append(self.capabilities.get(dim, 0.0))
            
        return np.array(capability_vector)
    
    def matches_intention(self, intention: str, belief_state: Dict) -> Tuple[float, float, str]:
        """Calculate how well this tool matches the intention given beliefs"""
        
        # Calculate base alignment from intention
        alignment_score = self._calculate_alignment(intention)
        
        # Adjust confidence based on belief state
        confidence = self._belief_weighted_confidence(belief_state, intention)
        
        # Generate human-readable reasoning
        reasoning = self._generate_reasoning(alignment_score, confidence, belief_state, intention)
        
        return alignment_score, confidence, reasoning
    
    def _calculate_alignment(self, intention: str) -> float:
        """Calculate alignment between tool capabilities and intention"""
        # Map intentions to required capabilities
        intention_requirements = {
            'provide_information': ['information_retrieval', 'recommendation'],
            'make_reservation': ['reservation_making', 'service_coordination'],
            'cultural_adaptation': ['cultural_adaptation', 'guest_preference_learning'],
            'anticipate_needs': ['anticipatory_service', 'guest_preference_learning'],
            'emotional_support': ['emotional_support', 'problem_resolution']
        }
        
        required_capabilities = intention_requirements.get(intention, [])
        if not required_capabilities:
            return 0.5  # Neutral alignment for unknown intentions
            
        # Calculate alignment as average of required capability strengths
        alignment_scores = [
            self.capabilities.get(cap, 0.0) 
            for cap in required_capabilities
        ]
        
        return sum(alignment_scores) / len(alignment_scores) if alignment_scores else 0.0
    
    def _belief_weighted_confidence(self, belief_state: Dict, intention: str) -> float:
        """Adjust confidence based on belief state"""
        base_confidence = 0.7
        
        # Boost confidence based on relevant beliefs
        belief_boosts = {
            'guest_culture': 0.1 if 'cultural' in intention else 0.0,
            'urgency_level': 0.15 if belief_state.get('urgency_level', {}).get('value', 0) > 0.7 else 0.0,
            'special_occasion': 0.2 if belief_state.get('special_occasion', {}).get('value') else 0.0,
            'business_context': 0.1 if belief_state.get('business_context', {}).get('value') else 0.0
        }
        
        total_boost = sum(
            boost for belief, boost in belief_boosts.items()
            if belief in belief_state and belief_state[belief].get('confidence', 0) > 0.5
        )
        
        return min(base_confidence + total_boost, 0.95)
    
    def _generate_reasoning(self, alignment: float, confidence: float, 
                          beliefs: Dict, intention: str) -> str:
        """Generate human-readable reasoning for tool selection"""
        reasons = []
        
        # Explain alignment
        if alignment > 0.8:
            reasons.append(f"Strong capability match for {intention} ({alignment:.2f})")
        elif alignment > 0.6:
            reasons.append(f"Good capability match for {intention} ({alignment:.2f})")
        else:
            reasons.append(f"Moderate capability match for {intention} ({alignment:.2f})")
            
        # Explain belief influences
        if beliefs.get('guest_culture', {}).get('value') == 'Japanese' and 'cultural' in self.capabilities:
            reasons.append("Tool has cultural adaptation capabilities for Japanese guests")
            
        if beliefs.get('special_occasion', {}).get('value') and 'anticipatory_service' in self.capabilities:
            reasons.append(f"Tool can provide anticipatory service for {beliefs['special_occasion']['value']}")
            
        # Explain confidence
        reasons.append(f"Overall confidence: {confidence:.2f}")
        
        return "; ".join(reasons)


class ToolSelector:
    """Selects appropriate tools based on intentions and beliefs"""
    
    def __init__(self):
        self.tool_affordances = self._initialize_tool_affordances()
        self.selection_history = []
        self.effectiveness_tracker = ToolEffectivenessTracker()
        
    def _initialize_tool_affordances(self) -> Dict[str, ToolAffordance]:
        """Initialize tool affordances for Omotenashi tools"""
        return {
            'property_info': ToolAffordance('property_info', {
                'information_retrieval': 0.95,
                'recommendation': 0.3,
                'cultural_adaptation': 0.2
            }),
            
            'recommendations': ToolAffordance('recommendations', {
                'information_retrieval': 0.7,
                'recommendation': 0.95,
                'guest_preference_learning': 0.8,
                'cultural_adaptation': 0.7,
                'anticipatory_service': 0.6
            }),
            
            'reservation': ToolAffordance('reservation', {
                'reservation_making': 0.95,
                'service_coordination': 0.8,
                'anticipatory_service': 0.7,
                'problem_resolution': 0.5
            }),
            
            'spa': ToolAffordance('spa', {
                'information_retrieval': 0.6,
                'reservation_making': 0.9,
                'recommendation': 0.8,
                'anticipatory_service': 0.8,
                'emotional_support': 0.7
            }),
            
            'checkin_checkout': ToolAffordance('checkin_checkout', {
                'service_coordination': 0.9,
                'problem_resolution': 0.8,
                'guest_preference_learning': 0.7,
                'anticipatory_service': 0.6
            })
        }
    
    def select_tool(self, intention: str, belief_state: Dict, 
                   context: Optional[Dict] = None) -> ToolSelectionResult:
        """Select best tool with full explainability"""
        
        candidates = []
        
        # Evaluate each tool
        for tool_name, tool_affordance in self.tool_affordances.items():
            alignment, confidence, reasoning = tool_affordance.matches_intention(
                intention, belief_state
            )
            
            # Get historical effectiveness if available
            historical_boost = self.effectiveness_tracker.get_effectiveness_score(
                tool_name, intention
            )
            
            final_score = alignment * confidence * (1 + historical_boost)
            
            candidates.append({
                'tool': tool_name,
                'score': final_score,
                'alignment': alignment,
                'confidence': confidence,
                'reasoning': reasoning,
                'belief_support': self._calculate_belief_support(tool_name, belief_state)
            })
        
        # Sort by score
        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        # Select best tool
        selected = candidates[0]
        
        # Log selection
        self._log_selection(selected, intention, belief_state, context)
        
        # Format alternatives
        alternatives = [
            (c['tool'], c['score'], c['reasoning']) 
            for c in candidates[1:4]  # Top 3 alternatives
        ]
        
        return ToolSelectionResult(
            tool_name=selected['tool'],
            confidence=selected['confidence'],
            reasoning=selected['reasoning'],
            belief_support=selected['belief_support'],
            alignment_score=selected['alignment'],
            alternative_tools=alternatives
        )
    
    def _calculate_belief_support(self, tool_name: str, belief_state: Dict) -> Dict[str, float]:
        """Calculate how each belief supports this tool selection"""
        support_scores = {}
        
        # Tool-specific belief support patterns
        belief_support_patterns = {
            'property_info': {
                'business_context': 0.3,
                'first_time_guest': 0.5
            },
            'recommendations': {
                'guest_culture': 0.4,
                'special_occasion': 0.6,
                'dietary_preferences': 0.7
            },
            'reservation': {
                'special_occasion': 0.8,
                'urgency_level': 0.6,
                'business_context': 0.4
            },
            'spa': {
                'special_occasion': 0.7,
                'wellness_focus': 0.9,
                'romantic_context': 0.6
            },
            'checkin_checkout': {
                'urgency_level': 0.5,
                'loyalty_status': 0.4
            }
        }
        
        patterns = belief_support_patterns.get(tool_name, {})
        
        for belief_name, support_weight in patterns.items():
            if belief_name in belief_state:
                belief_confidence = belief_state[belief_name].get('confidence', 0)
                support_scores[belief_name] = support_weight * belief_confidence
                
        return support_scores
    
    def _log_selection(self, selected: Dict, intention: str, 
                      belief_state: Dict, context: Optional[Dict]):
        """Log tool selection for analysis and learning"""
        self.selection_history.append({
            'timestamp': datetime.now(),
            'tool': selected['tool'],
            'intention': intention,
            'score': selected['score'],
            'belief_state': belief_state.copy(),
            'context': context,
            'reasoning': selected['reasoning']
        })
    
    def record_outcome(self, outcome: ToolUsageOutcome):
        """Record tool usage outcome for learning"""
        self.effectiveness_tracker.record_outcome(outcome)


class ToolEffectivenessTracker:
    """Tracks tool effectiveness for improving future selections"""
    
    def __init__(self):
        self.effectiveness_db = {}
        
    def record_outcome(self, outcome: ToolUsageOutcome):
        """Record tool usage outcome"""
        key = (outcome.tool_name, outcome.intention_type)
        
        if key not in self.effectiveness_db:
            self.effectiveness_db[key] = {
                'success_count': 0,
                'total_count': 0,
                'avg_satisfaction': 0.0,
                'avg_execution_time': 0.0
            }
        
        stats = self.effectiveness_db[key]
        stats['total_count'] += 1
        
        if outcome.success:
            stats['success_count'] += 1
            
        # Update rolling averages
        if outcome.guest_satisfaction is not None:
            stats['avg_satisfaction'] = (
                stats['avg_satisfaction'] * (stats['total_count'] - 1) + 
                outcome.guest_satisfaction
            ) / stats['total_count']
            
        stats['avg_execution_time'] = (
            stats['avg_execution_time'] * (stats['total_count'] - 1) + 
            outcome.execution_time_ms
        ) / stats['total_count']
    
    def get_effectiveness_score(self, tool_name: str, intention: str) -> float:
        """Get effectiveness score for tool-intention pair"""
        key = (tool_name, intention)
        
        if key not in self.effectiveness_db:
            return 0.0  # No historical data
            
        stats = self.effectiveness_db[key]
        
        if stats['total_count'] < 5:
            return 0.0  # Not enough data
            
        # Calculate effectiveness score
        success_rate = stats['success_count'] / stats['total_count']
        satisfaction_score = stats['avg_satisfaction'] / 5.0 if stats['avg_satisfaction'] > 0 else 0.5
        
        # Penalize slow tools
        speed_penalty = 0.0
        if stats['avg_execution_time'] > 1000:  # Over 1 second
            speed_penalty = 0.1
        elif stats['avg_execution_time'] > 2000:  # Over 2 seconds
            speed_penalty = 0.2
            
        return (success_rate * 0.6 + satisfaction_score * 0.4) - speed_penalty