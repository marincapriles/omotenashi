#!/usr/bin/env python3
"""
End-to-End ReAct Agent Validation with Tool Selection Precision
---------------------------------------------------------------
This script validates the ReAct agent implementation with a focus on
measuring tool selection precision, recall, and F1 scores.

Metrics calculated:
- Precision: correct tools used / total tools used
- Recall: correct tools used / expected tools
- F1 Score: harmonic mean of precision and recall
- Tool selection patterns and reasoning quality
"""

import os
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict
import statistics
from dotenv import load_dotenv

# Add the project root to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

# Import the agents
from src.omotenashi.react_agent import OmotenaashiReActAgent as ReactAgent, AgentResponse as ReactResponse

# Only import the original agent if it's available (fallback for development)
try:
    from src.omotenashi.agent import OmotenaashiAgent as OriginalAgent, AgentResponse as OriginalResponse
    ORIGINAL_AGENT_AVAILABLE = True
except ImportError:
    print("⚠️  Original agent not available - running ReAct-only validation")
    ORIGINAL_AGENT_AVAILABLE = False


@dataclass
class ToolSelectionMetrics:
    """Metrics for tool selection performance."""
    true_positives: int = 0  # Correctly selected expected tools
    false_positives: int = 0  # Selected tools that weren't expected
    false_negatives: int = 0  # Expected tools that weren't selected
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    
    def calculate_metrics(self):
        """Calculate precision, recall, and F1 score."""
        if self.true_positives + self.false_positives > 0:
            self.precision = self.true_positives / (self.true_positives + self.false_positives)
        else:
            self.precision = 0.0
            
        if self.true_positives + self.false_negatives > 0:
            self.recall = self.true_positives / (self.true_positives + self.false_negatives)
        else:
            self.recall = 0.0
            
        if self.precision + self.recall > 0:
            self.f1_score = 2 * (self.precision * self.recall) / (self.precision + self.recall)
        else:
            self.f1_score = 0.0


@dataclass
class ValidationScenario:
    """Test scenario with expected outcomes."""
    id: int
    name: str
    description: str
    guest_message: str
    expected_tools: Set[str]
    expected_patterns: List[str]  # Patterns to look for in response
    category: str  # dining, activities, spa, etc.


@dataclass
class ValidationResult:
    """Results for a single test scenario."""
    scenario: ValidationScenario
    actual_tools: Set[str]
    response_message: str
    reasoning: str
    execution_time: float
    metrics: ToolSelectionMetrics
    patterns_found: List[str]
    agent_type: str  # "react" or "original"


