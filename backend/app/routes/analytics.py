"""
Analytics and performance tracking routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any

from app.database import get_db
from app.models import User, Student, TestResult, MLPrediction
from app.schemas import StudentAnalytics
from app.auth import get_current_user

router = APIRouter()

@router.get("/student/{student_id}", response_model=StudentAnalytics)
def get_student_analytics(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive analytics for a student"""
    student = db.query(Student).filter(Student.id == student_id).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Check permissions
    if current_user.role == "teacher" and student.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this student's analytics"
        )
    
    # Get test statistics
    tests = db.query(TestResult).filter(TestResult.student_id == student_id).all()
    total_tests = len(tests)
    
    avg_score = db.query(func.avg(TestResult.score)).filter(
        TestResult.student_id == student_id
    ).scalar() or 0.0
    
    # Build test history
    test_history = []
    for test in tests:
        test_history.append({
            "id": test.id,
            "test_type": test.test_type,
            "score": test.score,
            "errors": test.errors,
            "time_taken": test.time_taken,
            "completed_at": test.completed_at.isoformat()
        })
    
    # Get ML predictions summary
    predictions = db.query(MLPrediction).join(TestResult).filter(
        TestResult.student_id == student_id
    ).all()
    
    risk_summary = {
        "dyslexia": {"count": 0, "avg_confidence": 0.0, "max_risk": "low"},
        "dysgraphia": {"count": 0, "avg_confidence": 0.0, "max_risk": "low"},
        "dyscalculia": {"count": 0, "avg_confidence": 0.0, "max_risk": "low"}
    }
    
    for pred in predictions:
        if pred.prediction_class in risk_summary:
            risk_summary[pred.prediction_class]["count"] += 1
            
            # Track highest risk level
            risk_levels = {"low": 1, "medium": 2, "high": 3}
            current_max = risk_levels.get(risk_summary[pred.prediction_class]["max_risk"], 0)
            new_risk = risk_levels.get(pred.risk_level, 0)
            if new_risk > current_max:
                risk_summary[pred.prediction_class]["max_risk"] = pred.risk_level
    
    # Calculate average confidence
    for category in risk_summary:
        cat_predictions = [p for p in predictions if p.prediction_class == category]
        if cat_predictions:
            avg_conf = sum(p.confidence_score for p in cat_predictions) / len(cat_predictions)
            risk_summary[category]["avg_confidence"] = round(avg_conf, 2)
    
    return {
        "student_id": student_id,
        "student_name": f"{student.first_name} {student.last_name}",
        "total_tests": total_tests,
        "avg_score": round(avg_score, 2),
        "test_history": test_history,
        "risk_summary": risk_summary
    }

@router.get("/overview", response_model=Dict[str, Any])
def get_overview_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get overview analytics (admin sees all, teacher sees their students)"""
    query = db.query(Student)
    
    if current_user.role == "teacher":
        query = query.filter(Student.teacher_id == current_user.id)
    
    students = query.all()
    total_students = len(students)
    
    # Total tests
    test_query = db.query(TestResult)
    if current_user.role == "teacher":
        student_ids = [s.id for s in students]
        test_query = test_query.filter(TestResult.student_id.in_(student_ids))
    
    total_tests = test_query.count()
    
    # Recent predictions
    pred_query = db.query(MLPrediction).join(TestResult)
    if current_user.role == "teacher":
        student_ids = [s.id for s in students]
        pred_query = pred_query.filter(TestResult.student_id.in_(student_ids))
    
    predictions = pred_query.order_by(MLPrediction.predicted_at.desc()).limit(10).all()
    
    # Risk distribution
    risk_distribution = {
        "low": 0,
        "medium": 0,
        "high": 0
    }
    
    for pred in pred_query.all():
        if pred.risk_level in risk_distribution:
            risk_distribution[pred.risk_level] += 1
    
    return {
        "total_students": total_students,
        "total_tests": total_tests,
        "risk_distribution": risk_distribution,
        "recent_activity": [
            {
                "prediction_class": p.prediction_class,
                "confidence": p.confidence_score,
                "risk_level": p.risk_level,
                "predicted_at": p.predicted_at.isoformat()
            }
            for p in predictions
        ]
    }
