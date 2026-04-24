# SmartSeason Backend - Field Monitoring System

A Django REST API backend for the SmartSeason field monitoring system, enabling farm administrators and field agents to track crop progress across multiple fields during a growing season.

## Features

**User Management**
- Role-based authentication (Admin, Superadmin & Field Agent)
- JWT token authentication with cookie storage
- User registration and login
- Session management

**Field Management**
- Create and manage farm fields with comprehensive data tracking
- Assign fields to field agents
- Track field status and crop stages
- View field history and updates
- Field notes system with author tracking
- Edit field details with automatic history tracking

**Field Updates**
- Track all changes to field stage, status, and assigned agent
- Automatic field history creation for audit trail
- Each change creates separate history entry
- View complete change history with timestamps

**Dashboard Analytics**
- Admin: View all fields with status breakdown
- Agents: View assigned fields overview
- Status insights (Active, At Risk, Completed)
- Stage breakdown tracking

## Technology Stack

- **Framework**: Django 6.0
- **API**: Django REST Framework
- **Authentication**: JWT (SimpleJWT) with Cookie-based storage
- **Database**: SQLite (development), MySQL/PostgreSQL (production ready)
- **CORS**: Configured for Next.js frontend

## Installation

### Prerequisites
- Python 3.8+
- pip or conda
- Virtual environment tool (venv/virtualenv)

### Setup Instructions

1. **Clone the repository**
```bash
cd smart_season_backend
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create `.env` file**
```bash
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

5. **Apply migrations**
```bash
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Run development server**
```bash
python manage.py runserver
```

Server will be available at `http://localhost:8000`

## Field Status Logic

The system automatically calculates field status based on the following logic:

### Status Determination
- **Active**: 
  - Planted stage: Always active
  - Growing stage: Active for first 45 days since planting
  - Ready stage: Always active
  
- **At Risk**: 
  - Growing stage after 45 days since planting
  - Indicates potential issues requiring agent attention
  
- **Completed**: 
  - Harvested stage: Field has completed its cycle

### Stage Progression
1. **Planted** - Initial stage when field is created
2. **Growing** - Crop is actively developing
3. **Ready** - Crop is mature and ready for harvest
4. **Harvested** - Final stage, harvest complete

### Field History Tracking
- Every change to stage, status, or assigned agent creates a history entry
- Each change is tracked separately (multiple changes = multiple history rows)
- History includes old value, new value, changed by user, and timestamp
- Provides complete audit trail for compliance and monitoring

## API Endpoints

### Authentication

#### Register User (Admin/Superadmin Only)
```http
POST /api/users/register/
Content-Type: application/json

{
  "email": "agent@example.com",
  "full_name": "John Doe",
  "phone_number": "+254712345678",
  "password": "SecurePass123!",
  "role": "agent"
}
```

#### Login
```http
POST /api/users/login/
Content-Type: application/json

{
  "email": "agent@example.com",
  "password": "SecurePass123!"
}
```

#### Get Current User
```http
GET /api/users/me/
```

#### Logout
```http
POST /api/users/logout/
```

#### List Agents (Admin/Superadmin Only)
```http
GET /api/users/agents/
```

### Fields Management

#### List Fields
```http
GET /api/fields/fields/
```

#### Create Field (Admin/Superadmin Only)
```http
POST /api/fields/fields/
Content-Type: application/json

{
  "name": "Field Gamma",
  "location": "Nakuru",
  "crop_type": "Wheat",
  "planting_date": "2026-04-15",
  "size_in_acres": 8.75,
  "stage": "planted",
  "assigned_to_id": 2,
  "notes": "Well-irrigated field"
}
```

#### Update Field
```http
PATCH /api/fields/fields/{field_id}/
Content-Type: application/json

{
  "stage": "growing",
  "status": "active"
}
```

#### Get Field History
```http
GET /api/fields/fields/{field_id}/history/
```

#### Get Field Notes
```http
GET /api/fields/fields/{field_id}/notes/
```

#### Add Field Note
```http
POST /api/fields/fields/{field_id}/notes/
Content-Type: application/json

{
  "note": "Crop is progressing well"
}
```

#### Update Note
```http
PATCH /api/fields/notes/{note_id}/
Content-Type: application/json

{
  "note": "Updated note content"
}
```

#### Delete Note
```http
DELETE /api/fields/notes/{note_id}/
```

## Authentication Flow

1. User logs in with email and password
2. Backend verifies credentials
3. JWT tokens are generated (access + refresh)
4. Tokens are set as httponly cookies
5. Frontend automatically includes cookies in requests
6. Access token expires in 4 hours, refresh token in 7 days

### Cookie Configuration
- **access_token**: 4 hours lifetime, httponly
- **refresh_token**: 7 days lifetime, httponly
- **user_role**: Readable by frontend, 4 hours lifetime

## Database Models

### User
- Custom user model with email as username
- Roles: admin, superadmin, agent
- Phone number with +254 prefix for Kenyan numbers

### Field
- Name, location, crop type
- Planting date tracking
- Size in acres
- Stage and status fields
- Assigned agent
- Created by admin
- Timestamps and notes

### FieldNote
- Linked to field and author
- Note content
- Created and updated timestamps
- Author can edit/delete own notes
- Admin/superadmin can edit/delete any note

### FieldHistory
- Tracks changes to field attributes
- Records old value, new value
- Changed by user
- Changed at timestamp
- Separate entry for each field change

## Environment Variables

```env
SECRET_KEY=your-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

## Deployment

### Production Checklist

1. Set `DEBUG=False`
2. Generate strong `SECRET_KEY`
3. Use environment variables for sensitive data
4. Enable SSL/TLS
5. Switch to PostgreSQL or MySQL
6. Configure proper backups
7. Set up error tracking
8. Use Gunicorn or uWSGI
9. Configure Nginx reverse proxy

## Troubleshooting

### CORS Errors
- Ensure frontend URL is in `CORS_ALLOWED_ORIGINS`
- Check that cookies are being sent with `credentials: 'include'`

### Authentication Errors
- Verify JWT tokens in cookies
- Check token expiration
- Ensure user role is set correctly

### Database Errors
- Run migrations: `python manage.py migrate`
- Check database connection in `.env`

## License

This project is part of the SmartSeason Field Monitoring System.

---

**Last Updated**: April 2026  
**Version**: 1.0.0
