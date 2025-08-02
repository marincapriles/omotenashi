"""
Pattern Testability Framework
Ensures every hospitality pattern has measurable outcomes and failover strategies
"""
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import yaml
from abc import ABC, abstractmethod


class PatternOutcome(Enum):
    """Possible outcomes of pattern execution"""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    FAILOVER_TRIGGERED = "failover_triggered"


@dataclass
class PatternMeasurement:
    """Measurement result for a pattern execution"""
    pattern_id: str
    timestamp: datetime
    outcome: PatternOutcome
    measurements: Dict[str, float]
    confidence_adjustment: float
    failover_used: Optional[str]
    guest_feedback: Optional[float]
    notes: List[str] = field(default_factory=list)


@dataclass
class TestablePattern:
    """A hospitality pattern with testable outcomes"""
    pattern_id: str
    description: str
    triggers: List[str]
    confidence_range: Tuple[float, float] = (0.2, 0.9)
    requires_confirmation: bool = False
    failover_strategy: Optional[str] = None
    success_metrics: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    belief_updates: Dict[str, Tuple[Any, float]] = field(default_factory=dict)
    tool_preferences: Dict[str, str] = field(default_factory=dict)
    
    def validate_outcome(self, expected: Dict[str, Any], 
                        actual: Dict[str, Any]) -> PatternMeasurement:
        """Validate pattern execution against expected outcomes"""
        measurements = {}
        all_success = True
        partial_success = False
        notes = []
        
        # Check each success metric
        for metric_name, metric_spec in self.success_metrics.items():
            if metric_name not in actual:
                notes.append(f"Missing metric: {metric_name}")
                all_success = False
                continue
                
            actual_value = actual[metric_name]
            
            # Check against specification
            if 'min' in metric_spec and actual_value < metric_spec['min']:
                all_success = False
                notes.append(f"{metric_name}: {actual_value} < min {metric_spec['min']}")
            elif 'max' in metric_spec and actual_value > metric_spec['max']:
                all_success = False
                notes.append(f"{metric_name}: {actual_value} > max {metric_spec['max']}")
            elif 'value' in metric_spec and actual_value != metric_spec['value']:
                all_success = False
                notes.append(f"{metric_name}: {actual_value} != expected {metric_spec['value']}")
            else:
                partial_success = True
                
            measurements[metric_name] = actual_value
        
        # Determine outcome
        if all_success:
            outcome = PatternOutcome.SUCCESS
            confidence_adjustment = 0.05  # Boost confidence
        elif partial_success:
            outcome = PatternOutcome.PARTIAL_SUCCESS
            confidence_adjustment = 0.0  # No change
        else:
            outcome = PatternOutcome.FAILURE
            confidence_adjustment = -0.1  # Reduce confidence
            
        # Check if failover was needed
        failover_used = None
        if 'failover_triggered' in actual and actual['failover_triggered']:
            outcome = PatternOutcome.FAILOVER_TRIGGERED
            failover_used = self.failover_strategy
            confidence_adjustment = -0.05
            
        return PatternMeasurement(
            pattern_id=self.pattern_id,
            timestamp=datetime.now(),
            outcome=outcome,
            measurements=measurements,
            confidence_adjustment=confidence_adjustment,
            failover_used=failover_used,
            guest_feedback=actual.get('guest_feedback'),
            notes=notes
        )
    
    def should_trigger(self, context: Dict[str, Any]) -> Tuple[bool, float]:
        """Check if pattern should trigger given context"""
        trigger_confidence = 0.0
        trigger_matches = 0
        
        # Check each trigger condition
        for trigger in self.triggers:
            if self._matches_trigger(trigger, context):
                trigger_matches += 1
                
        if trigger_matches > 0:
            trigger_confidence = min(
                trigger_matches / len(self.triggers),
                self.confidence_range[1]
            )
            trigger_confidence = max(trigger_confidence, self.confidence_range[0])
            
            return True, trigger_confidence
            
        return False, 0.0
    
    def _matches_trigger(self, trigger: str, context: Dict[str, Any]) -> bool:
        """Check if a single trigger matches the context"""
        # Simple keyword matching for now
        # In production, this would use more sophisticated NLP
        trigger_lower = trigger.lower()
        
        # Check in user message
        if 'user_message' in context:
            if trigger_lower in context['user_message'].lower():
                return True
                
        # Check in detected entities
        if 'entities' in context:
            for entity in context['entities']:
                if trigger_lower in str(entity).lower():
                    return True
                    
        # Check in beliefs
        if 'beliefs' in context:
            for belief, value in context['beliefs'].items():
                if trigger_lower in belief.lower():
                    return True
                if isinstance(value, dict) and 'value' in value:
                    if trigger_lower in str(value['value']).lower():
                        return True
                        
        return False


