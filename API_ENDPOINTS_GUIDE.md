# 🚀 API Endpoints Guide - Frontend Integration

This guide provides detailed information about what each endpoint expects from the frontend to prevent errors.

## 📋 **General Requirements**

### Headers
All authenticated endpoints require:
```javascript
{
  "Authorization": "Bearer <jwt_token>",
  "Content-Type": "application/json"
}
```

### Base URL
```
http://localhost:8000/api
```

---

## 🔐 **Authentication Endpoints**

### 1. User Registration
**Endpoint:** `POST /api/auth/register/`

**Request Body:**
```json
{
  "email": "student@example.com",
  "password": "password123",
  "password_confirm": "password123",
  "display_name": "John Doe"
}
```

**Validation Rules:**
- `email`: Must be valid email format, unique
- `password`: Minimum 8 characters, must match password_confirm
- `password_confirm`: Must match password exactly
- `display_name`: Required, max 100 characters

**Success Response (201):**
```json
{
  "user": {
    "id": "uuid",
    "email": "student@example.com",
    "display_name": "John Doe"
  },
  "token": "jwt_access_token"
}
```

**Error Responses:**
- `400`: Validation errors (password mismatch, invalid email, etc.)
- `500`: Server error

---

### 2. User Login
**Endpoint:** `POST /api/auth/login/`

**Request Body:**
```json
{
  "email": "student@example.com",
  "password": "password123"
}
```

**Validation Rules:**
- `email`: Must be valid email format
- `password`: Required

**Success Response (200):**
```json
{
  "user": {
    "id": "uuid",
    "email": "student@example.com",
    "display_name": "John Doe"
  },
  "token": "jwt_access_token"
}
```

**Error Responses:**
- `400`: Invalid credentials or missing fields
- `401`: Authentication failed

---

## 🏛️ **Academic Structure Endpoints**

### 3. Get All Universities
**Endpoint:** `GET /api/universities/`

**Headers:** None required (public endpoint)

**Success Response (200):**
```json
[
  {
    "id": "uuid",
    "name": "University of Technology",
    "country": "Nigeria"
  }
]
```

---

### 4. Get Colleges by University
**Endpoint:** `GET /api/universities/{university_id}/colleges/`

**Headers:** None required (public endpoint)

**URL Parameters:**
- `university_id`: Valid UUID of existing university

**Success Response (200):**
```json
[
  {
    "id": "uuid",
    "name": "College of Engineering and Technology",
    "university": "university_uuid",
    "university_name": "University of Technology"
  }
]
```

---

### 5. Get Programs by College
**Endpoint:** `GET /api/colleges/{college_id}/programs/`

**Headers:** None required (public endpoint)

**URL Parameters:**
- `college_id`: Valid UUID of existing college

**Success Response (200):**
```json
[
  {
    "id": "uuid",
    "name": "Bachelor of Science in Computer Science",
    "college": "college_uuid",
    "college_name": "College of Engineering",
    "university_name": "University of Technology",
    "duration": 4
  }
]
```

---

### 6. Get Courses by Program
**Endpoint:** `GET /api/programs/{program_id}/courses/`

**Headers:** None required (public endpoint)

**URL Parameters:**
- `program_id`: Valid UUID of existing program

**Query Parameters (Optional):**
- `year`: Integer (1, 2, 3, 4, etc.)
- `semester`: Integer (1, 2)

**Example:** `GET /api/programs/{program_id}/courses/?year=1&semester=1`

**Success Response (200):**
```json
[
  {
    "id": "uuid",
    "code": "CS101",
    "name": "Introduction to Programming",
    "credits": 3,
    "type": "core",
    "semester": 1,
    "year": 1,
    "program": "program_uuid",
    "program_name": "Computer Science"
  }
]
```

---

## 👨‍🎓 **Student Management Endpoints**

### 7. Get Student Profile
**Endpoint:** `GET /api/students/profile/`

**Headers:** Required (authenticated)

**Success Response (200):**
```json
{
  "id": "uuid",
  "university": {
    "id": "uuid",
    "name": "University of Technology",
    "country": "Nigeria"
  },
  "college": {
    "id": "uuid",
    "name": "College of Engineering",
    "university": "university_uuid",
    "university_name": "University of Technology"
  },
  "program": {
    "id": "uuid",
    "name": "Computer Science",
    "college": "college_uuid",
    "college_name": "College of Engineering",
    "university_name": "University of Technology",
    "duration": 4
  },
  "year": 1,
  "semester": 1,
  "courses": [
    {
      "id": "uuid",
      "course": "course_uuid",
      "course_code": "CS101",
      "course_name": "Introduction to Programming",
      "course_credits": 3,
      "course_type": "core",
      "grade": "A",
      "points": 5.0
    }
  ],
  "gpa": 4.25
}
```

