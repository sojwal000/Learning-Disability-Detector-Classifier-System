"""
Progress Tracking and Analytics Routes
Provides comprehensive progress analysis and visualizations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import numpy as np
import os

from app.database import get_db
from app.models import User, Student, TestResult, MLPrediction
from app.auth import get_current_user
from app.utils.pdf_generator import ProgressReportGenerator

router = APIRouter()

@router.get("/student/{student_id}/progress")
def get_student_progress(
    student_id: int,
    test_type: Optional[str] = None,
    days: int = 90,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get student progress over time with trend analysis
    
    Returns time-series data for charts showing improvement/decline
    """
    # Verify student exists
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
            detail="Not authorized to access this student"
        )
    
    # Get test results within date range
    start_date = datetime.utcnow() - timedelta(days=days)
    query = db.query(TestResult).filter(
        TestResult.student_id == student_id,
        TestResult.completed_at >= start_date
    )
    
    if test_type:
        query = query.filter(TestResult.test_type == test_type)
    
    results = query.order_by(TestResult.completed_at).all()
    
    if not results:
        return {
            "student_id": student_id,
            "test_type": test_type or "all",
            "progress_over_time": [],
            "overall_statistics": {
                "total_tests": 0,
                "average_score": 0,
                "improvement_rate": 0,
                "trend": "no_data",
                "best_test_type": "N/A",
                "best_score": 0
            }
        }
    
    # Build time series data - group by date and test type
    progress_over_time = []
    
    # Group results by test type and date (daily aggregation)
    from collections import defaultdict
    daily_scores = defaultdict(lambda: defaultdict(list))
    
    for result in results:
        date_key = result.completed_at.date().isoformat()
        daily_scores[date_key][result.test_type].append(result.score if result.score is not None else 0)
    
    # Create progress_over_time entries
    for date_str, test_types in sorted(daily_scores.items()):
        for test_type_name, scores in test_types.items():
            progress_over_time.append({
                "test_date": date_str,
                "test_type": test_type_name,
                "avg_score": float(np.mean(scores)) if scores else 0
            })
    
    # Calculate statistics
    scores = [r.score for r in results if r.score is not None]
    errors = [r.errors for r in results if r.errors is not None]
    
    # Find best test type
    test_type_scores = {}
    for result in results:
        if result.score is not None:
            if result.test_type not in test_type_scores:
                test_type_scores[result.test_type] = []
            test_type_scores[result.test_type].append(result.score)
    
    best_test_type = "N/A"
    best_score = 0
    if test_type_scores:
        best_test_type = max(test_type_scores.items(), key=lambda x: np.mean(x[1]))[0]
        best_score = float(np.mean(test_type_scores[best_test_type]))
    
    overall_statistics = {
        "total_tests": len(results),
        "average_score": float(np.mean(scores)) if scores else 0,
        "min_score": float(np.min(scores)) if scores else 0,
        "max_score": float(np.max(scores)) if scores else 0,
        "score_std": float(np.std(scores)) if scores else 0,
        "avg_errors": float(np.mean(errors)) if errors else 0,
        "improvement_rate": 0,
        "best_test_type": best_test_type,
        "best_score": best_score
    }
    
    # Calculate trend (linear regression on scores)
    if len(scores) >= 3:
        x = np.arange(len(scores))
        y = np.array(scores)
        coeffs = np.polyfit(x, y, 1)
        slope = coeffs[0]
        
        if slope > 0.5:
            trend = "improving"
        elif slope < -0.5:
            trend = "declining"
        else:
            trend = "stable"
        
        overall_statistics["improvement_rate"] = float(slope)
        overall_statistics["trend"] = trend
    else:
        trend = "insufficient_data"
        overall_statistics["trend"] = trend
    
    return {
        "student_id": student_id,
        "test_type": test_type or "all",
        "progress_over_time": progress_over_time,
        "overall_statistics": overall_statistics
    }