class PatternLibrary:
    """Manages testable hospitality patterns"""
    
    def __init__(self, patterns_file: Optional[str] = None):
        self.patterns: Dict[str, TestablePattern] = {}
        if patterns_file:
            self.load_patterns(patterns_file)
        else:
            self._initialize_flagship_patterns()
    
    def _initialize_flagship_patterns(self):
        """Initialize with flagship scenario patterns"""
        
        # Japanese Business Greeting Pattern
        self.patterns['japanese_business_greeting'] = TestablePattern(
            pattern_id='japanese_business_greeting',
            description='Formal greeting for Japanese business travelers',
            triggers=['Japanese', 'Tokyo', 'business', 'conference'],
            confidence_range=(0.7, 0.95),
            requires_confirmation=False,
            failover_strategy='standard_business_greeting',
            success_metrics={
                'communication_formality_score': {'min': 0.9},
                'cultural_appropriateness': {'min': 90, 'unit': 'percent'},
                'guest_satisfaction': {'min': 4.5, 'max': 5.0}
            },
            belief_updates={
                'guest_culture': ('Japanese', 0.95),
                'formality_preference': (0.9, 0.85),
                'business_context': (True, 0.9)
            },
            tool_preferences={
                'communication': 'formal_template',
                'recommendations': 'business_focused'
            }
        )
        
        # Anniversary Celebration Pattern
        self.patterns['anniversary_celebration'] = TestablePattern(
            pattern_id='anniversary_celebration',
            description='Special service for anniversary celebrations',
            triggers=['anniversary', 'celebrating', 'years together', 'special occasion'],
            confidence_range=(0.8, 0.95),
            requires_confirmation=False,
            failover_strategy='special_occasion_generic',
            success_metrics={
                'emotional_resonance_score': {'min': 0.85},
                'service_coordination_success': {'min': 90, 'unit': 'percent'},
                'upsell_acceptance_rate': {'min': 60, 'unit': 'percent'}
            },
            belief_updates={
                'special_occasion': ('anniversary', 1.0),
                'celebration_magnitude': (0.9, 0.95),
                'romantic_context': (True, 1.0)
            },
            tool_preferences={
                'recommendations': 'romantic_focused',
                'reservation': 'special_occasion',
                'spa': 'couples_package'
            }
        )
        
        # Standard Business Greeting (Failover)
        self.patterns['standard_business_greeting'] = TestablePattern(
            pattern_id='standard_business_greeting',
            description='Professional greeting for business travelers',
            triggers=['business', 'conference', 'meeting'],
            confidence_range=(0.5, 0.8),
            requires_confirmation=False,
            failover_strategy=None,
            success_metrics={
                'professionalism_score': {'min': 0.8},
                'guest_satisfaction': {'min': 4.0}
            },
            belief_updates={
                'business_context': (True, 0.8)
            },
            tool_preferences={
                'property_info': 'business_amenities'
            }
        )
    
    def load_patterns(self, patterns_file: str):
        """Load patterns from YAML file"""
        with open(patterns_file, 'r') as f:
            patterns_data = yaml.safe_load(f)
            
        for pattern_id, pattern_spec in patterns_data.items():
            self.patterns[pattern_id] = TestablePattern(
                pattern_id=pattern_id,
                **pattern_spec
            )
    
    def find_applicable_patterns(self, context: Dict[str, Any]) -> List[Tuple[TestablePattern, float]]:
        """Find all patterns that could apply to the current context"""
        applicable = []
        
        for pattern in self.patterns.values():
            should_trigger, confidence = pattern.should_trigger(context)
            if should_trigger:
                applicable.append((pattern, confidence))
                
        # Sort by confidence
        applicable.sort(key=lambda x: x[1], reverse=True)
        
        return applicable
    
    def get_pattern(self, pattern_id: str) -> Optional[TestablePattern]:
        """Get a specific pattern by ID"""
        return self.patterns.get(pattern_id)
    
    def record_pattern_outcome(self, measurement: PatternMeasurement):
        """Record the outcome of a pattern execution"""
        pattern = self.patterns.get(measurement.pattern_id)
        if pattern:
            # Adjust confidence range based on outcome
            if measurement.confidence_adjustment != 0:
                new_min = max(0.1, pattern.confidence_range[0] + measurement.confidence_adjustment)
                new_max = min(0.95, pattern.confidence_range[1] + measurement.confidence_adjustment)
                pattern.confidence_range = (new_min, new_max)


