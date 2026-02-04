"""
ML model inference for learning disability detection
"""
from sqlalchemy.orm import Session
from typing import Dict, Any
import numpy as np
import pickle
from pathlib import Path

from app.models import TestResult, MLPrediction

# Model paths (these would be trained models)
MODEL_DIR = Path("app/ml/models")

def run_ml_inference(test_result: TestResult, db: Session) -> MLPrediction:
    """
    Run ML inference on test result to predict learning disability
    """
    features = test_result.features
    test_type = test_result.test_type
    test_data = test_result.test_data
    
    # Determine which model to use
    if test_type == "reading":
        prediction_class, confidence, risk_level = predict_dyslexia(features)
        feedback = generate_reading_feedback(features, test_data)
    elif test_type == "writing":
        prediction_class, confidence, risk_level = predict_dysgraphia(features)
        feedback = generate_writing_feedback(features, test_data)
    elif test_type == "math":
        prediction_class, confidence, risk_level = predict_dyscalculia(features)
        feedback = generate_math_feedback(features, test_data)
    else:
        # For other test types
        prediction_class = "none"
        confidence = 0.5
        risk_level = "low"
        feedback = generate_general_feedback(features, test_data, test_type)
    
    # Add feedback to features
    features_with_feedback = features.copy()
    features_with_feedback['detailed_feedback'] = feedback
    
    # Create prediction record
    prediction = MLPrediction(
        test_result_id=test_result.id,
        model_type="sklearn",  # or "tensorflow" depending on model used
        model_name=f"{test_type}_classifier",
        prediction_class=prediction_class,
        confidence_score=confidence,
        risk_level=risk_level,
        features_used=features_with_feedback
    )
    
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    
    return prediction

def predict_dyslexia(features: Dict[str, Any]) -> tuple:
    """
    Predict dyslexia based on reading test features
    Uses rule-based system (can be replaced with trained ML model)
    """
    # Extract key features
    accuracy = features.get("accuracy", 100)
    reading_speed = features.get("reading_speed", 100)
    error_rate = features.get("error_rate", 0)
    reversed_letters = features.get("reversed_letters", 0)
    letter_confusions = features.get("letter_confusions", 0)
    
    # Calculate risk score
    risk_score = 0.0
    
    # Low accuracy indicator
    if accuracy < 70:
        risk_score += 0.3
    elif accuracy < 85:
        risk_score += 0.15
    
    # Slow reading speed (assuming normal is 150-200 wpm for adults, lower for children)
    if reading_speed < 80:
        risk_score += 0.25
    elif reading_speed < 120:
        risk_score += 0.15
    
    # High error rate
    if error_rate > 20:
        risk_score += 0.2
    elif error_rate > 10:
        risk_score += 0.1
    
    # Letter reversals
    if reversed_letters > 3:
        risk_score += 0.15
    elif reversed_letters > 0:
        risk_score += 0.05
    
    # Letter confusions
    if letter_confusions > 3:
        risk_score += 0.1
    
    # Determine classification
    if risk_score >= 0.6:
        prediction_class = "dyslexia"
        risk_level = "high"
    elif risk_score >= 0.35:
        prediction_class = "dyslexia"
        risk_level = "medium"
    elif risk_score >= 0.2:
        prediction_class = "dyslexia"
        risk_level = "low"
    else:
        prediction_class = "none"
        risk_level = "low"
    
    confidence = min(risk_score * 1.2, 0.95)  # Scale to confidence
    
    return prediction_class, round(confidence, 3), risk_level

def predict_dysgraphia(features: Dict[str, Any]) -> tuple:
    """
    Predict dysgraphia based on writing test features
    Uses rule-based system (can be replaced with trained ML model)
    """
    # Extract key features
    accuracy = features.get("accuracy", 100)
    spelling_errors = features.get("spelling_errors", 0)
    grammar_errors = features.get("grammar_errors", 0)
    letter_reversals = features.get("letter_reversals", 0)
    inconsistent_spacing = features.get("inconsistent_spacing", 0)
    writing_speed = features.get("writing_speed", 100)
    
    # Calculate risk score
    risk_score = 0.0
    
    # Low accuracy
    if accuracy < 60:
        risk_score += 0.3
    elif accuracy < 75:
        risk_score += 0.15
    
    # Spelling errors
    if spelling_errors > 5:
        risk_score += 0.25
    elif spelling_errors > 2:
        risk_score += 0.1
    
    # Grammar errors
    if grammar_errors > 4:
        risk_score += 0.15
    elif grammar_errors > 2:
        risk_score += 0.08
    
    # Letter reversals
    if letter_reversals > 2:
        risk_score += 0.15
    
    # Spacing issues
    if inconsistent_spacing > 0:
        risk_score += 0.1
    
    # Slow writing speed
    if writing_speed < 40:
        risk_score += 0.15
    
    # Determine classification
    if risk_score >= 0.6:
        prediction_class = "dysgraphia"
        risk_level = "high"
    elif risk_score >= 0.35:
        prediction_class = "dysgraphia"
        risk_level = "medium"
    elif risk_score >= 0.2:
        prediction_class = "dysgraphia"
        risk_level = "low"
    else:
        prediction_class = "none"
        risk_level = "low"
    
    confidence = min(risk_score * 1.2, 0.95)
    
    return prediction_class, round(confidence, 3), risk_level

