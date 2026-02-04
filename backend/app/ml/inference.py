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
    
    # Determine which model to use
    if test_type == "reading":
        prediction_class, confidence, risk_level = predict_dyslexia(features)
    elif test_type == "writing":
        prediction_class, confidence, risk_level = predict_dysgraphia(features)
    elif test_type == "math":
        prediction_class, confidence, risk_level = predict_dyscalculia(features)
    else:
        raise ValueError(f"Unknown test type: {test_type}")
    
    # Create prediction record
    prediction = MLPrediction(
        test_result_id=test_result.id,
        model_type="sklearn",  # or "tensorflow" depending on model used
        model_name=f"{test_type}_classifier",
        prediction_class=prediction_class,
        confidence_score=confidence,
        risk_level=risk_level,
        features_used=features
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
