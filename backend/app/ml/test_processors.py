"""
Test Processors for Different Assessment Types
Handles scoring and feature extraction for each test type
"""
from typing import Dict, Any, List
import re
import numpy as np

class MathTestProcessor:
    """Process math test results and extract features"""
    
    @staticmethod
    def process(test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process math test data
        
        Expected test_data:
        - problems: List of math problems
        - answers: List of student answers
        - correct_answers: List of correct answers
        - time_per_problem: List of time taken per problem
        """
        problems = test_data.get("problems", [])
        answers = test_data.get("answers", [])
        correct_answers = test_data.get("correct_answers", [])
        time_per_problem = test_data.get("time_per_problem", [])
        
        n_problems = len(problems)
        if n_problems == 0:
            return {"score": 0, "errors": 0, "features": {}}
        
        # Calculate accuracy
        correct_count = sum(1 for i in range(min(len(answers), len(correct_answers))) 
                          if str(answers[i]).strip() == str(correct_answers[i]).strip())
        accuracy = (correct_count / n_problems) * 100
        errors = n_problems - correct_count
        
        # Calculate speed metrics
        avg_time = np.mean(time_per_problem) if time_per_problem else 0
        time_consistency = 1.0 - (np.std(time_per_problem) / avg_time) if avg_time > 0 and time_per_problem else 0
        
        # Analyze error patterns
        error_types = {
            "calculation_errors": 0,
            "sign_errors": 0,
            "place_value_errors": 0
        }
        
        for i in range(min(len(answers), len(correct_answers))):
            if str(answers[i]).strip() != str(correct_answers[i]).strip():
                # Simple error classification
                try:
                    student_ans = float(answers[i])
                    correct_ans = float(correct_answers[i])
                    
                    # Check if sign is wrong
                    if student_ans == -correct_ans:
                        error_types["sign_errors"] += 1
                    # Check if magnitude is close (place value error)
                    elif abs(student_ans) / 10 == abs(correct_ans) or abs(student_ans) * 10 == abs(correct_ans):
                        error_types["place_value_errors"] += 1
                    else:
                        error_types["calculation_errors"] += 1
                except:
                    error_types["calculation_errors"] += 1
        
        features = {
            "accuracy": accuracy,
            "avg_time_per_problem": avg_time,
            "time_consistency": time_consistency,
            "calculation_errors": error_types["calculation_errors"],
            "sign_errors": error_types["sign_errors"],
            "place_value_errors": error_types["place_value_errors"],
            "completion_rate": len(answers) / n_problems if n_problems > 0 else 0
        }
        
        return {
            "score": accuracy,
            "errors": errors,
            "features": features
        }


class MemoryTestProcessor:
    """Process memory test results"""
    
    @staticmethod
    def process(test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process memory test data
        
        Expected test_data:
        - items_shown: List of items shown to student
        - items_recalled: List of items student recalled
        - recall_order: Order in which items were recalled
        - time_to_recall: Time taken to recall
        """
        items_shown = test_data.get("items_shown", [])
        items_recalled = test_data.get("items_recalled", [])
        recall_order = test_data.get("recall_order", [])
        time_to_recall = test_data.get("time_to_recall", 0)
        
        n_items = len(items_shown)
        if n_items == 0:
            return {"score": 0, "errors": 0, "features": {}}
        
        # Calculate recall accuracy
        correct_recalls = sum(1 for item in items_recalled if item in items_shown)
        recall_accuracy = (correct_recalls / n_items) * 100
        
        # Calculate order accuracy (serial recall)
        order_accuracy = 0
        if recall_order:
            correct_order = sum(1 for i, item in enumerate(recall_order) 
                              if i < len(items_shown) and item == items_shown[i])
            order_accuracy = (correct_order / n_items) * 100
        
        # False memories (items recalled but not shown)
        false_recalls = sum(1 for item in items_recalled if item not in items_shown)
        
        # Primacy and recency effects
        primacy_correct = 0
        recency_correct = 0
        if n_items >= 3:
            primacy_items = items_shown[:2]
            recency_items = items_shown[-2:]
            primacy_correct = sum(1 for item in primacy_items if item in items_recalled)
            recency_correct = sum(1 for item in recency_items if item in items_recalled)
        
        features = {
            "recall_accuracy": recall_accuracy,
            "order_accuracy": order_accuracy,
            "false_recalls": false_recalls,
            "primacy_score": primacy_correct,
            "recency_score": recency_correct,
            "time_to_recall": time_to_recall,
            "recall_rate": len(items_recalled) / n_items if n_items > 0 else 0
        }
        
        return {
            "score": recall_accuracy,
            "errors": n_items - correct_recalls + false_recalls,
            "features": features
        }


class AttentionTestProcessor:
    """Process attention/focus test results"""
    
    @staticmethod
    def process(test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process attention test data
        
        Expected test_data:
        - targets: List of target stimuli
        - distractors: List of distractor stimuli
        - responses: List of student responses
        - response_times: Time taken for each response
        - correct_targets: Number of correct target identifications
        - false_alarms: Number of incorrect target identifications
        """
        targets = test_data.get("targets", [])
        distractors = test_data.get("distractors", [])
        responses = test_data.get("responses", [])
        response_times = test_data.get("response_times", [])
        
        n_targets = len(targets)
        n_distractors = len(distractors)
        total_stimuli = n_targets + n_distractors
        
        if total_stimuli == 0:
            return {"score": 0, "errors": 0, "features": {}}
        
        # Calculate hits and false alarms
        correct_targets = test_data.get("correct_targets", 0)
        false_alarms = test_data.get("false_alarms", 0)
        
        # Calculate d' (sensitivity) and c (response bias)
        hit_rate = correct_targets / n_targets if n_targets > 0 else 0
        fa_rate = false_alarms / n_distractors if n_distractors > 0 else 0
        
        # Avoid extreme values for d' calculation
        hit_rate = max(0.01, min(0.99, hit_rate))
        fa_rate = max(0.01, min(0.99, fa_rate))
        
        from scipy import stats
        d_prime = stats.norm.ppf(hit_rate) - stats.norm.ppf(fa_rate)
        
        # Accuracy
        accuracy = ((correct_targets + (n_distractors - false_alarms)) / total_stimuli) * 100
        
        # Response time analysis
        avg_response_time = np.mean(response_times) if response_times else 0
        response_time_std = np.std(response_times) if response_times else 0
        consistency = 1.0 - (response_time_std / avg_response_time) if avg_response_time > 0 else 0
        
        # Sustained attention (performance over time)
        if len(response_times) >= 10:
            first_half = response_times[:len(response_times)//2]
            second_half = response_times[len(response_times)//2:]
            fatigue_effect = np.mean(second_half) - np.mean(first_half)
        else:
            fatigue_effect = 0
        
        features = {
            "accuracy": accuracy,
            "d_prime": float(d_prime),
            "hit_rate": hit_rate,
            "false_alarm_rate": fa_rate,
            "avg_response_time": avg_response_time,
            "response_consistency": consistency,
            "fatigue_effect": fatigue_effect
        }
        
        return {
            "score": accuracy,
            "errors": false_alarms + (n_targets - correct_targets),
            "features": features
        }


class PhonologicalTestProcessor:
    """Process phonological awareness test results"""
    
    @staticmethod
    def process(test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process phonological awareness test data
        
        Expected test_data:
        - tasks: List of phonological tasks
        - student_responses: Student's responses
        - correct_responses: Correct responses
        - task_types: Types of tasks (rhyming, segmentation, blending, etc.)
        """
        tasks = test_data.get("tasks", [])
        student_responses = test_data.get("student_responses", [])
        correct_responses = test_data.get("correct_responses", [])
        task_types = test_data.get("task_types", [])
        
        n_tasks = len(tasks)
        if n_tasks == 0:
            return {"score": 0, "errors": 0, "features": {}}
        
        # Calculate overall accuracy
        correct_count = sum(1 for i in range(min(len(student_responses), len(correct_responses)))
                          if str(student_responses[i]).strip().lower() == str(correct_responses[i]).strip().lower())
        accuracy = (correct_count / n_tasks) * 100
        errors = n_tasks - correct_count
        
        # Analyze performance by task type
        task_performance = {}
        for task_type in set(task_types):
            type_indices = [i for i, t in enumerate(task_types) if t == task_type]
            type_correct = sum(1 for i in type_indices 
                             if i < len(student_responses) and i < len(correct_responses)
                             and str(student_responses[i]).strip().lower() == str(correct_responses[i]).strip().lower())
            task_performance[task_type] = (type_correct / len(type_indices)) * 100 if type_indices else 0
        
        features = {
            "overall_accuracy": accuracy,
            "rhyming_accuracy": task_performance.get("rhyming", 0),
            "segmentation_accuracy": task_performance.get("segmentation", 0),
            "blending_accuracy": task_performance.get("blending", 0),
            "manipulation_accuracy": task_performance.get("manipulation", 0),
            "completion_rate": len(student_responses) / n_tasks if n_tasks > 0 else 0
        }
        
        return {
            "score": accuracy,
            "errors": errors,
            "features": features
        }


class VisualProcessingTestProcessor:
    """Process visual processing test results"""
    
    @staticmethod
    def process(test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process visual processing test data
        
        Expected test_data:
        - patterns: List of visual patterns shown
        - student_responses: Student's pattern recognitions
        - correct_responses: Correct pattern identifications
        - response_times: Time taken for each response
        """
        patterns = test_data.get("patterns", [])
        student_responses = test_data.get("student_responses", [])
        correct_responses = test_data.get("correct_responses", [])
        response_times = test_data.get("response_times", [])
        
        n_patterns = len(patterns)
        if n_patterns == 0:
            return {"score": 0, "errors": 0, "features": {}}
        
        # Calculate accuracy
        correct_count = sum(1 for i in range(min(len(student_responses), len(correct_responses)))
                          if str(student_responses[i]).strip() == str(correct_responses[i]).strip())
        accuracy = (correct_count / n_patterns) * 100
        errors = n_patterns - correct_count
        
        # Response time analysis
        avg_response_time = np.mean(response_times) if response_times else 0
        
        # Pattern complexity analysis (if provided)
        complexity_scores = test_data.get("pattern_complexity", [])
        if complexity_scores:
            # Performance on simple vs complex patterns
            simple_patterns = [i for i, c in enumerate(complexity_scores) if c < 3]
            complex_patterns = [i for i, c in enumerate(complexity_scores) if c >= 3]
            
            simple_accuracy = sum(1 for i in simple_patterns 
                                if i < len(student_responses) and i < len(correct_responses)
                                and student_responses[i] == correct_responses[i]) / len(simple_patterns) * 100 if simple_patterns else 0
            complex_accuracy = sum(1 for i in complex_patterns 
                                 if i < len(student_responses) and i < len(correct_responses)
                                 and student_responses[i] == correct_responses[i]) / len(complex_patterns) * 100 if complex_patterns else 0
        else:
            simple_accuracy = accuracy
            complex_accuracy = accuracy
        
        features = {
            "overall_accuracy": accuracy,
            "simple_pattern_accuracy": simple_accuracy,
            "complex_pattern_accuracy": complex_accuracy,
            "avg_response_time": avg_response_time,
            "completion_rate": len(student_responses) / n_patterns if n_patterns > 0 else 0
        }
        
        return {
            "score": accuracy,
            "errors": errors,
            "features": features
        }


# Factory pattern for test processors
TEST_PROCESSORS = {
    "math": MathTestProcessor,
    "memory": MemoryTestProcessor,
    "attention": AttentionTestProcessor,
    "phonological": PhonologicalTestProcessor,
    "visual_processing": VisualProcessingTestProcessor
}


def process_test(test_type: str, test_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process test data based on test type
    
    Args:
        test_type: Type of test
        test_data: Test data dictionary
        
    Returns:
        Dictionary with score, errors, and features
    """
    processor = TEST_PROCESSORS.get(test_type)
    if processor:
        return processor.process(test_data)
    else:
        # Default processing for unknown types
        return {
            "score": 0,
            "errors": 0,
            "features": {}
        }