def predict_dyscalculia(features: Dict[str, Any]) -> tuple:
    """
    Predict dyscalculia based on math test features
    Uses rule-based system (can be replaced with trained ML model)
    """
    # Extract key features
    accuracy = features.get("accuracy", 100)
    calculation_errors = features.get("calculation_errors", 0)
    concept_errors = features.get("concept_errors", 0)
    procedure_errors = features.get("procedure_errors", 0)
    number_reversals = features.get("number_reversals", 0)
    total_problems = features.get("total_problems", 10)
    
    # Calculate risk score
    risk_score = 0.0
    
    # Low accuracy
    if accuracy < 60:
        risk_score += 0.35
    elif accuracy < 75:
        risk_score += 0.2
    
    # Calculation errors
    calc_error_rate = (calculation_errors / max(total_problems, 1)) * 100
    if calc_error_rate > 40:
        risk_score += 0.25
    elif calc_error_rate > 20:
        risk_score += 0.12
    
    # Concept errors (more serious)
    concept_error_rate = (concept_errors / max(total_problems, 1)) * 100
    if concept_error_rate > 30:
        risk_score += 0.2
    elif concept_error_rate > 15:
        risk_score += 0.1
    
    # Number reversals
    if number_reversals > 2:
        risk_score += 0.15
    elif number_reversals > 0:
        risk_score += 0.08
    
    # Determine classification
    if risk_score >= 0.6:
        prediction_class = "dyscalculia"
        risk_level = "high"
    elif risk_score >= 0.35:
        prediction_class = "dyscalculia"
        risk_level = "medium"
    elif risk_score >= 0.2:
        prediction_class = "dyscalculia"
        risk_level = "low"
    else:
        prediction_class = "none"
        risk_level = "low"
    
    confidence = min(risk_score * 1.2, 0.95)
    
    return prediction_class, round(confidence, 3), risk_level

def load_ml_model(model_path: str):
    """Load a trained ML model from disk"""
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        return model
    except FileNotFoundError:
        return None

def prepare_features_for_model(features: Dict[str, Any], feature_names: list) -> np.ndarray:
    """Prepare features in the correct format for model input"""
    feature_vector = []
    for name in feature_names:
        feature_vector.append(features.get(name, 0))
    return np.array(feature_vector).reshape(1, -1)

