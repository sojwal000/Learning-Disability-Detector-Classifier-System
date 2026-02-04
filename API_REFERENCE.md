# API Reference

## Learning Disability Detector & Classifier System

Base URL: `http://localhost:8000/api`

All endpoints require authentication unless specified. Include JWT token in Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

---

## 🔐 Authentication Endpoints

### Register User

**POST** `/auth/register`

Create a new user account.

**Request Body:**

```json
{
  "username": "teacher1",
  "email": "teacher1@school.com",
  "password": "SecurePassword123",
  "full_name": "John Doe",
  "role": "teacher"
}
```

**Response:** `201 Created`

```json
{
  "id": 1,
  "username": "teacher1",
  "email": "teacher1@school.com",
  "full_name": "John Doe",
  "role": "teacher",
  "created_at": "2024-11-16T10:30:00",
  "is_active": true
}
```

**Roles:** `admin`, `teacher`

---

### Login

**POST** `/auth/login`

Authenticate and receive JWT token.

**Request Body:**

```json
{
  "username": "teacher1",
  "password": "SecurePassword123"
}
```

**Response:** `200 OK`

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "teacher1",
    "email": "teacher1@school.com",
    "full_name": "John Doe",
    "role": "teacher",
    "created_at": "2024-11-16T10:30:00",
    "is_active": true
  }
}
```

---

### Get Current User

**GET** `/auth/me`

Get authenticated user information.

**Response:** `200 OK`

```json
{
  "id": 1,
  "username": "teacher1",
  "email": "teacher1@school.com",
  "full_name": "John Doe",
  "role": "teacher",
  "created_at": "2024-11-16T10:30:00",
  "is_active": true
}
```

---

## 👨‍🎓 Student Endpoints

### List Students

**GET** `/students`

Get all students (teachers see only their students).

**Query Parameters:**

- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum records to return (default: 100)

**Response:** `200 OK`

```json
[
  {
    "id": 1,
    "first_name": "Emma",
    "last_name": "Johnson",
    "age": 10,
    "grade": "5th",
    "gender": "Female",
    "teacher_id": 1,
    "created_at": "2024-11-16T10:30:00"
  }
]
```

---

### Create Student

**POST** `/students`

Add a new student.

**Request Body:**

```json
{
  "first_name": "Emma",
  "last_name": "Johnson",
  "age": 10,
  "grade": "5th",
  "gender": "Female",
  "teacher_id": 1
}
```

**Response:** `201 Created`

```json
{
  "id": 1,
  "first_name": "Emma",
  "last_name": "Johnson",
  "age": 10,
  "grade": "5th",
  "gender": "Female",
  "teacher_id": 1,
  "created_at": "2024-11-16T10:30:00"
}
```

---

### Get Student

**GET** `/students/{student_id}`

Get specific student details.

**Response:** `200 OK`

```json
{
  "id": 1,
  "first_name": "Emma",
  "last_name": "Johnson",
  "age": 10,
  "grade": "5th",
  "gender": "Female",
  "teacher_id": 1,
  "created_at": "2024-11-16T10:30:00"
}
```

---

### Update Student

**PUT** `/students/{student_id}`

Update student information.

**Request Body:**

```json
{
  "first_name": "Emma",
  "last_name": "Johnson",
  "age": 11,
  "grade": "6th",
  "gender": "Female",
  "teacher_id": 1
}
```

**Response:** `200 OK`

---

### Delete Student

**DELETE** `/students/{student_id}`

Delete a student (admin only).

**Response:** `204 No Content`

---

## 📝 Test Endpoints

### Submit Test

**POST** `/tests/submit`

Submit test results with optional file uploads.

**Content-Type:** `multipart/form-data`

**Form Data:**

- `student_id` (required): Student ID
- `test_type` (required): `reading`, `writing`, or `math`
- `test_data` (required): JSON string with test data
- `time_taken` (optional): Time in seconds
- `audio_file` (optional): Audio recording file
- `handwriting_file` (optional): Handwriting image

**Example test_data for Reading:**

```json
{
  "text_provided": "The quick brown fox jumps over the lazy dog",
  "text_read": "The qick brown fox jmps over the lzy dog",
  "time_taken": 45
}
```

**Example test_data for Writing:**

```json
{
  "prompt": "Write about your favorite hobby",
  "text_written": "My favrite hoby is paiting...",
  "time_taken": 300
}
```

**Example test_data for Math:**

```json
{
  "problems": [
    {
      "question": "What is 15 + 27?",
      "correct_answer": "42",
      "student_answer": "42",
      "is_correct": true,
      "error_type": ""
    },
    {
      "question": "What is 8 × 7?",
      "correct_answer": "56",
      "student_answer": "54",
      "is_correct": false,
      "error_type": "calculation"
    }
  ],
  "time_taken": 180
}
```

**Response:** `201 Created`

```json
{
  "id": 1,
  "student_id": 1,
  "test_type": "reading",
  "score": 85.5,
  "errors": 3,
  "time_taken": 45,
  "completed_at": "2024-11-16T10:30:00"
}
```

---

### Get Student Tests

**GET** `/tests/student/{student_id}`

Get all tests for a specific student.

**Response:** `200 OK`

```json
[
  {
    "id": 1,
    "student_id": 1,
    "test_type": "reading",
    "score": 85.5,
    "errors": 3,
    "time_taken": 45,
    "completed_at": "2024-11-16T10:30:00"
  }
]
```

---

### Get Test

**GET** `/tests/{test_id}`

Get specific test details.

**Response:** `200 OK`

```json
{
  "id": 1,
  "student_id": 1,
  "test_type": "reading",
  "score": 85.5,
  "errors": 3,
  "time_taken": 45,
  "completed_at": "2024-11-16T10:30:00"
}
```

---

## 📊 Analytics Endpoints

### Get Student Analytics

**GET** `/analytics/student/{student_id}`

Get comprehensive analytics for a student.

**Response:** `200 OK`

```json
{
  "student_id": 1,
  "student_name": "Emma Johnson",
  "total_tests": 5,
  "avg_score": 82.5,
  "test_history": [
    {
      "id": 1,
      "test_type": "reading",
      "score": 85.5,
      "errors": 3,
      "time_taken": 45,
      "completed_at": "2024-11-16T10:30:00"
    }
  ],
  "risk_summary": {
    "dyslexia": {
      "count": 2,
      "avg_confidence": 0.65,
      "max_risk": "medium"
    },
    "dysgraphia": {
      "count": 0,
      "avg_confidence": 0.0,
      "max_risk": "low"
    },
    "dyscalculia": {
      "count": 1,
      "avg_confidence": 0.45,
      "max_risk": "low"
    }
  }
}
```

---

### Get Overview Analytics

**GET** `/analytics/overview`

Get system-wide analytics (admin sees all, teacher sees their students).

**Response:** `200 OK`

```json
{
  "total_students": 25,
  "total_tests": 150,
  "risk_distribution": {
    "low": 10,
    "medium": 8,
    "high": 7
  },
  "recent_activity": [
    {
      "prediction_class": "dyslexia",
      "confidence": 0.75,
      "risk_level": "high",
      "predicted_at": "2024-11-16T10:30:00"
    }
  ]
}
```

---

## 📄 Report Endpoints

### Generate Report

**POST** `/reports/generate/{student_id}`

Generate a comprehensive report for a student.

**Response:** `201 Created`

```json
{
  "id": 1,
  "student_id": 1,
  "report_type": "comprehensive",
  "classification": "Dyslexia",
  "risk_score": 0.65,
  "indicators": [
    {
      "category": "dyslexia",
      "occurrences": 2,
      "avg_confidence": 0.65,
      "risk_level": "medium",
      "description": "Moderate reading and word recognition challenges"
    }
  ],
  "recommendations": "**General Recommendations:**\n- Schedule comprehensive evaluation...",
  "report_path": "storage/reports/report_1_1_20241116.txt",
  "generated_at": "2024-11-16T10:30:00"
}
```

---

### Get Student Reports

**GET** `/reports/student/{student_id}`

Get all reports for a student.

**Response:** `200 OK`

```json
[
  {
    "id": 1,
    "student_id": 1,
    "report_type": "comprehensive",
    "classification": "Dyslexia",
    "risk_score": 0.65,
    "indicators": [...],
    "recommendations": "...",
    "report_path": "storage/reports/report_1_1_20241116.txt",
    "generated_at": "2024-11-16T10:30:00"
  }
]
```

---

### Download Report

**GET** `/reports/download/{report_id}`

Download report file.

**Response:** `200 OK`

- Content-Type: `application/pdf` or `text/plain`
- Content-Disposition: `attachment; filename="report_1_1.pdf"`

---

## ❌ Error Responses

### Standard Error Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Status Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `204 No Content` - Success with no response body
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

---

## 🔒 Authentication Flow

### Step-by-Step

1. **Register or Login**

   ```
   POST /api/auth/login
   → Receive access_token
   ```

2. **Store Token**

   ```javascript
   localStorage.setItem("token", access_token);
   ```

3. **Include in Requests**

   ```javascript
   headers: {
     'Authorization': `Bearer ${token}`
   }
   ```

4. **Handle Expiration**
   ```
   401 Unauthorized → Redirect to login
   ```

---

## 📝 Usage Examples

### JavaScript/Axios

```javascript
// Login
const login = async (username, password) => {
  const response = await axios.post("/api/auth/login", {
    username,
    password,
  });

  const token = response.data.access_token;
  localStorage.setItem("token", token);

  // Set default header
  axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
};