class PatternValidator:
    """Validates patterns against test scenarios"""
    
    def __init__(self, pattern_library: PatternLibrary):
        self.pattern_library = pattern_library
        self.validation_results: List[Dict[str, Any]] = []
    
    async def validate_pattern(self, pattern_id: str, 
                             test_scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate a pattern against test scenarios"""
        pattern = self.pattern_library.get_pattern(pattern_id)
        if not pattern:
            raise ValueError(f"Pattern not found: {pattern_id}")
            
        results = {
            'pattern_id': pattern_id,
            'total_scenarios': len(test_scenarios),
            'passed': 0,
            'partial': 0,
            'failed': 0,
            'measurements': []
        }
        
        for scenario in test_scenarios:
            # Check if pattern should trigger
            should_trigger, confidence = pattern.should_trigger(scenario['context'])
            
            if should_trigger:
                # Simulate pattern execution
                actual_outcome = await self._simulate_pattern_execution(
                    pattern, scenario['context']
                )
                
                # Validate outcome
                measurement = pattern.validate_outcome(
                    scenario.get('expected', {}),
                    actual_outcome
                )
                
                results['measurements'].append(measurement)
                
                # Update counts
                if measurement.outcome == PatternOutcome.SUCCESS:
                    results['passed'] += 1
                elif measurement.outcome == PatternOutcome.PARTIAL_SUCCESS:
                    results['partial'] += 1
                else:
                    results['failed'] += 1
            else:
                results['failed'] += 1
                
        # Calculate success rate
        results['success_rate'] = results['passed'] / results['total_scenarios']
        results['partial_rate'] = results['partial'] / results['total_scenarios']
        
        self.validation_results.append(results)
        
        return results
    
    async def _simulate_pattern_execution(self, pattern: TestablePattern,
                                        context: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate pattern execution for testing"""
        # This is a simplified simulation
        # In production, this would actually execute the pattern
        
        simulated_outcome = {
            'communication_formality_score': 0.92,
            'cultural_appropriateness': 93,
            'guest_satisfaction': 4.7,
            'emotional_resonance_score': 0.88,
            'service_coordination_success': 92,
            'upsell_acceptance_rate': 65,
            'professionalism_score': 0.85
        }
        
        # Add some randomness for realistic testing
        import random
        for key in simulated_outcome:
            if isinstance(simulated_outcome[key], float):
                simulated_outcome[key] *= (0.9 + random.random() * 0.2)
            elif isinstance(simulated_outcome[key], int):
                simulated_outcome[key] = int(simulated_outcome[key] * (0.9 + random.random() * 0.2))
                
        return simulated_outcome
    
    def generate_validation_report(self) -> str:
        """Generate a validation report"""
        report = ["Pattern Validation Report", "=" * 50, ""]
        
        for result in self.validation_results:
            report.append(f"Pattern: {result['pattern_id']}")
            report.append(f"Scenarios: {result['total_scenarios']}")
            report.append(f"Success Rate: {result['success_rate']:.2%}")
            report.append(f"Partial Success: {result['partial_rate']:.2%}")
            report.append(f"Failures: {result['failed']}")
            report.append("")
            
        return "\n".join(report)