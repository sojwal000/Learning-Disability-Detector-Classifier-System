"""
Report generation and download routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path

from app.database import get_db
from app.models import User, Student, Report
from app.schemas import ReportResponse
from app.auth import get_current_user
from app.utils.report_generator import generate_student_report

router = APIRouter()

@router.post("/generate/{student_id}", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def generate_report(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a comprehensive report for a student"""
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
            detail="Not authorized to generate report for this student"
        )
    
    # Generate report
    report = generate_student_report(student_id, db)
    
    return report

@router.get("/student/{student_id}", response_model=List[ReportResponse])
def get_student_reports(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all reports for a student"""
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
            detail="Not authorized to access this student's reports"
        )
    
    reports = db.query(Report).filter(Report.student_id == student_id).all()
    return reports

@router.get("/download/{report_id}")
def download_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download a report file"""
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check if report file exists
    if not report.report_path or not Path(report.report_path).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file not found"
        )
    
    return FileResponse(
        path=report.report_path,
        filename=f"report_{report.id}_{report.student_id}.pdf",
        media_type="application/pdf"
    )
