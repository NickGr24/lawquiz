# Legalia API Documentation

This document describes the REST API endpoints for the Legalia Django application using Django REST Framework.

## Base URL
```
http://localhost:8000/api/
https://lawquiz.md/api/
```

## Authentication

### JWT Authentication Endpoints

#### Get Access Token
```http
POST /api/auth/token/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```
Response:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Refresh Token
```http
POST /api/auth/token/refresh/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Verify Token
```http
POST /api/auth/token/verify/
Content-Type: application/json

{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Using JWT Token in Requests
Include the token in the Authorization header:
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## Disciplines (Courses) API

### List All Disciplines
```http
GET /api/disciplines/
```
Response:
```json
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 4,
            "name": "Teoria Generală a Dreptului",
            "slug": "teoria-generala-a-dreptului",
            "quiz_count": 13
        }
    ]
}
```

### Get Discipline Details (with quizzes)
```http
GET /api/disciplines/{id}/
```
Response:
```json
{
    "id": 4,
    "name": "Teoria Generală a Dreptului",
    "slug": "teoria-generala-a-dreptului",
    "quizzes": [
        {
            "id": 4,
            "title": "Teoria generală a dreptului ca știință juridică",
            "discipline": 4,
            "slug": "teoria-generala-a-dreptului-ca-stiinta-juridica",
            "question_count": 11,
            "user_score": null
        }
    ],
    "quiz_count": 13
}
```

### Get Quizzes for a Discipline
```http
GET /api/disciplines/{id}/quizzes/
```

## Quizzes API

### List All Quizzes
```http
GET /api/quizzes/
```
Response includes pagination and user scores for authenticated users.

### Get Quiz Details (with correct answers)
```http
GET /api/quizzes/{id}/
```
**Note:** This endpoint shows correct answers and is mainly for admin/review purposes.

### Take a Quiz (without correct answers)
```http
GET /api/quizzes/{id}/take/
```
Response:
```json
{
    "id": 4,
    "title": "Teoria generală a dreptului ca știință juridică",
    "questions": [
        {
            "id": 15,
            "content": "Cum pot fi divizate științele juridice?",
            "answers": [
                {
                    "id": 43,
                    "content": "teoria generală a dreptului, științele juridice istorice..."
                }
            ]
        }
    ],
    "question_count": 11
}
```

### Submit Quiz Answers
```http
POST /api/quizzes/{id}/submit/
Authorization: Bearer {token}
Content-Type: application/json

{
    "answers": {
        "15": 43,
        "16": 48,
        "17": 50
    }
}
```
Response:
```json
{
    "score": 72.73,
    "correct_answers": 8,
    "total_questions": 11,
    "passed": true,
    "results": [
        {
            "question_id": 15,
            "question": "Cum pot fi divizate științele juridice?",
            "user_answer_id": 43,
            "user_answer": "teoria generală a dreptului...",
            "correct_answer_id": 43,
            "correct_answer": "teoria generală a dreptului...",
            "is_correct": true
        }
    ]
}
```

### Get User's Quiz Scores
```http
GET /api/quizzes/my_scores/
Authorization: Bearer {token}
```
Response:
```json
[
    {
        "id": 1,
        "quiz": 4,
        "quiz_title": "Teoria generală a dreptului ca știință juridică",
        "discipline_name": "Teoria Generală a Dreptului",
        "score": 72.73
    }
]
```

## Questions API

### List All Questions
```http
GET /api/questions/
```

### Get Question Details
```http
GET /api/questions/{id}/
```

## Answers API

### List All Answers
```http
GET /api/answers/
```

### Get Answer Details
```http
GET /api/answers/{id}/
```

## Mobile App Integration

### React Native Example

```javascript
// Authentication
const login = async (username, password) => {
    const response = await fetch('http://localhost:8000/api/auth/token/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
    });
    
    const data = await response.json();
    // Store tokens in AsyncStorage
    await AsyncStorage.setItem('accessToken', data.access);
    await AsyncStorage.setItem('refreshToken', data.refresh);
    return data;
};

// Get disciplines
const getDisciplines = async () => {
    const response = await fetch('http://localhost:8000/api/disciplines/');
    return await response.json();
};

// Take a quiz
const takeQuiz = async (quizId) => {
    const response = await fetch(`http://localhost:8000/api/quizzes/${quizId}/take/`);
    return await response.json();
};

// Submit quiz
const submitQuiz = async (quizId, answers, token) => {
    const response = await fetch(`http://localhost:8000/api/quizzes/${quizId}/submit/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ answers }),
    });
    return await response.json();
};
```

## Error Handling

### Common HTTP Status Codes
- `200 OK`: Success
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Error Response Format
```json
{
    "detail": "Error message",
    "errors": {
        "field_name": ["Field-specific error message"]
    }
}
```

## Features

1. **JWT Authentication**: Secure token-based authentication
2. **CORS Enabled**: Configured for React Native frontend
3. **Pagination**: Automatic pagination for large datasets (20 items per page)
4. **User Scores**: Track quiz completion and scores per user
5. **Nested Serializers**: Optimized data structure with different detail levels
6. **Security**: Authenticated endpoints for quiz submission and score tracking
7. **Mobile Optimized**: Clean JSON responses suitable for mobile apps

## Development Setup

1. Install dependencies:
```bash
source venv/bin/activate
pip install djangorestframework djangorestframework-simplejwt django-cors-headers django-allauth requests cryptography
```

2. Run migrations:
```bash
python manage.py migrate
```

3. Start server:
```bash
python manage.py runserver
```

## Security Notes

- JWT tokens expire after 60 minutes (configurable)
- Refresh tokens expire after 7 days
- CORS is configured for localhost development
- For production, update CORS_ALLOWED_ORIGINS and set CORS_ALLOW_ALL_ORIGINS=False
- Ensure HTTPS in production for secure token transmission