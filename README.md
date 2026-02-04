# Learning Disability Detector & Classifier System

A comprehensive software system for screening students for learning disabilities (dyslexia, dysgraphia, dyscalculia) using ML-based assessment, teacher/parent questionnaires, and automated report generation.

## 🎯 Features

- **Student Screening Tests**: Reading, writing, and math assessments
- **Teacher/Parent Questionnaires**: Comprehensive behavioral observation forms
- **ML-Based Detection**: Automated classification using scikit-learn and TensorFlow
- **Performance Analytics**: Visual dashboards with charts and progress tracking
- **Downloadable Reports**: Comprehensive PDF reports with recommendations
- **Role-Based Access**: Separate admin and teacher accounts with JWT authentication
- **Local File Storage**: Audio recordings, handwriting samples, and reports

## 🛠️ Technology Stack

### Backend

- **FastAPI** (Python 3.10+) - Modern async web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM for database operations
- **JWT** - Secure authentication
- **Scikit-learn** - Classical ML models
- **TensorFlow** - Deep learning models
- **Python-Jose** - JWT token handling
- **Passlib** - Password hashing

### Frontend

- **React 18** - UI library
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Chart.js** - Data visualization
- **Vite** - Build tool and dev server
- **Pure CSS** - Custom styling (no frameworks)

## 📋 Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- PostgreSQL 14 or higher
- npm or yarn

## 🚀 Installation & Setup

### 1. Clone the Repository

```powershell
cd "c:\Users\Swastik\Desktop\ClientProjects\LDD&CS"
```

### 2. Database Setup

Create a PostgreSQL database:

```sql
CREATE DATABASE ld_detector;
CREATE USER ld_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ld_detector TO ld_user;
```

### 3. Backend Setup

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create .env file
Copy-Item .env.example .env

# Edit .env file with your database credentials
# DATABASE_URL=postgresql://ld_user:your_password@localhost:5432/ld_detector
# SECRET_KEY=generate-a-secure-key-here

# Create storage directories
mkdir storage\audio, storage\handwriting, storage\reports
```

### 4. Frontend Setup

```powershell
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install
```

## 🏃 Running the Application

### Start Backend Server

```powershell
# From backend directory with activated venv
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

### Start Frontend Development Server

```powershell
# From frontend directory (new terminal)
cd frontend
npm run dev
```

The application will be available at: `http://localhost:3000`

## 📚 Project Structure

```
LDD&CS/
├── backend/
│   ├── app/
│   │   ├── routes/          # API endpoints
│   │   │   ├── auth.py      # Authentication routes
│   │   │   ├── students.py  # Student management
│   │   │   ├── tests.py     # Test submission
│   │   │   ├── analytics.py # Analytics endpoints
│   │   │   └── reports.py   # Report generation
│   │   ├── ml/              # Machine learning modules
│   │   │   ├── feature_extraction.py  # Feature engineering
│   │   │   ├── inference.py           # ML predictions
│   │   │   └── models/                # Trained models
│   │   ├── utils/           # Utility functions
│   │   │   └── report_generator.py
│   │   ├── main.py          # FastAPI app entry point
│   │   ├── database.py      # Database configuration
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   └── auth.py          # JWT authentication
│   ├── storage/             # File storage
│   │   ├── audio/
│   │   ├── handwriting/
│   │   └── reports/
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   │   └── Layout.jsx
│   │   ├── pages/           # Page components
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Students.jsx
│   │   │   ├── StudentDetail.jsx
│   │   │   ├── TestSubmission.jsx
│   │   │   ├── Analytics.jsx
│   │   │   └── Reports.jsx
│   │   ├── context/         # React context
│   │   │   └── AuthContext.jsx
│   │   ├── services/        # API services
│   │   │   ├── api.js
│   │   │   └── services.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 🔐 Default User Setup

After starting the backend, you can register users through:

1. API endpoint: `POST /api/auth/register`
2. Frontend registration page: `http://localhost:3000/register`

Create an admin user:

```json
{
  "username": "admin",
  "email": "admin@example.com",
  "password": "SecurePassword123",
  "full_name": "System Administrator",
  "role": "admin"
}
```

## 📖 API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation powered by Swagger UI.

### Key Endpoints

**Authentication**

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

**Students**

- `GET /api/students` - List all students
- `POST /api/students` - Create new student
- `GET /api/students/{id}` - Get student details
- `PUT /api/students/{id}` - Update student
- `DELETE /api/students/{id}` - Delete student

**Tests**

- `POST /api/tests/submit` - Submit test results
- `GET /api/tests/student/{student_id}` - Get student's tests
- `GET /api/tests/{id}` - Get specific test

**Analytics**

- `GET /api/analytics/student/{id}` - Student analytics
- `GET /api/analytics/overview` - System overview

**Reports**

- `POST /api/reports/generate/{student_id}` - Generate report
- `GET /api/reports/student/{student_id}` - Get reports
- `GET /api/reports/download/{report_id}` - Download report

## 🧪 Testing

### Manual Testing Workflow

1. **Register and Login**

   - Create a teacher account
   - Login with credentials

2. **Add Students**

   - Navigate to Students page
   - Add student with details

3. **Submit Tests**

   - Go to Submit Test page
   - Select student and test type
   - Fill in test data
   - Submit

4. **View Analytics**

   - Check Dashboard for overview
   - View student detail page for individual analytics

5. **Generate Reports**
   - Navigate to Reports page
   - Select student
   - Generate and download report

## 🤖 ML Model Information

The system uses rule-based classifiers (can be replaced with trained models):

### Features Extracted

**Reading Tests (Dyslexia Detection)**

- Reading speed (words per minute)
- Error rate and types
- Letter reversals (b/d, p/q)
- Letter confusions
- Substitutions, omissions, additions

**Writing Tests (Dysgraphia Detection)**

- Spelling errors
- Grammar errors
- Capitalization issues
- Punctuation errors
- Letter reversals
- Spacing consistency

**Math Tests (Dyscalculia Detection)**

- Calculation errors
- Concept understanding errors
- Procedural errors
- Number reversals
- Problem-solving time

### Risk Classification

- **Low Risk**: 20-35% risk score
- **Medium Risk**: 35-60% risk score
- **High Risk**: 60%+ risk score

## 🔧 Configuration

### Environment Variables (.env)

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ld_detector

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
ALLOWED_ORIGINS=http://localhost:3000

# Storage
STORAGE_PATH=storage
```

### Generate Secret Key

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

## 🚨 Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure database exists

### Frontend API Connection Issues

- Confirm backend is running on port 8000
- Check CORS settings
- Verify proxy configuration in `vite.config.js`

### Import Errors

- Activate virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`

## 📝 Future Enhancements

- [ ] Train actual ML models with real data
- [ ] Add audio processing for speech analysis
- [ ] Implement handwriting image analysis
- [ ] Add parent portal
- [ ] Integrate with school management systems
- [ ] Multi-language support
- [ ] Mobile app development
- [ ] Advanced analytics with Chart.js
- [ ] Export reports to PDF format
- [ ] Email notifications

## 🤝 Contributing

This is a client project. For contributions or questions, contact the project maintainer.

## 📄 License

Proprietary - All rights reserved

## 👥 Support

For support, email: support@lddetector.com

---

**Built with ❤️ for better learning disability detection and support**