class ToolSelectionValidator:
    """Validates tool selection precision for both agent implementations."""
    
    def __init__(self, api_key: str = None):
        """Initialize validator with test scenarios."""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.scenarios = self._create_test_scenarios()
        self.react_results: List[ValidationResult] = []
        self.original_results: List[ValidationResult] = []
        
    def _create_test_scenarios(self) -> List[ValidationScenario]:
        """Create comprehensive test scenarios for tool selection validation."""
        scenarios = [
            # Dining scenarios
            ValidationScenario(
                id=1,
                name="Simple dinner request",
                description="Basic dinner request without specific preferences",
                guest_message="I'd like to have dinner tonight",
                expected_tools={"get_recommendations", "make_reservation"},
                expected_patterns=["restaurant", "dining", "reservation"],
                category="dining"
            ),
            ValidationScenario(
                id=2,
                name="Specific cuisine request",
                description="Request for specific cuisine type",
                guest_message="I'm craving Italian food with a view",
                expected_tools={"get_recommendations", "make_reservation"},
                expected_patterns=["Il Cielo", "rooftop", "Italian"],
                category="dining"
            ),
            ValidationScenario(
                id=3,
                name="Anniversary dinner",
                description="Special occasion dining with implicit needs",
                guest_message="We're celebrating our anniversary tonight",
                expected_tools={"get_recommendations", "make_reservation", "property_info"},
                expected_patterns=["special", "romantic", "champagne", "memorable"],
                category="dining"
            ),
            
            # Activity scenarios
            ValidationScenario(
                id=4,
                name="General activity inquiry",
                description="Open-ended activity request",
                guest_message="What can we do this afternoon?",
                expected_tools={"get_recommendations", "property_info"},
                expected_patterns=["activities", "experience", "afternoon"],
                category="activities"
            ),
            ValidationScenario(
                id=5,
                name="Adventure activity",
                description="Request for adventurous experiences",
                guest_message="I want an exciting adventure today",
                expected_tools={"get_recommendations", "make_reservation"},
                expected_patterns=["helicopter", "sailing", "adventure"],
                category="activities"
            ),
            
            # Spa scenarios
            ValidationScenario(
                id=6,
                name="Relaxation request",
                description="General spa and relaxation inquiry",
                guest_message="I need to relax after my long flight",
                expected_tools={"get_recommendations", "book_spa"},
                expected_patterns=["spa", "treatment", "relaxation", "jet lag"],
                category="spa"
            ),
            ValidationScenario(
                id=7,
                name="Couples spa",
                description="Spa request for two people",
                guest_message="Can you book a couples massage for tomorrow?",
                expected_tools={"book_spa"},
                expected_patterns={"couples", "massage", "moonlight", "ritual"},
                category="spa"
            ),
            
            # Check-in/out scenarios
            ValidationScenario(
                id=8,
                name="Early check-in",
                description="Request for early arrival",
                guest_message="Can we check in early tomorrow? We land at 9am",
                expected_tools={"modify_checkin_checkout"},
                expected_patterns=["early", "check-in", "11:00 AM", "arranged"],
                category="checkin"
            ),
            ValidationScenario(
                id=9,
                name="Late checkout",
                description="Request for extended stay",
                guest_message="Is late checkout available? We'd like to stay until evening",
                expected_tools={"modify_checkin_checkout"},
                expected_patterns=["late", "check-out", "6:00 PM", "extended"],
                category="checkin"
            ),
            
            # Complex scenarios requiring multiple tools
            ValidationScenario(
                id=10,
                name="Full evening planning",
                description="Complex request requiring multiple services",
                guest_message="Plan a romantic evening for us - dinner, activities, everything",
                expected_tools={"get_recommendations", "make_reservation", "property_info"},
                expected_patterns=["dinner", "sunset", "romantic", "complete experience"],
                category="complex"
            ),
            ValidationScenario(
                id=11,
                name="Day planning with preferences",
                description="Full day planning with specific needs",
                guest_message="We want a relaxing day - spa in the morning, light lunch, and maybe some easy activities",
                expected_tools={"get_recommendations", "book_spa", "make_reservation"},
                expected_patterns=["spa", "lunch", "relaxing", "morning", "activities"],
                category="complex"
            ),
            
            # Property information scenarios
            ValidationScenario(
                id=12,
                name="Property overview",
                description="General property information request",
                guest_message="Tell me about the resort amenities",
                expected_tools={"property_info"},
                expected_patterns=["pools", "beach", "golf", "fitness"],
                category="property"
            ),
            
            # Edge cases
            ValidationScenario(
                id=13,
                name="Ambiguous request",
                description="Vague request that could use multiple tools",
                guest_message="What do you recommend?",
                expected_tools={"get_recommendations", "property_info"},
                expected_patterns=["recommend", "options", "available"],
                category="edge"
            ),
            ValidationScenario(
                id=14,
                name="No tools needed",
                description="Question that shouldn't trigger tools",
                guest_message="What time is it?",
                expected_tools=set(),
                expected_patterns=["time"],
                category="edge"
            ),
            ValidationScenario(
                id=15,
                name="Implicit spa need",
                description="Request that implies spa without mentioning it",
                guest_message="My muscles are really sore from the flight",
                expected_tools={"get_recommendations", "book_spa"},
                expected_patterns=["spa", "massage", "treatment", "relief"],
                category="implicit"
            )
        ]
        
        return scenarios
    
    def _calculate_metrics(self, expected: Set[str], actual: Set[str]) -> ToolSelectionMetrics:
        """Calculate precision, recall, and F1 score for tool selection."""
        metrics = ToolSelectionMetrics()
        
        # Calculate true positives, false positives, false negatives
        metrics.true_positives = len(expected.intersection(actual))
        metrics.false_positives = len(actual - expected)
        metrics.false_negatives = len(expected - actual)
        
        # Calculate precision, recall, F1
        metrics.calculate_metrics()
        
        return metrics
    
    def validate_react_agent(self) -> bool:
        """Validate the ReAct agent implementation."""
        if not REACT_AVAILABLE:
            print("❌ ReAct agent not available for testing")
            return False
            
        print("\n🧪 Validating ReAct Agent Tool Selection")
        print("=" * 60)
        
        try:
            agent = ReactAgent(self.api_key)
            
            for scenario in self.scenarios:
                print(f"\nScenario {scenario.id}: {scenario.name}")
                print(f"Message: {scenario.guest_message}")
                
                start_time = time.time()
                try:
                    response = agent.process(scenario.guest_message)
                    execution_time = time.time() - start_time
                    
                    # Extract actual tools used
                    actual_tools = set(response.tools_used)
                    
                    # Calculate metrics
                    metrics = self._calculate_metrics(scenario.expected_tools, actual_tools)
                    
                    # Check for expected patterns
                    patterns_found = [p for p in scenario.expected_patterns 
                                    if p.lower() in response.message.lower()]
                    
                    # Create result
                    result = ValidationResult(
                        scenario=scenario,
                        actual_tools=actual_tools,
                        response_message=response.message,
                        reasoning=response.reasoning,
                        execution_time=execution_time,
                        metrics=metrics,
                        patterns_found=patterns_found,
                        agent_type="react"
                    )
                    
                    self.react_results.append(result)
                    
                    # Print immediate feedback
                    print(f"✓ Expected tools: {scenario.expected_tools}")
                    print(f"  Actual tools: {actual_tools}")
                    print(f"  Precision: {metrics.precision:.2f}, Recall: {metrics.recall:.2f}, F1: {metrics.f1_score:.2f}")
                    print(f"  Time: {execution_time:.2f}s")
                    
                except Exception as e:
                    print(f"❌ Error: {str(e)}")
                    
                # Reset memory for next scenario
                agent.reset_memory()
                
                # Small delay to avoid rate limits
                time.sleep(1)
                
        except Exception as e:
            print(f"❌ Failed to initialize ReAct agent: {str(e)}")
            return False
            
        return True
    
    def validate_original_agent(self) -> bool:
        """Validate the original LangGraph agent for comparison."""
        if not ORIGINAL_AGENT_AVAILABLE:
            print("❌ Original agent not available for comparison")
            return False
            
        print("\n\n🧪 Validating Original Agent Tool Selection (for comparison)")
        print("=" * 60)
        
        try:
            agent = OriginalAgent(self.api_key)
            
            for scenario in self.scenarios[:5]:  # Test subset for comparison
                print(f"\nScenario {scenario.id}: {scenario.name}")
                
                start_time = time.time()
                try:
                    response = agent.process_message(scenario.guest_message)
                    execution_time = time.time() - start_time
                    
                    # Extract actual tools used
                    actual_tools = set(response.tools_used)
                    
                    # Calculate metrics
                    metrics = self._calculate_metrics(scenario.expected_tools, actual_tools)
                    
                    # Create result
                    result = ValidationResult(
                        scenario=scenario,
                        actual_tools=actual_tools,
                        response_message=response.message,
                        reasoning=response.reasoning,
                        execution_time=execution_time,
                        metrics=metrics,
                        patterns_found=[],
                        agent_type="original"
                    )
                    
                    self.original_results.append(result)
                    
                    print(f"  Precision: {metrics.precision:.2f}, Recall: {metrics.recall:.2f}, F1: {metrics.f1_score:.2f}")
                    
                except Exception as e:
                    print(f"❌ Error: {str(e)}")
                    
                # Reset for next scenario
                agent.reset_conversation()
                time.sleep(1)
                
        except Exception as e:
            print(f"❌ Failed to initialize original agent: {str(e)}")
            return False
            
        return True
    
    def generate_report(self):
        """Generate comprehensive validation report."""
        print("\n\n" + "=" * 80)
        print("📊 TOOL SELECTION VALIDATION REPORT")
        print("=" * 80)
        
        # ReAct Agent Results
        if self.react_results:
            print("\n🤖 ReAct Agent Performance")
            print("-" * 40)
            
            # Overall metrics
            all_precisions = [r.metrics.precision for r in self.react_results]
            all_recalls = [r.metrics.recall for r in self.react_results]
            all_f1s = [r.metrics.f1_score for r in self.react_results]
            all_times = [r.execution_time for r in self.react_results]
            
            print(f"\nOverall Metrics:")
            print(f"  Average Precision: {statistics.mean(all_precisions):.3f}")
            print(f"  Average Recall: {statistics.mean(all_recalls):.3f}")
            print(f"  Average F1 Score: {statistics.mean(all_f1s):.3f}")
            print(f"  Average Response Time: {statistics.mean(all_times):.2f}s")
            
            # Category breakdown
            print(f"\nPerformance by Category:")
            categories = defaultdict(list)
            for result in self.react_results:
                categories[result.scenario.category].append(result.metrics.f1_score)
            
            for category, scores in categories.items():
                print(f"  {category.capitalize()}: F1 = {statistics.mean(scores):.3f}")
            
            # Perfect selections
            perfect = sum(1 for r in self.react_results if r.metrics.f1_score == 1.0)
            print(f"\nPerfect Tool Selections: {perfect}/{len(self.react_results)} ({perfect/len(self.react_results)*100:.1f}%)")
            
            # Common errors
            print(f"\nCommon Tool Selection Patterns:")
            over_selection = sum(1 for r in self.react_results if r.metrics.false_positives > 0)
            under_selection = sum(1 for r in self.react_results if r.metrics.false_negatives > 0)
            print(f"  Over-selection (extra tools): {over_selection} scenarios")
            print(f"  Under-selection (missing tools): {under_selection} scenarios")
            
            # Detailed failures
            print(f"\nScenarios with Tool Selection Issues:")
            for result in self.react_results:
                if result.metrics.f1_score < 1.0:
                    print(f"\n  Scenario {result.scenario.id}: {result.scenario.name}")
                    print(f"    Expected: {result.scenario.expected_tools}")
                    print(f"    Actual: {result.actual_tools}")
                    if result.metrics.false_positives > 0:
                        extra = result.actual_tools - result.scenario.expected_tools
                        print(f"    Extra tools: {extra}")
                    if result.metrics.false_negatives > 0:
                        missing = result.scenario.expected_tools - result.actual_tools
                        print(f"    Missing tools: {missing}")
        
        # Comparison with original agent
        if self.original_results:
            print("\n\n🔄 Comparison with Original Agent")
            print("-" * 40)
            
            react_subset = [r for r in self.react_results if r.scenario.id <= 5]
            
            if react_subset:
                react_f1 = statistics.mean([r.metrics.f1_score for r in react_subset])
                original_f1 = statistics.mean([r.metrics.f1_score for r in self.original_results])
                
                react_time = statistics.mean([r.execution_time for r in react_subset])
                original_time = statistics.mean([r.execution_time for r in self.original_results])
                
                print(f"\nF1 Score Comparison:")
                print(f"  ReAct Agent: {react_f1:.3f}")
                print(f"  Original Agent: {original_f1:.3f}")
                print(f"  Improvement: {(react_f1 - original_f1)/original_f1*100:+.1f}%")
                
                print(f"\nResponse Time Comparison:")
                print(f"  ReAct Agent: {react_time:.2f}s")
                print(f"  Original Agent: {original_time:.2f}s")
                print(f"  Difference: {(react_time - original_time)/original_time*100:+.1f}%")
        
        # Key insights
        print("\n\n🔍 Key Insights")
        print("-" * 40)
        
        if self.react_results:
            # Best performing scenarios
            best = sorted(self.react_results, key=lambda r: r.metrics.f1_score, reverse=True)[:3]
            print("\nBest Tool Selection Performance:")
            for r in best:
                print(f"  • {r.scenario.name}: F1 = {r.metrics.f1_score:.3f}")
            
            # Worst performing scenarios
            worst = sorted(self.react_results, key=lambda r: r.metrics.f1_score)[:3]
            print("\nNeeds Improvement:")
            for r in worst:
                print(f"  • {r.scenario.name}: F1 = {r.metrics.f1_score:.3f}")
            
            # Omotenashi embodiment
            pattern_coverage = [len(r.patterns_found)/len(r.scenario.expected_patterns) 
                              for r in self.react_results if r.scenario.expected_patterns]
            print(f"\nOmotenaashi Pattern Coverage: {statistics.mean(pattern_coverage)*100:.1f}%")
        
        print("\n" + "=" * 80)
        
        # Save detailed results to file
        self._save_detailed_results()
    
    def _save_detailed_results(self):
        """Save detailed results to JSON file."""
        results = {
            "validation_date": datetime.now().isoformat(),
            "react_results": [
                {
                    "scenario_id": r.scenario.id,
                    "scenario_name": r.scenario.name,
                    "guest_message": r.scenario.guest_message,
                    "expected_tools": list(r.scenario.expected_tools),
                    "actual_tools": list(r.actual_tools),
                    "precision": r.metrics.precision,
                    "recall": r.metrics.recall,
                    "f1_score": r.metrics.f1_score,
                    "execution_time": r.execution_time,
                    "patterns_found": r.patterns_found,
                    "response_preview": r.response_message[:200] + "..."
                }
                for r in self.react_results
            ],
            "summary": {
                "total_scenarios": len(self.react_results),
                "average_precision": statistics.mean([r.metrics.precision for r in self.react_results]) if self.react_results else 0,
                "average_recall": statistics.mean([r.metrics.recall for r in self.react_results]) if self.react_results else 0,
                "average_f1": statistics.mean([r.metrics.f1_score for r in self.react_results]) if self.react_results else 0,
                "average_response_time": statistics.mean([r.execution_time for r in self.react_results]) if self.react_results else 0
            }
        }
        
        with open("react_validation_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: react_validation_results.json")


def main():
    """Run the validation."""
    print("🚀 Starting ReAct Agent Tool Selection Validation")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n❌ ANTHROPIC_API_KEY not found!")
        print("Please set your API key:")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)
    
    # Create validator
    validator = ToolSelectionValidator(api_key)
    
    # Run validations
    if validator.validate_react_agent():
        print("\n✅ ReAct agent validation complete")
    
    # Optional: Compare with original agent
    if '--compare' in sys.argv:
        if validator.validate_original_agent():
            print("\n✅ Original agent validation complete")
    
    # Generate report
    validator.generate_report()
    
    print("\n✨ Validation complete!")


if __name__ == "__main__":
    main()