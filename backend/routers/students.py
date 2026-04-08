from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, crud, models
from ..auth import get_db, get_current_user, get_current_admin_user
from ..email_service import send_student_welcome_email

router = APIRouter(prefix="/students", tags=["students"])

@router.post("/", response_model=schemas.Student)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    db_user = crud.get_user_by_username(db, username=student.student_id_number)
    if db_user:
        raise HTTPException(status_code=400, detail="Student ID already registered")
    
    # Create the student
    created_student = crud.create_student(db=db, student=student)
    
    # Send welcome email with default password
    default_password = student.password or "password123"
    student_full_name = f"{created_student.first_name} {created_student.last_name}"
    
    send_student_welcome_email(
        student_email=created_student.contact_email,
        student_name=student_full_name,
        default_password=default_password,
        student_id=created_student.student_id_number
    )
    
    return created_student

@router.get("/", response_model=List[schemas.Student])
def read_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_students(db, skip=skip, limit=limit)

@router.get("/me/coassignees", response_model=List[schemas.AreaStudentsSchedule])
def get_my_coassignees(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Get all areas assigned to the current student and their co-students for each area/schedule.
    Only available for students.
    """
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can access this endpoint")
    
    # Get the student profile
    student = db.query(models.Student).filter(models.Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    # Get the student's co-assignees
    coassignees = crud.get_student_coassignees(db, student.id)
    return coassignees

@router.put("/{student_id}", response_model=schemas.Student)
def update_student(student_id: int, updates: schemas.StudentUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    student = crud.update_student(db, student_id, updates)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    success = crud.delete_student(db, student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"detail": "Student deleted"}
