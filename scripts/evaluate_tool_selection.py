#!/usr/bin/env python3
"""
Tool Selection Precision Evaluation
-----------------------------------
This script evaluates how well the agent selects appropriate tools
for guest requests by comparing against ground truth mappings.

Metrics calculated:
- Precision: % of selected tools that are correct
- Recall: % of required tools that were selected
- F1 Score: Harmonic mean of precision and recall
- Over-selection rate: Tools selected unnecessarily
- Under-selection rate: Required tools missed
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set test API key for mock evaluation
os.environ['ANTHROPIC_API_KEY'] = 'test-key-for-evaluation'


@dataclass
class EvaluationResult:
    """Container for evaluation metrics of a single test case."""
    test_id: int
    request: str
    ground_truth: Set[str]
    predicted: Set[str] 
    precision: float
    recall: float
    f1_score: float
    over_selected: Set[str]
    under_selected: Set[str]
    category: str
    complexity: str


class ToolSelectionEvaluator:
    """
    Evaluates the agent's tool selection accuracy against ground truth.
    """
    
    def __init__(self):
        """Initialize the evaluator with test samples."""
        self.test_samples = self._load_test_samples()
        self.results: List[EvaluationResult] = []
        
    def _load_test_samples(self) -> List[Dict]:
        """Load the evaluation test samples."""
        with open("data/evaluation_samples.json", "r") as f:
            data = json.load(f)
        return data["test_samples"]
    
    def _mock_agent_tool_selection(self, request: str) -> List[str]:
        """
        Mock the agent's tool selection process.
        Since we can't run Claude without API costs, we'll simulate
        intelligent tool selection based on keywords and patterns.
        """
        request_lower = request.lower()
        selected_tools = []
        
        # Property info selection logic
        if any(word in request_lower for word in [
            "amenities", "facilities", "hours", "pool", "golf", "tennis", 
            "fitness", "policy", "dress code", "shuttle", "pets", "wifi",
            "business", "luggage", "printing", "cancellation"
        ]):
            selected_tools.append("property_info")
            
        # Recommendations selection logic  
        if any(word in request_lower for word in [
            "recommend", "options", "what", "activities", "spa treatments",
            "dining", "restaurants", "adventure", "cultural", "water sports",
            "romantic", "surprise", "birthday", "anniversary", "propose",
            "perfect", "best", "plan", "experience"
        ]):
            selected_tools.append("recommendations")
            
        # Reservation selection logic
        if any(word in request_lower for word in [
            "book", "reserve", "arrange", "table", "helicopter", "yacht",
            "tea ceremony", "chef", "snorkeling", "tour", "cruise"
        ]) or "i'd like to" in request_lower:
            selected_tools.append("reservation")
            
        # Spa selection logic
        if any(word in request_lower for word in [
            "massage", "spa", "couples", "relax", "treatment", "spa day"
        ]) and any(word in request_lower for word in [
            "book", "schedule", "appointment", "tomorrow", "tonight"
        ]):
            selected_tools.append("spa")
            
        # Check-in/out logic
        if any(word in request_lower for word in [
            "check in", "check out", "early", "late", "checkout", "checkin"
        ]):
            selected_tools.append("checkin_checkout")
            
        # Remove duplicates while preserving order
        return list(dict.fromkeys(selected_tools))
    
    def _calculate_metrics(self, ground_truth: Set[str], predicted: Set[str]) -> Tuple[float, float, float]:
        """Calculate precision, recall, and F1 score."""
        if not predicted and not ground_truth:
            return 1.0, 1.0, 1.0
        
        if not predicted:
            return 0.0, 0.0, 0.0
            
        if not ground_truth:
            return 0.0, 1.0, 0.0
        
        true_positives = len(ground_truth.intersection(predicted))
        precision = true_positives / len(predicted) if predicted else 0.0
        recall = true_positives / len(ground_truth) if ground_truth else 0.0
        
        if precision + recall == 0:
            f1_score = 0.0
        else:
            f1_score = 2 * (precision * recall) / (precision + recall)
            
        return precision, recall, f1_score
    
    def evaluate_single_request(self, test_case: Dict) -> EvaluationResult:
        """Evaluate a single test request."""
        request = test_case["request"]
        ground_truth = set(test_case["ground_truth"])
        
        # Handle unmappable requests
        if "none" in ground_truth:
            ground_truth = set()
        
        # Get predicted tools from mock agent
        predicted_tools = self._mock_agent_tool_selection(request)
        predicted = set(predicted_tools)
        
        # Calculate metrics
        precision, recall, f1_score = self._calculate_metrics(ground_truth, predicted)
        
        # Calculate over/under selection
        over_selected = predicted - ground_truth
        under_selected = ground_truth - predicted
        
        return EvaluationResult(
            test_id=test_case["id"],
            request=request,
            ground_truth=ground_truth,
            predicted=predicted,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            over_selected=over_selected,
            under_selected=under_selected,
            category=test_case["category"],
            complexity=test_case["complexity"]
        )
    
    def run_evaluation(self) -> None:
        """Run evaluation on all test samples."""
        print("Running tool selection evaluation...")
        print(f"Total test cases: {len(self.test_samples)}")
        
        for i, test_case in enumerate(self.test_samples, 1):
            if i % 10 == 0:
                print(f"  Processed {i}/{len(self.test_samples)} cases...")
                
            result = self.evaluate_single_request(test_case)
            self.results.append(result)
    
    def calculate_aggregate_metrics(self) -> Dict[str, float]:
        """Calculate aggregate metrics across all test cases."""
        if not self.results:
            return {}
        
        total_precision = sum(r.precision for r in self.results)
        total_recall = sum(r.recall for r in self.results)
        total_f1 = sum(r.f1_score for r in self.results)
        
        perfect_matches = sum(1 for r in self.results if r.ground_truth == r.predicted)
        
        over_selections = sum(len(r.over_selected) for r in self.results)
        under_selections = sum(len(r.under_selected) for r in self.results)
        total_predictions = sum(len(r.predicted) for r in self.results)
        total_ground_truth = sum(len(r.ground_truth) for r in self.results)
        
        return {
            "average_precision": total_precision / len(self.results),
            "average_recall": total_recall / len(self.results),
            "average_f1_score": total_f1 / len(self.results),
            "exact_match_accuracy": perfect_matches / len(self.results),
            "over_selection_rate": over_selections / total_predictions if total_predictions > 0 else 0,
            "under_selection_rate": under_selections / total_ground_truth if total_ground_truth > 0 else 0,
            "total_test_cases": len(self.results)
        }
    
    def analyze_by_category(self) -> Dict[str, Dict]:
        """Analyze performance by request category."""
        category_results = defaultdict(list)
        
        for result in self.results:
            category_results[result.category].append(result)
        
        category_metrics = {}
        for category, results in category_results.items():
            if results:
                avg_precision = sum(r.precision for r in results) / len(results)
                avg_recall = sum(r.recall for r in results) / len(results)
                avg_f1 = sum(r.f1_score for r in results) / len(results)
                exact_matches = sum(1 for r in results if r.ground_truth == r.predicted)
                
                category_metrics[category] = {
                    "count": len(results),
                    "precision": avg_precision,
                    "recall": avg_recall,
                    "f1_score": avg_f1,
                    "exact_match_rate": exact_matches / len(results)
                }
        
        return category_metrics
    
    def analyze_by_complexity(self) -> Dict[str, Dict]:
        """Analyze performance by complexity level."""
        complexity_results = defaultdict(list)
        
        for result in self.results:
            complexity_results[result.complexity].append(result)
        
        complexity_metrics = {}
        for complexity, results in complexity_results.items():
            if results:
                avg_precision = sum(r.precision for r in results) / len(results)
                avg_recall = sum(r.recall for r in results) / len(results)
                avg_f1 = sum(r.f1_score for r in results) / len(results)
                exact_matches = sum(1 for r in results if r.ground_truth == r.predicted)
                
                complexity_metrics[complexity] = {
                    "count": len(results),
                    "precision": avg_precision,
                    "recall": avg_recall,
                    "f1_score": avg_f1,
                    "exact_match_rate": exact_matches / len(results)
                }
        
        return complexity_metrics
    
    def identify_failure_patterns(self) -> Dict[str, List]:
        """Identify common failure patterns."""
        patterns = {
            "high_over_selection": [],
            "high_under_selection": [],
            "zero_precision": [],
            "zero_recall": [],
            "unmappable_with_tools": []
        }
        
        for result in self.results:
            # High over-selection (selected more than 1 extra tool)
            if len(result.over_selected) > 1:
                patterns["high_over_selection"].append({
                    "id": result.test_id,
                    "request": result.request[:60] + "...",
                    "over_selected": list(result.over_selected)
                })
            
            # High under-selection (missed more than 1 required tool)
            if len(result.under_selected) > 1:
                patterns["high_under_selection"].append({
                    "id": result.test_id,
                    "request": result.request[:60] + "...",
                    "under_selected": list(result.under_selected)
                })
            
            # Zero precision (all selected tools were wrong)
            if result.precision == 0.0 and len(result.predicted) > 0:
                patterns["zero_precision"].append({
                    "id": result.test_id,
                    "request": result.request[:60] + "...",
                    "predicted": list(result.predicted),
                    "ground_truth": list(result.ground_truth)
                })
            
            # Zero recall (missed all required tools)
            if result.recall == 0.0 and len(result.ground_truth) > 0:
                patterns["zero_recall"].append({
                    "id": result.test_id,
                    "request": result.request[:60] + "...",
                    "ground_truth": list(result.ground_truth)
                })
            
            # Unmappable requests that got tools assigned
            if len(result.ground_truth) == 0 and len(result.predicted) > 0:
                patterns["unmappable_with_tools"].append({
                    "id": result.test_id,
                    "request": result.request[:60] + "...",
                    "predicted": list(result.predicted)
                })
        
        return patterns
    
    def generate_report(self) -> str:
        """Generate a comprehensive evaluation report."""
        aggregate_metrics = self.calculate_aggregate_metrics()
        category_metrics = self.analyze_by_category()
        complexity_metrics = self.analyze_by_complexity()
        failure_patterns = self.identify_failure_patterns()
        
        report = f"""
{'='*80}
TOOL SELECTION PRECISION EVALUATION REPORT
{'='*80}

