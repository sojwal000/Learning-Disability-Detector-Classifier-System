"""
Learning Disability Detector & Classifier System - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.routes import auth, students, tests, analytics, reports, progress
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

# Create storage directories
os.makedirs("storage/audio", exist_ok=True)
os.makedirs("storage/handwriting", exist_ok=True)
os.makedirs("storage/reports", exist_ok=True)

app = FastAPI(
    title="Learning Disability Detector & Classifier System",
    description="API for screening and detecting learning disabilities in students",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/storage", StaticFiles(directory="storage"), name="storage")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(students.router, prefix="/api/students", tags=["Students"])
app.include_router(tests.router, prefix="/api/tests", tags=["Tests"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(progress.router, prefix="/api/progress", tags=["Progress Tracking"])

@app.get("/")
def read_root():
    return {
        "message": "Learning Disability Detector & Classifier System API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