@router.get("/student/{student_id}/comparison")
def get_student_comparison(
    student_id: int,
    test_type: Optional[str] = None,
    days: int = 90,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Compare student performance against grade average
    """
    # Get student
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
            detail="Not authorized"
        )
    
    # Date filter
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get student's average scores by test type
    student_query = db.query(
        TestResult.test_type,
        func.avg(TestResult.score).label("avg_score"),
        func.count(TestResult.id).label("test_count")
    ).filter(
        TestResult.student_id == student_id,
        TestResult.completed_at >= start_date,
        TestResult.score.isnot(None)
    )
    
    if test_type:
        student_query = student_query.filter(TestResult.test_type == test_type)
    
    student_scores = student_query.group_by(TestResult.test_type).all()
    
    # Get grade average (all students in same grade)
    grade_query = db.query(
        TestResult.test_type,
        func.avg(TestResult.score).label("avg_score")
    ).join(Student).filter(
        Student.grade == student.grade,
        TestResult.completed_at >= start_date,
        TestResult.score.isnot(None)
    )
    
    if test_type:
        grade_query = grade_query.filter(TestResult.test_type == test_type)
    
    grade_averages = grade_query.group_by(TestResult.test_type).all()
    
    # Build comparison data
    test_types = []
    grade_avg_map = {ga.test_type: float(ga.avg_score) for ga in grade_averages if ga.avg_score is not None}
    
    student_total_avg = 0
    grade_total_avg = 0
    
    for ss in student_scores:
        grade_avg = grade_avg_map.get(ss.test_type, 0)
        student_avg = float(ss.avg_score) if ss.avg_score else 0
        
        test_types.append({
            "test_type": ss.test_type,
            "student_avg": student_avg,
            "grade_avg": grade_avg,
            "difference": student_avg - grade_avg,
            "test_count": ss.test_count
        })
        
        student_total_avg += student_avg
        grade_total_avg += grade_avg
    
    # Calculate overall averages
    num_test_types = len(test_types)
    student_overall_avg = student_total_avg / num_test_types if num_test_types > 0 else 0
    grade_overall_avg = grade_total_avg / num_test_types if num_test_types > 0 else 0
    
    # Calculate percentile
    all_grade_scores = db.query(TestResult.score).join(Student).filter(
        Student.grade == student.grade,
        TestResult.completed_at >= start_date,
        TestResult.score.isnot(None)
    ).all()
    
    if all_grade_scores:
        scores_list = [s[0] for s in all_grade_scores]
        overall_percentile = (sum(1 for s in scores_list if s <= student_overall_avg) / len(scores_list)) * 100
    else:
        overall_percentile = 50.0
    
    return {
        "student_id": student_id,
        "grade": student.grade,
        "test_types": test_types,
        "student_overall_avg": student_overall_avg,
        "grade_overall_avg": grade_overall_avg,
        "overall_percentile": overall_percentile
    }


@router.get("/student/{student_id}/heatmap")
def get_performance_heatmap(
    student_id: int,
    test_type: Optional[str] = None,
    days: int = 90,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get heatmap data showing performance across different areas
    
    Returns difficulty areas for visualization
    """
    # Get student
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
            detail="Not authorized"
        )
    
    # Date filter
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get test results grouped by test type
    query = db.query(
        TestResult.test_type,
        func.avg(TestResult.score).label('avg_score'),
        func.count(TestResult.id).label('test_count')
    ).filter(
        TestResult.student_id == student_id,
        TestResult.completed_at >= start_date,
        TestResult.score.isnot(None)
    )
    
    if test_type:
        query = query.filter(TestResult.test_type == test_type)
    
    dimensions_data = query.group_by(TestResult.test_type).all()
    
    dimensions = [
        {
            "dimension": dim[0].replace('_', ' ').title(),
            "score": float(dim[1]),
            "test_count": dim[2]
        }
        for dim in dimensions_data
    ]
    
    return {
        "student_id": student_id,
        "dimensions": dimensions
    }


