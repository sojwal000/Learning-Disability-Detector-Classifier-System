"""
SQLAlchemy database models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # admin, teacher
    full_name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    students = relationship("Student", back_populates="teacher")

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    age = Column(Integer)
    grade = Column(String(20))
    gender = Column(String(20))
    teacher_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    teacher = relationship("User", back_populates="students")
    test_results = relationship("TestResult", back_populates="student")
    questionnaires = relationship("Questionnaire", back_populates="student")
    reports = relationship("Report", back_populates="student")

class TestResult(Base):
    __tablename__ = "test_results"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    test_type = Column(String(50), nullable=False)  # reading, writing, math
    test_data = Column(JSON)  # Store raw test data
    features = Column(JSON)  # Extracted features
    score = Column(Float)
    errors = Column(Integer)
    time_taken = Column(Integer)  # in seconds
    audio_path = Column(String(255))
    handwriting_path = Column(String(255))
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("Student", back_populates="test_results")
    ml_predictions = relationship("MLPrediction", back_populates="test_result")

class Questionnaire(Base):
    __tablename__ = "questionnaires"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    respondent_type = Column(String(20))  # teacher, parent
    responses = Column(JSON)  # Store questionnaire responses
    score = Column(Float)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("Student", back_populates="questionnaires")

class MLPrediction(Base):
    __tablename__ = "ml_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    test_result_id = Column(Integer, ForeignKey("test_results.id"))
    model_type = Column(String(50))  # sklearn, tensorflow
    model_name = Column(String(100))
    prediction_class = Column(String(50))  # dyslexia, dysgraphia, dyscalculia, none
    confidence_score = Column(Float)
    risk_level = Column(String(20))  # low, medium, high
    features_used = Column(JSON)
    predicted_at = Column(DateTime, default=datetime.utcnow)
    
    test_result = relationship("TestResult", back_populates="ml_predictions")

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    report_type = Column(String(50))
    classification = Column(String(100))
    risk_score = Column(Float)
    indicators = Column(JSON)  # Key indicators found
    recommendations = Column(Text)
    report_path = Column(String(255))
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("Student", back_populates="reports")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100))
    details = Column(Text)
    ip_address = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)
