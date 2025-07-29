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

## User Profile API

### Get Current User Profile
```http
GET /api/me/
Authorization: Bearer {token}
```
Response:
```json
{
    "id": 1,
    "username": "student123",
    "email": "student@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2024-01-15T10:30:00Z",
    "streak": {
        "current_streak": 5,
        "longest_streak": 12,
        "last_active_date": "2024-07-29"
    },
    "total_quizzes_completed": 15,
    "average_score": 78.5
}
```

## Roadmap API

### Get User Progress for Discipline
```http
GET /api/roadmap/{discipline_id}/
Authorization: Bearer {token}
```
Response:
```json
{
    "discipline_id": 4,
    "name": "Teoria Generală a Dreptului",
    "quizzes": [
        {
            "id": 4,
            "title": "Teoria generală a dreptului ca știință juridică",
            "is_completed": true,
            "score": 87.5
        },
        {
            "id": 5,
            "title": "Originea și esența statului și dreptului",
            "is_completed": false,
            "score": null
        }
    ]
}
```

## Streak Tracking API

### Get User Streak
```http
GET /api/streak/
Authorization: Bearer {token}
```
Response:
```json
{
    "current_streak": 5,
    "longest_streak": 12,
    "last_active_date": "2024-07-29"
}
```

### Update User Streak
```http
POST /api/streak/update/
Authorization: Bearer {token}
```
Response:
```json
{
    "current_streak": 6,
    "longest_streak": 12,
    "last_active_date": "2024-07-30"
}
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
Authorization: Bearer {token}
```
**Note:** This endpoint now requires authentication.
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
import AsyncStorage from '@react-native-async-storage/async-storage';

// Base API configuration
const API_BASE_URL = 'http://localhost:8000/api';

// Helper function to get auth headers
const getAuthHeaders = async () => {
    const token = await AsyncStorage.getItem('accessToken');
    return {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
    };
};

// Authentication
const login = async (username, password) => {
    const response = await fetch(`${API_BASE_URL}/auth/token/`, {
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

// Get user profile
const getUserProfile = async () => {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/me/`, {
        headers,
    });
    return await response.json();
};

// Get disciplines
const getDisciplines = async () => {
    const response = await fetch(`${API_BASE_URL}/disciplines/`);
    return await response.json();
};

// Get user's roadmap for a discipline
const getDisciplineRoadmap = async (disciplineId) => {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/roadmap/${disciplineId}/`, {
        headers,
    });
    return await response.json();
};

// Get user streak
const getUserStreak = async () => {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/streak/`, {
        headers,
    });
    return await response.json();
};

// Update user streak (for daily check-ins)
const updateStreak = async () => {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/streak/update/`, {
        method: 'POST',
        headers,
    });
    return await response.json();
};

// Take a quiz (now requires authentication)
const takeQuiz = async (quizId) => {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/quizzes/${quizId}/take/`, {
        headers,
    });
    return await response.json();
};

// Submit quiz
const submitQuiz = async (quizId, answers) => {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/quizzes/${quizId}/submit/`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ answers }),
    });
    return await response.json();
};

// Get user's quiz scores
const getUserScores = async () => {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/quizzes/my_scores/`, {
        headers,
    });
    return await response.json();
};

// Example usage in a React Native component
const HomeScreen = () => {
    const [profile, setProfile] = useState(null);
    const [streak, setStreak] = useState(null);
    
    useEffect(() => {
        const loadUserData = async () => {
            try {
                const [profileData, streakData] = await Promise.all([
                    getUserProfile(),
                    getUserStreak()
                ]);
                setProfile(profileData);
                setStreak(streakData);
            } catch (error) {
                console.error('Error loading user data:', error);
            }
        };
        
        loadUserData();
    }, []);
    
    const handleDailyCheckIn = async () => {
        try {
            const updatedStreak = await updateStreak();
            setStreak(updatedStreak);
        } catch (error) {
            console.error('Error updating streak:', error);
        }
    };
    
    return (
        <View>
            <Text>Welcome, {profile?.username}!</Text>
            <Text>Current Streak: {streak?.current_streak} days</Text>
            <Button title="Daily Check-in" onPress={handleDailyCheckIn} />
        </View>
    );
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

## Security & Permissions

### API Endpoint Permissions

**Public Endpoints (No Authentication Required):**
- `GET /api/disciplines/` - List disciplines
- `GET /api/disciplines/{id}/` - Get discipline details
- `GET /api/disciplines/{id}/quizzes/` - Get quizzes for discipline
- `GET /api/quizzes/` - List all quizzes
- `POST /api/auth/token/` - Get JWT token

**Authenticated User Endpoints:**
- `GET /api/me/` - User profile
- `GET /api/roadmap/{discipline_id}/` - User progress roadmap
- `GET /api/streak/` - User streak information
- `POST /api/streak/update/` - Update user streak
- `GET /api/quizzes/{id}/take/` - Take a quiz *(now requires auth)*
- `POST /api/quizzes/{id}/submit/` - Submit quiz answers
- `GET /api/quizzes/my_scores/` - User's quiz scores

**Admin Only Endpoints:**
- `GET /api/questions/` - Full questions with correct answers
- `GET /api/answers/` - Full answers with correct flags
- `GET /api/quizzes/{id}/` - Full quiz details with correct answers

### Security Features

- **JWT Authentication**: Tokens expire after 60 minutes, refresh tokens after 7 days
- **CORS Configuration**: Configured for Expo development and production domains
- **Automatic Streak Tracking**: Streaks update automatically on quiz completion
- **Data Privacy**: Quiz answers without correct flags for taking quizzes
- **Permission Separation**: Admin-only access to sensitive quiz data

### CORS Configuration
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:19006",   # Expo local dev
    "https://legalia.app",      # Production frontend
    "https://lawquiz.md"        # Production frontend alternative
]
```

### Production Security Notes
- Set `CORS_ALLOW_ALL_ORIGINS = False` in production
- Use HTTPS for all API communications
- Regularly rotate JWT secret keys
- Monitor API usage for suspicious activity