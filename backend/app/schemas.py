"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str = Field(..., pattern="^(admin|teacher)$")

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Student Schemas
class StudentBase(BaseModel):
    first_name: str
    last_name: str
    age: Optional[int] = None
    grade: Optional[str] = None
    gender: Optional[str] = None

class StudentCreate(StudentBase):
    teacher_id: int

class StudentResponse(StudentBase):
    id: int
    teacher_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Test Schemas
class TestSubmission(BaseModel):
    student_id: int
    test_type: str = Field(..., pattern="^(reading|writing|math|memory|attention|phonological|visual_processing)$")
    test_data: Dict[str, Any]
    time_taken: Optional[int] = None

class TestResultResponse(BaseModel):
    id: int
    student_id: int
    test_type: str
    score: Optional[float] = None
    errors: Optional[int] = None
    time_taken: Optional[int] = None
    completed_at: datetime
    
    class Config:
        from_attributes = True

# Questionnaire Schemas
class QuestionnaireSubmission(BaseModel):
    student_id: int
    respondent_type: str = Field(..., pattern="^(teacher|parent)$")
    responses: Dict[str, Any]

class QuestionnaireResponse(BaseModel):
    id: int
    student_id: int
    respondent_type: str
    score: Optional[float] = None
    submitted_at: datetime
    
    class Config:
        from_attributes = True

# ML Prediction Schemas
class PredictionResponse(BaseModel):
    id: int
    test_result_id: int
    prediction_class: str
    confidence_score: float
    risk_level: str
    predicted_at: datetime
    
    class Config:
        from_attributes = True

# Report Schemas
class ReportResponse(BaseModel):
    id: int
    student_id: int
    report_type: str
    classification: str
    risk_score: float
    indicators: List[Dict[str, Any]]
    recommendations: str
    report_path: Optional[str] = None
    generated_at: datetime
    
    class Config:
        from_attributes = True

# Analytics Schemas
class StudentAnalytics(BaseModel):
    student_id: int
    student_name: str
    total_tests: int
    avg_score: float
    test_history: List[Dict[str, Any]]
    risk_summary: Dict[str, Any]
