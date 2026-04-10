# Clinical Rotation Assignment System v2

## 📋 System Description

The **Clinical Rotation Assignment System** is a comprehensive web-based platform designed to manage and streamline clinical rotation assignments for healthcare students and institutions. It enables administrators to assign students to clinical areas, track attendance, manage student profiles, and generate detailed analytics reports. The system provides role-based access control with dedicated dashboards for both administrators and students.

## 🛠 Tech Stack

### Backend
- **Framework:** FastAPI (Python)
- **Database:** SQLite with SQLAlchemy ORM
- **Authentication:** JWT tokens with python-jose
- **Password Security:** Bcrypt hashing with passlib
- **Email Service:** SendGrid integration
- **Environment:** Python 3.8+

### Frontend
- **Framework:** React 19
- **Build Tool:** Vite
- **HTTP Client:** Axios
- **Routing:** React Router v7
- **UI Components:** Lucide React (icons)
- **Alerts:** SweetAlert2
- **Package Manager:** npm

### Development Tools
- **ESLint:** Code quality and linting
- **Concurrently:** Run multiple processes simultaneously

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** installed
- **Node.js 16+** and npm installed
- **Git** for version control

### Installation & Startup

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd Clinical-Rotation-Assignment-System-v2
```

#### 2. Set environment variables
Create a `.env` file in the root directory:
```env
SENDGRID_API_KEY=your_sendgrid_api_key
DATABASE_URL=sqlite:///./clinical_rotation.db
SECRET_KEY=your_secret_key_here
```

#### 3. Backend Setup
```bash
# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Database migrations (automatic on first run)
cd backend
```

#### 4. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install
```

#### 5. Start the Application
```bash
# From the root directory (or use the provided script)
npm start  # in frontend directory - this also starts the backend

# OR manually in separate terminals:
# Terminal 1 - Backend:
python -m uvicorn backend.main:app --reload --port 8001

# Terminal 2 - Frontend:
cd frontend && npm run dev
```

#### 6. Access the Application
- **Frontend:** http://localhost:5173 (or http://127.0.0.1:5173)
- **Backend API:** http://localhost:8001
- **API Documentation:** http://localhost:8001/docs (Swagger UI)

#### Default Credentials
- **Username:** admin
- **Password:** admin123

---

## 📊 Key Features

### Core Functionality
- **User Management:** Role-based access control (Admin, Student)
- **Student Management:** Create, update, delete student records
- **Clinical Areas:** Manage clinical rotation areas
- **Assignments:** Assign students to clinical areas
- **Attendance Tracking:** Record and monitor student attendance
- **Analytics:** Generate reports and insights on assignments and attendance
- **User Profiles:** Manage user account information and settings

### API Endpoints
- `POST /auth/login` - User authentication
- `GET/POST /students` - Student management
- `GET/POST /areas` - Clinical area management
- `GET/POST /assignments` - Assignment management
- `GET/POST /attendance` - Attendance tracking
- `GET /analytics` - Analytics and reports
- `GET/PUT /profile` - User profile management

---

## 📁 Project Structure

```
Clinical-Rotation-Assignment-System-v2/
├── backend/                 # FastAPI backend
│   ├── main.py             # Application entry point
│   ├── models.py           # SQLAlchemy database models
│   ├── schemas.py          # Pydantic schemas for validation
│   ├── crud.py             # Database operations
│   ├── database.py         # Database configuration
│   ├── auth.py             # Authentication logic
│   ├── email_service.py    # Email service integration
│   ├── requirements.txt    # Python dependencies
│   └── routers/            # API route handlers
│       ├── auth.py
│       ├── students.py
│       ├── areas.py
│       ├── assignments.py
│       ├── attendance.py
│       ├── analytics.py
│       └── profile.py
├── frontend/               # React frontend
│   ├── src/
│   │   ├── App.jsx         # Main application component
│   │   ├── main.jsx        # Entry point
│   │   ├── api.js          # API client configuration
│   │   ├── components/     # Reusable components
│   │   └── pages/          # Page components
│   ├── package.json        # Node dependencies
│   ├── vite.config.js      # Vite configuration
│   └── index.html          # HTML template
├── requirements.txt        # Root-level Python dependencies
└── README.md              # This file
```

---

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:
```env
# SendGrid Email Configuration
SENDGRID_API_KEY=your_sendgrid_key

# Database
DATABASE_URL=sqlite:///./clinical_rotation.db

# JWT Secret
SECRET_KEY=your_secret_key_for_jwt

# API Configuration
API_PORT=8001
API_HOST=0.0.0.0
```

### Database
- Uses SQLite by default (lightweight and file-based)
- Automatic schema creation on startup
- Located at `./clinical_rotation.db`

---

## 📝 Development

### Running Tests
```bash
# Backend tests (if available)
pytest backend/

# Frontend linting
cd frontend && npm run lint
```

### Building for Production
```bash
# Frontend build
cd frontend && npm run build

# Output directory: frontend/dist/
```

---

## 🐛 Troubleshooting

### Backend Issues
- **Port 8001 already in use:** Change port in `venv/Scripts/activate` or use `--port 8002`
- **Database locked:** Delete `clinical_rotation.db` and restart (data will be lost)
- **Module not found:** Ensure virtual environment is activated and dependencies installed

### Frontend Issues
- **Dependencies not installing:** Clear npm cache: `npm cache clean --force`
- **Port 5173 already in use:** Vite will automatically try the next available port
- **API connection errors:** Verify backend is running on port 8001

---

## 📚 Recommendations for README Improvement

The current README.md provides basic information. Here are recommended enhancements:

1. **API Documentation**
   - Add Swagger/OpenAPI reference link
   - Document main endpoints with examples
   - Include request/response examples for key operations

2. **Deployment Guide**
   - Add production deployment instructions
   - Include Docker setup (Dockerfile, docker-compose.yml)
   - Provide deployment checklists for common platforms (AWS, Heroku, DigitalOcean)

3. **Security Best Practices**
   - Document password requirements
   - Add CORS configuration details
   - Include JWT token expiration settings

4. **Database Management**
   - Add database backup/restore procedures
   - Document migration strategies
   - Include database schema diagram

5. **Contribution Guidelines**
   - Add code style standards
   - Document Git workflow and branch naming
   - Include pull request template

6. **Troubleshooting & FAQ**
   - Expand with common issues and solutions
   - Add performance optimization tips
   - Include debugging recommendations

7. **Additional Documentation**
   - User manual for administrators
   - Student user guide
   - API testing examples (with curl or Postman)
   - Architecture and design decisions

8. **Related Resources**
   - Link to project documentation
   - Include issue tracking references
   - Add license information

---

## 📄 License

[Add your license here]

---

## 👥 Contributors

[Add contributors information here]

---

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub or contact the development team.