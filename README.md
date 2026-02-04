# Learning Disability Detector & Classifier System

A comprehensive software system for screening students for learning disabilities (dyslexia, dysgraphia, dyscalculia) using ML-based assessment, teacher/parent questionnaires, and automated report generation.

## 🎯 Features

- **Student Screening Tests** - Reading, writing, and math assessments
- **Teacher/Parent Questionnaires** - Comprehensive behavioral observation forms
- **ML-Based Detection** - Automated classification using scikit-learn and TensorFlow
- **Performance Analytics** - Visual dashboards with charts and progress tracking
- **Downloadable Reports** - Comprehensive PDF reports with recommendations
- **Role-Based Access** - Secure admin and teacher accounts with JWT authentication

## 🛠️ Technology Stack

**Backend:** FastAPI, PostgreSQL, SQLAlchemy, JWT, Scikit-learn, TensorFlow  
**Frontend:** React 18, React Router, Axios, Chart.js, Vite

## 📋 Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

## 🚀 Quick Start

### 1. Database Setup
```sql
CREATE DATABASE ld_detector;
CREATE USER ld_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ld_detector TO ld_user;
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database credentials
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Access the application at `http://localhost:3000`  
API Documentation at `http://localhost:8000/docs`

## 🔐 Configuration

Create a `.env` file in the backend directory:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/ld_detector
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

Generate a secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## 🤖 ML Detection

The system analyzes multiple factors:

- **Dyslexia:** Reading speed, error patterns, letter reversals
- **Dysgraphia:** Spelling, grammar, handwriting consistency
- **Dyscalculia:** Calculation errors, number reversals, problem-solving time

**Risk Levels:** Low (20-35%) | Medium (35-60%) | High (60%+)

## 📖 API Documentation

Key endpoints available at `http://localhost:8000/docs`:

- Authentication: `/api/auth/*`
- Students: `/api/students/*`
- Tests: `/api/tests/*`
- Analytics: `/api/analytics/*`
- Reports: `/api/reports/*`

## 📝 Future Enhancements

- Train models with real clinical data
- Audio and handwriting image analysis
- Parent portal
- Multi-language support
- Mobile app
- Email notifications

## 📄 License

Proprietary - All rights reserved

---

**Built with ❤️ for better learning disability detection and support**