**Error Responses:**
- `404`: Student profile not found
- `401`: Authentication required

---

### 8. Create Student Profile
**Endpoint:** `POST /api/students/profile/`

**Headers:** Required (authenticated)

**Request Body:**
```json
{
  "university": "university_uuid",
  "college": "college_uuid",
  "program": "program_uuid",
  "year": 1,
  "semester": 1
}
```

**Validation Rules:**
- `university`: Must be valid UUID of existing university
- `college`: Must be valid UUID of existing college
- `program`: Must be valid UUID of existing program
- `year`: Integer, typically 1-5
- `semester`: Integer, typically 1 or 2

**Success Response (201):**
```json
{
  "id": "uuid",
  "university": { /* university object */ },
  "college": { /* college object */ },
  "program": { /* program object */ },
  "year": 1,
  "semester": 1,
  "courses": [],
  "gpa": 0.0
}
```

**Error Responses:**
- `400`: Validation errors or profile already exists
- `401`: Authentication required
- `404`: Invalid university/college/program IDs

---

### 9. Update Student Profile
**Endpoint:** `PUT /api/students/profile/`

**Headers:** Required (authenticated)

**Request Body:** Same as create

**Success Response (200):** Same as create

**Error Responses:**
- `400`: Validation errors
- `401`: Authentication required
- `404`: Student profile not found

---

## 📚 **Course Management Endpoints**

### 10. Add Course to Student
**Endpoint:** `POST /api/students/courses/`

**Headers:** Required (authenticated)

**Request Body:**
```json
{
  "course_id": "course_uuid"
}
```

**Validation Rules:**
- `course_id`: Must be valid UUID of existing course
- Student must have a profile first
- Course cannot be already added

**Success Response (201):**
```json
{
  "message": "Course added successfully",
  "course": {
    "id": "uuid",
    "code": "CS101",
    "name": "Introduction to Programming",
    "credits": 3,
    "type": "core",
    "semester": 1,
    "year": 1,
    "grade": null,
    "added_at": null
  }
}
```

**Error Responses:**
- `400`: Course already added or validation errors
- `401`: Authentication required
- `404`: Student profile or course not found

---

### 11. Remove Course from Student
**Endpoint:** `DELETE /api/students/courses/{course_id}/`

**Headers:** Required (authenticated)

**URL Parameters:**
- `course_id`: Valid UUID of course to remove

**Success Response (200):**
```json
{
  "message": "Course removed successfully"
}
```

**Error Responses:**
- `401`: Authentication required
- `404`: Course not found or not enrolled

---

### 12. Update Course Grade
**Endpoint:** `PUT /api/students/courses/{course_id}/grade/`

**Headers:** Required (authenticated)

**URL Parameters:**
- `course_id`: Valid UUID of enrolled course

**Request Body:**
```json
{
  "grade": "A"
}
```

**Validation Rules:**
- `grade`: Must be one of: "A", "B+", "B", "C", "D", "E", "F"

**Success Response (200):**
```json
{
  "message": "Grade updated successfully",
  "course": {
    "id": "uuid",
    "course": "course_uuid",
    "course_code": "CS101",
    "course_name": "Introduction to Programming",
    "course_credits": 3,
    "course_type": "core",
    "grade": "A",
    "points": 5.0
  }
}
```

**Error Responses:**
- `400`: Invalid grade or validation errors
- `401`: Authentication required
- `404`: Course not found or not enrolled

---

### 13. Get Student Courses
**Endpoint:** `GET /api/students/courses/`

**Headers:** Required (authenticated)