// Create Student
const createStudent = async (studentData) => {
  const response = await axios.post("/api/students", studentData);
  return response.data;
};

// Submit Test with File
const submitTest = async (testData) => {
  const formData = new FormData();
  formData.append("student_id", testData.student_id);
  formData.append("test_type", testData.test_type);
  formData.append("test_data", JSON.stringify(testData.data));

  if (testData.audioFile) {
    formData.append("audio_file", testData.audioFile);
  }

  const response = await axios.post("/api/tests/submit", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
};
```

### Python/Requests

```python
import requests

# Login
response = requests.post(
    'http://localhost:8000/api/auth/login',
    json={'username': 'teacher1', 'password': 'password123'}
)
token = response.json()['access_token']

# Headers for authenticated requests
headers = {'Authorization': f'Bearer {token}'}

# Get students
response = requests.get(
    'http://localhost:8000/api/students',
    headers=headers
)
students = response.json()

# Submit test
test_data = {
    'text_provided': 'Sample text',
    'text_read': 'Sample text with errors'
}

files = {'audio_file': open('recording.wav', 'rb')}
data = {
    'student_id': 1,
    'test_type': 'reading',
    'test_data': json.dumps(test_data),
    'time_taken': 60
}

response = requests.post(
    'http://localhost:8000/api/tests/submit',
    headers=headers,
    data=data,
    files=files
)
```

---

## 🚀 Rate Limiting

Currently no rate limiting is implemented. For production:

- Implement rate limiting middleware
- Recommended: 100 requests per minute per user
- Use Redis for distributed rate limiting

---

## 📖 Interactive Documentation

Visit http://localhost:8000/docs for:

- Interactive API testing
- Automatic request/response examples
- Schema definitions
- Try it out feature

---

**API Version**: 1.0  
**Last Updated**: November 2024