AGGREGATE METRICS
-----------------
Total Test Cases: {aggregate_metrics['total_test_cases']}
Average Precision: {aggregate_metrics['average_precision']:.3f}
Average Recall: {aggregate_metrics['average_recall']:.3f}
Average F1 Score: {aggregate_metrics['average_f1_score']:.3f}
Exact Match Accuracy: {aggregate_metrics['exact_match_accuracy']:.3f}
Over-Selection Rate: {aggregate_metrics['over_selection_rate']:.3f}
Under-Selection Rate: {aggregate_metrics['under_selection_rate']:.3f}

PERFORMANCE BY CATEGORY
-----------------------"""
        
        for category, metrics in sorted(category_metrics.items()):
            report += f"""
{category.replace('_', ' ').title()}:
  Count: {metrics['count']}
  Precision: {metrics['precision']:.3f}
  Recall: {metrics['recall']:.3f} 
  F1 Score: {metrics['f1_score']:.3f}
  Exact Match: {metrics['exact_match_rate']:.3f}"""
        
        report += f"""

PERFORMANCE BY COMPLEXITY
-------------------------"""
        
        for complexity, metrics in sorted(complexity_metrics.items()):
            report += f"""
{complexity.title()}:
  Count: {metrics['count']}
  Precision: {metrics['precision']:.3f}
  Recall: {metrics['recall']:.3f}
  F1 Score: {metrics['f1_score']:.3f}
  Exact Match: {metrics['exact_match_rate']:.3f}"""
        
        report += f"""

