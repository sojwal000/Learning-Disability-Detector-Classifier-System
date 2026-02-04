"""
Test submission and processing routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import uuid
from pathlib import Path

from app.database import get_db
from app.models import User, Student, TestResult, MLPrediction
from app.schemas import TestSubmission, TestResultResponse
from app.auth import get_current_user
from app.ml.feature_extraction import extract_reading_features, extract_writing_features, extract_math_features
from app.ml.test_processors import process_test
from app.ml.inference import run_ml_inference

router = APIRouter()

STORAGE_PATH = Path("storage")

@router.post("/submit", response_model=TestResultResponse, status_code=status.HTTP_201_CREATED)
async def submit_test(
    student_id: int = Form(...),
    test_type: str = Form(...),
    test_data: str = Form(...),
    time_taken: Optional[int] = Form(None),
    audio_file: Optional[UploadFile] = File(None),
    handwriting_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit a test and process it"""
    # Verify student exists
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Parse test data
    try:
        test_data_dict = json.loads(test_data)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid test data format"
        )
    
    # Save files if provided
    audio_path = None
    handwriting_path = None
    
    if audio_file:
        audio_filename = f"{uuid.uuid4()}_{audio_file.filename}"
        audio_path = STORAGE_PATH / "audio" / audio_filename
        with open(audio_path, "wb") as f:
            content = await audio_file.read()
            f.write(content)
        audio_path = str(audio_path)
    
    if handwriting_file:
        handwriting_filename = f"{uuid.uuid4()}_{handwriting_file.filename}"
        handwriting_path = STORAGE_PATH / "handwriting" / handwriting_filename
        with open(handwriting_path, "wb") as f:
            content = await handwriting_file.read()
            f.write(content)
        handwriting_path = str(handwriting_path)
    
    # Extract features based on test type
    if test_type in ["reading", "writing"]:
        # Use legacy feature extraction for reading/writing
        if test_type == "reading":
            features = extract_reading_features(test_data_dict, audio_path)
        else:
            features = extract_writing_features(test_data_dict, handwriting_path)
    elif test_type in ["math", "memory", "attention", "phonological", "visual_processing"]:
        # Use new test processors
        result = process_test(test_type, test_data_dict)
        features = result["features"]
        score = result["score"]
        errors = result["errors"]
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid test type"
        )
    
    # Calculate basic metrics (if not already set by processor)
    if test_type in ["reading", "writing", "math"]:
        score = features.get("score", 0.0)
        errors = features.get("errors", 0)
    
    # Create test result
    test_result = TestResult(
        student_id=student_id,
        test_type=test_type,
        test_data=test_data_dict,
        features=features,
        score=score,
        errors=errors,
        time_taken=time_taken,
        audio_path=audio_path,
        handwriting_path=handwriting_path
    )
    
    db.add(test_result)
    db.commit()
    db.refresh(test_result)
    
    # Run ML inference
    try:
        prediction = run_ml_inference(test_result, db)
    except Exception as e:
        print(f"ML inference error: {e}")
        # Continue even if ML fails
    
    return test_result

@router.get("/student/{student_id}", response_model=List[TestResultResponse])
def get_student_tests(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all tests for a student"""
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
            detail="Not authorized to access this student's tests"
        )
    
    tests = db.query(TestResult).filter(TestResult.student_id == student_id).all()
    return tests

@router.get("/{test_id}", response_model=TestResultResponse)
def get_test(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific test result"""
    test = db.query(TestResult).filter(TestResult.id == test_id).first()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found"
        )
    
    return test
