from app.database import engine, Base
from app.models import User, Student, TestResult, Questionnaire, MLPrediction, Report, AuditLog

print('Creating all tables...')
Base.metadata.create_all(bind=engine)
print('✓ Database tables created successfully!')
print('')
print('You can now start the server with:')
print('  uvicorn app.main:app --reload')
