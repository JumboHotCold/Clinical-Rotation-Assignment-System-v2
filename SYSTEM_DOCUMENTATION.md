# Clinical Rotation Assignment System - Complete Documentation

## 📌 System Overview

The **Clinical Rotation Assignment System v2** is a comprehensive web-based platform designed to manage and streamline clinical rotation assignments for healthcare students and educational institutions. The system automates the process of assigning students to clinical areas, tracking attendance, managing student profiles, and generating analytics reports while enforcing scheduling constraints and preventing conflicts.

### **Core Objectives**
- **Automate Assignment Process:** Reduce manual scheduling errors and save administrative time
- **Ensure Fair Distribution:** Balance student distribution across clinical areas
- **Prevent Scheduling Conflicts:** Validate all assignments against time slots and capacity limits
- **Provide Real-Time Visibility:** Students can view their assignments and schedules instantly
- **Generate Insights:** Administrators can analyze attendance and assignment data through analytics dashboards

---

## 🏗️ System Architecture

### **Technology Stack**

**Backend:**
- FastAPI (Python) - High-performance modern web framework
- SQLite with SQLAlchemy ORM - Lightweight, serverless database
- JWT Authentication - Secure token-based authentication
- SendGrid Email API - Automated notifications

**Frontend:**
- React 19 - Modern, responsive UI library
- Vite - Fast build tool and development server
- Axios - HTTP client for API communication
- React Router v7 - Client-side routing

### **Key Components**

```
┌─────────────────────────────────┐
│         Frontend (React)          │
│  - Admin Dashboard               │
│  - Student Dashboard             │
│  - Login Interface               │
└───────────────┬─────────────────┘
                │ HTTP/REST API
┌───────────────▼─────────────────┐
│      Backend (FastAPI)           │
│  - Authentication Router         │
│  - Student Management            │
│  - Assignment & Scheduling       │
│  - Analytics & Reporting         │
│  - Area Management               │
└───────────────┬─────────────────┘
                │ SQL Queries
┌───────────────▼─────────────────┐
│    Database (SQLite)             │
│  - Students                      │
│  - Clinical Areas                │
│  - Rotation Schedules            │
│  - Assignments                   │
│  - Attendance Records            │
└─────────────────────────────────┘
```

---

## 👥 User Roles & Permissions

### **Administrator**
- Create and manage student records
- Define clinical rotation areas and capacity
- Create rotation schedules
- Assign students to clinical areas
- Validate and approve assignments
- View analytics and reports
- Manage system-wide settings

### **Student**
- View assigned clinical area and rotation schedule
- Track their attendance records
- Receive system announcements
- Update their profile information
- View their performance analytics

---

## 📊 System Diagrams - Detailed Explanations

### **Diagram 1: System Flowchart (Overall Flow)**

![Flowchart Purpose]

The system flowchart depicts the complete end-to-end user journey split into two parallel workflows:

**Admin Workflow (Left Path):**
1. **Admin Login** → Accesses administrative dashboard
2. **Input/Manage Student Records** → Add or update student information
3. **Create Rotation Schedule** → Define time periods and clinical areas
4. **Assign Students to Clinical Areas** → Map students to rotation slots
5. **Conflicts Found?** → System validates all assignments
   - If **YES**: Return to **Adjust Schedule** to resolve conflicts (overlaps, capacity exceeded)
   - If **NO**: Proceed to save the final schedule
6. **Save Final Schedule** → Lock in assignments and trigger automated notifications

**Student Workflow (Right Path):**
1. **Student Login** → Access personal dashboard
2. **View Assigned Area & Schedule** → Display their rotation assignment (automatically updated when admin saves)
3. **Receive Announcements** → Get notifications about schedule changes
4. **End** → Session complete

**Key Insight:** The validation loop ensures no conflicts ever reach the database, maintaining data integrity and preventing scheduling errors.

---

### **Diagram 2: DFD Level 0 (Context & Main Processes)**

![DFD Level 0 Purpose]

The Data Flow Diagram Level 0 provides a high-level, bird's-eye view of the entire system, showing how data flows between external entities, processes, and databases.

**External Entities:**
- **Admin:** Initiates actions and receives alerts/confirmations
- **Student:** Queries the system and receives schedule information

**Four Main Processes:**

1. **Process 1.0 - Manage Student Records (CRUD)**
   - Receives: Student information from Admin
   - Outputs: Stores/Updates in Student Database (D1)
   - Example Actions: Create new student, update contact info, manage profiles

2. **Process 2.0 - Manage Rotation Schedule (CRUD)**
   - Receives: Schedule parameters from Admin (dates, areas, capacity)
   - Outputs: Stores formatted schedules in Rotation Schedule Database (D2)
   - Example Actions: Define rotation periods, set area capacities, create time slots

3. **Process 3.0 - Assign Clinical Areas & Validate (Core Logic)**
   - **Inputs:** Student data (D1) + Available slots (D2) + Admin commands
   - **Outputs:** Validated assignments → D2, Conflict alerts → Admin
   - **Function:** Matches students to areas while checking for conflicts
   - **Feedback Loop:** Alerts admin immediately if conflicts detected

4. **Process 4.0 - Provide Student Access (Retrieval & Display)**
   - **Inputs:** Student login request + Database queries
   - **Outputs:** Displays student schedule and information on frontend
   - **Function:** Acts as the delivery mechanism for student-facing information

**Data Stores:**
- **D1: Student Database** - Centralized student profile data
- **D2: Rotation Schedule Database** - Assignment records and slot availability

**Key Insight:** Data flows in strict sequences—students cannot see schedules until admin approves them, ensuring consistency.

---