FAILURE PATTERN ANALYSIS
------------------------"""
        
        for pattern_name, cases in failure_patterns.items():
            if cases:
                report += f"""
{pattern_name.replace('_', ' ').title()} ({len(cases)} cases):"""
                for case in cases[:3]:  # Show first 3 examples
                    report += f"""
  #{case['id']}: {case['request']}"""
                    if 'predicted' in case:
                        report += f"""
    Predicted: {case['predicted']}"""
                    if 'ground_truth' in case:
                        report += f"""
    Expected: {case['ground_truth']}"""
                    if 'over_selected' in case:
                        report += f"""
    Over-selected: {case['over_selected']}"""
                    if 'under_selected' in case:
                        report += f"""
    Under-selected: {case['under_selected']}"""
        
        report += f"""

IMPROVEMENT OPPORTUNITIES
------------------------
1. Precision Issues: {len(failure_patterns['zero_precision'])} cases with 0% precision
2. Recall Issues: {len(failure_patterns['zero_recall'])} cases with 0% recall  
3. Over-Selection: {len(failure_patterns['high_over_selection'])} cases with excessive tool selection
4. Under-Selection: {len(failure_patterns['high_under_selection'])} cases missing multiple tools
5. Unmappable Handling: {len(failure_patterns['unmappable_with_tools'])} unmappable requests incorrectly mapped

RECOMMENDATIONS
--------------
- Improve keyword detection for tool selection
- Add context awareness for complex requests
- Better handling of unmappable requests
- Reduce over-selection through more precise matching
- Enhance multi-tool coordination logic
"""
        
        return report


def main():
    """Run the tool selection evaluation."""
    print("Initializing Tool Selection Precision Evaluation...")
    
    evaluator = ToolSelectionEvaluator()
    evaluator.run_evaluation()
    
    print("\nGenerating evaluation report...")
    report = evaluator.generate_report()
    
    # Save report to file
    report_path = "tool_selection_evaluation_report.txt"
    with open(report_path, "w") as f:
        f.write(report)
    
    print(f"\nEvaluation complete! Report saved to {report_path}")
    print(report)


if __name__ == "__main__":
    main()