**Success Response (200):**
```json
{
  "id": "uuid",
  "courses": [
    {
      "id": "course_uuid",
      "code": "CS101",
      "name": "Introduction to Programming",
      "credits": 3,
      "type": "core",
      "semester": 1,
      "year": 1,
      "grade": "A",
      "added_at": "2024-01-15T10:30:00Z"
    }
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses:**
- `401`: Authentication required
- `404`: Student profile not found

---

### 14. Bulk Update Student Courses
**Endpoint:** `PUT /api/students/courses/`

**Headers:** Required (authenticated)

**Request Body:**
```json
{
  "courses": [
    {
      "id": "course_uuid",
      "code": "CS101",
      "name": "Introduction to Programming",
      "credits": 3,
      "type": "core",
      "semester": 1,
      "year": 1,
      "grade": "A",
      "added_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": "course_uuid_2",
      "code": "CS102",
      "name": "Data Structures",
      "credits": 3,
      "type": "core",
      "semester": 1,
      "year": 1,
      "grade": "B+",
      "added_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

**Validation Rules:**
- `courses`: Array of course objects
- Each course must have: `id`, `code`, `name`, `credits`, `type`, `semester`, `year`
- Optional fields: `grade`, `added_at`

**Success Response (200):**
```json
{
  "message": "Courses updated successfully",
  "courses": [
    {
      "id": "course_uuid",
      "code": "CS101",
      "name": "Introduction to Programming",
      "credits": 3,
      "type": "core",
      "semester": 1,
      "year": 1,
      "grade": "A",
      "added_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

**Error Responses:**
- `400`: Validation errors
- `401`: Authentication required
- `404`: Student profile not found

---

## 🧮 **GPA Calculation Endpoints**

### 14. Calculate Current GPA
**Endpoint:** `GET /api/students/gpa/`

**Headers:** Required (authenticated)

**Success Response (200):**
```json
{
  "gpa": 4.25,
  "total_credits": 12,
  "total_points": 51.0,
  "graded_courses": 4,
  "breakdown": [
    {
      "course_code": "CS101",
      "course_name": "Introduction to Programming",
      "credits": 3,
      "grade": "A",
      "points": 5.0,
      "contribution": 15.0
    }
  ]
}
```

**Error Responses:**
- `401`: Authentication required
- `404`: Student profile not found

---

### 15. Generate Target GPA Grades
**Endpoint:** `POST /api/students/gpa/target/`

**Headers:** Required (authenticated)

**Request Body:**
```json
{
  "target_gpa": 4.0
}
```

**Validation Rules:**
- `target_gpa`: Float between 0.0 and 5.0

**Success Response (200):**
```json
{
  "message": "Target grades generated successfully",
  "target_gpa": 4.0,
  "actual_gpa": 4.02,
  "accuracy": "excellent",
  "grades": [
    {
      "course_id": "uuid",
      "course_code": "CS101",
      "course_name": "Introduction to Programming",
      "credits": 3,
      "required_grade": "A",
      "required_points": 5.0
    }
  ]
}
```

**Error Responses:**
- `400`: Invalid target GPA or validation errors
- `401`: Authentication required
- `404`: Student profile not found

---

### 16. Reset All Grades
**Endpoint:** `POST /api/students/gpa/reset/`

**Headers:** Required (authenticated)

**Success Response (200):**
```json
{
  "message": "All grades reset to A",
  "courses_updated": 4
}
```

**Error Responses:**
- `401`: Authentication required
- `404`: Student profile not found

---

## 🚨 **Common Error Prevention Tips**

### 1. **Always Check Authentication**
- Include JWT token in Authorization header
- Handle 401 responses by redirecting to login

### 2. **Validate UUIDs**
- Ensure all UUID parameters are valid format
- Check that referenced entities exist before making requests

### 3. **Handle CORS**
- The backend is configured with `CORS_ALLOW_ALL_ORIGINS = True`
- Include proper headers for preflight requests

### 4. **Error Handling**
- Always check response status codes
- Parse error messages from response body
- Implement proper loading states

### 5. **Data Validation**
- Validate form data before sending requests
- Ensure required fields are present
- Check data types and formats

### 6. **Rate Limiting**
- Implement proper loading states
- Avoid rapid successive requests
- Handle network timeouts gracefully

---

## 🔧 **Frontend Integration Example**

```javascript
// Example API service
class AcademicAPI {
  constructor() {
    this.baseURL = 'http://localhost:8000/api';
    this.token = localStorage.getItem('token');
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { 'Authorization': `Bearer ${this.token}` })
      },
      ...options
    };

    const response = await fetch(url, config);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || error.message || 'Request failed');
    }

    return response.json();
  }

  // Authentication
  async register(userData) {
    return this.request('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(userData)
    });
  }

  async login(credentials) {
    const response = await this.request('/auth/login/', {
      method: 'POST',
      body: JSON.stringify(credentials)
    });
    this.token = response.token;
    localStorage.setItem('token', this.token);
    return response;
  }

  // Student Profile
  async getStudentProfile() {
    return this.request('/students/profile/');
  }

  async createStudentProfile(profileData) {
    return this.request('/students/profile/', {
      method: 'POST',
      body: JSON.stringify(profileData)
    });
  }

  // Courses
  async addCourse(courseId) {
    return this.request('/students/courses/', {
      method: 'POST',
      body: JSON.stringify({ course_id: courseId })
    });
  }

  async updateGrade(courseId, grade) {
    return this.request(`/students/courses/${courseId}/grade/`, {
      method: 'PUT',
      body: JSON.stringify({ grade })
    });
  }

  // GPA
  async calculateGPA() {
    return this.request('/students/gpa/');
  }

  async generateTargetGPA(targetGPA) {
    return this.request('/students/gpa/target/', {
      method: 'POST',
      body: JSON.stringify({ target_gpa: targetGPA })
    });
  }
}
```

This comprehensive guide should help you integrate the frontend with the backend without errors. Make sure to handle all the validation rules and error cases properly!