def generate_writing_feedback(features: Dict[str, Any], test_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate detailed feedback for writing test"""
    feedback = {
        "errors": [],
        "skipped": [],
        "concerns": []
    }
    
    prompt = test_data.get("prompt", "")
    # Check both possible field names
    student_text = test_data.get("text_written", test_data.get("student_text", ""))
    
    if not prompt or not student_text:
        return feedback
    
    # Split into words for comparison
    prompt_words = prompt.strip().split()
    student_words = student_text.strip().split()
    
    # Check what was not written
    if len(student_words) < len(prompt_words):
        # Find the missing words at the end
        missing_words = ' '.join(prompt_words[len(student_words):])
        if missing_words:
            feedback["skipped"].append(f'Did not write: "{missing_words}"')
        
        # Calculate completion rate
        completion_rate = (len(student_words) / len(prompt_words) * 100)
        feedback["concerns"].append(f"Only wrote {len(student_words)} out of {len(prompt_words)} words ({completion_rate:.0f}%)")
    
    # Check for errors from features
    spelling_errors = features.get("spelling_errors", 0)
    if spelling_errors > 0:
        feedback["errors"].append(f"{spelling_errors} spelling error(s) detected")
    
    grammar_errors = features.get("grammar_errors", 0)
    if grammar_errors > 0:
        feedback["errors"].append(f"{grammar_errors} grammar error(s) found")
    
    letter_reversals = features.get("letter_reversals", 0)
    if letter_reversals > 0:
        feedback["errors"].append(f"{letter_reversals} letter reversal(s) detected")
    
    # Check concerns
    if features.get("inconsistent_spacing", 0) > 0:
        feedback["concerns"].append("Inconsistent spacing between words")
    
    if features.get("writing_speed", 100) < 50:
        feedback["concerns"].append("Writing speed below expected level")
    
    return feedback

def generate_reading_feedback(features: Dict[str, Any], test_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate detailed feedback for reading test"""
    feedback = {
        "errors": [],
        "skipped": [],
        "concerns": []
    }
    
    # Check accuracy
    accuracy = features.get("accuracy", 100)
    if accuracy < 85:
        feedback["errors"].append(f"Reading accuracy only {accuracy:.0f}% (target: 85%+)")
    
    # Check reversals and confusions
    reversed_letters = features.get("reversed_letters", 0)
    if reversed_letters > 0:
        feedback["errors"].append(f"{reversed_letters} letter reversal(s) during reading")
    
    letter_confusions = features.get("letter_confusions", 0)
    if letter_confusions > 0:
        feedback["errors"].append(f"{letter_confusions} letter confusion(s) observed")
    
    # Check reading speed
    reading_speed = features.get("reading_speed", 100)
    if reading_speed < 100:
        feedback["concerns"].append(f"Reading speed below average ({reading_speed:.0f} wpm)")
    
    error_rate = features.get("error_rate", 0)
    if error_rate > 10:
        feedback["concerns"].append(f"High error rate: {error_rate:.0f}%")
    
    return feedback

def generate_math_feedback(features: Dict[str, Any], test_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate detailed feedback for math test"""
    feedback = {
        "errors": [],
        "skipped": [],
        "concerns": []
    }
    
    answers = test_data.get("answers", [])
    problems = test_data.get("problems", [])
    correct_answers = test_data.get("correct_answers", [])
    
    # Check completion and show skipped problems
    if len(answers) < len(problems):
        skipped_count = len(problems) - len(answers)
        feedback["skipped"].append(f"{skipped_count} problem(s) not attempted")
        
        # Show which specific problems were skipped
        for i in range(len(answers), min(len(problems), len(answers) + 3)):
            problem = problems[i]
            # Handle if problem is an object or string
            if isinstance(problem, dict):
                problem_text = problem.get("question", problem.get("text", problem.get("problem", str(problem))))
            else:
                problem_text = str(problem)
            
            if len(problem_text) > 60:
                problem_text = problem_text[:60] + "..."
            feedback["skipped"].append(f'Problem {i+1} not done: "{problem_text}"')
    
    # Check error types
    calculation_errors = features.get("calculation_errors", 0)
    if calculation_errors > 0:
        feedback["errors"].append(f"{calculation_errors} calculation error(s)")
    
    sign_errors = features.get("sign_errors", 0)
    if sign_errors > 0:
        feedback["errors"].append(f"{sign_errors} sign error(s) (positive/negative confusion)")
    
    place_value_errors = features.get("place_value_errors", 0)
    if place_value_errors > 0:
        feedback["errors"].append(f"{place_value_errors} place value error(s)")
    
    # Check concerns
    accuracy = features.get("accuracy", 100)
    if accuracy < 75:
        feedback["concerns"].append(f"Overall accuracy needs improvement: {accuracy:.0f}%")
    
    completion_rate = features.get("completion_rate", 1.0)
    if completion_rate < 0.8:
        feedback["concerns"].append(f"Only {completion_rate*100:.0f}% of problems completed")
    
    return feedback

def generate_general_feedback(features: Dict[str, Any], test_data: Dict[str, Any], test_type: str) -> Dict[str, Any]:
    """Generate feedback for other test types"""
    feedback = {
        "errors": [],
        "skipped": [],
        "concerns": []
    }
    
    # Generic feedback based on common features
    accuracy = features.get("accuracy", features.get("recall_accuracy", 100))
    if accuracy < 75:
        feedback["concerns"].append(f"Performance below expected level: {accuracy:.0f}%")
    
    errors = features.get("errors", 0)
    if errors > 0:
        feedback["errors"].append(f"{errors} incorrect response(s)")
    
    false_recalls = features.get("false_recalls", 0)
    if false_recalls > 0:
        feedback["errors"].append(f"{false_recalls} false recall(s) or incorrect identification(s)")
    
    recall_rate = features.get("recall_rate", features.get("completion_rate", 1.0))
    if recall_rate < 0.8:
        feedback["skipped"].append(f"Only {recall_rate*100:.0f}% of items completed or recalled")
    
    return feedback