@router.get("/student/{student_id}/timeline")
def get_assessment_timeline(
    student_id: int,
    test_type: Optional[str] = None,
    days: int = 90,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get timeline view of all assessments with predictions
    """
    # Get student
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
            detail="Not authorized"
        )
    
    # Date filter
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get all test results with predictions
    query = db.query(TestResult).filter(
        TestResult.student_id == student_id,
        TestResult.completed_at >= start_date
    )
    
    if test_type:
        query = query.filter(TestResult.test_type == test_type)
    
    results = query.order_by(TestResult.completed_at.desc()).all()
    
    timeline = []
    for result in results:
        # Get ML predictions
        predictions = db.query(MLPrediction).filter(
            MLPrediction.test_result_id == result.id
        ).all()
        
        timeline.append({
            "id": result.id,
            "test_date": result.completed_at.isoformat(),
            "test_type": result.test_type,
            "score": result.score or 0,
            "detailed_results": result.test_data or {},
            "ml_prediction": predictions[0].confidence_score if predictions else None
        })
    
    return {
        "student_id": student_id,
        "timeline": timeline
    }


def calculate_percentile(score: float, test_type: str, grade: str, db: Session) -> float:
    """Calculate student percentile within their grade for a test type"""
    # Get all scores for this test type and grade
    scores = db.query(TestResult.score).join(Student).filter(
        and_(
            Student.grade == grade,
            TestResult.test_type == test_type,
            TestResult.score.isnot(None)
        )
    ).all()
    
    if not scores:
        return 50.0  # Default percentile
    
    scores_list = [s[0] for s in scores]
    percentile = (sum(1 for s in scores_list if s <= score) / len(scores_list)) * 100
    
    return round(percentile, 2)


def normalize_score(value: float, min_val: float, max_val: float, inverse: bool = False) -> float:
    """Normalize a value to 0-1 range"""
    if max_val == min_val:
        return 0.5
    
    normalized = (value - min_val) / (max_val - min_val)
    normalized = max(0, min(1, normalized))  # Clamp to 0-1
    
    if inverse:
        normalized = 1 - normalized
    
    return normalized


@router.get("/student/{student_id}/export-pdf")
def export_progress_pdf(
    student_id: int,
    test_type: Optional[str] = None,
    days: int = 90,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export student progress report as PDF
    
    Generates a comprehensive PDF report with charts and analytics
    """
    # Verify student exists
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
            detail="Not authorized to access this student"
        )
    
    try:
        # Fetch all required data by calling the endpoint functions
        # We need to recreate the logic here since we can't call the endpoints directly
        
        # Get progress data
        start_date = datetime.utcnow() - timedelta(days=days)
        query = db.query(TestResult).filter(
            TestResult.student_id == student_id,
            TestResult.completed_at >= start_date
        )
        
        if test_type:
            query = query.filter(TestResult.test_type == test_type)
        
        results = query.order_by(TestResult.completed_at.asc()).all()
        
        # Group by test type and date
        progress_over_time = []
        for result in results:
            progress_over_time.append({
                "test_date": result.completed_at.isoformat(),
                "test_type": result.test_type,
                "avg_score": result.score or 0
            })
        
        # Calculate overall statistics
        all_scores = [r.score for r in results if r.score is not None]
        if all_scores:
            avg_score = np.mean(all_scores)
            
            # Calculate trend
            if len(all_scores) >= 3:
                recent_avg = np.mean(all_scores[-3:])
                older_avg = np.mean(all_scores[:3])
                improvement = recent_avg - older_avg
                
                if improvement > 5:
                    trend = "improving"
                elif improvement < -5:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "stable"
            
            # Find best test type
            test_type_scores = {}
            for result in results:
                if result.test_type not in test_type_scores:
                    test_type_scores[result.test_type] = []
                if result.score is not None:
                    test_type_scores[result.test_type].append(result.score)
            
            best_test_type = max(test_type_scores.items(), key=lambda x: np.mean(x[1]))[0] if test_type_scores else "N/A"
            best_score = np.mean(test_type_scores[best_test_type]) if test_type_scores else 0
            
            overall_statistics = {
                "total_tests": len(results),
                "average_score": avg_score,
                "improvement_rate": improvement if len(all_scores) >= 3 else 0,
                "trend": trend,
                "best_test_type": best_test_type,
                "best_score": best_score
            }
        else:
            overall_statistics = {
                "total_tests": 0,
                "average_score": 0,
                "improvement_rate": 0,
                "trend": "stable",
                "best_test_type": "N/A",
                "best_score": 0
            }
        
        progress_data = {
            "progress_over_time": progress_over_time,
            "overall_statistics": overall_statistics
        }
        
        # Get comparison data
        test_types_query = db.query(
            TestResult.test_type,
            func.avg(TestResult.score).label('student_avg')
        ).filter(
            TestResult.student_id == student_id,
            TestResult.completed_at >= start_date,
            TestResult.score.isnot(None)
        )
        
        if test_type:
            test_types_query = test_types_query.filter(TestResult.test_type == test_type)
        
        test_types_data = test_types_query.group_by(TestResult.test_type).all()
        
        comparison_test_types = []
        for tt, student_avg in test_types_data:
            grade_avg = db.query(func.avg(TestResult.score)).join(Student).filter(
                and_(
                    Student.grade == student.grade,
                    TestResult.test_type == tt,
                    TestResult.completed_at >= start_date,
                    TestResult.score.isnot(None)
                )
            ).scalar() or 0
            
            comparison_test_types.append({
                "test_type": tt,
                "student_avg": float(student_avg),
                "grade_avg": float(grade_avg)
            })
        
        student_overall_avg = np.mean([t["student_avg"] for t in comparison_test_types]) if comparison_test_types else 0
        grade_overall_avg = np.mean([t["grade_avg"] for t in comparison_test_types]) if comparison_test_types else 0
        
        # Calculate percentile
        all_grade_scores = db.query(TestResult.score).join(Student).filter(
            and_(
                Student.grade == student.grade,
                TestResult.completed_at >= start_date,
                TestResult.score.isnot(None)
            )
        ).all()
        
        if all_grade_scores:
            scores_list = [s[0] for s in all_grade_scores]
            overall_percentile = (sum(1 for s in scores_list if s <= student_overall_avg) / len(scores_list)) * 100
        else:
            overall_percentile = 50.0
        
        comparison_data = {
            "test_types": comparison_test_types,
            "student_overall_avg": student_overall_avg,
            "grade_overall_avg": grade_overall_avg,
            "overall_percentile": overall_percentile
        }
        
        # Get heatmap data
        dimensions_query = db.query(
            TestResult.test_type,
            func.avg(TestResult.score).label('avg_score'),
            func.count(TestResult.id).label('test_count')
        ).filter(
            TestResult.student_id == student_id,
            TestResult.completed_at >= start_date,
            TestResult.score.isnot(None)
        )
        
        if test_type:
            dimensions_query = dimensions_query.filter(TestResult.test_type == test_type)
        
        dimensions_data = dimensions_query.group_by(TestResult.test_type).all()
        
        dimensions = [
            {
                "dimension": dim[0].replace('_', ' ').title(),
                "score": float(dim[1]),
                "test_count": dim[2]
            }
            for dim in dimensions_data
        ]
        
        heatmap_data = {"dimensions": dimensions}
        
        # Get timeline data (last 20 assessments)
        timeline_results = db.query(TestResult).filter(
            TestResult.student_id == student_id,
            TestResult.completed_at >= start_date
        )
        
        if test_type:
            timeline_results = timeline_results.filter(TestResult.test_type == test_type)
        
        timeline_results = timeline_results.order_by(TestResult.completed_at.desc()).limit(20).all()
        
        timeline = []
        for result in timeline_results:
            predictions = db.query(MLPrediction).filter(
                MLPrediction.test_result_id == result.id
            ).all()
            
            timeline.append({
                "test_date": result.completed_at.isoformat(),
                "test_type": result.test_type,
                "score": result.score or 0,
                "detailed_results": result.detailed_results or {},
                "ml_prediction": predictions[0].confidence_score if predictions else None
            })
        
        timeline_data = {"timeline": timeline}
        
        # Student data
        student_data = {
            'first_name': student.first_name,
            'last_name': student.last_name,
            'age': student.age,
            'grade': student.grade,
            'gender': student.gender
        }
        
        # Generate PDF
        generator = ProgressReportGenerator()
        
        # Create reports directory if it doesn't exist
        reports_dir = "storage/reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"progress_report_{student_id}_{timestamp}.pdf"
        output_path = os.path.join(reports_dir, filename)
        
        # Generate the PDF
        generator.generate_report(
            student_data=student_data,
            progress_data=progress_data,
            comparison_data=comparison_data,
            heatmap_data=heatmap_data,
            timeline_data=timeline_data,
            output_path=output_path
        )
        
        # Return the PDF file
        return FileResponse(
            path=output_path,
            media_type='application/pdf',
            filename=f"progress_report_{student.first_name}_{student.last_name}.pdf"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF report: {str(e)}"
        )
