# API Reference

Complete REST API documentation for the Universal Time Tracker server.

## Base URL
```
http://localhost:9000/api/v1
```

## Authentication
Currently no authentication required. All endpoints are publicly accessible.

## Response Format
All responses are in JSON format with consistent structure:

**Success Response:**
```json
{
  "data": {...},
  "message": "Success message"
}
```

**Error Response:**
```json
{
  "error": "Error description",
  "code": 400
}
```

## Endpoints

### Health Check

#### GET `/health`
Check server health and database connectivity.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-23T10:17:26.613599",
  "version": "1.0.0",
  "database": "connected"
}
```

### Projects

#### GET `/projects`
Get all projects.

**Response:**
```json
[
  {
    "id": 1,
    "name": "DADM Development",
    "type": "development",
    "language": "python",
    "framework": "flask",
    "created_at": "2025-06-23T10:06:19.224893",
    "last_activity": "2025-06-23T10:06:31.991902"
  }
]
```

#### POST `/projects`
Create or update a project.

**Request Body:**
```json
{
  "name": "My Project",
  "type": "development",
  "language": "python", 
  "framework": "flask",
  "path": "/path/to/project",
  "git_remote": "https://github.com/user/repo.git"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "My Project",
  "message": "Project created successfully"
}
```

### Sessions

#### POST `/sessions/start`
Start a new tracking session.

**Request Body:**
```json
{
  "project": "My Project",
  "description": "Working on user authentication",
  "category": "development"
}
```

**Response:**
```json
{
  "session_id": 123,
  "project": "My Project",
  "description": "Working on user authentication", 
  "category": "development",
  "start_time": "2025-06-23T10:30:00.000000",
  "message": "Session started successfully"
}
```

#### POST `/sessions/stop`
Stop the active session for a project.

**Request Body:**
```json
{
  "project": "My Project"
}
```

**Response:**
```json
{
  "session_id": 123,
  "description": "Working on user authentication",
  "duration_minutes": 45,
  "start_time": "2025-06-23T10:30:00.000000",
  "end_time": "2025-06-23T11:15:00.000000",
  "message": "Session stopped successfully"
}
```

#### POST `/sessions/break`
Start or end a break for the active session.

**Request Body:**
```json
{
  "project": "My Project",
  "break_type": "coffee"
}
```

**Response (Break Started):**
```json
{
  "action": "started",
  "break_type": "coffee",
  "start_time": "2025-06-23T10:45:00.000000",
  "message": "Break started: coffee"
}
```

**Response (Break Ended):**
```json
{
  "action": "ended",
  "break_type": "coffee", 
  "duration_minutes": 15,
  "message": "Break ended: coffee"
}
```

#### GET `/sessions/status`
Get current status for a project.

**Query Parameters:**
- `project` (required): Project name

**Response:**
```json
{
  "project": "My Project",
  "active_session": {
    "id": 123,
    "description": "Working on user authentication",
    "category": "development",
    "start_time": "2025-06-23T10:30:00.000000"
  },
  "active_break": {
    "type": "coffee",
    "start_time": "2025-06-23T10:45:00.000000"
  },
  "daily_summary": {
    "total_hours": 2.5,
    "sessions": 3
  }
}
```

#### POST `/sessions/commit`
Add git commit to active session.

**Request Body:**
```json
{
  "project": "My Project",
  "commit_hash": "abc123def456",
  "commit_message": "Add user authentication feature"
}
```

**Response:**
```json
{
  "message": "Commit linked to session",
  "commit_hash": "abc123de",
  "session_id": 123
}
```

### Reports

#### GET `/reports/{period}`
Generate time tracking reports.

**Path Parameters:**
- `period`: `today`, `week`, `month`

**Query Parameters:**
- `project` (optional): Filter by project name
- `format` (optional): Response format (`json` default)

**Response:**
```json
{
  "period": "week",
  "start_date": "2025-06-16",
  "end_date": "2025-06-22",
  "total_hours": 25.5,
  "total_sessions": 12,
  "category_breakdown": {
    "development": 18.2,
    "testing": 4.1,
    "meetings": 3.2
  },
  "project_breakdown": {
    "My Project": 20.3,
    "Other Project": 5.2
  },
  "sessions": [
    {
      "id": 123,
      "project": "My Project",
      "description": "Working on user auth",
      "category": "development",
      "start_time": "2025-06-23T10:30:00.000000",
      "end_time": "2025-06-23T11:15:00.000000",
      "duration_minutes": 45
    }
  ]
}
```

## Analytics Endpoints

### Activity Heatmap

#### GET `/analytics/heatmap`
Get GitHub-style activity heatmap data.

**Query Parameters:**
- `project` (required): Project name
- `year` (optional): Year (default: current year)

**Response:**
```json
{
  "year": 2025,
  "project": "My Project",
  "heatmap": [
    [
      {
        "date": "2025-01-01",
        "hours": 0,
        "level": 0,
        "day_of_week": 3,
        "month": 1,
        "in_year": true
      }
    ]
  ],
  "stats": {
    "total_hours": 245.5,
    "active_days": 89,
    "avg_hours_per_active_day": 2.76,
    "max_daily_hours": 8.5
  }
}
```

**Heatmap Levels:**
- `0`: No activity
- `1`: 0-2 hours
- `2`: 2-4 hours  
- `3`: 4-6 hours
- `4`: 6+ hours

### Category Breakdown

#### GET `/analytics/category-breakdown`
Get detailed category breakdown with trends.

**Query Parameters:**
- `project` (required): Project name
- `period` (optional): `week`, `month`, `quarter`, `year` (default: `month`)

**Response:**
```json
{
  "period": "month",
  "project": "My Project",
  "total_hours": 45.2,
  "categories": [
    {
      "category": "development",
      "hours": 32.1,
      "sessions": 18,
      "percentage": 71.0,
      "avg_session_duration": 1.78,
      "trend": "up",
      "daily_breakdown": {
        "2025-06-01": 2.5,
        "2025-06-02": 3.1
      }
    }
  ]
}
```

**Trend Values:**
- `up`: Increasing activity
- `down`: Decreasing activity
- `stable`: Consistent activity

### Productivity Trends

#### GET `/analytics/productivity-trends`
Get productivity trends and patterns.

**Query Parameters:**
- `project` (required): Project name
- `days` (optional): Number of days to analyze (default: 30)

**Response:**
```json
{
  "project": "My Project",
  "period_days": 30,
  "daily_breakdown": {
    "2025-06-23": {
      "hours": 3.5,
      "sessions": 2,
      "categories": ["development", "testing"]
    }
  },
  "hourly_breakdown": {
    "9": 2.1,
    "10": 3.5,
    "14": 2.8
  },
  "weekday_breakdown": {
    "Monday": 4.2,
    "Tuesday": 3.8,
    "Wednesday": 4.5
  },
  "insights": [
    "High productivity - averaging over 4 hours per day",
    "Most productive at 10:00 - 11:00",
    "Most productive on Wednesdays"
  ],
  "stats": {
    "avg_daily_hours": 3.2,
    "total_sessions": 25,
    "best_hour": 10,
    "best_weekday": "Wednesday"
  }
}
```

### Session Patterns

#### GET `/analytics/session-patterns`
Analyze session patterns and provide recommendations.

**Query Parameters:**
- `project` (required): Project name
- `days` (optional): Number of days to analyze (default: 30)

**Response:**
```json
{
  "project": "My Project",
  "period_days": 30,
  "session_lengths": {
    "average_hours": 1.8,
    "shortest_hours": 0.2,
    "longest_hours": 4.5,
    "distribution": {
      "short_sessions": 5,
      "medium_sessions": 15,
      "long_sessions": 3
    }
  },
  "break_analysis": {
    "total_break_minutes": 120,
    "break_types": {
      "coffee": {
        "count": 8,
        "avg_duration": 12.5
      },
      "lunch": {
        "count": 5,
        "avg_duration": 45.0
      }
    },
    "break_to_work_ratio": 0.15
  },
  "recommendations": [
    "Consider longer coding sessions for better flow state",
    "Great job on sustained focus!",
    "Your break timing is optimal"
  ]
}
```

## Dashboard

#### GET `/dashboard`
Serve interactive analytics dashboard (HTML page).

Visit in browser: http://localhost:9000/dashboard

Features:
- GitHub-style activity heatmap
- Interactive charts and graphs
- Real-time analytics
- Project selection and filtering

## Error Codes

- `400`: Bad Request - Invalid parameters
- `404`: Not Found - Project or resource not found
- `500`: Internal Server Error - Server error

## Rate Limiting
Currently no rate limiting implemented.

## Data Types

### Session Object
```json
{
  "id": 123,
  "project_id": 1,
  "start_time": "2025-06-23T10:30:00.000000",
  "end_time": "2025-06-23T11:15:00.000000",
  "duration_minutes": 45,
  "category": "development",
  "description": "Working on user authentication",
  "git_commits": [
    {
      "hash": "abc123",
      "message": "Add login endpoint",
      "timestamp": "2025-06-23T10:45:00.000000"
    }
  ]
}
```

### Break Object
```json
{
  "id": 456,
  "session_id": 123,
  "start_time": "2025-06-23T10:45:00.000000",
  "end_time": "2025-06-23T11:00:00.000000",
  "duration_minutes": 15,
  "break_type": "coffee"
}
```

### Project Object
```json
{
  "id": 1,
  "name": "My Project",
  "type": "development",
  "language": "python",
  "framework": "flask",
  "path": "/path/to/project",
  "git_remote": "https://github.com/user/repo.git",
  "created_at": "2025-06-23T09:00:00.000000",
  "last_activity": "2025-06-23T11:15:00.000000"
}
```