### **Diagram 3: DFD Level 1 (Decomposition of Process 3 - Assignment Logic)**

![DFD Level 1 Purpose]

This diagram zooms into Process 3.0 (Assignment & Validation), the most critical system component, breaking it into five sub-processes that execute sequentially:

**Sub-Process 3.1 - Fetch Student Data**
- Retrieves: Student profiles, academic history, and previous rotations
- Purpose: Gather complete student context for intelligent assignment
- Output: Formatted student information passed to assignment logic

**Sub-Process 3.2 - Fetch Area Availability**
- Retrieves: Current clinical area capacities, occupied slots, time conflicts
- Purpose: Understand which slots are available and have room
- Output: Valid slot data that meets capacity constraints

**Sub-Process 3.3 - Process Tentative Assignment**
- Combines: Admin's selection (which student → which area) + data from 3.1 & 3.2
- Purpose: Create a candidate assignment before validation
- Output: Tentative assignment object for checking

**Sub-Process 3.4 - Check Conflicts & Validate**
- **Validation Rules:**
  - Is the clinical area available at requested time?
  - Does the student's schedule conflict with the assignment?
  - Is there capacity remaining in the clinical area?
  - Are prerequisites met?
- if validation **FAILS**: Alert admin with specific conflict details (return to adjust)
- if validation **SUCCEEDS**: Hand assignment to next step

**Sub-Process 3.5 - Update Final Schedule**
- Commits: Validated assignment to database
- Updates: Clinical area capacity counts
- Notifies: System records the change for audit trails
- Output: Confirmation to admin and automatic notification to student

**Key Insight:** This tiered validation approach ensures no invalid data ever enters the database. Conflicts are caught at 3.4 rather than causing problems later.

---

## 🔄 Data Flow Summary

```
Admin Input
    ↓
[Process 1.0 & 2.0] Create base data (students & schedules)
    ↓
[D1 & D2] Data saved to databases
    ↓
Admin Initiates Assignment
    ↓
[Process 3.0] Runs validation logic (3.1 → 3.2 → 3.3 → 3.4 → 3.5)
    ↓
Conflicts Detected?
    ├─→ YES: Alert Admin → Adjust Schedule → Loop back
    └─→ NO: Finalize → [D2] Save assignment
    ↓
[Process 4.0] Retrieve data for student view
    ↓
Student Login
    ↓
Display: Student Dashboard with assignments
```

---

## 🔐 Security Features

- **JWT Token Authentication:** Stateless, scalable authentication
- **Password Hashing:** Bcrypt with salt for secure password storage
- **Role-Based Access Control (RBAC):** Different permissions for Admin vs Student
- **Database Integrity:** SQLAlchemy ORM prevents SQL injection
- **Environment Variables:** Sensitive data (API keys, secrets) separated from code

---

## 📈 Key Metrics & Capabilities

| Feature | Capability |
|---------|-----------|
| **Student Management** | Add/update/delete student records with profile details |
| **Schedule Creation** | Define rotation periods with customizable dates and times |
| **Conflict Detection** | Real-time validation against overlaps and capacity |
| **Area Management** | Define clinical areas with capacity limits |
| **Attendance Tracking** | Record student attendance per rotation |
| **Analytics** | View assignment distribution, completion rates, utilization metrics |
| **Notifications** | Automated email alerts via SendGrid integration |
| **User Session** | Secure login/logout with JWT expiration |

---

## 🚀 Getting Started

### Quick Start
```bash
# Backend setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install
npm run dev

# Backend (in separate terminal)
python -m uvicorn backend.main:app --reload --port 8001
```

### Access Points
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8001
- **API Documentation:** http://localhost:8001/docs

---

## 📝 System Workflow

1. **Admin creates students & rotation schedules** → Data stored in D1 & D2
2. **Admin initiates assignments** → Runs through validation pipeline (3.1-3.5)
3. **System validates conflicts** → Either approves or alerts for adjustment
4. **Students log in** → View their approved assignments
5. **Analytics generated** → Reports on assignments, attendance, utilization

---

## 🔄 Iterative Improvement Loop

The system enforces a **validation feedback loop**:
- Assignment attempt → Validation check → Conflict detected → Admin adjusts → Retry → Success

This ensures that **no invalid assignment ever reaches the production database**, maintaining data quality and system reliability.

---

## 📁 Project Structure

```
.
├── backend/              # FastAPI application
│   ├── main.py          # Entry point
│   ├── models.py        # Database models
│   ├── schemas.py       # Request/response schemas
│   ├── database.py      # Database configuration
│   ├── auth.py          # Authentication logic
│   ├── crud.py          # Database operations
│   └── routers/         # API endpoint groups
├── frontend/            # React application
│   ├── src/
│   │   ├── components/  # Reusable React components
│   │   ├── pages/       # Page-level components
│   │   ├── api.js       # API client setup
│   │   └── main.jsx     # App root
│   └── vite.config.js   # Vite configuration
└── README.md            # Project README
```

---

## ✅ System Validation Rules

The system enforces these critical rules during assignment:
- ✔️ No student can be assigned to overlapping time slots
- ✔️ Clinical areas cannot exceed their defined capacity
- ✔️ Each student must have a unique assignment per rotation period
- ✔️ All prerequisites must be met before assignment
- ✔️ Schedule cannot be approved with unresolved conflicts

---

## 🎯 Future Enhancements (Potential)
- Mobile app for students to track attendance on-site
- Automated scheduling algorithm to suggest optimal assignments
- Integration with hospital management systems
- Advanced analytics with machine learning recommendations
- Real-time conflict resolution suggestions

---

*Documentation Last Updated: April 10, 2026*
*System Version: 2.0*
