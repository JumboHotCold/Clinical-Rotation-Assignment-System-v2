from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine, ensure_schema_columns
from .routers import auth as auth_router
from .routers import students
from .routers import areas
from .routers import assignments
from .routers import attendance
from .routers import analytics
from .routers import profile

# Create the database tables automatically
models.Base.metadata.create_all(bind=engine)

# Ensure all schema columns exist (handles migrations)
ensure_schema_columns()

app = FastAPI(title="Clinical Rotation Assignment API")

# Allow requests from the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:5174", "http://127.0.0.1:5174",
        "http://localhost:5175", "http://127.0.0.1:5175"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}


# Auto-seed admin on startup if not exists
@app.on_event("startup")
def create_initial_data():
    db = SessionLocal()
    # Check if admin exists
    admin_user = crud.get_user_by_username(db, "admin")
    if not admin_user:
        hashed_password = crud.get_password_hash("admin123") # Default password
        new_admin = models.User(username="admin", hashed_password=hashed_password, role="admin")
        db.add(new_admin)
        db.commit()
    
    # Check if a student exists
    student_record = db.query(models.Student).filter(models.Student.student_id_number == "C-2023-001").first()
    if not student_record:
        s1 = schemas.StudentCreate(
            student_id_number="C-2023-001",
            first_name="Jane",
            last_name="Doe",
            contact_email="jane.doe@example.com",
            contact_phone="555-0100",
            program="BS Nursing",
            year_level="3rd Year",
            password="password123"
        )
        crud.create_student(db, s1)
        
    db.close()

# Include Routers
app.include_router(auth_router.router)
app.include_router(students.router)
app.include_router(areas.router)
app.include_router(assignments.router)
app.include_router(attendance.router)
app.include_router(analytics.router)
app.include_router(profile.router)
