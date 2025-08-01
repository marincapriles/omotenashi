#!/usr/bin/env python3
"""
End-to-End Agent Validation Framework
------------------------------------
This script tests the complete Omotenashi agent system with real Claude API calls
to validate the BDI framework, LangGraph workflow, tool coordination, and response quality.

Key validation areas:
1. Functional correctness - Does the workflow complete successfully?
2. Tool coordination - Are tools selected and used appropriately?
3. BDI adherence - Does the response embody Omotenashi principles?
4. Response quality - Is it helpful, accurate, and warm?
5. Knowledge base usage - Are facts and policies accurate?
"""

import os
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.omotenashi.agent import OmotenaashiAgent, AgentResponse


@dataclass
class ValidationResult:
    """Container for validation results of a single test scenario."""
    scenario_id: int
    scenario_name: str
    guest_message: str
    agent_response: AgentResponse
    execution_time: float
    scores: Dict[str, int]  # 1-4 scoring for each criterion
    issues: List[str]
    strengths: List[str]
    overall_score: float


class E2EValidator:
    """
    End-to-end validation framework for the Omotenashi agent.
    Tests complete workflows with real Claude API calls.
    """
    
    def __init__(self, api_key: str):
        """Initialize the validator with agent and test scenarios."""
        self.agent = OmotenaashiAgent(api_key)
        self.test_scenarios = self._load_test_scenarios()
        self.validation_results: List[ValidationResult] = []
        
    def _load_test_scenarios(self) -> List[Dict]:
        """Load the end-to-end test scenarios."""
        with open("data/e2e_test_scenarios.json", "r") as f:
            data = json.load(f)
        return data["test_scenarios"]
    
    def _evaluate_functional_correctness(self, scenario: Dict, response: AgentResponse, 
                                       execution_time: float) -> tuple[int, List[str], List[str]]:
        """Evaluate whether the agent workflow completed successfully."""
        issues = []
        strengths = []
        
        # Check if response was generated
        if not response.message:
            issues.append("No response message generated")
            return 1, issues, strengths
        
        # Check execution time (should be under 30 seconds for good UX)
        if execution_time > 30:
            issues.append(f"Slow response time: {execution_time:.1f}s")
        elif execution_time < 10:
            strengths.append(f"Fast response time: {execution_time:.1f}s")
        
        # Check if tools were used appropriately
        expected_tools = set(scenario["expected_outcomes"]["tools_used"])
        actual_tools = set(response.tools_used)
        
        if not actual_tools and expected_tools:
            issues.append("No tools used when tools were expected")
            return 2, issues, strengths
        
        # Tool accuracy assessment
        correct_tools = expected_tools.intersection(actual_tools)
        missing_tools = expected_tools - actual_tools
        extra_tools = actual_tools - expected_tools
        
        if missing_tools:
            issues.append(f"Missing expected tools: {list(missing_tools)}")
        if extra_tools:
            issues.append(f"Unexpected tools used: {list(extra_tools)}")
        
        if len(correct_tools) == len(expected_tools) and not extra_tools:
            strengths.append("Perfect tool selection")
            return 4, issues, strengths
        elif len(correct_tools) >= len(expected_tools) * 0.5:
            return 3, issues, strengths
        else:
            return 2, issues, strengths
    
    def _evaluate_bdi_adherence(self, scenario: Dict, response: AgentResponse) -> tuple[int, List[str], List[str]]:
        """Evaluate how well the response embodies Omotenashi BDI principles."""
        issues = []
        strengths = []
        
        message = response.message.lower()
        reasoning = response.reasoning.lower()
        
        # Check for Omotenashi keywords and concepts
        omotenashi_indicators = [
            "delighted", "pleasure", "exceptional", "anticipate", "exceed",
            "seamless", "memorable", "personalized", "genuine", "care",
            "warmth", "attention", "detail", "thoughtful"
        ]
        
        # Check for anticipatory service
        anticipatory_phrases = [
            "also recommend", "might also", "additionally", "perfect pairing",
            "complete the experience", "enhance", "complement"
        ]
        
        # Count Omotenashi indicators
        omotenashi_count = sum(1 for indicator in omotenashi_indicators if indicator in message)
        anticipatory_count = sum(1 for phrase in anticipatory_phrases if phrase in message)
        
        # Evaluate BDI grounding in reasoning
        bdi_keywords = ["belief", "desire", "intention", "omotenashi", "principle"]
        bdi_reasoning = sum(1 for keyword in bdi_keywords if keyword in reasoning)
        
        # Scoring logic
        total_indicators = omotenashi_count + anticipatory_count + bdi_reasoning
        
        if total_indicators >= 5:
            strengths.append("Strong Omotenashi embodiment with multiple indicators")
            return 4, issues, strengths
        elif total_indicators >= 3:
            strengths.append("Good Omotenashi presence")
            return 3, issues, strengths
        elif total_indicators >= 1:
            return 2, issues, strengths
        else:
            issues.append("Minimal Omotenashi principles evident")
            return 1, issues, strengths
    
    def _evaluate_response_quality(self, scenario: Dict, response: AgentResponse) -> tuple[int, List[str], List[str]]:
        """Evaluate the overall quality, helpfulness, and structure of the response."""
        issues = []
        strengths = []
        
        message = response.message
        
        # Check response length (should be substantial but not overwhelming)
        word_count = len(message.split())
        if word_count < 20:
            issues.append("Response too brief, lacks detail")
        elif word_count > 300:
            issues.append("Response too lengthy, may overwhelm guest")
        else:
            strengths.append("Appropriate response length")
        
        # Check for specific details from knowledge base
        specific_indicators = [
            "$", "pm", "am", "minute", "hour", "floor", "building",
            "confirmed", "available", "included", "complimentary"
        ]
        specificity_count = sum(1 for indicator in specific_indicators if indicator.lower() in message.lower())
        
        if specificity_count >= 3:
            strengths.append("Rich specific details provided")
        elif specificity_count < 1:
            issues.append("Lacks specific actionable details")
        
        # Check for clear structure and actionability
        if ":" in message or "•" in message or "-" in message:
            strengths.append("Well-structured response")
        
        # Check for warmth and hospitality tone
        warm_phrases = [
            "i'd be", "delighted", "pleasure", "happy to", "wonderful",
            "excellent", "perfect", "beautiful", "amazing"
        ]
        warmth_count = sum(1 for phrase in warm_phrases if phrase in message.lower())
        
        if warmth_count >= 2:
            strengths.append("Warm, hospitable tone")
        elif warmth_count == 0:
            issues.append("Response lacks warmth and hospitality")
        
        # Overall scoring
        if len(strengths) >= 3 and len(issues) == 0:
            return 4, issues, strengths
        elif len(strengths) >= 2 and len(issues) <= 1:
            return 3, issues, strengths
        elif len(strengths) >= 1:
            return 2, issues, strengths
        else:
            return 1, issues, strengths
    
    def _evaluate_knowledge_base_usage(self, scenario: Dict, response: AgentResponse) -> tuple[int, List[str], List[str]]:
        """Evaluate accuracy of knowledge base usage."""
        issues = []
        strengths = []
        
        message = response.message.lower()
        
        # Check for accurate property references
        accurate_refs = [
            "grand omotenashi resort", "kaiseki", "il cielo", "serenity spa",
            "michelin", "chef yamamoto", "200 rooms", "onsen"
        ]
        
        accuracy_count = sum(1 for ref in accurate_refs if ref in message)
        
        # Check for potential inaccuracies (things not in our knowledge base)
        potential_inaccuracies = [
            "nobu", "la bernardin", "ritz carlton", "four seasons",
            "downtown", "city center", "uber", "taxi"
        ]
        
        inaccuracy_count = sum(1 for inaccuracy in potential_inaccuracies if inaccuracy in message)
        
        if accuracy_count >= 2 and inaccuracy_count == 0:
            strengths.append("Accurate use of property knowledge base")
            return 4, issues, strengths
        elif accuracy_count >= 1 and inaccuracy_count == 0:
            return 3, issues, strengths
        elif inaccuracy_count > 0:
            issues.append(f"Potential inaccuracies or off-property references: {inaccuracy_count}")
            return 2, issues, strengths
        else:
            return 2, issues, strengths
    
    def validate_scenario(self, scenario: Dict) -> ValidationResult:
        """Validate a single test scenario."""
        print(f"Testing Scenario {scenario['id']}: {scenario['name']}")
        
        start_time = time.time()
        
        try:
            # Run the agent with the guest message
            response = self.agent.process_message(scenario["guest_message"])
            execution_time = time.time() - start_time
            
            # Evaluate all criteria
            func_score, func_issues, func_strengths = self._evaluate_functional_correctness(scenario, response, execution_time)
            bdi_score, bdi_issues, bdi_strengths = self._evaluate_bdi_adherence(scenario, response)
            quality_score, quality_issues, quality_strengths = self._evaluate_response_quality(scenario, response)
            kb_score, kb_issues, kb_strengths = self._evaluate_knowledge_base_usage(scenario, response)
            
            # Combine results
            scores = {
                "functional_correctness": func_score,
                "bdi_adherence": bdi_score,
                "response_quality": quality_score,
                "knowledge_base_usage": kb_score
            }
            
            all_issues = func_issues + bdi_issues + quality_issues + kb_issues
            all_strengths = func_strengths + bdi_strengths + quality_strengths + kb_strengths
            
            overall_score = sum(scores.values()) / len(scores)
            
            return ValidationResult(
                scenario_id=scenario["id"],
                scenario_name=scenario["name"],
                guest_message=scenario["guest_message"],
                agent_response=response,
                execution_time=execution_time,
                scores=scores,
                issues=all_issues,
                strengths=all_strengths,
                overall_score=overall_score
            )
            
        except Exception as e:
            print(f"  ❌ Error in scenario {scenario['id']}: {str(e)}")
            
            # Create error result
            return ValidationResult(
                scenario_id=scenario["id"],
                scenario_name=scenario["name"],
                guest_message=scenario["guest_message"],
                agent_response=AgentResponse("", [], f"Error: {str(e)}"),
                execution_time=time.time() - start_time,
                scores={"functional_correctness": 1, "bdi_adherence": 1, "response_quality": 1, "knowledge_base_usage": 1},
                issues=[f"Agent execution failed: {str(e)}"],
                strengths=[],
                overall_score=1.0
            )
    
    def run_validation(self, scenario_ids: List[int] = None) -> None:
        """Run validation on specified scenarios (or all if none specified)."""
        scenarios_to_test = self.test_scenarios
        if scenario_ids:
            scenarios_to_test = [s for s in self.test_scenarios if s["id"] in scenario_ids]
        
        print(f"Running end-to-end validation on {len(scenarios_to_test)} scenarios...")
        print("=" * 80)
        
        for i, scenario in enumerate(scenarios_to_test, 1):
            print(f"\n[{i}/{len(scenarios_to_test)}] ", end="")
            result = self.validate_scenario(scenario)
            self.validation_results.append(result)
            
            # Brief result summary
            print(f"  Score: {result.overall_score:.1f}/4.0 ({result.execution_time:.1f}s)")
            if result.issues:
                print(f"  Issues: {len(result.issues)}")
            if result.strengths:
                print(f"  Strengths: {len(result.strengths)}")
    
    def generate_summary_report(self) -> str:
        """Generate a comprehensive summary report."""
        if not self.validation_results:
            return "No validation results available."
        
        # Calculate aggregate metrics
        total_scenarios = len(self.validation_results)
        avg_overall_score = sum(r.overall_score for r in self.validation_results) / total_scenarios
        avg_execution_time = sum(r.execution_time for r in self.validation_results) / total_scenarios
        
        # Score breakdown
        score_breakdown = {}
        for criterion in ["functional_correctness", "bdi_adherence", "response_quality", "knowledge_base_usage"]:
            avg_score = sum(r.scores[criterion] for r in self.validation_results) / total_scenarios
            score_breakdown[criterion] = avg_score
        
        # Success rate
        successful_scenarios = sum(1 for r in self.validation_results if r.overall_score >= 3.0)
        success_rate = successful_scenarios / total_scenarios
        
        # Common issues and strengths
        all_issues = []
        all_strengths = []
        for result in self.validation_results:
            all_issues.extend(result.issues)
            all_strengths.extend(result.strengths)
        
        # Top issues and strengths
        from collections import Counter
        top_issues = Counter(all_issues).most_common(5)
        top_strengths = Counter(all_strengths).most_common(5)
        
        report = f"""
{'='*80}
OMOTENASHI AGENT END-TO-END VALIDATION REPORT
{'='*80}

EXECUTIVE SUMMARY
-----------------
Total Scenarios Tested: {total_scenarios}
Overall Average Score: {avg_overall_score:.2f}/4.0 ({avg_overall_score/4*100:.1f}%)
Success Rate (≥3.0): {success_rate:.1f}% ({successful_scenarios}/{total_scenarios} scenarios)
Average Response Time: {avg_execution_time:.1f} seconds

DETAILED METRICS
----------------
Functional Correctness: {score_breakdown['functional_correctness']:.2f}/4.0
BDI Adherence: {score_breakdown['bdi_adherence']:.2f}/4.0
Response Quality: {score_breakdown['response_quality']:.2f}/4.0
Knowledge Base Usage: {score_breakdown['knowledge_base_usage']:.2f}/4.0

SCENARIO PERFORMANCE BREAKDOWN
------------------------------"""
        
        for result in self.validation_results:
            status = "✅" if result.overall_score >= 3.0 else "⚠️" if result.overall_score >= 2.0 else "❌"
            report += f"""
{status} Scenario {result.scenario_id}: {result.scenario_name}
   Score: {result.overall_score:.1f}/4.0 | Time: {result.execution_time:.1f}s
   Tools: {', '.join(result.agent_response.tools_used) if result.agent_response.tools_used else 'None'}"""
        
        report += f"""

TOP ISSUES IDENTIFIED
--------------------"""
        for issue, count in top_issues:
            report += f"""
• {issue} ({count} occurrences)"""
        
        report += f"""

TOP STRENGTHS OBSERVED
---------------------"""
        for strength, count in top_strengths:
            report += f"""
• {strength} ({count} occurrences)"""
        
        report += f"""

RECOMMENDATIONS
--------------
1. Focus on scenarios scoring below 3.0 for immediate improvement
2. Address most common issues identified above
3. Leverage observed strengths in weaker areas
4. {"Optimize response time" if avg_execution_time > 15 else "Response time is acceptable"}
5. {"Improve BDI adherence" if score_breakdown['bdi_adherence'] < 3.0 else "BDI implementation is strong"}
"""
        
        return report
    
    def save_detailed_results(self, filename: str = None) -> str:
        """Save detailed results to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"e2e_validation_results_{timestamp}.json"
        
        # Convert results to serializable format
        serializable_results = []
        for result in self.validation_results:
            result_dict = asdict(result)
            # Convert AgentResponse to dict
            result_dict['agent_response'] = {
                'message': result.agent_response.message,
                'tools_used': result.agent_response.tools_used,
                'reasoning': result.agent_response.reasoning
            }
            serializable_results.append(result_dict)
        
        with open(filename, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        return filename


def main():
    """Run end-to-end validation."""
    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment")
        print("Please set your API key to run end-to-end validation")
        sys.exit(1)
    
    print("🧪 Initializing Omotenashi End-to-End Validation...")
    
    validator = E2EValidator(api_key)
    
    # Option to test specific scenarios
    if len(sys.argv) > 1:
        try:
            scenario_ids = [int(x) for x in sys.argv[1:]]
            print(f"Testing specific scenarios: {scenario_ids}")
            validator.run_validation(scenario_ids)
        except ValueError:
            print("Invalid scenario IDs. Please provide integers.")
            sys.exit(1)
    else:
        # Test first 5 scenarios by default to avoid high API costs
        print("Testing first 5 scenarios (use 'python e2e_validation.py 1 2 3...' for specific scenarios)")
        validator.run_validation([1, 2, 3, 4, 5])
    
    # Generate and display results
    print("\n" + "="*80)
    print("Generating validation report...")
    
    summary = validator.generate_summary_report()
    print(summary)
    
    # Save detailed results
    filename = validator.save_detailed_results()
    print(f"\n📊 Detailed results saved to: {filename}")


if __name__ == "__main__":
    main()